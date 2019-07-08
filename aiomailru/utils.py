import re
from datetime import datetime
from enum import Enum
from http.cookies import Morsel

EMAIL_PATTERN = r"(^[a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+)\.([a-zA-Z0-9-.]+$)"
PRIVILEGES = ['photos', 'guestbook', 'stream', 'messages', 'events']


def full_scope():
    return ' '.join(PRIVILEGES)


class SignatureCircuit(Enum):
    """Signature circuit.

    .. _Подпись запроса
        https://api.mail.ru/docs/guides/restapi/#sig

    """

    UNDEFINED = 0
    CLIENT_SERVER = 1
    SERVER_SERVER = 2


def parseaddr(address):
    """Converts an e-mail address to a tuple - (screen name, domain name).

    Args:
        address (str): e-mail address

    Returns:
        domain_name(str): domain name
        screen_name (str): screen name

    """

    pattern = re.compile(EMAIL_PATTERN)
    match = pattern.match(address)

    if match is None:
        raise ValueError("email address %r is not valid" % address)

    screen_name, domain_name, _ = match.groups()
    return domain_name, screen_name


class Cookie(dict):
    """Represents cookie in a browser."""

    expires_fmt = '%a, %d %b %Y %H:%M:%S GMT'

    def __init__(self, *args):
        super().__init__(*args)

    @classmethod
    def from_morsel(cls, morsel):
        """Converts a cookie morsel to dictionary.

        Args:
            morsel (http.cookies.Morsel): cookie morsel

        Returns:
            cookie (dict): cookie for the browser.

        """

        domain = morsel['domain']
        expires = morsel['expires']
        path = morsel['path']
        size = len(morsel.key) + len(morsel.value)
        http_only = True if morsel['httponly'] else False
        secure = True if morsel['secure'] else False

        if expires:
            session = False
            expires = datetime.strptime(expires, cls.expires_fmt).timestamp()
        else:
            session = True
            expires = None

        if not domain.startswith('.'):
            domain = '.' + domain

        cookie = cls({
            'name': morsel.key,
            'value': morsel.value,
            'domain': domain,
            'path': path,
            'expires': expires,
            'size': size,
            'httpOnly': http_only,
            'secure': secure,
            'session': session,
        })

        return cookie

    @classmethod
    def to_morsel(cls, cookie):
        """Converts a dictionary to cookie morsel.

        Args:
            cookie (dict): cookie from the browser.

        Returns:
            morsel (http.cookies.Morsel): cookie morsel

        """

        morsel = Morsel()
        morsel.set(cookie['name'], cookie['value'], cookie['value'])

        if cookie['expires']:
            dt = datetime.fromtimestamp(cookie['expires'])
            expires = dt.strftime(cls.expires_fmt)
        else:
            expires = None

        morsel['expires'] = expires
        morsel['path'] = cookie['path']
        morsel['domain'] = cookie['domain']
        morsel['secure'] = cookie['secure']
        morsel['httponly'] = cookie['httpOnly']

        return morsel
