"""My.Mail.Ru scrapers."""

import asyncio
import logging
from concurrent.futures import FIRST_COMPLETED
from functools import lru_cache
from uuid import uuid4

from .api import APIMethod
from .browser import Browser
from .objects import Event, GroupItem
from .sessions import TokenSession


log = logging.getLogger(__name__)


class APIScraper(Browser):
    """API scraper."""

    def __init__(self, session: TokenSession, browser=None):
        super().__init__(session, browser)

    def __getattr__(self, name):
        return scrapers.get(name, APIMethod)(self, name)


class APIScraperMethod(APIMethod):
    """API scraper's method."""

    name = ''

    def __init__(self, api: APIScraper, name=''):
        super().__init__(api, self.name or name)

    def __getattr__(self, name):
        name = self.name + '.' + name
        return scrapers.get(name, APIMethod)(self.api, name)

    async def __call__(self, **params):
        scrape = params.pop('scrape') if 'scrape' in params else False
        call = self.call if scrape else super.__call__
        return await call(**params)

    async def call(self, **params):
        raise NotImplementedError()


class GroupsGet(APIScraperMethod):
    """Returns a list of the communities to which the current user belongs."""

    name = 'groups.get'
    url = 'https://my.mail.ru/my/communities'

    class S:
        """Scripts."""

        class S:
            """Selectors."""

            content = (
                'html body '
                'div.l-content '
                'div.l-content__center '
                'div.l-content__center__inner '
                'div.groups-catalog '
                'div.groups-catalog__mine-groups '
                'div.groups-catalog__small-groups '
            )
            catalog = f'{content} div.groups__container'
            groups = f'{catalog} div.groups__item'
            bar = f'{content} div.groups-catalog__groups-more'
            button = f'{bar} span.ui-button-gray'

        click = f'document.querySelector("{S.button}").click()'
        bar_css = 'n => n.getAttribute("style")'
        loaded = f'document.querySelectorAll("{S.groups}").length > {{}}'

    s = S
    ss = S.S

    async def call(self, **params):
        offset = params.get('offset', 0)
        limit = params.get('limit', 5)
        page = await self.api.page(self.url, force=True)
        return await self.scrape(page, [], offset, limit)

    async def scrape(self, page, groups, offset, limit):
        """Appends groups from the `page` to the `groups` list."""

        _ = await page.screenshot()
        catalog = await page.J(self.ss.catalog)
        elements = await catalog.JJ(self.ss.groups)

        start, stop = offset, min(offset + limit, len(elements))
        limit -= stop - start

        for i in range(start, stop):
            item = await GroupItem.from_element(elements[i])
            link = item['link'].lstrip('/')
            resp = await self.api.session.public_request([link])
            group = (await self.api.users.getInfo(uids=resp['uid']))[0]
            groups.append(group)

        bar = await page.J(self.ss.bar)
        css = await page.Jeval(self.ss.bar, self.s.bar_css) or '' if bar else ''

        if limit == 0 or 'display: none;' in css:
            return groups
        else:
            await page.evaluate(self.s.click)
            await page.waitForFunction(self.s.loaded.format(len(groups)))
            return await self.scrape(page, groups, len(elements), limit)


class GroupsGetInfo(APIScraperMethod):
    """Returns information about communities by their IDs."""

    name = 'groups.getInfo'

    class S:
        """Selectors."""

        main_page = (
            'html body '
            'div[id="boosterCanvas"] '
            'div.l-content div.l-content__center '
            'div.l-content__center__inner div.b-community__main-page '
        )
        closed_signage = f'{main_page} div.mf_cc'

    async def call(self, **params):
        uids = params['uids']
        infos = await self.api.users.getInfo(uids=uids)

        for info in infos:
            if 'group_info' in info:
                info['group_info'].update(await self.scrape(info['link']))

        return infos

    async def scrape(self, url):
        """Returns additional information about a group.

        Object fields that are scraped here:
            - 'is_closed' - information whether the group's stream events
                are available for current user.

        """

        page = await self.api.page(url, force=True)
        signage = await page.J(self.S.closed_signage)
        is_closed = True if signage is not None else False
        await page.close()

        return {'is_closed': is_closed}


class StreamGetByAuthor(APIScraperMethod):
    """Returns a list of events from user or community stream by their IDs."""

    name = 'stream.getByAuthor'

    class S:
        """Scripts."""

        class S:
            """Selectors."""

            history = 'div[data-mru-fragment="home/history"]'
            event = 'div.b-history-event'

        class X:
            """Xpath expressions."""

            history = (
                '/html/body/div[@id="boosterCanvas"]'
                '//div[@data-mru-fragment="home/history"]'
            )
            loaded = f'{history}[@data-state][@data-state!="loading"]'
            loading = f'{history}[@data-state="loading"]'

        scroll = 'window.scroll(0, document.body.scrollHeight)'
        state = 'n => n.getAttribute("data-state")'

    s = S
    ss = S.S
    sx = S.X

    async def call(self, **params):
        uid = params.get('uid')
        skip = params.get('skip')
        limit = params.get('limit')
        uid = uid if uid is None else str(uid)
        uuid = skip if skip else uuid4().hex
        user = (await self.api.users.getInfo(uids=uid))[0]
        return await self.scrape(user['link'], skip, limit, uuid)

    @lru_cache(maxsize=None)
    async def scrape(self, url, skip, limit, uuid):
        """Returns a list of events from user or community stream.

        Args:
            url (str): Stream URL.
            skip (str): Latest event ID to skip.
            limit (int): Number of events to return.
            uuid (str): Unique identifier. May be used to prevent
                function from returning result from cache.

        Returns:
            events (list): Stream events.

        """

        events = []

        async for event in self.stream(url):
            if skip:
                skip = skip if event['id'] != skip else False
            else:
                events.append(event)

            if len(events) >= limit:
                break

        return events

    async def stream(self, url):
        """Yields stream events from the beginning to the end.

        Args:
            url: Stream URL.

        Yields:
            event (Event): Stream event.

        """

        page = await self.api.page(url)

        history = await page.J(self.ss.history)
        history_ctx = history.executionContext
        state, elements = None, []

        while state != 'noevents':
            offset = len(elements)
            elements = await history.JJ(self.ss.event)

            for i in range(offset, len(elements)):
                event = await Event.from_element(elements[i])
                yield event

            await page.evaluate(self.s.scroll)

            tasks = [
                page.waitForXPath(self.sx.loading),
                page.waitForXPath(self.sx.loaded),
            ]

            _, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)

            for task in tasks:
                if not task.promise.done():
                    task.promise.set_result(None)
                    task._cleanup()

            for future in pending:
                future.cancel()

            state = await history_ctx.evaluate(self.s.state, history)
            if state == 'loading':
                await page.waitForXPath(self.sx.loaded)


scrapers = {
    'stream': APIScraperMethod,
    'groups': APIScraperMethod,
    GroupsGet.name: GroupsGet,
    GroupsGetInfo.name: GroupsGetInfo,
    StreamGetByAuthor.name: StreamGetByAuthor,
}
