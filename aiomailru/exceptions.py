class Error(Exception):
    pass


class AuthorizationError(Error):
    pass


class APIError(Error):
    def __init__(self, error):
        super().__init__(error)
        self.code = error['error_code']
        self.msg = error['error_msg']

    def __str__(self):
        return 'ERROR {code}: {msg}'.format(code=self.code, msg=self.msg)


class APIScrapperError(Error):
    code = 0

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return 'ERROR {code}: {msg}'.format(code=self.code, msg=self.msg)


class CookieError(APIScrapperError):
    code = 1
