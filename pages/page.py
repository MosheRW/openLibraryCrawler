from playwright.sync_api import ElementHandle, Page
from helpers.browser import Browser
from helpers.screenshots_taker import take_screenshot
from time import sleep


base_page_selector = {
    "login_buttons": "a.btn",
}


class BasePage:
    _log_in_element: ElementHandle | None = None

    def __init__(self, page: Page | None = None):
        self.is_logged_in = False
        if page is None:
            page = Browser.get_instance().get_browser().new_page()
            self.page = page
        else:
            self.page = page

    def _is_logged_in(self) -> bool:
        if self.page is None:
            raise ValueError("Page instance is not initialized.")

        login_buttons = self.page.query_selector_all(
            base_page_selector["login_buttons"])

        self.is_logged_in = True

        for button in login_buttons:
            if button.inner_text().strip().lower() == "log in":
                self._log_in_element = button
                self.is_logged_in = False
                break

        if self.is_logged_in:
            print("User is already logged in.")
        return self.is_logged_in

    def _is_registered(self) -> bool:
        return self.is_logged_in

    def _register(self, username: str, password: str) -> None:
        pass

    def _login(self) -> None:
        if self._log_in_element is None:
            raise ValueError("Login element not found on the page.")
        self._log_in_element.click()

    def login(self) -> None:
        if not self._is_logged_in():
            self._login()

    def take_screenshot(self, name: str | None = None) -> None:
        if name is None:
            name = self.page.title().replace(" ", "_").lower()
        take_screenshot(self.page, name)
