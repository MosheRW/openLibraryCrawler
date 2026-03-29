from playwright.sync_api import Page
from pages.page import BasePage
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
    def __init__(self, page: Page | None = None):
        super().__init__(page)

    def navigate(self) -> None:
        self.page.goto("https://openlibrary.org/")

    def get_books(self, limit: int = 5, prev_books: list[Book] | None = None) -> list[Book]:
        self.page.wait_for_selector(
            searchResultsPageSelector["results_list_container"], timeout=5000)
        book_elements = self.page.query_selector_all(
            searchResultsPageSelector["results_list_container"])

        current_limit = limit - len(prev_books) if prev_books else limit
        books: list[Book] = []

        for element in book_elements[:current_limit]:
            title_element = element.query_selector(
                searchResultsPageSelector["title"])
            author_element = element.query_selector(
                searchResultsPageSelector["author"])
            year_element = element.query_selector(
                searchResultsPageSelector["year"])
            url_element = element.query_selector(
                searchResultsPageSelector["url"])
            url_element = url_element.get_attribute(
                "href") if url_element is not None else None

            title = title_element.inner_text().strip() if title_element else "Unknown Title"
            author = author_element.inner_text().strip() if author_element else "Unknown Author"

            year_text = year_element.inner_text().strip().rsplit(
                " ", 1)[-1] if year_element else "Unknown Year"
            year = int(year_text) if year_text.isdigit() else 0
            url = f"https://openlibrary.org{url_element}" if url_element else None

            books.append(Book(title, author, year, url))

        if prev_books is not None:
            books = prev_books + books

        if len(books) < limit:
            self.go_to_next_page()
            return self.get_books(limit, books)
        else:
            return books

    def get_books_urls(self, limit: int = 5) -> list[str]:
        books = self.get_books(limit)
        return [book.url for book in books if book.url is not None]

    def go_to_next_page(self) -> None:
        next_button = self.page.query_selector(
            searchResultsPageSelector["next_button"])

        if next_button:
            next_button.click()
            self.page.wait_for_load_state("networkidle")
            self.take_screenshot("next_page")


if __name__ == "__main__":

    search_results_page = SearchResultsPage()
    search_results_page.take_screenshot("search_results_page")
