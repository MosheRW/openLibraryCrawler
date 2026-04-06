import yaml


class Account:
    def __init__(self, email: str, username: str, password: str):
        self._email = email
        self._username = username
        self._password = password

    def __str__(self) -> str:
        return f"Account(email='{self.email}', username='{self.username}', password='{'*' * len(self.password)}')'"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def email(self) -> str:
        return self._email

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password


class Settings:
    def __init__(self, headless: bool = True, output_format: str = "json", output_directory: str = "results",
                 initialize_book_shelves: bool = True, print_info: bool = True, print_errors: bool = True, save_results: bool = True, log_level: str = "INFO", log_file: str = "app.log"):
        self._headless = headless
        self._output_format = output_format
        self._output_directory = output_directory
        self._initialize_book_shelves = initialize_book_shelves
        self._print_info = print_info
        self._print_errors = print_errors
        self._save_results = save_results
        self._log_level = log_level
        self._log_file = log_file

    @property
    def headless(self) -> bool:
        return self._headless

    @property
    def output_format(self) -> str:
        return self._output_format

    @property
    def output_directory(self) -> str:
        return self._output_directory

    @property
    def print_info(self) -> bool:
        return self._print_info

    @property
    def print_errors(self) -> bool:
        return self._print_errors

    @property
    def save_results(self) -> bool:
        return self._save_results

    @property
    def initialize_book_shelves(self) -> bool:
        return self._initialize_book_shelves

    @property
    def log_level(self) -> str:
        return self._log_level

    @property
    def log_file(self) -> str:
        return self._log_file


class Query:
    def __init__(self, query: str, max_year: int = 2024, limit: int = 10):
        self._query = query
        self._max_year = max_year
        self._limit = limit

    @property
    def query(self) -> str:
        return self._query

    @property
    def max_year(self) -> int:
        return self._max_year

    @property
    def limit(self) -> int:
        return self._limit


class Config:
    _instance = None
    _initialized = False

    _account: Account
    _queries: list[Query]
    _settings: Settings

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with open("options.yaml", "r") as f:
            config_data = yaml.safe_load(f)
            self._account = Account(**config_data["account"])
            self._queries = [Query(**query)
                             for query in config_data["queries"]]
            self._settings = Settings(**config_data["settings"])
        self._initialized = True

    @property
    def account(self) -> Account:
        return self._account

    @property
    def queries(self) -> list[Query]:
        return self._queries

    @property
    def settings(self) -> Settings:
        return self._settings
