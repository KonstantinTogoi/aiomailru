import aiohttp
import asyncio
import hashlib
from yarl import URL

from aiomailru.exceptions import Error, AuthorizationError, APIError
from aiomailru.parser import AuthPageParser
from aiomailru.utils import full_scope, parseaddr, SignatureCircuit


class Session:
    """A wrapper around aiohttp.ClientSession."""

    __slots__ = 'session'

    def __init__(self, session=None):
        self.session = session or aiohttp.ClientSession()

    def __await__(self):
        return self.authorize().__await__()

    async def __aenter__(self):
        return await self.authorize()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def authorize(self):
        return self

    async def close(self):
        await self.session.close()


class PublicSession(Session):
    """Session for calling public API methods of Platform@Mail.Ru."""

    url = 'http://appsmail.ru/platform'
    content_type = 'text/javascript; charset=utf-8'

    async def request(self, path=(), params=None):
        """Requests public data.

        Args:
            path (tuple): additional parts for url, e.g. ('mail', 'grishin')
            params (dict): request's parameters

        Returns:
            response (dict): JSON object response.

        """

        url = '/'.join((self.url, *path))

        try:
            async with self.session.get(url, params=params) as resp:
                status = resp.status
                response = await resp.json(content_type=self.content_type)
        except aiohttp.ContentTypeError:
            raise Error('got non-REST path: %s' % url)

        if status != 200:
            raise APIError(response['error'])

        return response


class TokenSession(PublicSession):
    """Session for sending authorized requests."""

    url = 'http://appsmail.ru/platform/api'
    error_msg = "See https://api.mail.ru/docs/guides/restapi/#sig."

    __slots__ = 'app_id', 'private_key', 'secret_key', 'session_key', 'uid'

    def __init__(self, app_id, private_key, secret_key,
                 access_token, uid, session=None):
        super().__init__(session)
        self.app_id = app_id
        self.private_key = private_key
        self.secret_key = secret_key
        self.session_key = access_token
        self.uid = uid

    @property
    def sig_circuit(self):
        if self.uid and self.private_key:
            return SignatureCircuit.CLIENT_SERVER
        elif self.secret_key:
            return SignatureCircuit.SERVER_SERVER
        else:
            return SignatureCircuit.UNDEFINED

    @property
    def basic_params(self):
        params = {'app_id': self.app_id, 'session_key': self.session_key}
        if self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            params['secure'] = '1'
        return params

    def params_to_str(self, params):
        params = ['%s=%s' % (k, str(params[k])) for k in sorted(params)]

        if self.sig_circuit is SignatureCircuit.CLIENT_SERVER:
            return self.uid + ''.join(params) + self.private_key
        elif self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            return ''.join(params) + self.secret_key
        else:
            raise Error(self.error_msg)

    def sign_params(self, params):
        """Signs the request parameters according to signature circuit.

        Args:
            params (dict): request parameters

        Returns:
            sig (str): signature

        """

        query = self.params_to_str(params)
        sig = hashlib.md5(query.encode('UTF-8')).hexdigest()
        return sig

    async def request(self, path=(), params=None):
        """Sends an authorized request.

        Args:
            path (tuple): additional parts for url, e.g. ('mail', 'grishin')
            params (dict): request's parameters, contains key 'method', e.g.
                {
                    "method": "stream.getByAuthor",
                    "uid": "15410773191172635989",
                    "limit": 10,
                }

        Returns:
            response (dict): JSON object response.

        """

        url = '/'.join((self.url, *path))

        params = dict(params or {})
        params.update(self.basic_params)
        params.update({'sig': self.sign_params(params)})

        async with self.session.get(url, params=params) as resp:
            status = resp.status
            response = await resp.json(content_type=self.content_type)

        if status != 200:
            raise APIError(response['error'])

        return response


class ClientSession(TokenSession):

    error_msg = "Pass 'uid' and 'private_key' to use client-server circuit."

    def __init__(self, app_id, private_key, access_token, uid, session=None):
        super().__init__(app_id, private_key, '', access_token, uid, session)


class ServerSession(TokenSession):

    error_msg = "Pass 'secret_key' to use server-server circuit."

    def __init__(self, app_id, secret_key, access_token, session=None):
        super().__init__(app_id, '', secret_key, access_token, '', session)


class ImplicitSession(TokenSession):

    auth_url = 'https://connect.mail.ru/oauth/authorize'
    redirect_uri = 'http%3A%2F%2Fconnect.mail.ru%2Foauth%2Fsuccess.html'

    __slots__ = ('email', 'passwd', 'scope',
                 'expires_in', 'refresh_token', 'token_type')

    def __init__(self, app_id, private_key, secret_key,
                 email, passwd, scope, session=None):
        super().__init__(app_id, private_key, secret_key, '', '', session)
        self.email = email
        self.passwd = passwd
        self.scope = scope or full_scope()

    @property
    def params(self):
        """Authorization parameters."""
        return {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'token',
            'scope': self.scope,
        }

    async def authorize(self, num_attempts=1, retry_interval=1):
        url, html = await self._get_auth_page()

        for attempt_num in range(num_attempts):
            if url.path.endswith('oauth/authorize'):
                url, html = await self._process_auth_form(html)

            if url.query.get('fail') == '1':
                raise AuthorizationError('invalid login or password')

            if url.path.endswith('/oauth/success.html'):
                await self._get_auth_response()
                return self

            if attempt_num >= num_attempts:
                raise AuthorizationError('Authorization failed')

            await asyncio.sleep(retry_interval)
            url, html = await self._get_auth_page()

    async def _get_auth_page(self):
        """Returns url and html code of authorization page."""

        async with self.session.get(self.auth_url, params=self.params) as resp:
            if resp.status != 200:
                raise AuthorizationError("Wrong 'app_id' or 'scope'.")
            url, html = resp.url, await resp.text()

        return url, html

    async def _process_auth_form(self, html):
        """Submits a form with e-mail, password and scope
        to get access token and user id.

        Args:
            html (str): authorization page's html code

        Returns:
            url (URL): redirected page's url
            html (str): redirected page's html code

        """

        parser = AuthPageParser()
        parser.feed(html)
        form_url, form_data = parser.url, dict(parser.inputs)
        parser.close()

        domain, login = parseaddr(self.email)
        form_data['Login'] = login
        form_data['Domain'] = domain + '.ru'
        form_data['Password'] = self.passwd

        async with self.session.post(form_url, data=form_data) as resp:
            url, status, html = resp.url, resp.status, await resp.text()

        if status != 200:
            raise AuthorizationError("Failed to process authorization form")

        return url, html

    async def _get_auth_response(self):
        async with self.session.get(self.auth_url, params=self.params,
                                    allow_redirects=False) as resp:
            url = URL(resp.headers['Location'])
            url = URL('?' + url.fragment)

        try:
            self.session_key = url.query['access_token']
            self.expires_in = url.query['expires_in']
            self.refresh_token = url.query['refresh_token']
            self.token_type = url.query['token_type']
            self.uid = url.query['x_mailru_vid']
        except KeyError as e:
            key = e.args[0]
            raise AuthorizationError('%s is missing in the auth response' % key)


class ImplicitClientSession(ImplicitSession):
    def __init__(self, app_id, private_key, email, passwd, scope, session=None):
        super().__init__(app_id, private_key, '', email, passwd, scope, session)


class ImplicitServerSession(ImplicitSession):
    def __init__(self, app_id, secret_key, email, passwd, scope, session=None):
        super().__init__(app_id, '', secret_key, email, passwd, scope, session)
