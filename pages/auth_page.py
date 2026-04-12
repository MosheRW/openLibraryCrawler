from playwright.async_api import ElementHandle, Page
from helpers.configs import Config

auth_page_selector = {
    # OpenLibrary reuses the same form element for both login and registration;
    # the id is 'register' even when the form is in login mode.
    "container": "form[id='register'].login.olform",
    "login_buttons": "a.btn",
    "email_input": "input[name='username']",
    "password_input": "input[name='password']",
    "submit_button": "button[type='submit']",

}


class AuthPage:
    def __init__(self, page: Page):
        self.page = page

        self._log_in_element: ElementHandle | None = None
        self.is_logged_in = False
        self._config = Config()

    def _get_credentials(self) -> tuple[str, str, str] | None:
        return self._config.account.email, self._config.account.username, self._config.account.password

    async def login(self) -> None:
        if not await self._is_logged_in():
            await self._navigate()
            cred = self._get_credentials()
            if cred is None:
                raise ValueError("Credentials not found in the configuration.")

            email, username, password = cred
            if email and password:
                await self._log_in(email, password)

    async def _is_logged_in(self) -> bool:
        if self.page is None:
            raise ValueError("Page instance is not initialized.")

        login_buttons = await self.page.query_selector_all(
            auth_page_selector["login_buttons"])

        self.is_logged_in = True

        for button in login_buttons:
            if (await button.inner_text()).strip().lower() == "log in":
                self._log_in_element = button
                self.is_logged_in = False
                break

        return self.is_logged_in

    async def _await_page_load(self) -> None:
        await self.page.wait_for_selector(
            auth_page_selector["container"], timeout=5000)

    async def _navigate(self) -> None:
        if self._log_in_element is None:
            raise ValueError("Login element not found on the page.")
        await self._log_in_element.click()

    async def _log_in(self, username: str, password: str) -> None:
        # OpenLibrary's login form accepts the email address in the field
        # named 'username'. The caller passes email as the first argument.
        await self._await_page_load()

        form = await self.page.query_selector(auth_page_selector["container"])
        if form is None:
            raise ValueError("Login form not found on the page.")

        email_input = await form.query_selector(auth_page_selector["email_input"])
        password_input = await form.query_selector(auth_page_selector["password_input"])

        if email_input is None or password_input is None:
            raise ValueError(
                "Email or password input not found in the login form.")

        await email_input.fill(username)
        await password_input.fill(password)
        submit_button = await form.query_selector(auth_page_selector["submit_button"])

        if submit_button is None:
            raise ValueError("Submit button not found in the login form.")

        await submit_button.click()
        # OpenLibrary doesn't expose a reliable post-login DOM signal (no unique
        # element appears, no predictable URL pattern). A fixed timeout allows the
        # session cookie to be set and the page to settle before checking login state.
        await self.page.wait_for_timeout(5000)
        if not await self._is_logged_in():
            raise ValueError("Login failed. Please check your credentials.")
