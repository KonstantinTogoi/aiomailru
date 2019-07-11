class Error(Exception):
    pass


class AuthError(Error):
    pass


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
