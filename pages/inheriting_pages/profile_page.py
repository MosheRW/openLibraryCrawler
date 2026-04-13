from playwright.async_api import Page
from helpers.configs import Config
from helpers.logger import Log, print_error, print_info, print_warning
from helpers.results import title_to_filename
from methods.measure_page_performance import measure_page_performance
from pages.inheriting_pages.base_page import BasePage
from helpers.browser import Browser

profile_page_selector = {
    "want to read count": "a[data-ol-link-track='MyBooksSidebar|WantToRead'] > span.li-count",
    "currently reading count": "a[data-ol-link-track='MyBooksSidebar|CurrentlyReading'] > span.li-count",
    "already read count": "a[data-ol-link-track='MyBooksSidebar|AlreadyRead'] > span.li-count",
    "clear shelf": "form.reading-log.primary-action",

}


class ProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    @classmethod
    async def create(cls) -> "ProfilePage":
        instance = cls(await Browser.get_instance().get_page())
        config = Config()
        await instance.navigate(config.account.username)
        await instance.initialize()
        return instance

    async def navigate(self, username: str, count: int = 0) -> None:
        await self.page.goto(f"https://openlibrary.org/people/{username}/books")
        if await self.is_503_error():
            print_error(
                "503 error detected on profile page, retrying navigation...")
            if count <= 5:
                await self.navigate(username, count + 1)
            else:
                print_error(
                    "Exceeded maximum retry attempts for loading profile page.")
                raise Exception(
                    "Failed to load profile page after multiple attempts.")

        threshold = 2000
        des = await measure_page_performance(self.page, self.page.url, threshold)
        warning = None
        if not des["is_within_threshold"]:
            warning = f"load_time {des['load_time_ms']}ms exceeded threshold {threshold}ms"
            print_warning(f"[PERF] profile_page: {warning}")
        self.logger.add_log(Log(url=self.page.url, page="profile_page", dom_content_loaded_ms=des["dom_content_loaded_ms"], first_paint_ms=des[
                            "first_paint_ms"], load_time_ms=des["load_time_ms"], is_within_threshold=des["is_within_threshold"], warning=warning))

    async def _get_quantity(self, selector: str) -> int:
        """
        Retrieves the quantity of books for a given shelf by its selector.
        It first reloads the page to ensure the data is up-to-date, then waits for the element corresponding to the selector to be available.
        If the element is found, it extracts the inner text, trims it, and attempts to convert it to an integer.
        If any step fails (element not found or conversion error), it logs an error and returns 0.
        """

        # Reload is required because OpenLibrary updates sidebar counts asynchronously.
        # Note: get_want_and_already_read_quantities calls this method twice,
        # resulting in two full page reloads per assertion.
        await self.page.reload()
        await self.page.wait_for_selector(profile_page_selector[selector])
        element = await self.page.query_selector(profile_page_selector[selector])

        if element is None:
            print_error(f"Element for selector '{selector}' not found.")
            return 0

        quantity_text = (await element.inner_text()).strip()
        try:
            return int(quantity_text)
        except ValueError:
            print_error(f"Could not convert '{quantity_text}' to an integer.")
            return 0

    async def get_want_to_read_quantity(self) -> int:
        return await self._get_quantity("want to read count")

    async def get_currently_reading_quantity(self) -> int:
        return await self._get_quantity("currently reading count")

    async def get_already_read_quantity(self) -> int:
        return await self._get_quantity("already read count")

    async def get_want_and_already_read_quantities(self, title: str | None = None) -> tuple[int, int]:
        if title is not None:
            await self.take_screenshot(name=title_to_filename(title), query="profile_page_quantities")
        else:
            await self.take_screenshot(name="profile_page_quantities")

        want_to_read = await self.get_want_to_read_quantity()
        already_read = await self.get_already_read_quantity()
        return want_to_read, already_read

    async def navigate_to_want_to_read_shelf(self) -> None:
        await self.page.wait_for_selector(profile_page_selector["want to read count"])
        await self.page.click(profile_page_selector["want to read count"])

    async def navigate_to_already_read_shelf(self) -> None:
        await self.page.wait_for_selector(profile_page_selector["already read count"])
        await self.page.click(profile_page_selector["already read count"])

    async def _clear_shelf(self, shelf_click_selector: str) -> None:
        """
        Clears a shelf by repeatedly deactivating the first book until the shelf is empty. It handles potential issues with page updates by checking if the URL changes after each click and waiting if it doesn't. It also reloads the page after every ITERATIONS_BEFORE_RELOAD attempts to ensure the DOM is updated.
        """

        await self.page.click(shelf_click_selector)

        while True:
            button = await self.page.query_selector(profile_page_selector["clear shelf"])

            if button is None:
                print_info("No more books to remove from this shelf.")
                break
            else:
                current_url = self.page.url
                await button.click()
                
                print_info("Book removed, checking for next one...")

                if self.page.url == current_url:
                    await self.page.wait_for_timeout(1000)
                else:
                    await self.page.go_back()
                    continue

                await self.page.reload()

    async def remove_all_books_from_shelves(self) -> None:
        print_info("Clearing 'Want to Read' shelf...")
        while await self.get_want_to_read_quantity() > 0:
            await self._clear_shelf(profile_page_selector["want to read count"])

        print_info("Clearing 'Already Read' shelf...")
        while await self.get_already_read_quantity() > 0:
            await self._clear_shelf(profile_page_selector["already read count"])
