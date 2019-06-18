import re
from datetime import datetime
from enum import Enum

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

        if morsel['expires']:
            expires = datetime.strptime(morsel['expires'], cls.expires_fmt)
        else:
            expires = datetime.fromtimestamp(0)

        if morsel['domain'].startswith('.'):
            domain = morsel['domain']
        else:
            domain = '.' + morsel['domain']

        cookie = cls({
            'name': morsel.key,
            'value': morsel.value,
            'domain': domain,
            'path': morsel['path'],
            'expires': expires.timestamp(),
            'size': len(morsel.key) + len(morsel.value),
            'httpOnly': True if morsel['httponly'] else False,
            'secure': True if morsel['secure'] else False,
            'session': False,
        })

        return cookie
