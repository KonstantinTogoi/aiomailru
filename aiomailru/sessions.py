import aiohttp
import asyncio
import hashlib
from yarl import URL

from .exceptions import Error, AuthError, APIError
from .parser import AuthPageParser
from .utils import full_scope, parseaddr, SignatureCircuit, Cookie


class Session:
    """A wrapper around aiohttp.ClientSession."""

    __slots__ = ('session', )

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

    PUBLIC_URL = 'http://appsmail.ru/platform'
    CONTENT_TYPE = 'text/javascript; charset=utf-8'

    async def public_request(self, segments=(), params=None):
        """Requests public data.

        Args:
            segments (tuple): additional segments for URL path.
            params (dict): URL parameters.

        Returns:
            response (dict): JSON object response.

        """

        url = f'{self.PUBLIC_URL}/{"/".join(segments)}'

        try:
            async with self.session.get(url, params=params) as resp:
                status = resp.status
                response = await resp.json(content_type=self.CONTENT_TYPE)
        except aiohttp.ContentTypeError:
            raise Error(f'got non-REST path: {url}')

        if status != 200:
            raise APIError(response['error'])

        return response


class TokenSession(PublicSession):
    """Session for sending authorized requests."""

    API_URL = f'{PublicSession.PUBLIC_URL}/api'
    ERROR_MSG = 'See https://api.mail.ru/docs/guides/restapi/#sig.'

    __slots__ = ('app_id', 'private_key', 'secret_key', 'session_key', 'uid')

    def __init__(self, app_id, private_key, secret_key,
                 access_token, uid, cookies=(), session=None):
        super().__init__(session)
        self.app_id = app_id
        self.private_key = private_key
        self.secret_key = secret_key
        self.session_key = access_token
        self.uid = uid
        self.cookies = cookies

    @property
    def cookies(self):
        """HTTP cookies from cookie jar."""
        return [Cookie.from_morsel(m) for m in self.session.cookie_jar]

    @cookies.setter
    def cookies(self, cookies):
        loose_cookies = []

        for cookie in cookies:
            loose_cookie = Cookie.to_morsel(cookie)
            loose_cookies.append((loose_cookie.key, loose_cookie))

        self.session.cookie_jar.update_cookies(loose_cookies)

    @property
    def sig_circuit(self):
        if self.uid and self.private_key:
            return SignatureCircuit.CLIENT_SERVER
        elif self.secret_key:
            return SignatureCircuit.SERVER_SERVER
        else:
            return SignatureCircuit.UNDEFINED

    @property
    def required_params(self):
        """Required parameters."""
        params = {'app_id': self.app_id, 'session_key': self.session_key}
        if self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            params['secure'] = '1'
        return params

    def params_to_str(self, params):
        query = ''.join(f'{k}={str(params[k])}' for k in sorted(params))

        if self.sig_circuit is SignatureCircuit.CLIENT_SERVER:
            return f'{self.uid}{query}{self.private_key}'
        elif self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            return f'{query}{self.secret_key}'
        else:
            raise Error(self.ERROR_MSG)

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

    async def request(self, segments=(), params=()):
        """Sends a request.

        Args:
            segments (tuple): additional segments for URL path.
            params (dict): URL parameters, contains key 'method', e.g.
                {
                    "method": "stream.getByAuthor",
                    "uid": "15410773191172635989",
                    "limit": 10,
                }

        Returns:
            response (dict): JSON object response.

        """

        url = f'{self.API_URL}/{"/".join(segments)}'

        params = {k: params[k] for k in params if params[k]}
        params.update(self.required_params)
        params.update({'sig': self.sign_params(params)})

        async with self.session.get(url, params=params) as resp:
            status = resp.status
            response = await resp.json(content_type=self.CONTENT_TYPE)

        if status != 200:
            raise APIError(response['error'])

        return response


class ClientSession(TokenSession):

    ERROR_MSG = 'Pass "uid" and "private_key" to use client-server circuit.'

    def __init__(self, app_id, private_key, access_token, uid,
                 cookies=(), session=None):
        super().__init__(app_id, private_key, '',
                         access_token, uid, cookies, session)


class ServerSession(TokenSession):

    ERROR_MSG = 'Pass "secret_key" to use server-server circuit.'

    def __init__(self, app_id, secret_key, access_token,
                 cookies=(), session=None):
        super().__init__(app_id, '', secret_key,
                         access_token, '', cookies, session)


class ImplicitSession(TokenSession):

    OAUTH_URL = 'https://connect.mail.ru/oauth/authorize'
    REDIRECT_URI = 'http%3A%2F%2Fconnect.mail.ru%2Foauth%2Fsuccess.html'

    __slots__ = ('email', 'passwd', 'scope',
                 'expires_in', 'refresh_token', 'token_type')

    def __init__(self, app_id, private_key, secret_key,
                 email, passwd, scope, session=None):
        super().__init__(app_id, private_key, secret_key, '', '', (), session)
        self.email = email
        self.passwd = passwd
        self.scope = scope or full_scope()

    @property
    def params(self):
        """Authorization parameters."""
        return {
            'client_id': self.app_id,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'token',
            'scope': self.scope,
        }

    async def authorize(self, num_attempts=1, retry_interval=1):
        url, html = await self._get_auth_page()

        for attempt_num in range(num_attempts):
            if url.path.endswith('oauth/authorize'):
                url, html = await self._process_auth_form(html)

            if url.query.get('fail') == '1':
                raise AuthError('invalid login or password')

            if url.path.endswith('/oauth/success.html'):
                await self._get_auth_response()
                return self

            if attempt_num >= num_attempts:
                raise AuthError('Authorization failed')

            await asyncio.sleep(retry_interval)
            url, html = await self._get_auth_page()

    async def _get_auth_page(self):
        """Returns url and html code of authorization page."""

        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            if resp.status != 200:
                raise AuthError("Wrong 'app_id' or 'scope'.")
            url, html = resp.url, await resp.text()

        return url, html

    async def _process_auth_form(self, html):
        """Submits a form with e-mail, password and domain
        to get access token and user id.

        Args:
            html (str): authorization page's html code.

        Returns:
            url (URL): redirected page's url.
            html (str): redirected page's html code.

        """

        parser = AuthPageParser()
        parser.feed(html)
        form_url, form_data = parser.form
        parser.close()

        domain, login = parseaddr(self.email)
        form_data['Login'] = login
        form_data['Domain'] = f'{domain}.ru'
        form_data['Password'] = self.passwd

        async with self.session.post(form_url, data=form_data) as resp:
            if resp.status != 200:
                raise AuthError('Failed to process authorization form')
            url, status, html = resp.url, resp.status, await resp.text()

        return url, html

    async def _get_auth_response(self):
        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            location = URL(resp.history[-1].headers['Location'])
            url = URL(f'?{location.fragment}')

        try:
            self.session_key = url.query['access_token']
            self.expires_in = url.query['expires_in']
            self.refresh_token = url.query['refresh_token']
            self.token_type = url.query['token_type']
            self.uid = url.query['x_mailru_vid']
        except KeyError as e:
            key = e.args[0]
            raise AuthError(f'"{key}" is missing in the auth response')


class ImplicitClientSession(ImplicitSession):
    def __init__(self, app_id, private_key, email, passwd, scope, session=None):
        super().__init__(app_id, private_key, '', email, passwd, scope, session)


class ImplicitServerSession(ImplicitSession):
    def __init__(self, app_id, secret_key, email, passwd, scope, session=None):
        super().__init__(app_id, '', secret_key, email, passwd, scope, session)
