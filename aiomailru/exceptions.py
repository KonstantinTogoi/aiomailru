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
        return "ERROR %d: %s" % (self.code, self.msg)
