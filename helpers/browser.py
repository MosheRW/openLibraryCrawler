from playwright.sync_api import Browser as PWBrowser
from playwright.sync_api import Playwright, sync_playwright


class Browser:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._playwright_ctx = sync_playwright()
        self._playwright: Playwright | None = None
        self._browser: PWBrowser | None = None
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "Browser":
        return cls()

    def get_browser(self) -> PWBrowser:
        if self._browser is None:
            self._playwright = self._playwright_ctx.start()
            self._browser = self._playwright.chromium.launch(headless=False)
        return self._browser

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

