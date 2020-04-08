Session
=======

Request
-------

The session makes **GET** requests when you call methods of an :code:`API` instance.
Lets consider example at https://api.mail.ru/docs/guides/restapi/#client:

.. code-block:: python

    from aiomailru import TokenSession, API

    app_id = 123456
    private_key = '7815696ecbf1c96e6894b779456d330e'
    secret_key = ''
    session_key = 'be6ef89965d58e56dec21acb9b62bdaa'
    uid = '1324730981306483817'

    session = TokenSession(app_id, private_key, secret_key, access_token, uid)
    api = API(session)

    events = await api.stream.get()

is equivalent to the following **GET** request:

.. code-block:: shell

    https://appsmail.ru/platform/api?method=stream.get&app_id=123456&session_key=be6ef89965d58e56dec21acb9b62bdaa&sig=5073f15c6d5b6ab2fde23ac43332b002

By default, the session tries to infer which signature circuit to use:

* if :code:`uid` and :code:`private_key` are not empty strings - **client-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#client
* else if :code:`secret_key` is not an empty string - **server-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#server
* else exception is raised

You can explicitly choose a circuit for signing requests by passing
to :code:`API` one of the following sessions:

Client-Server signature circuit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ClientSession
^^^^^^^^^^^^^

:code:`ClientSession` is a subclass of :code:`TokenSession`.

.. code-block:: python

    from aiomailru import ClientSession, API

    session = ClientSession(app_id, 'private key', 'access token', uid)
    api = API(session)
    ...

CodeClientSession
^^^^^^^^^^^^^^^^^

:code:`CodeClientSession` is a subclass of :code:`CodeSession`.

.. code-block:: python

    from aiomailru import CodeClientSession, API

    async with CodeClientSession(app_id, 'private key', code, redirect_uri) as session:
        api = API(session)
        ...

ImplicitClientSession
^^^^^^^^^^^^^^^^^^^^^

:code:`ImplicitClientSession` is a subclass of :code:`ImplicitSession`.

.. code-block:: python

    from aiomailru import ImplicitClientSession, API

    async with ImplicitClientSession(app_id, 'private key', email, passwd, scope) as session:
        api = API(session)
        ...

PasswordClientSession
^^^^^^^^^^^^^^^^^^^^^

:code:`PasswordClientSession` is a subclass of :code:`PasswordSession`.

.. code-block:: python

    from aiomailru import PasswordClientSession, API

    async with PasswordClientSession(app_id, 'private key', email, passwd, scope) as session:
        api = API(session)
        ...

RefreshClientSession
^^^^^^^^^^^^^^^^^^^^

:code:`RefreshClientSession` is a subclass of :code:`RefreshSession`.

.. code-block:: python

    from aiomailru import RefreshClientSession, API

    async with RefreshClientSession(app_id, 'private key', refresh_token) as session:
        api = API(session)
        ...

Server-Server signature circuit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ServerSession
^^^^^^^^^^^^^

:code:`ServerSession` is a subclass of :code:`TokenSession`.

.. code-block:: python

    from aiomailru import ServerSession, API

    session = ServerSession(app_id, 'secret key', 'access token')
    api = API(session)
    ...

CodeServerSession
^^^^^^^^^^^^^^^^^

:code:`CodeServerSession` is a subclass of :code:`CodeSession`.

.. code-block:: python

    from aiomailru import CodeServerSession, API

    async with CodeServerSession(app_id, 'secret key', code, redirect_uri) as session:
        api = API(session)
        ...

ImplicitServerSession
^^^^^^^^^^^^^^^^^^^^^

:code:`ImplicitServerSession` is a subclass of :code:`ImplicitSession`.

.. code-block:: python

    from aiomailru import ImplicitServerSession, API

    async with ImplicitServerSession(app_id, 'secret key', email, passwd, scope) as session:
        api = API(session)
        ...

PasswordServerSession
^^^^^^^^^^^^^^^^^^^^^

:code:`PasswordServerSession` is a subclass of :code:`PasswordSession`.

.. code-block:: python

    from aiomailru import PasswordServerSession, API

    async with PasswordServerSession(app_id, 'secret key', email, passwd, scope) as session:
        api = API(session)
        ...

RefreshServerSession
^^^^^^^^^^^^^^^^^^^^

:code:`RefreshServerSession` is a subclass of :code:`RefreshSession`.

.. code-block:: python

    from aiomailru import RefreshServerSession, API

    async with RefreshServerSession(app_id, 'secret key', refresh_token) as session:
        api = API(session)
        ...

Response
--------

By default, a session after executing request returns response's body
as :code:`dict` if executing was successful, otherwise it raises an exception.

You can pass :code:`pass_error` parameter to :code:`TokenSession`
for returning original response (including errors).

Error
-----

In case of an error, by default, an exception is raised.
You can pass :code:`pass_error` parameter to :code:`TokenSession`
for returning original error's body as :code:`dict`:

.. code-block:: python

    {"error": {"error_code": 202, "error_msg": "Access to this object is denied"}}
