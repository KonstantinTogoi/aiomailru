import re
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
