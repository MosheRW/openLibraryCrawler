from playwright.async_api import Page
from helpers.logger import Logger
from helpers.screenshots_taker import ScreenshotsTaker
from pages.auth_page import AuthPage


class BasePage:

    def __init__(self, page: Page):
        self._page = page
        self.auth = AuthPage(page)
        self.logger = Logger()

    @property
    def is_logged_in(self) -> bool:
        return self.auth.is_logged_in

    async def initialize(self) -> "BasePage":
        await self.auth.login()
        return self

    async def login(self) -> None:
        await self.auth.login()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise ValueError("Page instance is not initialized.")
        return self._page

    async def take_screenshot(self, name: str | None = None, query: str | None = None) -> None:
        if name is None:
            name = (await self._page.title()).replace(" ", "_").lower()
        await ScreenshotsTaker().take_screenshot(self._page, name, query)

    async def is_503_error(self) -> bool:
        content = await self._page.content()
        return "503 Service Unavailable" in content
