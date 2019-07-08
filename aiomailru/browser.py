import logging
import os
from pyppeteer import connect, launch


log = logging.getLogger(__name__)


class Browser:
    """A wrapper around pyppeteer.browser.Browser."""

    endpoint = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')

    def __init__(self, browser=None):
        self.browser = browser

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

    async def page(self, url, force=False, cookies=()):
        """Makes new page and returns its object.

        Args:
            url (str): URL to navigate page to. The url should
                include scheme, e.g. `https://`.
            force (bool): `True` - to always return a new page.
            cookies (tuple): cookies for the page.

        Returns:
            page (pyppeteer.page.Page): page.

        """

        if not self.browser:
            await self.start()

        blank_page = None
        for page in await self.browser.pages():
            if page.url == 'about:blank':
                blank_page = page
            elif force:
                continue
            elif page.url == url:
                break
        else:
            page = blank_page or await self.browser.newPage()
            await page.setViewport({'width': 1200,  'height': 1920})
            await page.setCookie(*cookies)

            log.debug('go to %s ..' % url)
            await page.goto(url)

        return page
