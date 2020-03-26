Session
=======

By default, the session tries to infer which signature circuit to use:

* if :code:`uid` and :code:`private_key` are not empty strings - **client-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#client
* else if :code:`secret_key` is not an empty string - **server-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#server
* else exception is raised

You can explicitly choose a circuit for signing requests by passing
to :code:`API` one of the following sessions:

Client-Server signature circuit
-------------------------------

ClientSession
~~~~~~~~~~~~~

:code:`ClientSession` is a subclass of :code:`TokenSession`.

.. code-block:: python

    from aiomailru import ClientSession, API

    session = ClientSession(app_id, 'private key', 'access token', uid)
    api = API(session)

CodeClientSession
~~~~~~~~~~~~~~~~~

:code:`CodeClientSession` is a subclass of :code:`CodeSession`.

.. code-block:: python

    from aiomailru import CodeClientSession, API

    async with CodeClientSession(app_id, 'private key', code, redirect_uri) as session:
        api = API(session)

ImplicitClientSession
~~~~~~~~~~~~~~~~~~~~~

:code:`ImplicitClientSession` is a subclass of :code:`ImplicitSession`.

.. code-block:: python

    from aiomailru import ImplicitClientSession, API

    async with ImplicitClientSession(app_id, 'private key', email, passwd, scope) as session:
        api = API(session)

PasswordClientSession
~~~~~~~~~~~~~~~~~~~~~

:code:`PasswordClientSession` is a subclass of :code:`PasswordSession`.

.. code-block:: python

    from aiomailru import PasswordClientSession, API

    async with PasswordClientSession(app_id, 'private key', email, passwd, scope) as session:
        api = API(session)

RefreshClientSession
~~~~~~~~~~~~~~~~~~~~

:code:`RefreshClientSession` is a subclass of :code:`RefreshSession`.

.. code-block:: python

    from aiomailru import RefreshClientSession, API

    async with RefreshClientSession(app_id, 'private key', refresh_token) as session:
        api = API(session)

Server-Server signature circuit
-------------------------------

ServerSession
~~~~~~~~~~~~~

:code:`ServerSession` is a subclass of :code:`TokenSession`.

.. code-block:: python

    from aiomailru import ServerSession, API

    session = ServerSession(app_id, 'secret key', 'access token')
    api = API(session)

CodeServerSession
~~~~~~~~~~~~~~~~~

:code:`CodeServerSession` is a subclass of :code:`CodeSession`.

.. code-block:: python

    from aiomailru import CodeServerSession, API

    async with CodeServerSession(app_id, 'secret key', code, redirect_uri) as session:
        api = API(session)

ImplicitServerSession
~~~~~~~~~~~~~~~~~~~~~

:code:`ImplicitServerSession` is a subclass of :code:`ImplicitSession`.

.. code-block:: python

    from aiomailru import ImplicitServerSession, API

    async with ImplicitServerSession(app_id, 'secret key', email, passwd, scope) as session:
        api = API(session)

PasswordServerSession
~~~~~~~~~~~~~~~~~~~~~

:code:`PasswordServerSession` is a subclass of :code:`PasswordSession`.

.. code-block:: python

    from aiomailru import PasswordServerSession, API

    async with PasswordServerSession(app_id, 'secret key', email, passwd scope) as session:
        api = API(session)

RefreshServerSession
~~~~~~~~~~~~~~~~~~~~

:code:`RefreshServerSession` is a subclass of :code:`RefreshSession`.

.. code-block:: python

    from aiomailru import RefreshServerSession, API

    async with RefreshServerSession(app_id, 'secret key', refresh_token) as session:
        api = API(session)
