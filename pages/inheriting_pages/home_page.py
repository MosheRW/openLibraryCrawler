from playwright.async_api import Page
from helpers.browser import Browser
from helpers.results import title_to_filename
from pages.inheriting_pages.base_page import BasePage
from pages.inheriting_pages.search_results_page import SearchResultsPage


home_page_selectors = {
    "input_search": "input[name='q']",
    "search_button": "input.search-bar-submit[type='submit']"
}


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    @classmethod
    async def create(cls, page: Page | None = None) -> "HomePage":
        instance = cls(await Browser.get_instance().get_page())
        await instance.navigate()
        await instance.initialize()
        return instance

    async def navigate(self) -> None:
        await self.page.goto("https://openlibrary.org/")

    def _build_query(self, title: str | None, author: str | None, year: int | None) -> str:
        query_parts = []
        if title:
            query_parts.append(f"title:{title}")
        if author:
            query_parts.append(f"author:{author}")
        if year:
            query_parts.append(f"first_publish_year:[ * TO {year} ]")
        return " AND ".join(query_parts)

    async def _search_books(self, title: str | None = None, author: str | None = None, year: int | None = None, limit: int = 5) -> SearchResultsPage:
        query = self._build_query(title, author, year)
        await self.navigate()
        await self.page.wait_for_selector(home_page_selectors["input_search"])
        await self.page.fill(home_page_selectors["input_search"], query)
        await self.page.wait_for_selector(home_page_selectors["search_button"])
        await self.page.click(home_page_selectors["search_button"])
        await self.take_screenshot(f"search_results_page_{1}", title_to_filename(f"{title}_{author}_{year}"))

        return SearchResultsPage(self.page, query)

    async def search_books_by_title_under_year(self, query: str, year: int) -> SearchResultsPage:
        return await self._search_books(title=query, year=year)

    async def search_books_by_author_under_year(self, query: str, year: int) -> SearchResultsPage:
        return await self._search_books(author=query, year=year)
