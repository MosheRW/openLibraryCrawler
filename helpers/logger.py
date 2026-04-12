from helpers.results import Results
from helpers.screenshots_taker import ScreenshotsTaker

from .configs import Config
import json
from pathlib import Path
config = Config()


def print_info(message):
    if config.settings.print_info:
        print(f"\033[94m[INFO]\033[0m {message}")


def print_error(message):
    if config.settings.print_errors:
        print(f"\033[91m[ERROR]\033[0m {message}")


class Log:

    _url: str
    _page: str
    _first_paint_ms: int
    _dom_content_loaded_ms: int
    _load_time_ms: int
    _is_within_threshold: bool

    def __init__(self, url: str, page: str, first_paint_ms: int, dom_content_loaded_ms: int, load_time_ms: int, is_within_threshold: bool):

        self._url = url
        self._page = page
        self._first_paint_ms = first_paint_ms
        self._dom_content_loaded_ms = dom_content_loaded_ms
        self._load_time_ms = load_time_ms
        self._is_within_threshold = is_within_threshold

    def __str__(self):
        return f"URL: {self._url}, Page: {self._page}, First Paint: {self._first_paint_ms} ms, DOM Content Loaded: {self._dom_content_loaded_ms} ms, Load Time: {self._load_time_ms} ms, Within Threshold: {self._is_within_threshold}"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def page(self):
        return self._page

    @property
    def first_paint_ms(self):
        return self._first_paint_ms

    @property
    def dom_content_loaded_ms(self):
        return self._dom_content_loaded_ms

    @property
    def load_time_ms(self):
        return self._load_time_ms

    @property
    def is_within_threshold(self):
        return self._is_within_threshold


class Logger:

    _instance = None
    _initialized = False

    _results: Results
    _logs: list[Log] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = True
            cls._instance._results = Results()
        return cls._instance

    def __init__(self):
        if not self._initialized:
            return self.__new__(self.__class__)

    @staticmethod
    def info(message):
        print_info(message)

    def error(self, message):
        print_error(message)

    def add_log(self, log: Log):
        print_info(f"Adding log: {log}")
        self._logs.append(log)

    def get_logs(self) -> list[Log]:
        return self._logs

    def clear_logs(self):
        self._logs.clear()

    def save_logs(self):
        print_info(f"Saving {len(self._logs)} logs...")
        logs_data = [
            {
                "page": log.page,
                "url": log._url,
                "first_paint_ms": log.first_paint_ms,
                "dom_content_loaded_ms": log.dom_content_loaded_ms,
                "load_time_ms": log.load_time_ms,
                "is_within_threshold": log.is_within_threshold
            }
            for log in self._logs
        ]

        if not self._results.results_path.exists():
            self._results.results_path.mkdir(parents=True, exist_ok=True)

        output_path = Path(self._results.results_path,
                           "performance_report.json")
        with open(output_path, "w") as f:
            json.dump(logs_data, f, indent=2)
