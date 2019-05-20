"""My.Mail.Ru API."""

from .sessions import TokenSession


class API:
    """API."""

    __slots__ = ('session', )

    def __init__(self, session: TokenSession):
        self.session = session

    def __getattr__(self, method_name):
        return APIMethod(self, method_name)

    async def __call__(self, method_name, **params):
        return await getattr(self, method_name)(**params)


class APIMethod:
    """API's method."""

    __slots__ = ('api', 'name')

    def __init__(self, api: API, name: str):
        self.api = api
        self.name = name

    def __getattr__(self, method_name):
        return APIMethod(self.api, self.name + '.' + method_name)

    async def __call__(self, **params):
        params = dict(params)
        params['method'] = self.name
        return await self.api.session.request(params=params)
