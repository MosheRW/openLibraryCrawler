from playwright.async_api import Page
from pages.inheriting_pages.base_page import BasePage
from helpers.browser import Browser

book_page_selector = {
    "master button": "button.book-progress-btn.primary-action > span.btn-text",
    "master button active": "button.book-progress-btn.primary-action.activated > span.btn-text",
    "arrow button": "div.generic-dropper__actions > a",
    "buttons elements": "div.read-statuses > form.reading-log > button.nostyle-btn",
}


class BookPage(BasePage):
    def __init__(self, page: Page, book_url: str):
        super().__init__(page)
        self.book_url = book_url

    @classmethod
    async def create(cls, book_url: str, page: Page | None = None) -> "BookPage":
        if page is None:
            page = await Browser.get_instance().get_page()
        instance = cls(page, book_url)
        await instance.navigate()
        await instance.initialize()
        return instance

    async def navigate(self) -> None:
        await self.page.goto(self.book_url)
        await self.page.wait_for_selector("div.generic-dropper-wrapper.my-books-dropper")

    async def click_master_reading_button(self, title: str) -> bool | str:
        await self.page.wait_for_selector(book_page_selector["master button"])
        master_element = await self.page.query_selector(
            book_page_selector["master button active"])
        if master_element is None:
            master_element = await self.page.query_selector(
                book_page_selector["master button"])

            if master_element is None:
                return False

            if (await master_element.inner_text()).strip().lower() == title.lower():
                await master_element.click()
                return True
            return False

        element_title = (await master_element.inner_text()).strip().lower()
        if element_title == title.lower():
            return True
        elif element_title != title.lower():
            return element_title

        return False

    async def invert_reading_buttons(self) -> None:
        arrow_element = await self.page.query_selector(
            book_page_selector["arrow button"])
        if arrow_element is not None:
            await arrow_element.click()

    async def click_a_reading_button(self, title: str) -> bool:
        button_elements = await self.page.query_selector_all(
            book_page_selector["buttons elements"])

        for button in button_elements:
            if (await button.inner_text()).strip().lower() == title.lower():
                if not await button.is_visible():
                    await self.invert_reading_buttons()
                await button.click()
                return True
        return False

    async def set_book_as_want_to_read(self) -> int:
        result = await self.click_master_reading_button("Want to Read")
        if result is not True:
            res = await self.click_a_reading_button("Want to Read")
            if res:
                result = True

        if result == False:
            return 0
        elif result is True:
            return 1
        else:
            return -1

    async def set_book_as_already_read(self) -> int:
        result = await self.click_master_reading_button("Already Read")
        if result is not True:
            res = await self.click_a_reading_button("Already Read")
            if res:
                result = True
        if result == False:
            return 0
        elif result is True:
            return 1
        else:
            return -1

    async def set_book_as_currently_reading(self) -> int:
        result = await self.click_master_reading_button("Currently Reading")
        if result is not True:
            res = await self.click_a_reading_button("Currently Reading")
            if res:
                result = True

        if result == False:
            return 0
        elif result is True:
            return 1
        else:
            return -1
