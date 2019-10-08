class Error(Exception):

    @property
    def error(self):
        return self.args[0]

    def __init__(self, error: str or dict):
        arg = error if isinstance(error, dict) else {
            'error': 'internal_error',
            'error_description': error,
        }
        super().__init__(arg)


class OAuthError(Error):
    """OAuth error."""

    def __init__(self, error: str):
        super().__init__({'error': 'oauth_error', 'error_description': error})


class CustomOAuthError(Error):
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


class NotAvailableClientError(CustomOAuthError):
    """Application is not available (in test mode)."""

    ERROR = {
        'error': 'not_available_client',
        'error_description': 'application is in the test mode'
    }


class APIError(Error):
    def __init__(self, error):
        super().__init__(error)
        self.code = error['error_code']
        self.msg = error['error_msg']

    def __str__(self):
        return f'Error {self.code}: {self.msg}'


class APIScrapperError(Error):
    code = 0

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return f'Error {self.code}: {self.msg}'


class CustomAPIError(Error):
    ERROR = {'error_code': 0, 'error_msg': ''}

    def __init__(self):
        super().__init__(self.ERROR)


class EmptyObjectsError(CustomAPIError):
    ERROR = {'error_code': 202, 'error_msg': 'empty objects'}


class EmptyGroupsError(CustomAPIError):
    ERROR = {'error_code': 202, 'error_msg': 'empty groups'}


class AccessDeniedError(CustomAPIError):
    ERROR = {
        'error_code': 202,
        'error_msg': 'Access to this object is denied',
    }


class BlackListError(CustomAPIError):
    ERROR = {
        'error_code': 202,
        'error_msg': 'Access to this object is denied: you are in blacklist',
    }


class CookieError(APIScrapperError):
    code = 1
