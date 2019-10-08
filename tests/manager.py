"""Test data manager."""
import json
import os

import aiomailru.logging
from aiomailru import API
from aiomailru.sessions import TokenSession, ImplicitSession


TEST_CASE_NAME = os.environ.get('AIOMAILRU_TEST_CASE_NAME', 'example')


class Manager:
    """Test data manager."""

    @property
    def accounts(self):
        with open(self.accounts_path) as f:
            return json.load(f)

    @accounts.setter
    def accounts(self, value):
        with open(self.accounts_path, 'w') as f:
            json.dump(value, f, indent=2)

    @property
    def applications(self):
        with open(self.applications_path) as f:
            return json.load(f)

    @applications.setter
    def applications(self, value):
        with open(self.applications_path, 'w') as f:
            json.dump(value, f, indent=2)

    @property
    def cookies(self):
        with open(self.cookies_path) as f:
            return json.load(f)

    @cookies.setter
    def cookies(self, value):
        with open(self.cookies_path, 'w') as f:
            json.dump(value, f, indent=2)

    @property
    def tokens(self):
        with open(self.tokens_path) as f:
            return json.load(f)

    @tokens.setter
    def tokens(self, value):
        with open(self.tokens_path, 'w') as f:
            json.dump(value, f, indent=2)

    def __init__(self, test_case_name=TEST_CASE_NAME):
        self.accounts_path = f'data/accounts/{test_case_name}.json'
        self.applications_path = f'data/applications/{test_case_name}.json'
        self.cookies_path = f'data/cookies/{test_case_name}.json'
        self.tokens_path = f'data/tokens/{test_case_name}.json'

    def update_account(self, user_acc_name, uid):
        """Updates account uid."""
        accounts = self.accounts
        accounts[user_acc_name]['uid'] = uid
        self.accounts = accounts

    def update_cookies(self, user_acc_name, app_name, user_cookies):
        """Updates user cookies."""
        cookies = self.cookies
        if user_acc_name not in cookies:
            cookies[user_acc_name] = {}
        cookies[user_acc_name][app_name] = user_cookies
        self.cookies = cookies

    def update_token(self, user_acc_name, app_name, user_token):
        """Updates user token."""
        tokens = self.tokens
        if user_acc_name not in tokens:
            tokens[user_acc_name] = {}
        tokens[user_acc_name][app_name] = user_token
        self.tokens = tokens


async def authorize(user_acc_name, admin_acc_name, app_name, app_id=0):
    print('authorize', user_acc_name, 'at', app_name)

    manager = Manager()
    accounts = manager.accounts
    applications = manager.applications

    # account must be registered in test data
    acc_info = accounts[user_acc_name]
    # if application is new
    if admin_acc_name not in applications:
        applications[admin_acc_name] = {app_name: {
            'app_id': app_id,
            'private_key': '',
            'secret_key': '',
            'scope': '',
        }}
        manager.applications = applications
    app_info = applications[admin_acc_name][app_name]

    # authorize
    s = await ImplicitSession(**acc_info, **app_info, pass_error=True)
    manager.update_account(user_acc_name, s.uid)
    manager.update_cookies(user_acc_name, app_name, s.cookies)
    manager.update_token(user_acc_name, app_name, s.session_key)
    await s.close()


async def login(user_acc_name, admin_acc_name, app_name, app_id=0):
    print('login', user_acc_name, 'at', app_name)

    manager = Manager()
    cookies = manager.cookies
    tokens = manager.tokens

    # if account wasn't authorized yet at all
    if user_acc_name not in cookies or user_acc_name not in tokens:
        await authorize(user_acc_name, admin_acc_name, app_name, app_id)
        cookies = manager.cookies
        tokens = manager.cookies

    # if account wasn't authorized at the app
    elif app_name not in cookies[user_acc_name] or \
            app_name not in tokens[user_acc_name]:
        await authorize(user_acc_name, admin_acc_name, app_name, app_id)
        cookies = manager.cookies
        tokens = manager.cookies

    accounts = manager.accounts
    applications = manager.applications

    acc_info = accounts[user_acc_name]
    app_info = applications[admin_acc_name][app_name]
    token_info = {
        'access_token': tokens[user_acc_name][app_name],
        'cookies': cookies[user_acc_name][app_name],
    }
    return TokenSession(**acc_info, **app_info, **token_info, pass_error=True)
