from playwright.async_api import Browser as PWBrowser, Playwright as AsyncPlaywright
from playwright.async_api import async_playwright


class Browser:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._playwright: AsyncPlaywright | None = None
        self._browser: PWBrowser | None = None
        self._page = None
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "Browser":
        return cls()

    async def get_browser(self) -> PWBrowser:
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=False)
        return self._browser

    async def get_page(self):
        if self._page is None:
            browser = await self.get_browser()
            self._page = await browser.new_page()
        return self._page

    async def close(self) -> None:
        if self._page is not None:
            await self._page.close()
            self._page = None

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None
