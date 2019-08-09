import logging
import os
from pyppeteer import connect, launch


log = logging.getLogger(__name__)


class Browser:
    """A wrapper around pyppeteer.browser.Browser."""

    endpoint = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')
    viewport = os.environ.get('PYPPETEER_BROWSER_VIEWPORT', '800,600')

    def __init__(self, browser=None):
        self.browser = browser
        self.contexts = {}

    def __await__(self):
        return self.start().__await__()

    async def start(self):
        """Starts chrome process or connects to the existing chrome."""

        if self.browser:
            pass
        elif self.endpoint:
            browser_conn = {'browserWSEndpoint': self.endpoint}
            log.debug('connecting: {}'.format(browser_conn))
            self.browser = await connect(browser_conn)
        else:
            log.debug('launching new browser..')
            self.browser = await launch()

        return self

    async def page(self, url, session_key, cookies=(), force=False):
        """Makes new page and returns its object.

        Args:
            url (str): URL to navigate page to. The url should
                include scheme, e.g. `https://`.
            session_key (str): access token.
            cookies (tuple): cookies for the page.
            force (bool): `True` - to always return a new context.

        Returns:
            page (pyppeteer.page.Page): page.

        """

        if not self.browser:
            await self.start()

        if (url, session_key) in self.contexts:
            context = self.contexts[(url, session_key)]
        elif force:
            context = await self.browser.createIncognitoBrowserContext()
        else:
            context = await self.browser.createIncognitoBrowserContext()
            self.contexts[(url, session_key)] = context

        blank_page = None
        for target in context.targets():
            if target.url == 'about:blank':
                blank_page = await target.page()
            elif target.url == url:
                page = await target.page()
                break
        else:
            page = blank_page or await context.newPage()
            viewport = ('width', 'height'), map(int, self.viewport.split(','))
            await page.setViewport(dict(zip(*viewport)))
            await page.setCookie(*cookies)

            log.debug('go to %s ..' % url)
            await page.goto(url)

        return page
