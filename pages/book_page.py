from playwright.sync_api import Page
from pages.auth_page import AuthPage
from pages.page import BasePage

book_page_selector = {
    "master button": "button.book-progress-btn.primary-action > span.btn-text",
    "master button active": "button.book-progress-btn.primary-action.activated > span.btn-text",
    "arrow button": "div.generic-dropper__actions > a",
    "buttons elements": "div.read-statuses > form.reading-log > button.nostyle-btn",
}


class BookPage(BasePage):
    def __init__(self, book_url: str):
        super().__init__()
        self.book_url = book_url
        self.navigate()
        super().login()
        if not self.is_logged_in:
            auth = AuthPage(self.page)
            auth.log_in("moshewinberg+tests@gmail.com", "b6HhJp2sF3g4R-X")

    def navigate(self) -> None:
        self.page.goto(self.book_url)

    def click_master_reading_button(self, title: str) -> bool:
        master_element = self.page.query_selector(
            book_page_selector["master button active"])
        if master_element is None:
            master_element = self.page.query_selector(
                book_page_selector["master button"])

            if master_element is None:
                return False

            if master_element.inner_text().strip().lower() == title.lower():
                master_element.click()
                return True
            return False

        elif master_element.inner_text().strip().lower() == title.lower():
            return True
        return False

    def invert_reading_buttons(self) -> None:
        arrow_element = self.page.query_selector(
            book_page_selector["arrow button"])
        if arrow_element is not None:
            arrow_element.click()

    def click_a_reading_button(self, title: str) -> None:
        button_elements = self.page.query_selector_all(
            book_page_selector["buttons elements"])

        for button in button_elements:
            if button.inner_text().strip().lower() == title.lower():
                if not button.is_visible():
                    self.invert_reading_buttons()
                button.click()
                return

        self.page.click(
            book_page_selector["add_to_reading_list_button"], timeout=5000)

    def set_book_as_want_to_read(self) -> None:
        if not self.click_master_reading_button("Want to Read"):
            self.click_a_reading_button("Want to Read")

    def set_book_as_already_read(self) -> None:
        if not self.click_master_reading_button("Already Read"):
            self.click_a_reading_button("Already Read")

    def set_book_as_currently_reading(self) -> None:
        if not self.click_master_reading_button("Currently Reading"):
            self.click_a_reading_button("Currently Reading")
