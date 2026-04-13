from helpers.results import Results
from helpers.screenshots_taker import ScreenshotsTaker

from .configs import Config
import json
import logging
from pathlib import Path
config = Config()

_file_logger = logging.getLogger("openLibraryCrawler")
_file_logger.setLevel(getattr(logging, config.settings.log_level.upper(), logging.INFO))
_handler = logging.FileHandler(config.settings.log_file, encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
_file_logger.addHandler(_handler)


def print_info(message):
    if config.settings.print_info:
        print(f"\033[94m[INFO]\033[0m {message}")


def print_error(message):
    if config.settings.print_errors:
        print(f"\033[91m[ERROR]\033[0m {message}")


def print_warning(message):
    if config.settings.print_info:
        print(f"\033[93m[WARNING]\033[0m {message}")


class Log:

    _url: str
    _page: str
    _first_paint_ms: int
    _dom_content_loaded_ms: int
    _load_time_ms: int
    _is_within_threshold: bool
    _warning: str | None

    def __init__(self, url: str, page: str, first_paint_ms: int, dom_content_loaded_ms: int, load_time_ms: int, is_within_threshold: bool, warning: str | None = None):

        self._url = url
        self._page = page
        self._first_paint_ms = first_paint_ms
        self._dom_content_loaded_ms = dom_content_loaded_ms
        self._load_time_ms = load_time_ms
        self._is_within_threshold = is_within_threshold
        self._warning = warning

    def __str__(self):
        base = f"URL: {self._url}, Page: {self._page}, First Paint: {self._first_paint_ms} ms, DOM Content Loaded: {self._dom_content_loaded_ms} ms, Load Time: {self._load_time_ms} ms, Within Threshold: {self._is_within_threshold}"
        return base if self._warning is None else f"{base}, Warning: {self._warning}"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def page(self):
        return self._page

    @property
    def url(self):
        return self._url

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

    @property
    def warning(self) -> str | None:
        return self._warning


class Logger:

    _instance = None
    _initialized = False

    _results: Results
    _logs: list[Log]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = True
            cls._instance._results = Results()
            cls._instance._logs = []
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
        msg = f"{log.page} | load={log.load_time_ms}ms fp={log.first_paint_ms}ms dcl={log.dom_content_loaded_ms}ms | url={log.url}"
        if log.warning:
            _file_logger.warning(f"{msg} | {log.warning}")
        else:
            _file_logger.info(msg)

    def get_logs(self) -> list[Log]:
        return self._logs

    def clear_logs(self):
        self._logs.clear()

    def save_logs(self):
        print_info(f"Saving {len(self._logs)} logs...")
        logs_data = [
            {
                "page": log.page,
                "url": log.url,
                "first_paint_ms": log.first_paint_ms,
                "dom_content_loaded_ms": log.dom_content_loaded_ms,
                "load_time_ms": log.load_time_ms,
                "is_within_threshold": log.is_within_threshold,
                **({"warning": log.warning} if log.warning is not None else {}),
            }
            for log in self._logs
        ]

        if not self._results.results_path.exists():
            self._results.results_path.mkdir(parents=True, exist_ok=True)

        output_path = Path(self._results.results_path,
                           "performance_report.json")
        with open(output_path, "w") as f:
            json.dump(logs_data, f, indent=2)
