from enum import Enum

from playwright.async_api import Page
from helpers.logger import Log, print_error, print_warning
from helpers.results import title_to_filename
from methods.measure_page_performance import measure_page_performance
from pages.inheriting_pages.base_page import BasePage
from helpers.browser import Browser
from helpers.configs import Config
from datetime import datetime
book_page_selector = {
    "master button": "button.book-progress-btn.primary-action > span.btn-text",
    "master button active": "button.book-progress-btn.primary-action.activated > span.btn-text",
    "arrow button": "div.generic-dropper__actions > a",
    "buttons elements": "div.read-statuses > form.reading-log > button.nostyle-btn",
}


class ReadingStatus(Enum):
    NOT_SUCCESS = -1
    FAILURE = 0
    SUCCESS = 1


class BookPage(BasePage):
    def __init__(self, page: Page, book_url: str):
        super().__init__(page)
        self.book_url = book_url

    async def _log(self, title: str = ""):
        threshold = Config().settings.thresholds.book_ms
        des = await measure_page_performance(self._page, self._page.url, threshold)
        warning = None
        if not des["is_within_threshold"]:
            warning = f"load_time {des['load_time_ms']}ms exceeded threshold {threshold}ms"
            print_warning(f"[PERF] book_page{title}: {warning}")
        self.logger.add_log(Log(date=datetime.now(), url=self.book_url, description=title, page="book_page", dom_content_loaded_ms=des["dom_content_loaded_ms"], first_paint_ms=des[
            "first_paint_ms"], load_time_ms=des["load_time_ms"], is_within_threshold=des["is_within_threshold"], warning=warning))

    @classmethod
    async def create(cls, book_url: str, page: Page | None = None) -> "BookPage":
        if page is None:
            page = await Browser.get_instance().get_page()
        instance = cls(page, book_url)
        await instance.navigate()
        await instance.initialize()
        return instance

    async def navigate(self, count: int = 0) -> None:
        await self._page.goto(self.book_url)

        if await self.is_503_error():
            print_warning(
                "503 error detected on book page, retrying navigation...")
            if count <= 5:
                await self.navigate(count + 1)
            else:
                print_error(
                    "Exceeded maximum retry attempts for loading book page.")
                raise Exception(
                    "Failed to load book page after multiple attempts.")

        await self._page.wait_for_selector("div.generic-dropper-wrapper.my-books-dropper")
        await self._log(" - navigate")

    async def click_master_reading_button(self, title: str) -> ReadingStatus:
        """
        First, we check if the master button is active. If it is, we compare its title with the provided title.
        If they match, we return True.
        If they don't match, we return the actual title of the active button, which indicates that the book is marked as a different status.
        If the master button is not active, we look for the inactive master button.
        If we find it and its title matches the provided title, we click it to mark the book with the desired status and return True.
        If we don't find any master button or if the titles don't match, we return False, indicating that the book is not marked with the desired status and we couldn't change it using the master button.
        """
        await self._page.wait_for_selector(book_page_selector["master button"])

        master_element = await self._page.query_selector(
            book_page_selector["master button active"])

        # if the master button is inactive:
        if master_element is None:
            master_element = await self._page.query_selector(
                book_page_selector["master button"])

        # if there is no master button, we return failure:
            if master_element is None:
                return ReadingStatus.FAILURE

        # if the master button is inactive and its title matches the provided title, we click it and return success:
            if (await master_element.inner_text()).strip().lower() == title.lower():
                await master_element.click()
                return ReadingStatus.SUCCESS

        # if the master button is inactive and its title does not match the provided title, we return not success:
            return ReadingStatus.NOT_SUCCESS

        # if the master button is active, we compare its title with the provided title:
        element_title = (await master_element.inner_text()).strip().lower()

        # if the master button is active and its title matches the provided title, we return success:
        if element_title == title.lower():
            return ReadingStatus.SUCCESS
        else:
            # if the master button is active and its title does not match the provided title, we return not success:
            return ReadingStatus.NOT_SUCCESS

    async def invert_reading_buttons(self) -> None:
        arrow_element = await self._page.query_selector(
            book_page_selector["arrow button"])
        if arrow_element is not None:
            await arrow_element.click()

    async def click_a_reading_button(self, title: str) -> ReadingStatus:
        button_elements = await self._page.query_selector_all(
            book_page_selector["buttons elements"])

        for button in button_elements:
            if (await button.inner_text()).strip().lower() == title.lower():
                if not await button.is_visible():
                    await self.invert_reading_buttons()
                await button.click()
                return ReadingStatus.SUCCESS
        return ReadingStatus.FAILURE

    async def is_book_marked_as(self, title: str) -> int:
        result = await self.click_master_reading_button(title)
        if result is not ReadingStatus.SUCCESS:
            res = await self.click_a_reading_button(title)
            if res == ReadingStatus.SUCCESS:
                result = ReadingStatus.SUCCESS

        await self._log(" - set_book_as_" + title.lower().replace(" ", "_"))
        title = await self._page.title()
        # Wait for the activated button state to appear in the DOM, confirming
        # the shelf change before taking the screenshot. Falls back gracefully
        # if the button never activates (e.g. book was already in that state).
        try:
            await self._page.wait_for_selector(
                book_page_selector["master button active"], timeout=3000
            )
        except Exception:
            pass
        await self.take_screenshot(title_to_filename(title))

        if result == ReadingStatus.FAILURE:
            return 0
        elif result == ReadingStatus.SUCCESS:
            return 1
        else:
            return -1

    async def set_book_as_want_to_read(self) -> int:
        return await self.is_book_marked_as("Want to Read")

    async def set_book_as_already_read(self) -> int:
        return await self.is_book_marked_as("Already Read")

    async def set_book_as_currently_reading(self) -> int:
        return await self.is_book_marked_as("Currently Reading")
