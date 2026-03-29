from playwright.sync_api import Page
from pages.auth_page import AuthPage
from pages.page import BasePage

profile_page_selector = {
    "want to read count": "a[data-ol-link-track='MyBooksSidebar|WantToRead'] > span.li-count",
    "currently reading count": "a[data-ol-link-track='MyBooksSidebar|CurrentlyReading'] > span.li-count",
    "already read count": "a[data-ol-link-track='MyBooksSidebar|AlreadyRead'] > span.li-count",

}


class ProfilePage(BasePage):
    def __init__(self):
        super().__init__()
        super().login()
        if not self.is_logged_in:
            auth = AuthPage(self.page)
            auth.log_in("moshewinberg+tests@gmail.com", "b6HhJp2sF3g4R-X")
        self.navigate("m0526750830")

    def navigate(self, username: str) -> None:
        self.page.goto(f"https://openlibrary.org/people/{username}/books")


    def _get_quantity(self, selector: str) -> int:
        element = self.page.query_selector(profile_page_selector[selector])

        if element is None:
            print(f"Element for selector '{selector}' not found.")
            return 0

        quantity_text = element.inner_text().strip()
        try:
            return int(quantity_text)
        except ValueError:
            print(f"Could not convert '{quantity_text}' to an integer.")
            return 0

    def get_want_to_read_quantity(self) -> int:
        return self._get_quantity("want to read count")

    def get_currently_reading_quantity(self) -> int:
        return self._get_quantity("currently reading count")

    def get_already_read_quantity(self) -> int:
        return self._get_quantity("already read count")