REST API
========

List of all methods is available here: https://api.mail.ru/docs/reference/rest/.

.. code-block:: python

    from aiomailru import API

    api = API(session)

    events = await api.strream.get()  # events for current user
    friends = await api.friends.get()  # current user's friends

List of some objects is available here: `objects.md <https://github.com/KonstantinTogoi/aiomailru/blob/master/docs/objects.md>`_.

Under the hood each API request is enriched with parameters (https://api.mail.ru/docs/guides/restapi/#params):

* :code:`method`, required
* :code:`app_id`, required
* :code:`sig`, required (https://api.mail.ru/docs/guides/restapi/#sig)
* :code:`session_key`, required
* :code:`uid` if necessary
* :code:`secure` if necessary

to `authorize request <https://api.mail.ru/docs/guides/restapi/#session>`_.

By default, the session tries to infer which signature circuit to use:

* if :code:`uid` and :code:`private_key` are not empty strings - **client-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#client
* else if :code:`secret_key` is not an empty string - **server-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#server
* else exception is raised
