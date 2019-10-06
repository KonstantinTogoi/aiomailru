import json
from os.path import dirname, join
from urllib.parse import unquote

import pytest

from aiomailru.exceptions import Error, OAuthError, APIError
from aiomailru.utils import SignatureCircuit
from aiomailru.sessions import (
    PublicSession,
    TokenSession,
    ImplicitSession,
)

data_path = join(dirname(__file__), 'data')


class TestPublicSession:
    """Tests of PublicSession class."""

    @pytest.yield_fixture
    async def session(self):
        s = PublicSession()
        yield s
        await s.close()

    @pytest.fixture
    def error_content(self):
        return {
            'error': {
                'error_code': -1,
                'error_msg': 'test error msg'
            }
        }

    @pytest.fixture
    def error_session(self, httpserver, session, error_content):
        httpserver.serve_content(**{
            'code': 401,
            'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
            'content': json.dumps(error_content),
        })
        session.PUBLIC_URL = httpserver.url
        return session

    @pytest.fixture
    def resp_content(self):
        return {'key': 'value'}

    @pytest.fixture
    def resp_session(self, httpserver, session, resp_content):
        httpserver.serve_content(**{
            'code': 200,
            'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
            'content': json.dumps(resp_content)
        })
        session.PUBLIC_URL = httpserver.url
        return session

    @pytest.mark.asyncio
    async def test_public_request_error(self, error_content, error_session):
        error_session.pass_error = True
        response = await error_session.public_request()
        assert response == error_content

    @pytest.mark.asyncio
    async def test_public_request(self, resp_content, resp_session):
        resp_session.pass_error = True
        response = await resp_session.public_request()
        assert response == resp_content

        resp_session.pass_error = False
        response = await resp_session.public_request()
        assert response == resp_content

    @pytest.mark.asyncio
    async def test_public_request_exception(self, error_session):
        error_session.pass_error = False
        with pytest.raises(APIError):
            await error_session.public_request()


class TestTokenSession:
    """Tests of TokenSession class."""

    @pytest.yield_fixture
    async def session(self):
        s = TokenSession(
            app_id=123,
            private_key='"private key"',
            secret_key='"secret key"',
            access_token='"access token"',
            uid=789
        )
        yield s
        await s.close()

    @pytest.fixture
    def error_content(self):
        return {
            'error': {
                'error_code': -1,
                'error_msg': 'test error msg'
            }
        }

    @pytest.fixture
    def error_session(self, httpserver, session, error_content):
        httpserver.serve_content(**{
            'code': 401,
            'headers': {'Content-Type': TokenSession.CONTENT_TYPE},
            'content': json.dumps(error_content),
        })
        session.API_URL = httpserver.url
        return session

    @pytest.fixture
    def resp_content(self):
        return {'key': 'value'}

    @pytest.fixture
    def resp_session(self, httpserver, session, resp_content):
        httpserver.serve_content(**{
            'code': 200,
            'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
            'content': json.dumps(resp_content)
        })
        session.API_URL = httpserver.url
        return session

    def test_sig_circuit(self, session):
        assert session.sig_circuit is SignatureCircuit.CLIENT_SERVER
        session.uid = None
        assert session.sig_circuit is SignatureCircuit.SERVER_SERVER
        session.uid = 789
        session.private_key = ''
        assert session.sig_circuit is SignatureCircuit.SERVER_SERVER
        session.secret_key = ''
        assert session.sig_circuit is SignatureCircuit.UNDEFINED

    def test_required_params(self, session):
        assert 'app_id' in session.required_params
        assert 'session_key' in session.required_params
        assert 'secure' not in session.required_params
        session.private_key = ''
        assert 'secure' in session.required_params

    def test_params_to_str(self, session):
        params = {'"a"': 1, '"b"': 2, '"c"': 3}

        query = session.params_to_str(params)
        assert query == '789"a"=1"b"=2"c"=3"private key"'

        session.uid = None
        query = session.params_to_str(params)
        assert query == '"a"=1"b"=2"c"=3"secret key"'

        session.secret_key = ''
        with pytest.raises(Error):
            _ = session.params_to_str(params)

    @pytest.mark.asyncio
    async def test_request_error(self, error_content, error_session):
        error_session.pass_error = True
        response = await error_session.request(params={'key': 'value'})
        assert response == error_content

    @pytest.mark.asyncio
    async def test_request(self, resp_content, resp_session):
        resp_session.pass_error = True
        response = await resp_session.request(params={'key': 'value'})
        assert response == resp_content

        resp_session.pass_error = False
        response = await resp_session.request(params={'key': 'value'})
        assert response == resp_content

    @pytest.mark.asyncio
    async def test_request_exception(self, error_session):
        error_session.pass_error = False
        with pytest.raises(APIError):
            await error_session.request(params={'key': 'value'})


class TestImplicitSession:
    """Tests of ImplicitSession class."""

    @pytest.yield_fixture
    async def session(self):
        s = ImplicitSession(
            app_id=123,
            private_key='"private key"',
            secret_key='"secret key"',
            email='email@example.ru',
            passwd='password',
            scope='permission1 permission2 permission3',
            uid=789
        )
        yield s
        await s.close()

    @pytest.fixture
    def auth_dialog(self):
        with open(join(data_path, 'dialogs', 'auth_dialog.html')) as f:
            return f.read()

    @pytest.fixture
    def access_dialog(self):
        with open(join(data_path, 'dialogs', 'access_dialog.html')) as f:
            return f.read()

    @pytest.mark.asyncio
    async def test_get_auth_dialog(self, httpserver, session, auth_dialog):
        # success
        httpserver.serve_content(**{
            'code': 200,
            'headers': {'Content-Type': 'text/html'},
            'content': auth_dialog,
        })
        session.OAUTH_URL = httpserver.url
        url, html = await session._get_auth_dialog()

        assert url.query['client_id'] == str(session.app_id)
        assert url.query['redirect_uri'] == unquote(session.REDIRECT_URI)
        assert url.query['response_type'] == session.params['response_type']
        assert url.query['scope'] == session.scope
        assert html == auth_dialog

        # fail
        httpserver.serve_content(**{
            'code': 400,
            'headers': {'Content-Type': 'text/json'},
            'content': json.dumps({'error': '', 'error_description': ''})
        })
        with pytest.raises(OAuthError):
            _ = await session._get_auth_dialog()

    @pytest.mark.asyncio
    async def test_post_auth_dialog(self, httpserver, session,
                              auth_dialog, access_dialog):
        # success
        httpserver.serve_content(**{'code': 200, 'content': access_dialog})
        auth_dialog = auth_dialog.replace(
            'https://auth.mail.ru/cgi-bin/auth', httpserver.url,
        )
        url, html = await session._post_auth_dialog(auth_dialog)
        assert html == access_dialog

        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        with pytest.raises(OAuthError):
            _ = await session._post_auth_dialog(auth_dialog)

    @pytest.mark.asyncio
    async def test_post_access_dialog(self, httpserver, session, access_dialog):
        # success
        httpserver.serve_content(**{'code': 200, 'content': 'blank page'})
        access_dialog = access_dialog.replace(
            'https://connect.mail.ru/oauth/authorize', httpserver.url
        )
        url, html = await session._post_access_dialog(access_dialog)
        assert html == 'blank page'

        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        with pytest.raises(OAuthError):
            _ = await session._post_access_dialog(access_dialog)

    @pytest.mark.asyncio
    async def test_get_access_token(self, httpserver, session):
        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        session.OAUTH_URL = httpserver.url
        with pytest.raises(OAuthError):
            _ = await session._get_access_token()
