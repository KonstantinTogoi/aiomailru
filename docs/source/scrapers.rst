Scrapers
========

The following scrapers are available:

* :code:`groups.get`
* :code:`groups.getInfo`
* :code:`groups.join`
* :code:`stream.getByAuthor`, works only with a group's id

.. code-block:: python

    from aiomailru.scrapers import APIScraper

    api = APIScraper(session)
    groups = await api.groups.get(scrape=True)  # current user's groups

Scrapers have the following requirements:

* Cookies
* Pyppeteer
* Browserless

Cookies
-------

If :code:`session` is instance of :code:`TokenSession` you must set cookies
that were given by :code:`ImplicitSession`:

.. code-block:: python

    session = ServerSession(app_id, secret_key, access_token, cookies=cookies)

Pyppeteer
---------

Scrapers require an instance of Chrome.

You can start a new Chrome process:

.. code-block:: python

    from aiomailru.scrapers import APIScraper
    from pyppeteer import launch

    browser = await launch()
    api = APIScraper(session, browser=browser)

    print(browser.wsEndpoint)  # your browser's endpoint

or connect to the existing Chrome:

.. code-block:: python

    from aiomailru.scrapers import APIScraper
    from pyppeteer import connect

    browser_conn = {'browserWSEndpoint': 'your_endpoint'}
    browser = await connect(browser_conn)
    api = APIScraper(session, browser=browser)

Export environment variable

.. code-block:: shell

    $ export PYPPETEER_BROWSER_ENDPOINT='your_endpoint'

to automatically connect to Chrome:

.. code-block:: python

    from aiomailru.scrapers import APIScraper
    api = APIScraper(session)  # connects to PYPPETEER_BROWSER_ENDPOINT

Browserless
-----------

You can replace :code:`pyppeteer.launch` with  :code:`pyppeteer.connect`.
See https://www.browserless.io

Start headless chrome using

.. code-block:: shell

    $ docker-compose up -d chrome

Export environment variable

.. code-block:: shell

    $ export PYPPETEER_BROWSER_ENDPOINT=ws://localhost:3000

to automatically connect to Browserless container:

.. code-block:: python

    from aiomailru.scrapers import APIScraper
    api = APIScraper(session)  # connects to ws://localhost:3000
