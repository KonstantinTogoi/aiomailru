import os

from test_sessions import login
from aiomailru.scrapers import APIScraper


class TestScrapers:
    test_acc_name = os.environ.get('AIOMAILRU_TEST_ACC_NAME', '<account_name>')
    test_app_id = os.environ.get('AIOMAILRU_TEST_APP_NAME', '<application_id>')

    print('got test account name:', test_acc_name)
    print('got test application id:', test_app_id)

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

    @staticmethod
    async def test_groups_get(acc_name, app_id):
        print('test "groups.get"')
        session = await login(acc_name, acc_name, app_id)
        api = APIScraper(session)
        resp = await api.groups.get(
            **dict(TestScrapers.params_groups_get), scrape=True
        )
        TestScrapers.check_groups_get(resp)
        await session.close()
        print('"groups.get" tested successfully')

    @staticmethod
    async def test_groups_get_info(acc_name, app_id):
        print('test "groups.getInfo"')
        session = await login(acc_name, acc_name, app_id)
        app = APIScraper(session)
        resp = await app.groups.getInfo(
            **dict(TestScrapers.params_groups_get_info), scrape=True
        )
        TestScrapers.check_groups_get_info(resp)
        await session.close()
        print('"groups.getInfo" tested successfully')

    @staticmethod
    async def test_groups_join(acc_name, app_id):
        print('test "groups.join"')
        session = await login(acc_name, acc_name, app_id)
        api = APIScraper(session)
        resp = await api.groups.join(
            **dict(TestScrapers.params_groups_join), scrape=True
        )
        TestScrapers.check_groups_join(resp)
        await session.close()
        print('"groups.join" tested successfully')

    @staticmethod
    async def test_stream_get_by_author(acc_name, app_id):
        print('test "stream.getByAuthor"')
        session = await login(acc_name, acc_name, app_id)
        api = APIScraper(session)
        resp = await api.stream.getByAuthor(
            **dict(TestScrapers.params_stream_get_by_author), scrape=True
        )
        TestScrapers.check_stream_get_by_author(resp)
        await session.close()
        print('"stream.getByAuthor" tested successfully')

    @staticmethod
    async def test(
            acc_name=test_acc_name,
            app_id=test_app_id
            ):
        await TestScrapers.test_groups_get(
            acc_name=acc_name, app_id=app_id)
        await TestScrapers.test_groups_get_info(
            acc_name=acc_name, app_id=app_id)
        await TestScrapers.test_groups_join(
            acc_name=acc_name, app_id=app_id)
        await TestScrapers.test_stream_get_by_author(
            acc_name=acc_name, app_id=app_id)
