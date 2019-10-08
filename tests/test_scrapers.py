import os

import pytest

skip_scrapers, reason = False, ''
try:
    from aiomailru.scrapers import APIScraper
    from manager import login
except ModuleNotFoundError:
    skip_scrapers, reason = True, 'pyppeteer not found'


test_acc_name = os.environ.get('AIOMAILRU_TEST_ACC_NAME')
test_app_name = os.environ.get('AIOMAILRU_TEST_APP_NAME')

if not test_acc_name:
    skip_scrapers, reason = True, 'account name not found'
else:
    print('got test account name:', test_acc_name)
if not test_app_name:
    skip_scrapers, reason = True, 'application name not found'
else:
    print('got test application id:', test_app_name)


@pytest.mark.skipif(skip_scrapers, reason=reason)
class TestScrapers:

    dummy_params = ()
    params_groups_get = dummy_params
    params_groups_get_info = dummy_params
    params_groups_join = dummy_params
    params_stream_get_by_author = dummy_params

    @staticmethod
    def dummy_check(response):
        assert True

    check_groups_get = dummy_check
    check_groups_get_info = dummy_check
    check_groups_join = dummy_check
    check_stream_get_by_author = dummy_check

    async def test_groups_get(self, acc_name, app_name):
        print('test "groups.get"')
        session = await login(acc_name, acc_name, app_name)
        api = APIScraper(session)
        resp = await api.groups.get(
            **dict(self.params_groups_get), scrape=True
        )
        self.check_groups_get(resp)
        await session.close()
        print('"groups.get" tested successfully')

    async def test_groups_get_info(self, acc_name, app_name):
        print('test "groups.getInfo"')
        session = await login(acc_name, acc_name, app_name)
        app = APIScraper(session)
        resp = await app.groups.getInfo(
            **dict(self.params_groups_get_info), scrape=True
        )
        TestScrapers.check_groups_get_info(resp)
        await session.close()
        print('"groups.getInfo" tested successfully')

    async def test_groups_join(self, acc_name, app_name):
        print('test "groups.join"')
        session = await login(acc_name, acc_name, app_name)
        api = APIScraper(session)
        resp = await api.groups.join(
            **dict(self.params_groups_join), scrape=True
        )
        self.check_groups_join(resp)
        await session.close()
        print('"groups.join" tested successfully')

    async def test_stream_get_by_author(self, acc_name, app_name):
        print('test "stream.getByAuthor"')
        session = await login(acc_name, acc_name, app_name)
        api = APIScraper(session)
        resp = await api.stream.getByAuthor(
            **dict(self.params_stream_get_by_author), scrape=True
        )
        self.check_stream_get_by_author(resp)
        await session.close()
        print('"stream.getByAuthor" tested successfully')

    async def test(self, acc_name=test_acc_name, app_name=test_app_name):
        await self.test_groups_get(acc_name, app_name)
        await self.test_groups_get_info(acc_name, app_name)
        await self.test_groups_join(acc_name, app_name)
        await self.test_stream_get_by_author(acc_name, app_name)
