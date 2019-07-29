import aiohttp
import asyncio
import hashlib
import logging
from yarl import URL

from .exceptions import Error, AuthError, MyMailAuthError, APIError
from .parser import AuthPageParser
from .utils import full_scope, parseaddr, SignatureCircuit, Cookie


log = logging.getLogger(__name__)


class Session:
    """A wrapper around aiohttp.ClientSession."""

    __slots__ = ('pass_error', 'session')

    def __init__(self, pass_error=False, session=None):
        self.pass_error = pass_error
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
                content = await resp.json(content_type=self.CONTENT_TYPE)
        except aiohttp.ContentTypeError:
            msg = f'got non-REST path: {url}'
            log.error(msg)
            raise Error(msg)

        if self.pass_error:
            response = content
        elif 'error' in content:
            log.error(content['error'])
            raise APIError(content['error'])
        else:
            response = content

        return response


class TokenSession(PublicSession):
    """Session for sending authorized requests."""

    API_URL = f'{PublicSession.PUBLIC_URL}/api'
    ERROR_MSG = 'See https://api.mail.ru/docs/guides/restapi/#sig.'

    __slots__ = ('app_id', 'private_key', 'secret_key', 'session_key', 'uid')

    def __init__(self, app_id, private_key, secret_key, access_token, uid,
                 cookies=(), pass_error=False, session=None):
        super().__init__(pass_error, session)
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
            content = await resp.json(content_type=self.CONTENT_TYPE)

        if self.pass_error:
            response = content
        elif 'error' in content:
            log.error(content['error'])
            raise APIError(content['error'])
        else:
            response = content

        return response


class ClientSession(TokenSession):

    ERROR_MSG = 'Pass "uid" and "private_key" to use client-server circuit.'

    def __init__(self, app_id, private_key, access_token, uid, cookies=(),
                 pass_error=False, session=None):
        super().__init__(app_id, private_key, '', access_token, uid, cookies,
                         pass_error, session)


class ServerSession(TokenSession):

    ERROR_MSG = 'Pass "secret_key" to use server-server circuit.'

    def __init__(self, app_id, secret_key, access_token, cookies=(),
                 pass_error=False, session=None):
        super().__init__(app_id, '', secret_key, access_token, '', cookies,
                         pass_error, session)


class ImplicitSession(TokenSession):

    OAUTH_URL = 'https://connect.mail.ru/oauth/authorize'
    REDIRECT_URI = 'http%3A%2F%2Fconnect.mail.ru%2Foauth%2Fsuccess.html'

    GET_AUTH_DIALOG_ERROR_MSG = 'Failed to open authorization dialog.'
    POST_AUTH_DIALOG_ERROR_MSG = 'Form submission failed.'
    GET_ACCESS_TOKEN_ERROR_MSG = 'Failed to receive access token.'

    __slots__ = ('email', 'passwd', 'scope',
                 'expires_in', 'refresh_token', 'token_type')

    def __init__(self, app_id, private_key, secret_key, email, passwd, scope,
                 pass_error=False, session=None):
        super().__init__(app_id, private_key, secret_key, '', '', (),
                         pass_error, session)
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
        for attempt_num in range(num_attempts):
            log.debug(f'getting authorization dialog {self.OAUTH_URL}')
            url, html = await self._get_auth_dialog()

            if url.path == '/oauth/authorize':
                log.debug(f'authorizing at {url}')
                url, html = await self._post_auth_dialog(html)

            if url.path == '/oauth/success.html':
                await self._get_access_token()
                return self
            elif url.query.get('fail') == '1':
                log.error('Invalid login or password.')
                raise AuthError()

            await asyncio.sleep(retry_interval)
        else:
            log.error('Authorization failed.')
            raise Error('Authorization failed.')

    async def _get_auth_dialog(self):
        """Returns url and html code of authorization dialog."""

        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            if resp.status != 200:
                log.error(self.GET_AUTH_DIALOG_ERROR_MSG)
                raise Error(self.GET_AUTH_DIALOG_ERROR_MSG)
            else:
                url, html = resp.url, await resp.text()

        if 'Не указано приложение' in html:
            raise MyMailAuthError()

        return url, html

    async def _post_auth_dialog(self, html):
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
                log.error(self.POST_AUTH_DIALOG_ERROR_MSG)
                raise Error(self.POST_AUTH_DIALOG_ERROR_MSG)
            else:
                url, html = resp.url, await resp.text()

        return url, html

    async def _get_access_token(self):
        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            if resp.status != 200:
                log.error(self.GET_ACCESS_TOKEN_ERROR_MSG)
                raise Error(self.GET_ACCESS_TOKEN_ERROR_MSG)
            else:
                location = URL(resp.history[-1].headers['Location'])
                url = URL(f'?{location.fragment}')

        try:
            self.session_key = url.query['access_token']
            self.expires_in = url.query['expires_in']
            self.refresh_token = url.query['refresh_token']
            self.token_type = url.query['token_type']
            self.uid = url.query['x_mailru_vid']
        except KeyError as e:
            raise Error(f'"{e.args[0]}" is missing in the auth response')


class ImplicitClientSession(ImplicitSession):
    def __init__(self, app_id, private_key, email, passwd, scope,
                 pass_error=False, session=None):
        super().__init__(app_id, private_key, '', email, passwd, scope,
                         pass_error, session)


class ImplicitServerSession(ImplicitSession):
    def __init__(self, app_id, secret_key, email, passwd, scope,
                 pass_error=False, session=None):
        super().__init__(app_id, '', secret_key, email, passwd, scope,
                         pass_error, session)
