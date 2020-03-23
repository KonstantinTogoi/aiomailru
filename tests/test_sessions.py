import json
from os.path import dirname, join
from urllib.parse import unquote

import pytest

from aiomailru.exceptions import (
    Error, OAuthError, APIError, EmptyResponseError
)
from aiomailru.utils import SignatureCircuit
from aiomailru.sessions import (
    PublicSession,
    TokenSession,
    ImplicitSession,
)

data_path = join(dirname(__file__), 'data')


class TestPublicSession:
    """Tests of PublicSession class."""

    @pytest.mark.asyncio
    async def test_error_request(self, error_server, error):
        async with PublicSession() as session:
            session.PUBLIC_URL = error_server.url

            session.pass_error = True
            response = await session.public_request()
            assert response == error

    @pytest.mark.asyncio
    async def test_error_request_with_raising(self, error_server):
        async with PublicSession() as session:
            session.PUBLIC_URL = error_server.url

            session.pass_error = False
            with pytest.raises(APIError):
                await session.public_request()

    @pytest.mark.asyncio
    async def test_dummy_request(self, dummy_server, dummy):
        async with PublicSession() as session:
            session.PUBLIC_URL = dummy_server.url

            session.pass_error = True
            response = await session.public_request()
            assert response == dummy

    @pytest.mark.asyncio
    async def test_dummy_request_with_raising(self, dummy_server):
        async with PublicSession() as session:
            session.PUBLIC_URL = dummy_server.url

            session.pass_error = False
            with pytest.raises(EmptyResponseError):
                await session.public_request()

    @pytest.mark.asyncio
    async def test_data_request(self, data_server, data):
        async with PublicSession() as session:
            session.PUBLIC_URL = data_server.url

            session.pass_error = True
            response = await session.public_request()
            assert response == data

            session.pass_error = False
            response = await session.public_request()
            assert response == data


class TestTokenSession:
    """Tests of TokenSession class."""

    @pytest.fixture
    def app(self):
        return {'app_id': 123, 'private_key': '', 'secret_key': ''}

    @pytest.fixture
    def token(self):
        return {'access_token': '', 'uid': 0}

    @pytest.mark.asyncio
    async def test_sig_circuit(self, app, token):
        async with TokenSession(**app, **token) as session:
            assert session.sig_circuit is SignatureCircuit.UNDEFINED

            session.secret_key = 'secret key'
            assert session.sig_circuit is SignatureCircuit.SERVER_SERVER

            session.uid = 456
            session.private_key = 'private key'
            assert session.sig_circuit is SignatureCircuit.CLIENT_SERVER

    @pytest.mark.asyncio
    async def test_required_params(self, app, token):
        async with TokenSession(**app, **token) as session:
            assert 'app_id' in session.required_params
            assert 'session_key' in session.required_params
            assert 'secure' not in session.required_params
            session.uid = 456
            session.private_key = ''
            session.secret_key = 'secret key'
            assert 'secure' in session.required_params

    @pytest.mark.asyncio
    async def test_params_to_str(self, app, token):
        async with TokenSession(**app, **token) as session:
            params = {'"a"': 1, '"b"': 2, '"c"': 3}

            session.uid = 789
            session.private_key = 'private key'
            query = session.params_to_str(params)
            assert query == '789"a"=1"b"=2"c"=3private key'

            session.uid = 0
            session.private_key = ''
            session.secret_key = 'secret key'
            query = session.params_to_str(params)
            assert query == '"a"=1"b"=2"c"=3secret key'

            session.secret_key = ''
            with pytest.raises(Error):
                _ = session.params_to_str(params)

    @pytest.mark.asyncio
    async def test_error_request(self, app, token, error_server, error):
        async with TokenSession(**app, **token) as session:
            session.API_URL = error_server.url
            session.secret_key = 'secret key'

            session.pass_error = True
            response = await session.request(params={'key': 'value'})
            assert response == error

    @pytest.mark.asyncio
    async def test_error_request_with_raising(self, app, token, error_server):
        async with TokenSession(**app, **token) as session:
            session.API_URL = error_server.url
            session.secret_key = 'secret key'

            session.pass_error = False
            with pytest.raises(APIError):
                await session.request(params={'key': 'value'})

    @pytest.mark.asyncio
    async def test_dummy_request(self, app, token, dummy_server, dummy):
        async with TokenSession(**app, **token) as session:
            session.API_URL = dummy_server.url
            session.secret_key = 'secret key'

            session.pass_error = True
            response = await session.request(params={'key': 'value'})
            assert response == dummy

    @pytest.mark.asyncio
    async def test_dummy_request_with_raising(self, app, token, dummy_server):
        async with TokenSession(**app, **token) as session:
            session.API_URL = dummy_server.url
            session.secret_key = 'secret key'

            session.pass_error = False
            with pytest.raises(EmptyResponseError):
                await session.request(params={'key': 'value'})

    @pytest.mark.asyncio
    async def test_data_request(self, app, token, data_server, data):
        async with TokenSession(**app, **token) as session:
            session.API_URL = data_server.url
            session.secret_key = 'secret key'

            session.pass_error = True
            response = await session.request(params={'key': 'value'})
            assert response == data

            session.pass_error = False
            response = await session.request(params={'key': 'value'})
            assert response == data


class TestImplicitSession:
    """Tests of ImplicitSession class."""

    @pytest.fixture
    def app(self):
        return {'app_id': 123, 'private_key': '', 'secret_key': ''}

    @pytest.fixture
    def cred(self):
        return {
            'email': 'email@example.ru',
            'passwd': 'password',
            'scope': 'permission1 permission2 permission3',
        }

    @pytest.mark.asyncio
    async def test_get_auth_dialog(self, app, cred, httpserver, auth_dialog):
        # success
        httpserver.serve_content(**{
            'code': 200,
            'headers': {'Content-Type': 'text/html'},
            'content': auth_dialog,
        })
        session = ImplicitSession(**app, **cred)
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

        await session.close()

    @pytest.mark.asyncio
    async def test_post_auth_dialog(self, app, cred, httpserver,
                                    auth_dialog, access_dialog):
        # success
        httpserver.serve_content(**{'code': 200, 'content': access_dialog})
        session = ImplicitSession(**app, **cred)

        auth_dialog = auth_dialog.replace(
            'https://auth.mail.ru/cgi-bin/auth', httpserver.url,
        )
        url, html = await session._post_auth_dialog(auth_dialog)
        assert html == access_dialog

        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        with pytest.raises(OAuthError):
            _ = await session._post_auth_dialog(auth_dialog)

        await session.close()

    @pytest.mark.asyncio
    async def test_post_access_dialog(self, app, cred, httpserver, access_dialog):
        # success
        httpserver.serve_content(**{'code': 200, 'content': 'blank page'})
        session = ImplicitSession(**app, **cred)

        access_dialog = access_dialog.replace(
            'https://connect.mail.ru/oauth/authorize', httpserver.url
        )
        url, html = await session._post_access_dialog(access_dialog)
        assert html == 'blank page'

        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        with pytest.raises(OAuthError):
            _ = await session._post_access_dialog(access_dialog)

        await session.close()

    @pytest.mark.asyncio
    async def test_get_access_token(self, app, cred, httpserver):
        # fail
        httpserver.serve_content(**{'code': 400, 'content': ''})
        session = ImplicitSession(**app, **cred)
        session.OAUTH_URL = httpserver.url

        with pytest.raises(OAuthError):
            _ = await session._get_access_token()

        await session.close()
