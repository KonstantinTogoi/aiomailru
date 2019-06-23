import logging
import os
from pyppeteer import connect, launch

from .api import API


log = logging.getLogger(__name__)


class Browser(API):
    """A wrapper around pyppeteer.browser.Browser."""

    __slots__ = ('browser', )

    endpoint = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')

    def __init__(self, session=None, browser=None):
        super().__init__(session)
        self.browser = browser

    def __await__(self):
        return self.start().__await__()

    async def start(self):
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

    async def page(self, url):
        if not self.browser:
            await self.start()

        blank_page = None
        for page in await self.browser.pages():
            if page.url == 'about:blank':
                blank_page = page
            if page.url == url:
                break
        else:
            log.debug('creating new page..')
            page = blank_page or await self.browser.newPage()
            await page.setViewport({'width': 1200,  'height': 1920})
            cookies = self.session.cookies

            if cookies:
                log.debug('setting cookies..')
                await page.setCookie(*cookies)

            log.debug('go to %s ..' % url)
            await page.goto(url)

        return page
