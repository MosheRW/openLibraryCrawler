from time import sleep

from playwright.sync_api import ElementHandle, Page
from pages.page import BasePage

auth_page_selector = {
    "container": "form[id='register'].login.olform",
}


class AuthPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def await_page_load(self) -> None:
        self.page.wait_for_selector(
            auth_page_selector["container"], timeout=5000)

    def log_in(self, username: str, password: str) -> None:
        self.await_page_load()

        form = self.page.query_selector(auth_page_selector["container"])
        if form is None:
            raise ValueError("Login form not found on the page.")

        email_input = form.query_selector("input[name='username']")
        password_input = form.query_selector("input[name='password']")

        if email_input is None or password_input is None:
            raise ValueError(
                "Email or password input not found in the login form.")

        email_input.fill(username)
        password_input.fill(password)
        submit_button = form.query_selector("button[type='submit']")

        if submit_button is None:
            raise ValueError("Submit button not found in the login form.")

        submit_button.click()
        sleep(5)  # Wait for login to process
        if not super()._is_logged_in():  # Update login status after attempting to log in
            raise ValueError("Login failed. Please check your credentials.")
