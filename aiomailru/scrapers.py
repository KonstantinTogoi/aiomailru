"""My.Mail.Ru scrapers."""

import asyncio
import logging
import sys
from functools import wraps

from .exceptions import (
    APIError,
    APIScrapperError,
    CookieError,
    EmptyObjectsError,
    EmptyGroupsError,
    AccessDeniedError,
    BlackListError,
)
from .api import API, APIMethod
from .browser import Browser
from .objects import Event, GroupItem
from .sessions import TokenSession


# monkey patching for python 3.5
if sys.version_info[1] == 5:
    from collections import OrderedDict
    from pyppeteer.execution_context import JSHandle

    async def get_properties(self):
        """Get all properties of this handle."""
        response = (await self._client.send('Runtime.getProperties', {
            'objectId': self._remoteObject.get('objectId', ''),
            'ownProperties': True,
        }))
        result = OrderedDict()
        for prop in response['result']:
            if prop.get('enumerable'):
                key = prop.get('name')
                value = prop.get('value')
                result[key] = self._context._objectHandleFactory(value)
        return result

    JSHandle.getProperties = get_properties


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
            main_page = '%s div.b-community__main-page' % content
            closed_signage = '%s div.mf_cc' % main_page
            profile = '%s div.profile' % main_page
            profile_content = '%s div.profile__contentBlock' % profile

            class SelectorTemplates:
                """Common templates of selectors."""
                hidden = '%s[style="display: none;"]'
                visible = '%s:not([style="display: none;"])'

        class ScriptTemplates:
            """Common templates of scripts."""
            getattr = 'n => n.getAttribute("%s")'
            selector = 'document.querySelector("%s")'
            selector_all = 'document.querySelectorAll("%s")'
            click = '{0}.click()'.format(selector)
            computed_style = 'window.getComputedStyle({0})'.format(selector)
            display = '{0}["display"]'.format(computed_style)
            visible = '{0} != "none"'.format(display)
            length = '{0}.length'.format(selector_all)

        scroll = 'window.scroll(0, document.body.scrollHeight)'

    s = Scripts
    ss = Scripts.Selectors
    sst = Scripts.ScriptTemplates
    ssst = Scripts.Selectors.SelectorTemplates

    def __init__(self, api: APIScraper, name: str):
        super().__init__(api, name)
        self.page = None

    def __getattr__(self, name):
        name = self.name + '.' + name
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

    url = 'https://my.mail.ru/my/communities'

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            groups = (
                scraper.ss.content +
                ' div.groups-catalog'
                ' div.groups-catalog__mine-groups'
                ' div.groups-catalog__small-groups'
            )
            bar = '%s div.groups-catalog__groups-more' % groups
            hidden_bar = scraper.ssst.hidden % bar
            visible_bar = scraper.ssst.visible % bar
            catalog = '%s div.groups__container' % groups
            button = '%s span.ui-button-gray' % bar
            progress_button = '%s span.progress' % bar
            item = '%s div.groups__item' % catalog

        click = scraper.sst.click % Selectors.button
        button_class = scraper.sst.getattr % 'class'
        bar_css = scraper.sst.getattr % 'style'
        loaded = '{0} > %d'.format(scraper.sst.length % Selectors.item)

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, limit=10, offset=0, ext=0):
        info = await self.api.users.getInfo(uids='')
        if isinstance(info, dict):
            return info
        url = self.url
        log.debug('go to %s' % url)
        self.page = await self.api.page(
            url,
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
        log.debug('scrape subset: offset={0}, limit={1}'.format(offset, limit))

        groups, cnt = [], 0
        async for group in self.Iterator(self, ext):
            if cnt < offset:
                continue
            else:
                groups.append(group)
            cnt += 1

            if len(groups) >= limit:
                break

        return groups

    class Iterator:
        """Yields groups from the beginning to the end."""

        def __init__(self, method, ext):
            self.counter = 0
            self.m = method
            self.ext = ext

            self.catalog = None
            self.load_more_hidden_bar = None
            self.load_more_bar = True
            self.elements = []

        async def __aiter__(self):
            self.catalog = await self.m.page.J(self.m.ss.catalog)
            if self.catalog:
                self.elements = await self.catalog.JJ(self.m.ss.item)
            return self

        async def __anext__(self):
            if self.counter >= self.offset:
                if self.load_more_bar is None:
                    raise StopAsyncIteration
                elif self.load_more_hidden_bar is not None:
                    raise StopAsyncIteration
                else:
                    await self.load_more()

            if self.catalog is None:
                raise StopAsyncIteration

            i = self.counter
            self.counter += 1

            element = self.elements[i]
            item = await GroupItem.from_element(element)
            link = item['link'].lstrip('/')
            resp = await self.m.api.session.public_request([link])
            group = await self.m.api.users.getInfo(uids=resp['uid'])
            return group[0] if self.ext else group[0]['uid']

        @property
        def offset(self):
            return len(self.elements)

        async def load_more(self):
            # click 'more' button
            if await self.m.page.J(self.m.ss.button):
                await self.m.page.evaluate(self.m.s.click)
            # wait downloading
            progress_button = True
            while progress_button:
                progress_button = await self.m.page.J(self.m.ss.progress_button)
            # get groups' DOM elements
            self.elements = await self.catalog.JJ(self.m.ss.item)
            # get 'load more' bar
            self.load_more_hidden_bar = await self.m.page.J(self.m.ss.hidden_bar)
            self.load_more_bar = await self.m.page.J(self.m.ss.bar)


class GroupsGetInfo(multiscraper):
    """Returns information about communities by their IDs."""

    class Scripts(multiscraper.s):
        class Selectors(multiscraper.ss):
            pass

    s = Scripts
    ss = Scripts.Selectors

    empty_objects_error = EmptyGroupsError
    ignored_errors = (APIError, KeyError)  # KeyError when group_info is absent

    async def init(self, uids=''):
        info = await self.api.users.getInfo(uids=uids)
        if isinstance(info, dict):
            return info
        url = info[0]['link']
        log.debug('go to %s' % url)
        self.page = await self.api.page(
            url,
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
                scraper.ss.profile_content +
                ' div.profile__activeLinks'
                ' div.profile__activeLinks_community'
            )
            join_span = '%s span.profile__activeLinks_button_enter' % links
            sent_span = '%s span.profile__activeLinks_link_modarated' % links
            approved_span = '%s span.profile__activeLinks_link_inGroup' % links
            auth_span = '%s div.l-popup_community-authorization' % links

        join_span_visible = scraper.sst.visible % Selectors.join_span
        sent_span_visible = scraper.sst.visible % Selectors.sent_span
        approved_span_visible = scraper.sst.visible % Selectors.approved_span

        join_click = '{0}'.format(scraper.sst.click % Selectors.join_span)

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, group_id=''):
        info = await self.api.users.getInfo(uids=group_id)
        if isinstance(info, dict):
            return info
        url = info[0]['link']
        log.debug('go to %s' % url)
        self.page = await self.api.page(
            url,
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

    class Scripts(scraper.s):
        class Selectors(scraper.ss):
            feed = '%s div.b-community__main-page__feed' % scraper.ss.main_page
            stream = '%s div.b-history[data-state]' % feed
            updating_stream = '%s[data-state=""]' % stream
            loading_stream = '%s[data-state="loading"]' % stream
            loaded_stream = '%s[data-state="loaded"]' % stream
            ended_stream = '%s[data-state="noevents"]' % stream
            content = '%s div.content-wrapper' % feed
            event = '%s div.b-history-event[data-astat]' % stream

    s = Scripts
    ss = Scripts.Selectors

    async def init(self, uid='', limit=10, skip=''):
        info = await self.api.users.getInfo(uids=uid)
        if isinstance(info, dict):
            return info
        url = info[0]['link']
        log.debug('go to %s' % url)
        self.page = await self.api.page(
            url,
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

        log.debug('scrape subset: skip={0}, limit={1}'.format(skip, limit))

        try:
            events = []
            async for event in self.Iterator(self):
                if skip:
                    skip = skip if event['id'] != skip else False
                else:
                    events.append(event)

                if len(events) >= limit:
                    break
        except (AccessDeniedError, BlackListError) as e:
            if self.api.session.pass_error:
                return e.error
            else:
                raise e

        return events

    class Iterator:
        """Yields stream events from the beginning to the end."""

        def __init__(self, method):
            self.counter = 0
            self.m = method

            self.ended_stream = None
            self.elements = []
            self.events = []
            self.content = None

        async def __aiter__(self):
            self.content = await self.m.page.J(self.m.ss.content)
            if self.content is None:
                log.debug('content is None ' + self.m.ss.content)
                signage = await self.m.page.J(self.m.ss.closed_signage)
                if signage:
                    raise AccessDeniedError()
                else:
                    raise BlackListError()
            self.elements = await self.content.JJ(self.m.ss.event)
            for element in self.elements[self.offset:]:
                self.events.append(await Event.from_element(element))
            return self

        async def __anext__(self):
            if self.counter >= self.offset:
                if await self.m.page.J(self.m.ss.ended_stream):
                    raise StopAsyncIteration
                else:
                    await self.load_more()

            if self.content is None:
                raise StopAsyncIteration

            i = self.counter
            self.counter += 1

            return self.events[i]

        @property
        def offset(self):
            return len(self.events)

        async def load_more(self):
            await self.m.page.evaluate(self.m.s.scroll)  # scroll

            # until stream's state is updated to 'loaded'
            loading_stream, updating_stream = True, True
            while loading_stream or updating_stream:
                stream = False
                # until stream's state is updated to 'loading' or 'updating'
                while not stream and self.content:
                    stream = await self.m.page.waitForSelector(self.m.ss.stream)
                    self.content = await self.m.page.J(self.m.ss.content)

                loading_stream = await self.m.page.J(self.m.ss.loading_stream)
                updating_stream = await self.m.page.J(self.m.ss.updating_stream)

            self.elements = await self.content.JJ(self.m.ss.event)
            for element in self.elements[self.offset:]:
                self.events.append(await Event.from_element(element))


scrapers = {
    'groups': APIScraperMethod,
    'groups.get': GroupsGet,
    'groups.getInfo': GroupsGetInfo,
    'groups.join': GroupsJoin,
    'stream': APIScraperMethod,
    'stream.getByAuthor': StreamGetByAuthor,
}
