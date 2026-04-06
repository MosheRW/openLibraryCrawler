from playwright.async_api import Page
from helpers.logger import print_info
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
    def __init__(self, page: Page):
        super().__init__(page)

    async def navigate(self) -> None:
        await self.page.goto("https://openlibrary.org/")

    async def get_books(self, limit: int = 5, prev_books: list[Book] | None = None) -> list[Book]:
        await self.page.wait_for_selector(
            searchResultsPageSelector["results_list_container"], timeout=5000)
        book_elements = await self.page.query_selector_all(
            searchResultsPageSelector["results_list_container"])

        current_limit = limit - len(prev_books) if prev_books else limit
        books: list[Book] = []

        for element in book_elements[:current_limit]:
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
            year = int(year_text) if year_text.isdigit() else 0
            url = f"https://openlibrary.org/{url_element.split('/')[1]}/{url_element.split('/')[2]}" if url_element else None

            books.append(Book(title, author, year, url))

        if prev_books is not None:
            books = prev_books + books

        if len(books) < limit:
            await self.go_to_next_page()
            return await self.get_books(limit, books)
        else:
            return books

    async def get_books_urls(self, limit: int = 5) -> list[str]:
        books = await self.get_books(limit)
        books_set = set([book.url for book in books if book.url is not None])
        return list(books_set)

    async def go_to_next_page(self) -> None:
        next_button = await self.page.query_selector(
            searchResultsPageSelector["next_button"])

        if next_button:
            await next_button.click()
            await self.page.wait_for_load_state("networkidle")
            await self.take_screenshot("next_page")
