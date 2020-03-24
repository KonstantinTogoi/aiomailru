import atexit
import os

import pytest

from aiomailru.sessions import ImplicitSession, TokenSession


EMAIL = os.environ.get('MAILRU_EMAIL')
PASSWD = os.environ.get('MAILRU_PASSWD')
CLIENT_ID = os.environ.get('MAILRU_CLIENT_ID')
PRIVATE_KEY = os.environ.get('MAILRU_PRIVATE_KEY')
SECRET_KEY = os.environ.get('MAILRU_SECRET_KEY')
SCOPE = os.environ.get('MAILRU_SCOPE')

BROWSER_ENDPOINT = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')

skip_scrapers = False
try:
    from aiomailru.scrapers import APIScraper
except ModuleNotFoundError:
    reasons = ['pyppeteer not found']
else:
    reasons = []
    if EMAIL is None:
        reasons.append('MAILRU_EMAIL (user e-mail) not set')
    if PASSWD is None:
        reasons.append('MAILRU_PASSWD (password) not set')
    if CLIENT_ID is None:
        reasons.append('MAILRU_CLIENT_ID (app id) not set')
    if PRIVATE_KEY is None:
        reasons.append('MAILRU_PRIVATE_KEY not set')
    if SECRET_KEY is None:
        reasons.append('MAILRU_SECRET_KEY not set')
    if SCOPE is None:
        reasons.append('MAILRU_SCOPE (permissions) not set')
    if BROWSER_ENDPOINT is None:
        reasons.append('PYPPETEER_BROWSER_ENDPOINT (Chrome endpoint) not set')


if reasons:
    skip_scrapers = True
    atexit.register(lambda: print('\n'.join(reasons)))
    atexit.register(lambda: print('Scrapers tests were skipped'))


GROUP_ID = os.environ.get(
    'MAILRU_GROUP_ID',
    '13076836623474228010'  # My@Mail.Ru official community
)


@pytest.mark.skipif(skip_scrapers, reason=';'.join(reasons))
class TestScrapers:

    @pytest.fixture
    def app(self):
        return CLIENT_ID, PRIVATE_KEY, SECRET_KEY

    @pytest.fixture
    def cred(self):
        return EMAIL, PASSWD, SCOPE

    @pytest.fixture
    async def api(self, app, cred):
        async with ImplicitSession(*app, *cred) as session:
            token = session.session_key
            cookies = session.cookies
        return APIScraper(TokenSession(*app, token, 0, cookies=cookies))

    @pytest.mark.asyncio
    async def test_groups_get(self, api: APIScraper):
        _ = await api.groups.get(scrape=True)

    @pytest.mark.asyncio
    async def test_groups_get_info(self, api: APIScraper):
        _ = await api.groups.getInfo(uids=GROUP_ID, scrape=True)

    @pytest.mark.asyncio
    async def test_groups_join(self, api: APIScraper):
        _ = await api.groups.join(group_id=GROUP_ID, scrape=True)

    @pytest.mark.asyncio
    async def test_stream_get_by_author(self, api: APIScraper):
        _ = await api.stream.getByAuthor(uid=GROUP_ID, scrape=True)
