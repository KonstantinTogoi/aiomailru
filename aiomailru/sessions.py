import asyncio
import hashlib
import logging

import aiohttp
from yarl import URL

from .exceptions import (
    Error,
    OAuthError,
    InvalidGrantError,
    InvalidClientError,
    InvalidUserError,
    ClientNotAvailableError,
    APIError,
    EmptyResponseError,
)
from .parsers import AuthPageParser, AccessPageParser
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

        url = self.PUBLIC_URL + '/' + '/'.join(segments)

        try:
            async with self.session.get(url, params=params) as resp:
                content = await resp.json(content_type=self.CONTENT_TYPE)
        except aiohttp.ContentTypeError:
            msg = 'got non-REST path: %s' % url
            log.error(msg)
            raise Error(msg)

        if self.pass_error:
            response = content
        elif 'error' in content:
            log.error(content)
            raise APIError(content)
        elif content:
            response = content
        else:
            log.error('got empty response: %s' % url)
            raise EmptyResponseError()

        return response


class TokenSession(PublicSession):
    """Session for executing authorized requests."""

    API_URL = PublicSession.PUBLIC_URL + '/api'
    ERROR_MSG = 'See https://api.mail.ru/docs/guides/restapi/#sig.'

    __slots__ = ('app_id', 'private_key', 'secret_key', 'session_key', 'uid')

    def __init__(self, app_id, private_key, secret_key, access_token, uid,
                 cookies=(), pass_error=False, session=None, **kwargs):
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
        query = ''.join(k + '=' + str(params[k]) for k in sorted(params))

        if self.sig_circuit is SignatureCircuit.CLIENT_SERVER:
            return str(self.uid) + query + self.private_key
        elif self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            return query + self.secret_key
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

        url = self.API_URL + '/' + '/'.join(segments)

        params = {k: params[k] for k in params if params[k]}
        params.update(self.required_params)
        params.update({'sig': self.sign_params(params)})

        async with self.session.get(url, params=params) as resp:
            content = await resp.json(content_type=self.CONTENT_TYPE)

        if self.pass_error:
            response = content
        elif 'error' in content:
            log.error(content)
            raise APIError(content)
        elif content:
            response = content
        else:
            log.error('got empty response: %s' % url)
            raise EmptyResponseError()

        return response


class ClientSession(TokenSession):
    """Session for executing requests in client applications."""

    ERROR_MSG = 'Pass "uid" and "private_key" to use client-server circuit.'

    def __init__(self, app_id, private_key, access_token, uid, cookies=(),
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, '', access_token, uid, cookies,
                         pass_error, session)


class ServerSession(TokenSession):
    """Session for executing requests in server applications."""

    ERROR_MSG = 'Pass "secret_key" to use server-server circuit.'

    def __init__(self, app_id, secret_key, access_token, cookies=(),
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, '', secret_key, access_token, '', cookies,
                         pass_error, session)


class CodeSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Authorization Code Grant).

    The Authorization Code grant is used by confidential and public
    clients to exchange an authorization code for an access token.

    .. _OAuth 2.0 Authorization Code Grant
        https://oauth.net/2/grant-types/authorization-code/

    .. _Авторизация для сайтов
        https://api.mail.ru/docs/guides/oauth/sites/

    .. _Авторизация для мобильных сайтов
        https://api.mail.ru/docs/guides/oauth/mobile-web/

    """

    OAUTH_URL = 'https://connect.mail.ru/oauth/token'
    GET_ACCESS_TOKEN_ERROR_MSG = 'Failed to receive access token.'

    __slots__ = ('code', 'redirect_uri', 'refresh_token', 'expires_in')

    def __init__(self, app_id, private_key, secret_key, code, redirect_uri,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, secret_key, '', '', (),
                         pass_error, session, **kwargs)
        self.code = code
        self.redirect_uri = redirect_uri

    @property
    def params(self):
        """Authorization request's parameters."""
        return {
            'client_id': self.app_id,
            'client_secret': self.secret_key,
            'grant_type': 'authorization_code',
            'code': self.code,
            'redirect_uri': self.redirect_uri,
        }

    async def authorize(self):
        """Authorize with OAuth 2.0 (Authorization Code)."""

        async with self.session.post(self.OAUTH_URL, data=self.params) as resp:
            content = await resp.json(content_type=self.CONTENT_TYPE)

        if 'error' in content:
            log.error(content)
            raise OAuthError(content)
        elif content:
            try:
                self.refresh_token = content['refresh_token']
                self.expires_in = content['expires_in']
                self.session_key = content['access_token']
                self.uid = content['x_mailru_vid']
            except KeyError as e:
                raise OAuthError(str(e.args[0]) + ' is missing in the response')
        else:
            raise OAuthError('got empty authorization response')

        return self


class CodeClientSession(CodeSession):
    """`CodeSession` without `secret_key` argument."""

    def __init__(self, app_id, private_key, code, redirect_uri,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, '', code, redirect_uri,
                         pass_error, session, **kwargs)


class CodeServerSession(CodeSession):
    """`CodeSession` without `private_key` argument."""

    def __init__(self, app_id, secret_key, code, redirect_uri,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, '', secret_key, code, redirect_uri,
                         pass_error, session, **kwargs)


class ImplicitSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Implicit Grant).

    The Implicit flow was a simplified OAuth flow previously recommended
    for native apps and JavaScript apps where the access token was returned
    immediately without an extra authorization code exchange step.

    .. _OAuth 2.0 Implicit Grant
        https://oauth.net/2/grant-types/implicit/

    .. _Авторизация для Standalone-приложений
        https://api.mail.ru/docs/guides/oauth/standalone/

    """

    OAUTH_URL = 'https://connect.mail.ru/oauth/authorize'
    REDIRECT_URI = 'http%3A%2F%2Fconnect.mail.ru%2Foauth%2Fsuccess.html'

    AUTHORIZE_NUM_ATTEMPTS = 1
    AUTHORIZE_RETRY_INTERVAL = 3

    GET_AUTH_DIALOG_ERROR_MSG = 'Failed to open authorization dialog.'
    POST_AUTH_DIALOG_ERROR_MSG = 'Form submission failed.'
    GET_ACCESS_TOKEN_ERROR_MSG = 'Failed to receive access token.'
    POST_ACCESS_DIALOG_ERROR_MSG = 'Failed to process access dialog.'

    __slots__ = ('email', 'passwd', 'scope',
                 'refresh_token', 'expires_in', 'token_type')

    def __init__(self, app_id, private_key, secret_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, secret_key, '', '', (),
                         pass_error, session, **kwargs)
        self.email = email
        self.passwd = passwd
        self.scope = scope or full_scope()

    @property
    def params(self):
        """Authorization request's parameters."""
        return {
            'client_id': self.app_id,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'token',
            'scope': self.scope,
        }

    async def authorize(self, num_attempts=None, retry_interval=None):
        """Authorize with OAuth 2.0 (Implicit flow)."""

        num_attempts = num_attempts or self.AUTHORIZE_NUM_ATTEMPTS
        retry_interval = retry_interval or self.AUTHORIZE_RETRY_INTERVAL

        for attempt_num in range(num_attempts):
            log.debug('getting authorization dialog %s' % self.OAUTH_URL)
            url, html = await self._get_auth_dialog()

            if 'Не указано приложение' in html:
                raise InvalidClientError()
            elif url.path == '/oauth/authorize':
                log.debug('authorizing at %s' % url)
                url, html = await self._post_auth_dialog(html)

            if url.path == '/oauth/authorize':
                if 'fail' in url.query:
                    log.error('Invalid e-mail %s or password.' % self.email)
                    raise InvalidGrantError()
                elif 'Необходим доступ к вашим данным' in html:
                    log.debug('giving rights at %s' % url)
                    url, html = await self._post_access_dialog(html)

            if 'Авторизация запрещена' in html:
                log.debug('access denied')
                raise ClientNotAvailableError()
            elif url.path == '/oauth/success.html':
                log.debug('getting access token')
                await self._get_access_token()
                log.debug('authorized successfully')
                return self
            elif url.path == '/recovery':
                log.error('User %s is blocked.' % self.email)
                raise InvalidUserError()

            await asyncio.sleep(retry_interval)
        else:
            log.error('%d login attempts exceeded.' % num_attempts)
            raise OAuthError('%d login attempts exceeded.' % num_attempts)

    async def _get_auth_dialog(self):
        """Returns url and html code of authorization dialog."""

        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            if resp.status != 200:
                log.error(self.GET_AUTH_DIALOG_ERROR_MSG)
                raise OAuthError(self.GET_AUTH_DIALOG_ERROR_MSG)
            else:
                url, html = resp.url, await resp.text()

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
        form_data['Domain'] = domain + '.ru'
        form_data['Password'] = self.passwd

        async with self.session.post(form_url, data=form_data) as resp:
            if resp.status != 200:
                log.error(self.POST_AUTH_DIALOG_ERROR_MSG)
                raise OAuthError(self.POST_AUTH_DIALOG_ERROR_MSG)
            else:
                url, html = resp.url, await resp.text()

        return url, html

    async def _post_access_dialog(self, html):
        """Clicks button 'allow' in a page with access dialog.

        Args:
            html (str): html code of the page with access form.

        Returns:
            url (URL): redirected page's URL.
            html (str): redirected page's html code.

        """

        parser = AccessPageParser()
        parser.feed(html)
        parser.close()

        form_url, form_data = parser.form

        async with self.session.post(form_url, data=form_data) as resp:
            if resp.status != 200:
                log.error(self.POST_ACCESS_DIALOG_ERROR_MSG)
                raise OAuthError(self.POST_ACCESS_DIALOG_ERROR_MSG)
            else:
                url, html = resp.url, await resp.text()

        return url, html

    async def _get_access_token(self):
        async with self.session.get(self.OAUTH_URL, params=self.params) as resp:
            if resp.status != 200:
                log.error(self.GET_ACCESS_TOKEN_ERROR_MSG)
                raise OAuthError(self.GET_ACCESS_TOKEN_ERROR_MSG)
            else:
                location = URL(resp.history[-1].headers['Location'])
                url = URL('?' + location.fragment)

        try:
            self.session_key = url.query['access_token']
            self.expires_in = url.query.get('expires_in')
            self.refresh_token = url.query['refresh_token']
            self.token_type = url.query.get('token_type')
            self.uid = url.query.get('x_mailru_vid')
        except KeyError as e:
            raise OAuthError(str(e.args[0]) + ' is missing in the response')


class ImplicitClientSession(ImplicitSession):
    """`ImplicitSession` without `secret_key` argument."""

    def __init__(self, app_id, private_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, '', email, passwd, scope,
                         pass_error, session, **kwargs)


class ImplicitServerSession(ImplicitSession):
    """`ImplicitSession` without `private_key` argument."""

    def __init__(self, app_id, secret_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, '', secret_key, email, passwd, scope,
                         pass_error, session, **kwargs)


class PasswordSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Password Grant).

    The Password grant type is a way to exchange a user's credentials
    for an access token.

    .. _OAuth 2.0 Password Grant
        https://oauth.net/2/grant-types/password/

    .. _Авторизация по логину и паролю
        https://api.mail.ru/docs/guides/oauth/client-credentials/

    """

    OAUTH_URL = 'https://appsmail.ru/oauth/token'

    __slots__ = ('email', 'passwd', 'scope', 'refresh_token', 'expires_in')

    def __init__(self, app_id, private_key, secret_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, secret_key, '', '', (),
                         pass_error, session, **kwargs)
        self.email = email
        self.passwd = passwd
        self.scope = scope or full_scope()

    @property
    def params(self):
        """Authorization request's parameters."""
        return {
            'grant_type': 'password',
            'client_id': self.app_id,
            'client_secret': self.secret_key,
            'username': self.email,
            'password': self.passwd,
            'scope': self.scope,
        }

    async def authorize(self):
        """Authorize with OAuth 2.0 (Password Grant)."""

        async with self.session.post(self.OAUTH_URL, data=self.params) as resp:
            content = await resp.json(content_type=self.CONTENT_TYPE)

        if 'error' in content:
            log.error(content)
            raise OAuthError(content)
        elif content:
            try:
                self.refresh_token = content['refresh_token']
                self.expires_in = content.get('expires_in')
                self.session_key = content['access_token']
                self.uid = content.get('x_mailru_vid')
            except KeyError as e:
                raise OAuthError(str(e.args[0]) + ' is missing in the response')
        else:
            raise OAuthError('got empty authorization response')

        return self


class PasswordClientSession(PasswordSession):
    """`PasswordSession` without `secret_key` argument."""

    def __init__(self, app_id, private_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, '', email, passwd, scope,
                         pass_error, session, **kwargs)


class PasswordServerSession(PasswordSession):
    """`PasswordSession` without `private_key` argument."""

    def __init__(self, app_id, secret_key, email, passwd, scope,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, '', secret_key, email, passwd, scope,
                         pass_error, session, **kwargs)


class RefreshSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Refresh Token).

    The Refresh Token grant type is used by clients to exchange
    a refresh token for an access token when the access token has expired.

    .. _OAuth 2.0 Refresh Token
        https://oauth.net/2/grant-types/refresh-token/

    .. _Использование refresh_token
        https://api.mail.ru/docs/guides/oauth/client-credentials/#refresh_token

    """

    OAUTH_URL = 'https://appsmail.ru/oauth/token'

    __slots__ = ('refresh_token', 'expires_in')

    def __init__(self, app_id, private_key, secret_key, refresh_token,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, secret_key, '', '', (),
                         pass_error, session, **kwargs)
        self.refresh_token = refresh_token

    @property
    def params(self):
        """Authorization request's parameters."""
        return {
            'grant_type': 'refresh_token',
            'client_id': self.app_id,
            'refresh_token': self.refresh_token,
            'client_secret': self.secret_key,
        }

    async def authorize(self):
        """Authorize with OAuth 2.0 (Refresh Token)."""

        async with self.session.post(self.OAUTH_URL, data=self.params) as resp:
            content = await resp.json(content_type=self.CONTENT_TYPE)

        if 'error' in content:
            log.error(content)
            raise OAuthError(content)
        elif content:
            try:
                self.refresh_token = content['refresh_token']
                self.expires_in = content.get('expires_in')
                self.session_key = content['access_token']
                self.uid = content.get('x_mailru_vid')
            except KeyError as e:
                raise OAuthError(str(e.args[0]) + ' is missing in the response')
        else:
            raise OAuthError('got empty authorization response')

        return self


class RefreshClientSession(RefreshSession):
    """`RefreshSession` without `secret_key` argument."""

    def __init__(self, app_id, private_key, refresh_token,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, private_key, '', refresh_token,
                         pass_error, session, **kwargs)


class RefreshServerSession(RefreshSession):
    """`RefreshSession` without `private_key` argument."""

    def __init__(self, app_id, secret_key, refresh_token,
                 pass_error=False, session=None, **kwargs):
        super().__init__(app_id, '', secret_key, refresh_token,
                         pass_error, session, **kwargs)
