import asyncio
from pathlib import Path

from playwright.async_api import ElementHandle, Page
import yaml

auth_page_selector = {
    "container": "form[id='register'].login.olform",
    "login_buttons": "a.btn",

}


class AuthPage:
    def __init__(self, page: Page):
        self.page = page

        self._log_in_element: ElementHandle | None = None
        self.is_logged_in = False

    def _get_credentials(self) -> tuple[str, str, str] | None:
        options_path = Path(__file__).resolve().parents[1] / "options.yaml"

        with options_path.open("r", encoding="utf-8") as options_file:
            options = yaml.safe_load(options_file) or {}

        account = options.get("account") or {}
        email = (account.get("email") or "").strip()
        username = (account.get("username") or "").strip()
        password = (account.get("password") or "").strip()

        if not username or not password:
            return None

        if username in {"your_username", "your_email@example.com"}:
            return None

        if password == "your_password":
            return None

        return email, username, password

    async def login(self) -> None:
        if not await self._is_logged_in():
            await self._navigate()
            cred = self._get_credentials()
            if cred is None:
                print(
                    "No valid credentials found in options.yaml. Please provide your email, username, and password to log in.")
                return
            email, username, password = cred
            if email and password:
                await self._log_in(email, password)

    async def _is_logged_in(self) -> bool:
        if self.page is None:
            raise ValueError("Page instance is not initialized.")

        print("Checking if user is already logged in...")
        login_buttons = await self.page.query_selector_all(
            auth_page_selector["login_buttons"])

        self.is_logged_in = True

        for button in login_buttons:
            if (await button.inner_text()).strip().lower() == "log in":
                self._log_in_element = button
                self.is_logged_in = False
                break

        if self.is_logged_in:
            print("User is already logged in.")
        return self.is_logged_in

    async def _await_page_load(self) -> None:
        await self.page.wait_for_selector(
            auth_page_selector["container"], timeout=5000)

    async def _navigate(self) -> None:
        if self._log_in_element is None:
            raise ValueError("Login element not found on the page.")
        await self._log_in_element.click()

    async def _log_in(self, username: str, password: str) -> None:
        await self._await_page_load()

        form = await self.page.query_selector(auth_page_selector["container"])
        if form is None:
            raise ValueError("Login form not found on the page.")

        email_input = await form.query_selector("input[name='username']")
        password_input = await form.query_selector("input[name='password']")

        if email_input is None or password_input is None:
            raise ValueError(
                "Email or password input not found in the login form.")

        await email_input.fill(username)
        await password_input.fill(password)
        submit_button = await form.query_selector("button[type='submit']")

        if submit_button is None:
            raise ValueError("Submit button not found in the login form.")

        await submit_button.click()
        await asyncio.sleep(5)  # Wait for login to process
        if not await self._is_logged_in():
            raise ValueError("Login failed. Please check your credentials.")
