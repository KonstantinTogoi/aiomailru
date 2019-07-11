"""My.Mail.Ru scrapers."""

import asyncio
import logging
from concurrent.futures import FIRST_COMPLETED
from functools import lru_cache
from uuid import uuid4

from .exceptions import APIScrapperError, CookieError
from .api import API, APIMethod
from .browser import Browser
from .objects import Event, GroupItem
from .sessions import TokenSession


log = logging.getLogger(__name__)


class APIScraper(API, Browser):
    """API scraper."""

    __slots__ = ('browser', )

    def __init__(self, session: TokenSession, browser=None):
        API.__init__(self, session)
        Browser.__init__(self, browser)

    def __getattr__(self, name):
        return scrapers.get(name, APIMethod)(self, name)


class APIScraperMethod(APIMethod):
    """API scraper's method."""

    def __init__(self, api: APIScraper, name: str):
        super().__init__(api, name)

    def __getattr__(self, name):
        name = f'{self.name}.{name}'
        return scrapers.get(name, APIMethod)(self.api, name)

    async def __call__(self, scrape=False, **params):
        call = self.call if scrape else super().__call__
        return await call(**params)

    async def call(self, **params):
        raise NotImplementedError()


class GroupsGet(APIScraperMethod):
    """Returns a list of the communities to which the current user belongs."""

    url = 'https://my.mail.ru/my/communities'

    class Scripts:
        class Selectors:
            content = (
                'html body '
                'div.l-content '
                'div.l-content__center '
                'div.l-content__center__inner '
                'div.groups-catalog '
                'div.groups-catalog__mine-groups '
                'div.groups-catalog__small-groups '
            )
            bar = f'{content} div.groups-catalog__groups-more'
            catalog = f'{content} div.groups__container'
            button = f'{bar} span.ui-button-gray'
            item = f'{catalog} div.groups__item'

        click = f'document.querySelector("{Selectors.button}").click()'
        bar_css = 'n => n.getAttribute("style")'
        loaded = f'document.querySelectorAll("{Selectors.item}").length > {{}}'

    s = Scripts
    ss = Scripts.Selectors

    async def call(self, **params):
        cookies = self.api.session.cookies
        if not cookies:
            raise CookieError('Cookie jar is empty. Set cookies.')

        ext = params.get('ext', 0)
        limit = params.get('limit', 100)
        offset = params.get('offset', 0)
        page = await self.api.page(self.url, force=True, cookies=cookies)
        return await self.scrape(page, [], ext, limit, offset)

    async def scrape(self, page, groups, ext, limit, offset):
        """Appends groups from the `page` to the `groups` list."""

        _ = await page.screenshot()
        catalog = await page.J(self.ss.catalog)
        elements = await catalog.JJ(self.ss.item)

        start, stop = offset, min(offset + limit, len(elements))
        limit -= stop - start

        for i in range(start, stop):
            item = await GroupItem.from_element(elements[i])
            link = item['link'].lstrip('/')
            resp = await self.api.session.public_request([link])
            group, *_ = await self.api.users.getInfo(uids=resp['uid'])
            if ext:
                groups.append(group)
            else:
                groups.append(group['uid'])

        bar = await page.J(self.ss.bar)
        css = await page.Jeval(self.ss.bar, self.s.bar_css) or '' if bar else ''

        if limit == 0 or 'display: none;' in css:
            return groups
        else:
            await page.evaluate(self.s.click)
            await page.waitForFunction(self.s.loaded.format(len(groups)))
            return await self.scrape(page, groups, ext, limit, len(elements))


class GroupsGetInfo(APIScraperMethod):
    """Returns information about communities by their IDs."""

    class Scripts:
        class Selectors:
            main_page = (
                'html body '
                'div.l-content '
                'div.l-content__center '
                'div.l-content__center__inner '
                'div.b-community__main-page '
            )
            closed_signage = f'{main_page} div.mf_cc'

    s = Scripts
    ss = Scripts.Selectors

    async def call(self, **params):
        cookies = self.api.session.cookies
        if not cookies:
            raise CookieError('Cookie jar is empty. Set cookies.')

        uids = params['uids']
        info_list = await self.api.users.getInfo(uids=uids)

        for info in info_list:
            if 'group_info' in info:
                url = info['link']
                page = await self.api.page(url, force=True, cookies=cookies)
                group_info = await self.scrape(page)
                info['group_info'].update(group_info)

        return info_list

    async def scrape(self, page):
        """Returns additional information about a group.

        Object fields that are scraped here:
            - 'is_closed' - information whether the group's stream events
                are closed for current user.

        """

        signage = await page.J(self.ss.closed_signage)
        is_closed = True if signage is not None else False
        group_info = {'is_closed': is_closed}

        return group_info


class GroupsJoin(APIScraperMethod):
    """With this method you can join the group."""

    class Scripts:
        class Selectors:
            content = (
                'html body '
                'div.l-content '
                'div.l-content__center '
                'div.l-content__center__inner '
                'div.b-community__main-page '
                'div.profile div.profile__contentBlock '
            )
            links = (
                f'{content} '
                'div.profile__activeLinks '
                'div.profile__activeLinks_community '
            )
            join_span = f'{links} span.profile__activeLinks_button_enter'
            sent_span = f'{links} span.profile__activeLinks_link_modarated'
            approved_span = f'{links} span.profile__activeLinks_link_inGroup'
            auth_span = f'{links} div.l-popup_community-authorization'

        selector = 'document.querySelector("{}")'
        get_style = f'window.getComputedStyle({selector})'
        visible = f'{get_style}["display"] != "none"'
        join_span_visible = visible.format(Selectors.join_span)
        sent_span_visible = visible.format(Selectors.sent_span)
        approved_span_visible = visible.format(Selectors.approved_span)

        join_click = f'document.querySelector("{Selectors.join_span}").click();'

    s = Scripts
    ss = Scripts.Selectors

    async def call(self, **params):
        cookies = self.api.session.cookies
        if not cookies:
            raise CookieError('Cookie jar is empty. Set cookies.')

        group_id = params['group_id']
        info, *_ = await self.api.users.getInfo(uids=str(group_id))
        page = await self.api.page(info['link'], force=True, cookies=cookies)

        return await self.scrape(page)

    async def scrape(self, page):
        if await page.evaluate(self.s.join_span_visible):
            return await self.join(page)
        elif await page.evaluate(self.s.sent_span_visible):
            return 1
        elif await page.evaluate(self.s.approved_span_visible):
            return 1
        else:
            raise APIScrapperError('A join button not found.')

    async def join(self, page):
        await page.evaluate(self.s.join_click)
        await asyncio.sleep(1)

        if await page.evaluate(self.s.sent_span_visible):
            return 1
        elif await page.evaluate(self.s.approved_span_visible):
            return 1
        else:
            raise APIScrapperError('Failed to send join request.')


class StreamGetByAuthor(APIScraperMethod):
    """Returns a list of events from user or community stream by their IDs."""

    class Scripts:
        class Selectors:
            history = 'div[data-mru-fragment="home/history"]'
            event = 'div.b-history-event[data-astat]'

        class XPaths:
            history = (
                '/html/body/div[@id="boosterCanvas"]'
                '//div[@data-mru-fragment="home/history"]'
            )
            loaded = f'{history}[@data-state][@data-state!="loading"]'
            loading = f'{history}[@data-state="loading"]'

        scroll = 'window.scroll(0, document.body.scrollHeight)'
        state = 'n => n.getAttribute("data-state")'

    s = Scripts
    ss = Scripts.Selectors
    sx = Scripts.XPaths

    async def call(self, **params):
        uid = params.get('uid')
        skip = params.get('skip')
        limit = params.get('limit')
        uuid = skip if skip else uuid4().hex
        return await self.scrape(uid, skip, limit, uuid)

    @lru_cache(maxsize=None)
    async def scrape(self, uid, skip, limit, uuid):
        """Returns a list of events from user or community stream.

        Args:
            uid (int): User ID.
            skip (str): Latest event ID to skip.
            limit (int): Number of events to return.
            uuid (str): Unique identifier. May be used to prevent
                function from returning result from cache.

        Returns:
            events (list): Stream events.

        """

        cookies = self.api.session.cookies
        if not cookies:
            raise CookieError('Cookie jar is empty. Set cookies.')

        user, *_ = await self.api.users.getInfo(uids=uid)
        page = await self.api.page(user['link'], cookies=cookies)
        events = []

        async for event in self.stream(page):
            if skip:
                skip = skip if event['id'] != skip else False
            else:
                events.append(event)

            if len(events) >= limit:
                break

        return events

    async def stream(self, page):
        """Yields stream events from the beginning to the end.

        Args:
            page (pyppeteer.page.Page): Page with the stream.

        Yields:
            event (Event): Stream event.

        """

        history = await page.J(self.ss.history)
        history_ctx = history.executionContext
        state, elements = None, []

        while state != 'noevents':
            for element in await history.JJ(self.ss.event):
                yield await Event.from_element(element)

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
                state = await history_ctx.evaluate(self.s.state, history)


scrapers = {
    'groups': APIScraperMethod,
    'groups.get': GroupsGet,
    'groups.getInfo': GroupsGetInfo,
    'groups.join': GroupsJoin,
    'stream': APIScraperMethod,
    'stream.getByAuthor': StreamGetByAuthor,
}
