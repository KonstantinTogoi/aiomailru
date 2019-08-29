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
                'html body '
                'div.l-content '
                'div.l-content__center '
                'div.l-content__center__inner '
            )
            main_page = f'{content} div.b-community__main-page '
            profile = f'{main_page} div.profile '
            profile_content = f'{profile} div.profile__contentBlock '

        class ScriptTemplates:
            """Common templates of scripts."""
            getattr = 'n => n.getAttribute("%s")'
            selector = 'document.querySelector("%s")'
            selector_all = 'document.querySelectorAll("%s")'
            click = f'{selector}.click()'
            getstyle = f'window.getComputedStyle({selector})'
            visible = f'{getstyle}["display"] != "none"'
            length = f'{selector_all}.length'

        scroll = 'window.scroll(0, document.body.scrollHeight)'

    s = Scripts
    ss = Scripts.Selectors
    st = Scripts.ScriptTemplates

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


def with_page(coro):
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

    url = 'https://my.mail.ru/my/communities'

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            groups = (
                f'{scraper.ss.content} '
                'div.groups-catalog '
                'div.groups-catalog__mine-groups '
                'div.groups-catalog__small-groups '
            )
            bar = f'{groups} div.groups-catalog__groups-more'
            catalog = f'{groups} div.groups__container'
            button = f'{bar} span.ui-button-gray'
            item = f'{catalog} div.groups__item'

        click = scraper.st.click % Selectors.button
        bar_css = scraper.st.getattr % 'style'
        loaded = f'{scraper.st.length % Selectors.item} > %d'

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, limit=10, offset=0, ext=0):
        self.page = await self.api.page(
            self.url,
            self.api.session.session_key,
            self.api.session.cookies,
        )
        _ = await self.page.screenshot()
        return True

    @with_page
    async def call(self, *, limit=10, offset=0, ext=0):
        return await self.scrape([], ext, limit, offset)

    async def scrape(self, groups, ext, limit, offset):
        """Appends groups from the `page` to the `groups` list."""

        catalog = await self.page.J(self.ss.catalog)
        if catalog is None:
            return []

        elements = await catalog.JJ(self.ss.item)
        start, stop = offset, min(offset + limit, len(elements))
        limit -= stop - start

        for i in range(start, stop):
            item = await GroupItem.from_element(elements[i])
            link = item['link'].lstrip('/')
            resp = await self.api.session.public_request([link])
            group, *_ = await self.api.users.getInfo(uids=resp['uid'])
            groups.append(group if ext else group['uid'])

        if limit == 0:
            return groups
        elif await self.page.J(self.ss.bar) is None:
            return groups
        elif 'display: none;' in \
                (await self.page.Jeval(self.ss.bar, self.s.bar_css) or ''):
            return groups
        else:
            await self.page.evaluate(self.s.click)
            await self.page.waitForFunction(self.s.loaded % len(groups))
            return await self.scrape(groups, ext, limit, len(elements))


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

    @with_page
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
                f'{scraper.ss.profile_content} '
                'div.profile__activeLinks '
                'div.profile__activeLinks_community '
            )
            join_span = f'{links} span.profile__activeLinks_button_enter'
            sent_span = f'{links} span.profile__activeLinks_link_modarated'
            approved_span = f'{links} span.profile__activeLinks_link_inGroup'
            auth_span = f'{links} div.l-popup_community-authorization'

        join_span_visible = scraper.st.visible % Selectors.join_span
        sent_span_visible = scraper.st.visible % Selectors.sent_span
        approved_span_visible = scraper.st.visible % Selectors.approved_span

        join_click = f'{scraper.st.click % Selectors.join_span}'

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

    @with_page
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
            feed = f'{scraper.ss.main_page} div.b-community__main-page__feed '
            history = f'{feed} div.b-history '
            event = f'{history} div.b-history-event[data-astat] '

        history_state = scraper.st.getattr % 'data-state'

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

    @with_page
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

        state, elements = '', []

        while state != 'noevents':
            offset = len(elements)
            history = await self.page.J(self.ss.history)
            elements = await history.JJ(self.ss.event)
            for element in elements[offset:]:
                yield await Event.from_element(element)

            await self.page.evaluate(self.s.scroll)
            await asyncio.sleep(self.DELAY)
            state = await self.page.Jeval(self.ss.history, self.s.history_state)

            while state not in ['noevents', 'loaded']:
                await asyncio.sleep(self.DELAY)
                state = await self.page.Jeval(
                    self.ss.history, self.s.history_state)


scrapers = {
    'groups': APIScraperMethod,
    'groups.get': GroupsGet,
    'groups.getInfo': GroupsGetInfo,
    'groups.join': GroupsJoin,
    'stream': APIScraperMethod,
    'stream.getByAuthor': StreamGetByAuthor,
}
