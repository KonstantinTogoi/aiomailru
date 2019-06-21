"""My.Mail.Ru scrapers."""

import asyncio
import logging
import os
from concurrent.futures import FIRST_COMPLETED
from functools import lru_cache
from pyppeteer import connect, launch
from uuid import uuid4

from .api import API, APIMethod
from .objects.event import Event
from .sessions import TokenSession


log = logging.getLogger(__name__)
browser_endpoint = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')
browser_conn = {'browserWSEndpoint': browser_endpoint}


class APIScraper(API):
    """API scraper."""

    __slots__ = ('browser', )

    def __init__(self, session: TokenSession):
        super().__init__(session)
        self.browser = None

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

    async def browser(self):
        if self.api.browser is not None:
            return self.api.browser
        elif browser_endpoint is None:
            log.debug('launching new browser..')
            browser = await launch()
        else:
            log.debug('connecting to browser: {}'.format(browser_endpoint))
            browser = await connect(browser_conn)

        self.api.browser = browser
        return self.api.browser

    async def page(self, url):
        browser = await self.browser()
        pages = await browser.pages()
        blank_page = None

        for page in pages:
            if page.url == 'about:blank':
                blank_page = page
            if page.url == url:
                break
        else:
            log.debug('creating new page..')
            page = blank_page or await browser.newPage()
            await page.setViewport({'width': 1920,  'height': 1200})
            cookies = self.api.session.cookies

            if cookies:
                log.debug('setting cookies..')
                await page.setCookie(*cookies)

            log.debug('go to %s ..' % url)
            await page.goto(url)

        return page


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
        scrape = params.pop('scrape') if 'scrape' in params else False

        if scrape:
            uid = params.get('uid')
            uid = uid if uid is None else str(uid)
            skip = params.get('skip')
            limit = params.get('limit')
            uuid = skip if skip else uuid4().hex
            user = (await self.api.users.getInfo(uids=uid))[0]
            return await self.scrape(user['link'], skip, limit, uuid)
        else:
            return await super().__call__(**params)

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

        page = await self.page(url)

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

            for task in tasks:
                if not task.promise.done():
                    task.promise.set_result(None)
                    task._cleanup()

            for future in pending:
                future.cancel()

            state = await history_ctx.evaluate(self.history_state_js, history)
            if state == 'loading':
                await page.waitForXPath(self.history_loaded_state)


scrapers = {
    'stream': APIScraperMethod,
    StreamGetByAuthor.name: StreamGetByAuthor,
}
