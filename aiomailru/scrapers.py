"""My.Mail.Ru scrapers."""

import asyncio
import logging
from concurrent.futures import FIRST_COMPLETED
from functools import lru_cache
from pyppeteer import launch
from uuid import uuid4

from .api import API, APIMethod
from .objects.event import Event
from .sessions import TokenSession


log = logging.getLogger(__name__)


class APIScraper(API):
    """API scraper."""

    __slots__ = ('browser', 'pages', )

    def __init__(self, session: TokenSession):
        super().__init__(session)
        self.browser = None
        self.pages = {}

    def __getattr__(self, name):
        return scrapers.get(name, APIMethod)(self, name)


class APIScraperMethod(APIMethod):
    """API scraper's method."""

    name = ''

    def __init__(self, api: APIScraper, name=''):
        super().__init__(api, self.name or name)
        self.api = api

    def __getattr__(self, name):
        name = self.name + '.' + name
        return scrapers.get(name, APIMethod)(self.api, name)


class StreamGetByAuthor(APIScraperMethod):
    """Returns a list of events from user or community stream by their IDs."""

    name = 'stream.getByAuthor'

    scroll_js = 'window.scroll(0, document.body.scrollHeight)'

    history_selector = 'div[data-mru-fragment="home/history"]'
    history_state_js = 'n => n.getAttribute("data-state")'

    event_selector = 'div.b-history-event'

    history_loaded_state = '/html/body/div[@id="boosterCanvas"]' \
                           '//div[@data-mru-fragment="home/history"]' \
                           '[@data-state]' \
                           '[@data-state!="loading"]'

    history_loading_state = '/html/body/div[@id="boosterCanvas"]' \
                            '//div[@data-mru-fragment="home/history"]' \
                            '[@data-state="loading"]'

    async def __call__(self, **params):
        uid = params['uid']
        skip = params.get('skip')
        scrape = params.get('scrape')
        limit = params.get('limit', 10)
        uuid = skip if skip else uuid4().hex
        user = (await self.api.users.getInfo(uids=str(uid)))[0]

        if scrape:
            return await self.scrape(user['link'], skip, limit, uuid)
        else:
            return await super().__call__(uid=uid, skip=skip, limit=limit)

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

        if self.api.browser is None:
            log.debug('launching browser..')
            self.api.browser = await launch()

        if url not in self.api.pages:
            log.debug('creating new page..')
            page = await self.api.browser.newPage()
            log.debug('go to %s' % url)
            await page.goto(url)
            self.api.pages[url] = page
        else:
            page = self.api.pages[url]

        history = await page.J(self.history_selector)
        history_ctx = history.executionContext
        state, elements = None, []

        while state != 'noevents':
            offset = len(elements)
            elements = await history.JJ(self.event_selector)

            for i in range(offset, len(elements)):
                event = await Event.from_element(elements[i])
                yield event

            await page.evaluate(self.scroll_js)

            tasks = [
                page.waitForXPath(self.history_loading_state),
                page.waitForXPath(self.history_loaded_state),
            ]

            _, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
            for future in pending:
                future.cancel()

            state = await history_ctx.evaluate(self.history_state_js, history)
            if state == 'loading':
                await page.waitForXPath(self.history_loaded_state)


scrapers = {
    'stream': APIScraperMethod,
    StreamGetByAuthor.name: StreamGetByAuthor,
}
