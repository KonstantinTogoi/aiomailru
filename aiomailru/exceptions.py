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


class AuthError(Error):

    ERROR = {
        'error': 'invalid_user_credentials',
        'error_description': 'invalid login or password',
    }

    def __init__(self):
        super().__init__(self.ERROR)


class MyMailAuthError(Error):
    """Invalid client id."""

    ERROR = {
        'error': 'invalid_client',
        'error_description': 'invalid client id',
    }

    def __init__(self):
        super().__init__(self.ERROR)


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


class CookieError(APIScrapperError):
    code = 1
