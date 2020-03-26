.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: https://github.com/KonstantinTogoi/aiomailru/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/aiomailru.svg
    :target: https://pypi.python.org/pypi/aiomailru

.. image:: https://img.shields.io/pypi/pyversions/aiomailru.svg
    :target: https://pypi.python.org/pypi/aiomailru

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
    :target: https://aiomailru.readthedocs.io/en/latest/

.. image:: https://travis-ci.org/KonstantinTogoi/aiomailru.svg
    :target: https://travis-ci.org/KonstantinTogoi/aiomailru

.. index-start-marker1

aiomailru
=========

aiomailru is a `my.mail.ru <https://my.mail.ru>`_ python API wrapper.
The main features are:

* authorization (`Authorization Code <https://oauth.net/2/grant-types/authorization-code/>`_, `Implicit Flow <https://oauth.net/2/grant-types/implicit/>`_, `Password Grant <https://oauth.net/2/grant-types/password/>`_, `Refresh Token <https://oauth.net/2/grant-types/refresh-token/>`_)
* `REST API <https://api.mail.ru/docs/reference/rest/>`_ methods
* web scrapers

Usage
-----

To use Platform@Mail.Ru API you need a registered app and
`Mail.Ru <https://mail.ru>`_ account.
For more details, see
`aiomailru Documentation <https://aiomailru.readthedocs.io/>`_.

Client application
~~~~~~~~~~~~~~~~~~

Use :code:`ClientSession` when REST API is needed in:

- a client component of the client-server application
- a standalone mobile/desktop application

i.e. when you embed your app's info (private key) in publicly available code.

.. code-block:: python

    from aiomailru import ClientSession, API

    session = ClientSession(app_id, private_key, access_token, uid)
    api = API(session)

    events = await api.stream.get()
    friends = await api.friends.getOnline()

Pass :code:`access_token` and :code:`uid`
that were received after authorization. For more details, see
`aiomailru Documentation <https://aiomailru.readthedocs.io/>`_.

Server application
~~~~~~~~~~~~~~~~~~

Use :code:`ServerSession` when REST API is needed in:

- a server component of the client-server application
- requests from your servers

.. code-block:: python

    from aiomailru import ServerSession, API

    session = ServerSession(app_id, secret_key, access_token)
    api = API(session)

    events = await api.stream.get()
    friends = await api.friends.getOnline()

Pass :code:`access_token` that was received after authorization.
For more details, see
`aiomailru Documentation <https://aiomailru.readthedocs.io/>`_.

Installation
------------

.. code-block:: shell

    $ pip install aiomailru

or

.. code-block:: shell

    $ python setup.py install

Supported Python Versions
-------------------------

Python 3.5, 3.6, 3.7 and 3.8 are supported.

.. index-end-marker1

Test
----

Run all tests.

.. code-block:: shell

    $ python setup.py test

Run tests with PyTest.

.. code-block:: shell

    $ python -m pytest [-k TEST_NAME]

License
-------

aiomailru is released under the BSD 2-Clause License.
