import json
import pytest

from aiomailru.exceptions import APIError
from aiomailru.sessions import PublicSession


class TestPublicSession:

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
    def uid_content(self):
        return {'uid': 123456}

    @pytest.fixture
    def uid_session(self, httpserver, session, uid_content):
        httpserver.serve_content(**{
            'code': 200,
            'headers': {'Content-Type': PublicSession.CONTENT_TYPE},
            'content': json.dumps(uid_content)
        })
        session.PUBLIC_URL = httpserver.url
        return session

    @pytest.mark.asyncio
    async def test_public_request_error(self, error_content, error_session):
        error_session.pass_error = True
        response = await error_session.public_request()
        assert response == error_content

    @pytest.mark.asyncio
    async def test_public_request_uid(self, uid_content, uid_session):
        uid_session.pass_error = True
        response = await uid_session.public_request()
        assert response == uid_content

        uid_session.pass_error = False
        response = await uid_session.public_request()
        assert response == uid_content

    @pytest.mark.asyncio
    async def test_public_request_exception(self, error_session):
        error_session.pass_error = False
        with pytest.raises(APIError):
            await error_session.public_request()
