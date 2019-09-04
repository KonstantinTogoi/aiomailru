import logging
import os
from pyppeteer import connect, launch


log = logging.getLogger(__name__)


class Browser:
    """A wrapper around pyppeteer.browser.Browser."""

    endpoint = os.environ.get('PYPPETEER_BROWSER_ENDPOINT')
    viewport = os.environ.get('PYPPETEER_BROWSER_VIEWPORT', '800,600')
    slow_mo = int(os.environ.get('PYPPETEER_BROWSER_SLOW_MO', '200'))

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
            self.browser = await connect(browser_conn, slowmMo=self.slow_mo)
        else:
            log.debug('launching new browser..')
            self.browser = await launch(slowMo=self.slow_mo)

        return self

    async def page(self, url, session_key,
                   cookies=(), force=False, context=None):
        """Makes new page and returns its object.

        Args:
            url (str): URL to navigate page to. The url should
                include scheme, e.g. `https://`.
            session_key (str): access token.
            cookies (tuple): cookies for the page.
            force (bool): `True` - to always return a new context.
            context (pyppeteer.browser.BrowserContext): browser context.

        Returns:
            page (pyppeteer.page.Page): page.

        """

        if not self.browser:
            await self.start()

        if context:
            pass
        elif (url, session_key) in self.contexts:
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
            await page.setRequestInterception(True)

            @page.on('request')
            async def on_request(request):
                if request.url.endswith('.png') or request.url.endswith('.jpg'):
                    await request.abort()
                else:
                    await request.continue_()

            await page.goto(url)

        return page
