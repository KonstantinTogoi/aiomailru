Authorization
=============

The preferred way to authorize is an :code:`async with` statement.
After authorization the session will have the following attributes:

* :code:`session_key` aka :code:`access_token`
* :code:`refresh_token`
* :code:`expires_in`
* :code:`token_type` if Implicit Grant used
* :code:`uid`

Authorization Code Grant
------------------------

.. code-block:: python

    from aiomailru import CodeSession, API

    app_id = 123456
    private_key = ''
    secret_key = 'xyz'

    async with CodeSession(app_id, private_key, secret_key, code, redirect_uri) as session:
        api = API(session)
        ...

About OAuth 2.0 Authorization Code Grant: https://oauth.net/2/grant-types/authorization-code/

For more details, see https://api.mail.ru/docs/guides/oauth/sites/
and https://api.mail.ru/docs/guides/oauth/mobile-web/

Implicit Grant
--------------

.. code-block:: python

    from aiomailru import ImplicitSession, API

    app_id = 123456
    private_key = 'abcde'
    secret_key = ''

    async with ImplicitSession(app_id, private_key, secret_key, email, passwd, scope) as session:
        api = API(session)
        ...

About OAuth 2.0 Implicit Grant: https://oauth.net/2/grant-types/implicit/

For more details, see https://api.mail.ru/docs/guides/oauth/standalone/

Password Grant
--------------

.. code-block:: python

    from aiomailru import PasswordSession, API

    app_id = 123456
    private_key = 'abcde'
    secret_key = ''

    async with PasswordSession(app_id, private_key, secret_key, email, passwd, scope) as session:
        api = API(session)
        ...

About OAuth 2.0 Password Grant: https://oauth.net/2/grant-types/password/

For more details, see https://api.mail.ru/docs/guides/oauth/client-credentials/

Refresh Token
-------------

.. code-block:: python

    from aiomailru import RefreshSession, API

    app_id = 123456
    private_key = ''
    secret_key = 'xyz'

    async with RefreshSession(app_id, private_key, secret_key, refresh_token) as session:
        api = API(session)
        ...

About OAuth 2.0 Refresh Token: https://oauth.net/2/grant-types/refresh-token/

For more details, see https://api.mail.ru/docs/guides/oauth/client-credentials/#refresh_token
