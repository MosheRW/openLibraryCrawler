from playwright.sync_api import sync_playwright, Page
from helpers.browser import Browser
from helpers.screenshots_taker import take_screenshot
from pages.page import BasePage
from pages.search_results_page import SearchResultsPage


class HomePage(BasePage):
    def __init__(self, page: Page | None = None):
        super().__init__(page)
        self.navigate()

    def navigate(self) -> None:
        self.page.goto("https://openlibrary.org/")

    def _build_query(self, title: str | None, author: str | None, year: int | None) -> str:
        query_parts = []
        if title:
            query_parts.append(f"title:{title}")
        if author:
            query_parts.append(f"author:{author}")
        if year:
            query_parts.append(f"first_publish_year:[ * TO {year} ]")
        return " AND ".join(query_parts)

    def _search_books(self, title: str | None = None, author: str | None = None, year: int | None = None, limit: int = 5) -> SearchResultsPage:
        query = self._build_query(title, author, year)
        self.navigate()
        self.page.wait_for_selector("input[name='q']", timeout=5000)
        self.page.fill("input[name='q']", query)
        self.page.click("input.search-bar-submit[type='submit']", timeout=5000)
        self.take_screenshot("search_results")

        return SearchResultsPage(self.page)

    def search_books_by_title_under_year(self, query: str, year: int) -> SearchResultsPage:
        return self._search_books(title=query, year=year)

    def search_books_by_author_under_year(self, query: str, year: int) -> SearchResultsPage:
        return self._search_books(author=query, year=year)
