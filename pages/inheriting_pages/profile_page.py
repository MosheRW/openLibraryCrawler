from playwright.async_api import Page
from pages.inheriting_pages.base_page import BasePage
from helpers.browser import Browser

profile_page_selector = {
    "want to read count": "a[data-ol-link-track='MyBooksSidebar|WantToRead'] > span.li-count",
    "currently reading count": "a[data-ol-link-track='MyBooksSidebar|CurrentlyReading'] > span.li-count",
    "already read count": "a[data-ol-link-track='MyBooksSidebar|AlreadyRead'] > span.li-count",

}


class ProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    @classmethod
    async def create(cls) -> "ProfilePage":
        instance = cls(await Browser.get_instance().get_page())
        await instance.navigate("REDACTED_USERNAME")
        await instance.initialize()
        return instance

    async def navigate(self, username: str) -> None:
        await self.page.goto(f"https://openlibrary.org/people/{username}/books")

    async def _get_quantity(self, selector: str) -> int:
        element = await self.page.query_selector(profile_page_selector[selector])

        if element is None:
            print(f"Element for selector '{selector}' not found.")
            return 0

        quantity_text = (await element.inner_text()).strip()
        try:
            return int(quantity_text)
        except ValueError:
            print(f"Could not convert '{quantity_text}' to an integer.")
            return 0

    async def get_want_to_read_quantity(self) -> int:
        return await self._get_quantity("want to read count")

    async def get_currently_reading_quantity(self) -> int:
        return await self._get_quantity("currently reading count")

    async def get_already_read_quantity(self) -> int:
        return await self._get_quantity("already read count")

    async def get_