
from playwright.async_api import Page
from datetime import datetime

from pathlib import Path


def title_to_filename(title: str) -> str:
    filename = "".join(c for c in title if c.isalnum()
                       or c in (" ", "_", "-")).rstrip()
    filename = filename.replace(" ", "_")
    return filename[:50]


class Results:
    _initialized = False
    _instance = None

    _prename: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._prename = title_to_filename(
            datetime.now().strftime("%Y%m%d%H%M%S"))
        self._initialized = True
        return

    @property
    def prename(self) -> str:
        return self._prename

    # Directory creation was moved to Logger.save_logs() and Playwright's screenshot()
    # (which creates parent directories automatically). This method is kept for reference.
    def _create_results_path(self, prename=None) -> Path:
        path = Path("results")
        path.mkdir(parents=True, exist_ok=True)
        path = Path("results", prename or self._prename)
        path.mkdir(parents=True, exist_ok=True)
        path = Path("results", prename or self._prename, "screenshots")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def screenshots_path(self) -> Path:
        return Path("results", self._prename, "screenshots")

    @property
    def results_path(self) -> Path:
        return Path("results", self._prename)
