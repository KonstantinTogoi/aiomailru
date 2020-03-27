"""Exceptions."""


class Error(Exception):
    """Base exception."""

    ERROR = 'internal_error'

    @property
    def error(self):
        return self.args[0]

    def __init__(self, error: str or dict):
        arg = error if isinstance(error, dict) else {
            'error': self.ERROR,
            'error_description': error,
        }
        super().__init__(arg)


class OAuthError(Error):
    """OAuth error."""

    ERROR = 'oauth_error'


class CustomOAuthError(OAuthError):
    """Custom errors that raised when authorization failed."""

    ERROR = {'error': '', 'error_description': ''}

    def __init__(self):
        super().__init__(self.ERROR)


class InvalidGrantError(CustomOAuthError):
    """Invalid user credentials."""

    ERROR = {
        'error': 'invalid_grant',
        'error_description': 'invalid login or password',
    }


class InvalidClientError(CustomOAuthError):
    """Invalid client id."""

    ERROR = {
        'error': 'invalid_client',
        'error_description': 'invalid client id',
    }


class InvalidUserError(CustomOAuthError):
    """Invalid user (blocked)."""

    ERROR = {
        'error': 'invalid_user',
        'error_description': 'user is blocked',
    }


class ClientNotAvailableError(CustomOAuthError):
    """Application is not available (in test mode)."""

    ERROR = {
        'error': 'client_not_available',
        'error_description': 'application is in the test mode'
    }


class APIError(Error):
    def __init__(self, error):
        super().__init__(error)
        self.code = error['error']['error_code']
        self.msg = error['error']['error_msg']

    def __str__(self):
        return 'Error {code}: {msg}'.format(code=self.code, msg=self.msg)


class APIScrapperError(Error):
    code = 0

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return 'Error {code}: {msg}'.format(code=self.code, msg=self.msg)


class CustomAPIError(APIError):
    """Custom API error."""

    ERROR = {'error': {'error_code': 0, 'error_msg': ''}}

    def __init__(self):
        super().__init__(self.ERROR)


class EmptyResponseError(CustomAPIError):
    ERROR = {'error': {'error_code': -1, 'error_msg': 'empty response'}}


class EmptyObjectsError(CustomAPIError):
    ERROR = {'error': {'error_code': 202, 'error_msg': 'empty objects'}}


class EmptyGroupsError(CustomAPIError):
    ERROR = {'error': {'error_code': 202, 'error_msg': 'empty groups'}}


class AccessDeniedError(CustomAPIError):
    ERROR = {'error': {
        'error_code': 202,
        'error_msg': 'Access to this object is denied',
    }}


class BlackListError(CustomAPIError):
    ERROR = {'error': {
        'error_code': 202,
        'error_msg': 'Access to this object is denied: you are in blacklist',
    }}


class CookieError(APIScrapperError):
    code = 1
