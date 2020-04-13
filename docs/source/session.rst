Session
=======

The session makes **GET** requests when you call instance of :code:`APIMethod`
class that are returned as attributes of an :code:`API` class instance.

Request
-------

By default, the session
(:code:`CodeSession`, :code:`ImplicitSession`, :code:`PasswordSession`, :code:`RefreshSession`)
tries to infer which signature generation circuit to use:

* if :code:`uid` and :code:`private_key` are not empty strings - **client-server** signature generation circuit is used
* else if :code:`secret_key` is not an empty string - **server-server** signature generation circuit is used
* else exception is raised

You can explicitly set a signature generation circuit for signing requests
by passing to :code:`API` one of the sessions below.

Client-Server signature generation circuit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's consider the following example of API request with client-server signature:

.. code-block:: python

    from aiomailru import TokenSession, API

    session = TokenSession(
        app_id=423004,
        private_key='7815696ecbf1c96e6894b779456d330e',
        secret_key='',
        access_token='be6ef89965d58e56dec21acb9b62bdaa',
        uid='1324730981306483817',
    )
    api = API(session)

    friends = await api.friends.get()

It is equivalent to **GET** request:

.. code-block:: shell

    https://appsmail.ru/platform/api
        ?method=friends.get
        &app_id=423004
        &session_key=be6ef89965d58e56dec21acb9b62bdaa
        &sig=5073f15c6d5b6ab2fde23ac43332b002

The following steps were taken:

1. request parameters were sorted and concatenated - :code:`app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa`
2. :code:`uid`, sorted request parameters, :code:`private_key` were concatenated - :code:`1324730981306483817app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa7815696ecbf1c96e6894b779456d330e`
3. signature :code:`5073f15c6d5b6ab2fde23ac43332b002` calculated as MD5 of the previous string
4. signature appended to **GET** request parameters

For more details, see https://api.mail.ru/docs/guides/restapi/#client.

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

Server-Server signature generation circuit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's consider the following example of API request with server-server signature:

.. code-block:: python

    from aiomailru import TokenSession, API

    session = TokenSession(
        app_id=423004,
        private_key='',
        secret_key='3dad9cbf9baaa0360c0f2ba372d25716',
        access_token='be6ef89965d58e56dec21acb9b62bdaa',
        uid='',
    )
    api = API(session)

    friends = await api.friends.get()

It is equivalent to **GET** request:

.. code-block:: shell

    https://appsmail.ru/platform/api
        ?method=friends.get
        &app_id=423004
        &session_key=be6ef89965d58e56dec21acb9b62bdaa
        &sig=4a05af66f80da18b308fa7e536912bae

The following steps were taken:

1. parameter :code:`secure` = :code:`1` appended to parameters
2. request parameters were sorted and concatenated - :code:`app_id=423004method=friends.getsecure=1session_key=be6ef89965d58e56dec21acb9b62bdaa`
3. sorted request parameters and :code:`secret_key` were concatenated - :code:`1324730981306483817app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa3dad9cbf9baaa0360c0f2ba372d25716`
4. signature :code:`4a05af66f80da18b308fa7e536912bae` calculated as MD5 of the previous string
5. signature appended to **GET** request parameters

For more details, see  https://api.mail.ru/docs/guides/restapi/#server.

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
as :code:`dict` if executing was successful, otherwise it raises exception.

You can pass :code:`pass_error` parameter to :code:`TokenSession`
for returning original response (including errors).

Error
-----

In case of an error, by default, exception is raised.
You can pass :code:`pass_error` parameter to :code:`TokenSession`
for returning original error's body as :code:`dict`:

.. code-block:: python

    {
        "error": {
            "error_code": 202,
            "error_msg": "Access to this object is denied"
        }
    }
