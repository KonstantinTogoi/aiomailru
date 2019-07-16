# Platform@Mail.Ru Python REST API wrapper

- [About](#about)
- [Getting Started](#getting-started)
    + [REST API](#rest-api)
        - [ImplicitSession](#implicitsession)
        - [TokenSession](#tokensession)
        - [Making API request](#making-api-request)
            + [Client-Server circuit](#client-server-circuit)
            + [Server-Server circuit](#server-server-circuit)
    + [Scrapers](#scrapers)
        - [Cookies](#cookies)
        - [Pyppeteer](#pyppeteer)
        - [Browserless](#browserless)
- [License](#license)

## About

This is a [my.mail.ru](https://my.mail.ru) (Russian social network) python API
wrapper. The main features are:

* support of [REST API](https://api.mail.ru/docs/reference/rest/) methods
* extra methods (scrapers) based on REST API methods


## Getting Started

Install package using pip

    pip install aiomailru

### REST API

To use Platform@Mail.Ru API you need a registered app and
[Mail.Ru](https://mail.ru) account:

1. Sign up in [Mail.Ru](https://mail.ru).
2. Create **standalone** application.
3. Save **client_id** (aka **app_id**), **private_key**, **secret_key** (aka **app_secret**).
4. Use **app_id**, list of required permissions and user credentials to get **session_key** (aka **access_token**).
5. Use the access token to make method requests.

After signing up visit the Platform@Mail.Ru REST API
[documentation page](https://api.mail.ru/docs/)
and create a new
[standalone application](https://api.mail.ru/docs/guides/standalone-apps/):
https://api.mail.ru/apps/my/add

```python
app_id = 'your_client_id'
private_key = 'your_private_key'
secret_key = 'your_secret_key'
```

#### ImplicitSession

You can authenticate with [Platform@Mail.Ru OAuth2](https://api.mail.ru/docs/guides/oauth/)
by passing user credentials and permissions

```python
from aiomailru.utils import full_scope

email = 'user_email'
password = 'user_password'
scope = full_scope()
```

to `ImplicitSession`

```python
from aiomailru.sessions import ImplicitSession

session = await ImplicitSession(
        app_id=app_id,
        private_key=private_key,
        secret_key=secret_key,
        email=email,
        passwd=password,
        scope=scope,
)
```

List of all permissions is available here:
https://api.mail.ru/docs/guides/restapi/#permissions.

Now you can make requests (See. [Making API request](#making-api-request)).
After authentication you will get session key `session.session_key` and
user ID `session.uid`. Save them to make requests later.

```python
access_token = session.session_key
uid = session.uid
cookies = session.cookies
```

Cookies are required for scraping. See [Scrapers](#scrapers).

#### TokenSession

If you already have an access token and either of two:

- `uid` and `private_key`
- `secret_key`

```python
from aiomailru.sessions import TokenSession
session = TokenSession(
    app_id=app_id,
    private_key=private_key,
    secret_key=secret_key,
    access_token=access_token,
    uid=uid,
)
```

you can instantiate `TokenSession` and make requests.

#### Making API request

List of all methods is available here: https://api.mail.ru/docs/reference/rest/

```python
from aiomailru import API
api = API(session)

# current user's friends
friends = await api.friends.get()

# events for current user
events = await api.strream.get()
```

List of some objects is available here: [./docs/objects.md](https://github.com/KonstantinTogoi/aiomailru/blob/master/docs/objects.md)

Under the hood each API request is enriched with:

- the set of required parameters
(https://api.mail.ru/docs/guides/restapi/#params):
    + `method`
    + `app_id`
    + `sig` (https://api.mail.ru/docs/guides/restapi/#sig)
- `session_key`
- `uid` if necessary
- `secure` if necessary

to [authorize request](https://api.mail.ru/docs/guides/restapi/#session).

By default, the session tries to inference which signature circuit to use:

- if `uid` and `private_key` are not empty strings - **client-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#client
- else if `secret_key` is not an empty string - **server-server** signature circuit is used https://api.mail.ru/docs/guides/restapi/#server
- else exception is raised

You can explicitly choose a circuit for signing requests by passing to `API`
one of the following sessions:

##### Client-Server circuit

```python
from aiomailru import ImplicitClientSession, API
session = await ImplicitClientSession(app_id, private_key, email, password, scope)
api = API(session)
```

or if you already have an access token

```python
from aiomailru import ClientSession, API
session = ClientSession(app_id, private_key, access_token, uid)
api = API(session)
```

##### Server-server circuit

```python
from aiomailru import ImplicitServerSession, API
session = await ImplicitServerSession(app_id, secret_key, email, password, scope)
api = API(session)
```

or if you already have an access token

```python
from aiomailru import ServerSession, API
session = ServerSession(app_id, secret_key, access_token)
api = API(session)
```


### Scrapers

The following scrapers are available:

- `groups.get`
- `groups.getInfo`
- `groups.join`
- `stream.getByAuthor`

```python
from aiomailru.scrapers import APIScraper

api = APIScraper(session)

# current user's groups
groups = await api.groups.get()
```

Scrapers have the following requirements:

#### Cookies

If `session` is instance of [`TokenSession`](#tokensession) you must set cookies
that were given by [`ImplicitSession`](#implicitsession):

```python
session = ServerSession(app_id, secret_key, access_token, cookies=cookies)
```

#### Pyppeteer

Scrapers require an instance of Chrome.

You can start a new Chrome process:

```python
from aiomailru.scrapers import APIScraper
from pyppeteer import launch

browser = await launch()
api = APIScraper(session, browser=browser)

print(browser.wsEndpoint)  # your browser's endpoint
```

or connect to the existing Chrome:

```python
from aiomailru.scrapers import APIScraper
from pyppeteer import connect

browser_conn = {'browserWSEndpoint': 'your_endpoint'}
browser = await connect(browser_conn)
api = APIScraper(session, browser=browser)
```

Export environment variable

```bash
export PYPPETEER_BROWSER_ENDPOINT='your_endpoint'
```

to automatically connect to Chrome:

```python
from aiomailru.scrapers import APIScraper

api = APIScraper(session)  # connects to PYPPETEER_BROWSER_ENDPOINT
```

#### Browserless

You can replace `pyppeteer.launch` with  `pyppeteer.connect`. See https://www.browserless.io

Start headless chrome using

```bash
docker-compose up -d chrome
```

Export environment variable

```bash
export PYPPETEER_BROWSER_ENDPOINT=ws://localhost:3000
```

to automatically connect to Browserless container:

```python
from aiomailru.scrapers import APIScraper

api = APIScraper(session)  # connects to ws://localhost:3000
```

## License

**aiomailru** is released under the BSD 2-Clause License.
