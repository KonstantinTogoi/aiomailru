"""Test data manager."""
import json
import os

import aiomailru.logging
from aiomailru import API
from aiomailru.sessions import TokenSession, ImplicitSession


test_case_name = os.environ.get('AIOMAILRU_TEST_CASE_NAME', 'example')
accounts_path = f'data/accounts/{test_case_name}.json'
applications_path = f'data/applications/{test_case_name}.json'
cookies_path = f'data/cookies/{test_case_name}.json'
tokens_path = f'data/tokens/{test_case_name}.json'


def update_account(user_acc_name, uid):
    """Updates account uid."""

    with open(accounts_path) as f:
        accounts = json.load(f)

    accounts[user_acc_name]['uid'] = uid

    with open(accounts_path, 'w') as fw:
        json.dump(accounts, fw, indent=2)


def update_cookies(user_acc_name, app_id, user_cookies):
    """Updates user cookies."""

    with open(cookies_path) as fr:
        cookies = json.load(fr)

    if user_acc_name not in cookies:
        cookies[user_acc_name] = {}

    cookies[user_acc_name][app_id] = user_cookies

    with open(cookies_path, 'w') as fw:
        json.dump(cookies, fw, indent=2)


def update_token(user_acc_name, app_id, user_token):
    """Updates user token."""

    with open(tokens_path, 'r') as fr:
        tokens = json.load(fr)

    if user_acc_name not in tokens:
        tokens[user_acc_name] = {}

    tokens[user_acc_name][app_id] = user_token

    with open(tokens_path, 'w') as fw:
        json.dump(tokens, fw, indent=2)


async def authorize(user_acc_name, admin_acc_name, app_id):
    print('authorize', user_acc_name, 'at', app_id)

    with open(accounts_path) as f:
        accounts = json.load(f)
    with open(applications_path) as f:
        applications = json.load(f)

    acc_info = accounts[user_acc_name]
    app_info = applications.get(admin_acc_name, {
        str(app_id): {
            'app_id': int(app_id),
            'secret_key': '',
            'scope': 'stream messages'
        }
    })[app_id]

    s = await ImplicitSession(**acc_info, **app_info, pass_error=True)
    update_account(user_acc_name, s.uid)
    update_cookies(user_acc_name, app_id, s.cookies)
    update_token(user_acc_name, app_id, s.session_key)
    await s.close()


async def login(user_acc_name, admin_acc_name, app_id):
    print('login', user_acc_name, 'at', app_id)

    with open(accounts_path) as f:
        accounts = json.load(f)
    with open(applications_path) as f:
        applications = json.load(f)
    with open(cookies_path) as f:
        cookies = json.load(f)
    with open(tokens_path) as f:
        tokens = json.load(f)

    # if account wasn't authorized yet at all
    if user_acc_name not in cookies or user_acc_name not in tokens:
        await authorize(user_acc_name, admin_acc_name, app_id)
        with open(cookies_path, 'r') as fr:
            cookies = json.load(fr)
        with open(tokens_path, 'r') as fr:
            tokens = json.load(fr)

    # if account wasn't authorized at the app
    elif app_id not in cookies[user_acc_name] or \
            app_id not in tokens[user_acc_name]:
        await authorize(user_acc_name, admin_acc_name, app_id)
        with open(cookies_path, 'r') as fr:
            cookies = json.load(fr)
        with open(tokens_path, 'r') as fr:
            tokens = json.load(fr)

    acc_info = accounts[user_acc_name]
    app_info = applications.get(admin_acc_name, {
        str(app_id): {
            'app_id': int(app_id),
            'secret_key': '',
        }
    })[app_id]
    token_info = {
        'access_token': tokens[user_acc_name][app_id],
        'cookies': cookies[user_acc_name][app_id],
    }
    return TokenSession(**acc_info, **app_info, **token_info, pass_error=True)
