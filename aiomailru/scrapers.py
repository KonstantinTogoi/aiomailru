"""My.Mail.Ru scrapers."""

import asyncio
import logging
from functools import wraps

from .exceptions import (
    APIError,
    APIScrapperError,
    CookieError,
    EmptyObjectsError,
    EmptyGroupsError,
)
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

    class Scripts:
        """Common scripts."""
        class Selectors:
            """Common selectors."""
            content = (
                ' html body'
                ' div.l-content'
                ' div.l-content__center'
                ' div.l-content__center__inner'
            )
            main_page = f'{content} div.b-community__main-page'
            profile = f'{main_page} div.profile'
            profile_content = f'{profile} div.profile__contentBlock'

            class SelectorTemplates:
                """Common templates of selectors."""
                hidden = '%s[style="display: none;"]'
                visible = '%s:not([style="display: none;"])'

        class ScriptTemplates:
            """Common templates of scripts."""
            getattr = 'n => n.getAttribute("%s")'
            getclass = getattr % 'class'
            getstyle = getattr % 'style'
            selector = 'document.querySelector("%s")'
            selector_all = 'document.querySelectorAll("%s")'
            click = f'{selector}.click()'
            computed_style = f'window.getComputedStyle({selector})'
            display = f'{computed_style}["display"]'
            visible = f'{display} != "none"'
            length = f'{selector_all}.length'

        scroll = 'window.scroll(0, document.body.scrollHeight)'

    s = Scripts
    ss = Scripts.Selectors
    sst = Scripts.ScriptTemplates
    ssst = Scripts.Selectors.SelectorTemplates

    def __init__(self, api: APIScraper, name: str):
        super().__init__(api, name)
        self.page = None

    def __getattr__(self, name):
        name = f'{self.name}.{name}'
        return scrapers.get(name, APIMethod)(self.api, name)

    async def __call__(self, scrape=False, **params):
        call = self.call if scrape else super().__call__
        return await call(**params)

    async def init(self, **params):
        pass

    async def call(self, **params):
        await self.init(**params)


class APIScraperMultiMethod(APIScraperMethod):

    multiarg = 'uids'
    empty_objects_error = EmptyObjectsError
    ignored_errors = (APIError, )

    async def __call__(self, scrape=False, **params):
        call = self.multicall if scrape else super().__call__()
        return await call(**params)

    async def multicall(self, **params):
        args = params[self.multiarg].split(',')
        result = []
        for arg in args:
            params.pop(self.multiarg)
            params.update({self.multiarg: arg})

            # when `self.api.session.pass_error` is False
            try:
                resp = await self.call(**params)
            except self.ignored_errors:
                resp = self.empty_objects_error().error

            # when `self.api.session.pass_error` is True
            if isinstance(resp, dict) and 'error_code' in resp:
                pass
            else:
                result.append(resp[0])

        if not result and self.empty_objects_error is not None:
            if self.api.session.pass_error:
                return self.empty_objects_error().error
            else:
                raise self.empty_objects_error
        else:
            return result


scraper = APIScraperMethod
multiscraper = APIScraperMultiMethod


def with_init(coro):
    @wraps(coro)
    async def wrapper(self: scraper, **kwargs):
        if not self.api.session.cookies:
            raise CookieError('Cookie jar is empty. Set cookies.')
        init_result = await self.init(**kwargs)
        if isinstance(init_result, dict):
            return init_result
        else:
            return await coro(self, **kwargs)

    return wrapper


class GroupsGet(scraper):
    """Returns a list of the communities to which the current user belongs."""

    DELAY = 0.3  # delay before checking loaded groups

    url = 'https://my.mail.ru/my/communities'

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            groups = (
                f'{scraper.ss.content}'
                ' div.groups-catalog'
                ' div.groups-catalog__mine-groups'
                ' div.groups-catalog__small-groups'
            )
            bar = f'{groups} div.groups-catalog__groups-more'
            hidden_bar = scraper.ssst.hidden % bar
            visible_bar = scraper.ssst.visible % bar
            catalog = f'{groups} div.groups__container'
            button = f'{bar} span.ui-button-gray'
            progress_button = f'{bar} span.progress'
            item = f'{catalog} div.groups__item'

        click = scraper.sst.click % Selectors.button
        button_class = scraper.sst.getattr % 'class'
        bar_css = scraper.sst.getattr % 'style'
        loaded = f'{scraper.sst.length % Selectors.item} > %d'

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, limit=10, offset=0, ext=0):
        info = await self.api.users.getInfo(uids='')
        if isinstance(info, dict):
            return info
        self.page = await self.api.page(
            self.url,
            self.api.session.session_key,
            self.api.session.cookies,
        )
        _ = await self.page.screenshot()
        return True

    @with_init
    async def call(self, *, limit=10, offset=0, ext=0):
        return await self.scrape(ext, limit, offset)

    async def scrape(self, ext, limit, offset):
        """Appends groups from the `page` to the `groups` list."""
        groups, cnt = [], 0
        async for group in self.groups(ext):
            if cnt < offset:
                continue
            else:
                groups.append(group)
            cnt += 1

            if len(groups) >= limit:
                break

        return groups

    async def groups(self, ext):
        visible_bar, button, elements = True, True, []

        while visible_bar:
            offset = len(elements)
            catalog = await self.page.J(self.ss.catalog)
            elements = await catalog.JJ(self.ss.item)
            for element in elements[offset:]:
                item = await GroupItem.from_element(element)
                link = item['link'].lstrip('/')
                resp = await self.api.session.public_request([link])
                group = await self.api.users.getInfo(uids=resp['uid'])
                yield group[0] if ext else group[0]['uid']

            if await self.page.J(self.ss.button):
                await self.page.evaluate(self.s.click)

            await asyncio.sleep(self.DELAY)
            progress_button = await self.page.J(self.ss.progress_button)
            while progress_button:
                await asyncio.sleep(self.DELAY)
                progress_button = await self.page.J(self.ss.progress_button)

            visible_bar = await self.page.J(self.ss.visible_bar)


class GroupsGetInfo(multiscraper):
    """Returns information about communities by their IDs."""

    class Scripts(multiscraper.s):
        class Selectors(multiscraper.ss):
            closed_signage = f'{multiscraper.ss.main_page} div.mf_cc'

    s = Scripts
    ss = Scripts.Selectors

    empty_objects_error = EmptyGroupsError
    ignored_errors = (APIError, KeyError)  # KeyError when group_info is absent

    async def init(self, uids=''):
        info = await self.api.users.getInfo(uids=uids)
        if isinstance(info, dict):
            return info
        self.page = await self.api.page(
            info[0]['link'],
            self.api.session.session_key,
            self.api.session.cookies,
            True,
        )
        _ = await self.page.screenshot()
        return True

    @with_init
    async def call(self, *, uids=''):
        return await self.scrape(uids)

    async def scrape(self, uids):
        """Returns additional information about a group.

        Object fields that are scraped here:
            - 'is_closed' - information whether the group's stream events
                are closed for current user.

        """

        info = await self.api.users.getInfo(uids=uids)
        signage = await self.page.J(self.ss.closed_signage)
        is_closed = True if signage is not None else False
        info[0]['group_info'].update({'is_closed': is_closed})
        return info


class GroupsJoin(scraper):
    """With this method you can join the group."""

    retry_interval = 1
    num_attempts = 10

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            links = (
                f'{scraper.ss.profile_content}'
                ' div.profile__activeLinks'
                ' div.profile__activeLinks_community'
            )
            join_span = f'{links} span.profile__activeLinks_button_enter'
            sent_span = f'{links} span.profile__activeLinks_link_modarated'
            approved_span = f'{links} span.profile__activeLinks_link_inGroup'
            auth_span = f'{links} div.l-popup_community-authorization'

        join_span_visible = scraper.sst.visible % Selectors.join_span
        sent_span_visible = scraper.sst.visible % Selectors.sent_span
        approved_span_visible = scraper.sst.visible % Selectors.approved_span

        join_click = f'{scraper.sst.click % Selectors.join_span}'

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, group_id=''):
        info = await self.api.users.getInfo(uids=group_id)
        if isinstance(info, dict):
            return info
        self.page = await self.api.page(
            info[0]['link'],
            self.api.session.session_key,
            self.api.session.cookies,
            True,
        )
        _ = await self.page.screenshot()
        return True

    @with_init
    async def call(self, *, group_id=''):
        return await self.scrape()

    async def scrape(self):
        if await self.page.evaluate(self.s.join_span_visible):
            return await self.join()
        elif await self.page.evaluate(self.s.sent_span_visible):
            return 1
        elif await self.page.evaluate(self.s.approved_span_visible):
            return 1
        else:
            raise APIScrapperError('A join button not found.')

    async def join(self):
        for i in range(self.num_attempts):
            await self.page.evaluate(self.s.join_click)
            await asyncio.sleep(self.retry_interval)

            if await self.page.evaluate(self.s.sent_span_visible):
                return 1
            elif await self.page.evaluate(self.s.approved_span_visible):
                return 1

        raise APIScrapperError('Failed to send join request.')


class StreamGetByAuthor(scraper):
    """Returns a list of events from user or community stream by their IDs."""

    DELAY = 0.3  # delay before checking history's state

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            feed = f'{scraper.ss.main_page} div.b-community__main-page__feed'
            stream = f'{feed} div.b-history'
            event = f'{stream} div.b-history-event[data-astat]'

        stream_state = scraper.sst.getattr % 'data-state'

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, uid='', limit=10, skip=''):
        info = await self.api.users.getInfo(uids=uid)
        if isinstance(info, dict):
            return info
        self.page = await self.api.page(
            info[0]['link'],
            self.api.session.session_key,
            self.api.session.cookies,
        )
        _ = await self.page.screenshot()
        return True

    @with_init
    async def call(self, *, uid='', limit=10, skip=''):
        return await self.scrape(limit, skip)

    async def scrape(self, limit, skip):
        """Returns a list of events from user or community stream."""

        events = []
        async for event in self.stream():
            if skip:
                skip = skip if event['id'] != skip else False
            else:
                events.append(event)

            if len(events) >= limit:
                break

        return events

    async def stream(self):
        """Yields stream events from the beginning to the end."""

        st, elements = '', []

        while st != 'noevents':
            offset = len(elements)
            stream = await self.page.J(self.ss.stream)
            elements = await stream.JJ(self.ss.event)
            for element in elements[offset:]:
                yield await Event.from_element(element)

            await self.page.evaluate(self.s.scroll)

            await asyncio.sleep(self.DELAY)
            st = await self.page.Jeval(self.ss.stream, self.s.stream_state)
            while st not in ['noevents', 'loaded']:
                await asyncio.sleep(self.DELAY)
                st = await self.page.Jeval(self.ss.stream, self.s.stream_state)


scrapers = {
    'groups': APIScraperMethod,
    'groups.get': GroupsGet,
    'groups.getInfo': GroupsGetInfo,
    'groups.join': GroupsJoin,
    'stream': APIScraperMethod,
    'stream.getByAuthor': StreamGetByAuthor,
}
