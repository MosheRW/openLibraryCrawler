from datetime import datetime
from playwright.async_api import Page
from helpers.logger import Log, print_warning
from helpers.results import title_to_filename
from methods.measure_page_performance import measure_page_performance
from pages.inheriting_pages.base_page import BasePage
from utils.book import Book

searchResultsPageSelector = {
    "results_list_container": "li.searchResultItem",
    "title": "h3.booktitle",
    "author": "span.bookauthor > a",
    "year": "span.resultDetails > span:first-child",
    "url": "h3.booktitle > a",
    "next_button": "a.ChoosePage[data-ol-link-track='Pager|Next']"
}


class SearchResultsPage(BasePage):

    def __init__(self, page: Page, query: str = ""):
        super().__init__(page)
        self.current_page = 1
        self.query = query

    async def _log(self):
        threshold = 3000
        des = await measure_page_performance(self._page, self._page.url, threshold)
        warning = None
        if not des["is_within_threshold"]:
            warning = f"load_time {des['load_time_ms']}ms exceeded threshold {threshold}ms"
            print_warning(f"[PERF] search_results_page: {warning}")
        self.logger.add_log(Log(url=self._page.url, date=datetime.now(), page="search_results_page", dom_content_loaded_ms=des["dom_content_loaded_ms"], first_paint_ms=des[
                            "first_paint_ms"], load_time_ms=des["load_time_ms"], is_within_threshold=des["is_within_threshold"], warning=warning))

    async def navigate(self) -> None:
        await self._page.reload()
        await self._log()

    async def get_books(self, limit: int = 5, prev_books: list[Book] | None = None) -> list[Book]:
        await self._page.wait_for_selector(
            searchResultsPageSelector["results_list_container"], timeout=5000)
        book_elements = await self._page.query_selector_all(
            searchResultsPageSelector["results_list_container"])

        current_limit = limit - len(prev_books) if prev_books else limit
        books: list[Book] = []
        books_set = set()

        for element in book_elements:
            if len(books) >= current_limit or len(books_set) >= current_limit:
                break

            title_element = await element.query_selector(
                searchResultsPageSelector["title"])
            author_element = await element.query_selector(
                searchResultsPageSelector["author"])
            year_element = await element.query_selector(
                searchResultsPageSelector["year"])
            url_element = await element.query_selector(
                searchResultsPageSelector["url"])
            url_element = await url_element.get_attribute(
                "href") if url_element is not None else None

            title = (await title_element.inner_text()).strip() if title_element else "Unknown Title"
            author = (await author_element.inner_text()).strip() if author_element else "Unknown Author"

            year_text = (await year_element.inner_text()).strip().rsplit(
                " ", 1)[-1] if year_element else "Unknown Year"

            # Books without a publication year are skipped: a missing year means
            # the advanced search filter (first_publish_year:[* TO year]) can't be
            # verified for that entry, so it's safer to exclude it.
            if year_text.lower() == "unknown year":
                continue

            year = int(year_text) if year_text.isdigit() else 0
            url = f"https://openlibrary.org/{url_element.split('/')[1]}/{url_element.split('/')[2]}" if url_element else None

            book = Book(title, author, year, url)
            if book.url not in books_set:
                books.append(book)
                books_set.add(book.url)

        if prev_books is not None:
            books = prev_books + books

        # If this page didn't reach the limit, try the next page recursively.
        # When there is no next page, go_to_next_page() is a no-op and get_books_urls()
        # deduplicates the result — so fewer books than `limit` may be returned silently
        # if the search has fewer results than requested.
        if len(books) < limit:
            await self.go_to_next_page()
            return await self.get_books(limit, books)
        else:
            return books

    async def get_books_urls(self, limit: int = 5) -> list[str]:
        books = await self.get_books(limit)
        books_set = [book.url for book in books if book.url is not None]
        return books_set

    async def go_to_next_page(self) -> None:
        next_button = await self._page.query_selector(
            searchResultsPageSelector["next_button"])

        if next_button:
            await next_button.click()
            await self._page.wait_for_load_state("load")
            self.current_page += 1
            await self.take_screenshot(f"search_results_page_{self.current_page}", title_to_filename(self.query))


async def search_results_page_factory(page: Page, query: str = "") -> SearchResultsPage:
    results = SearchResultsPage(page, query)
    await results.navigate()
    return results
