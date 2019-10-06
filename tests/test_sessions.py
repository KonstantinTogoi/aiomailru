import json
import pytest

from aiomailru.exceptions import Error, APIError
from aiomailru.utils import SignatureCircuit
from aiomailru.sessions import (
    PublicSession,
    TokenSession,
)


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
