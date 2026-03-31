from playwright.async_api import Page
from helpers.screenshots_taker import take_screenshot
from pages.auth_page import AuthPage


class BasePage:
    
    def __init__(self, page: Page):
        self.page = page
        self.auth = AuthPage(page)        

    @property
    def is_logged_in(self) -> bool:
        return self.auth.is_logged_in

    async def initialize(self) -> "BasePage":
        await self.auth.login()
        return self

    async def login(self) -> None:
        await self.auth.login()

    @property
    def get_page(self) -> Page:
        if self.page is None:
            raise ValueError("Page instance is not initialized.")
        return self.page
  

  
    async def take_screenshot(self, name: str | None = None) -> None:
        if name is None:
            name = (await self.page.title()).replace(" ", "_").lower()
        await take_screenshot(self.page, name)

