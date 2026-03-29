from pages.book_page import BookPage
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
import time


if __name__ == "__main__":
    # home_page = HomePage()
    # home_page.take_screenshot("home_page")

    # search_results_page = home_page.search_books_by_title_under_year(
    #     "The Great Gatsby", 2026)

    # books = search_results_page.get_books_urls(limit=35)

    # print(len(books), books)

    book_page = BookPage(
        "https://openlibrary.org/works/OL468431W/The_Great_Gatsby?edition=key%3A/books/OL35657482M")

    book_page.set_book_as_want_to_read()
    time.sleep(2)
    book_page.set_book_as_already_read()
    time.sleep(2)
    book_page.set_book_as_want_to_read()
    time.sleep(2)
    book_page.set_book_as_currently_reading()
    time.sleep(2)
    book_page.set_book_as_want_to_read()
    time.sleep(2)
    book_page.set_book_as_already_read()
    time.sleep(2)
    book_page.set_book_as_currently_reading()
    time.sleep(2)
    book_page.set_book_as_want_to_read()
    time.sleep(2)
    book_page.set_book_as_currently_reading()
    time.sleep(2)
