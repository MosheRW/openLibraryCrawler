
from playwright.async_api import Page

from pathlib import Path

from helpers.logger import print_info
from helpers.results import Results, title_to_filename


class ScreenshotsTaker:
    _initialized = False
    _instance = None

    _prename: str
    _results: Results

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._results = Results()
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    # Directory creation is handled automatically by Playwright's screenshot() call.
    # This method is kept for cases where explicit directory setup is needed before a run.
    def _create_screenshots_path(self, prename=None) -> Path:
        path = Path("results", prename or self._prename, "screenshots")
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def take_screenshot(self, page: Page, name: str, query: str | None = None) -> None:
        if query:
            path = self._results.screenshots_path / \
                query / f"{title_to_filename(name)}.png"
        else:
            path = self._results.screenshots_path / \
                f"{title_to_filename(name)}.png"
        await page.screenshot(path=path, full_page=True, type="png")
        print_info(f"Screenshot saved to: {path}")
