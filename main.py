from pages.book_page import BookPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from pages.search_results_page import SearchResultsPage
import time
import random
import asyncio


async def search_books_by_title_under_year(title: str, year: int, limit: int = 5) -> list[str]:
    home_page = HomePage()
    search_results_page = home_page.search_books_by_title_under_year(
        title, year)
    return search_results_page.get_books_urls(limit)


async def add_books_to_reading_list(urls: list[str]):
    want_to_read = already_read = 0
    for url in urls:
        book_page = BookPage(url)
        if random.choice([True, False]):
            book_page.set_book_as_want_to_read()
            want_to_read += 1
        else:
            book_page.set_book_as_already_read()
            already_read += 1
    print(
        f"Added {want_to_read} books to 'Want to Read' and {already_read} books to 'Already Read'.")
    return want_to_read, already_read


async def assert_reading_list_count(expected_want_to_read: int, expected_already_read: int):
    profile_page = ProfilePage()
    actual_want_to_read = profile_page.get_want_to_read_quantity()
    actual_already_read = profile_page.get_already_read_quantity()

    assert actual_want_to_read == expected_want_to_read, f"Expected {expected_want_to_read} books in 'Want to Read', but found {actual_want_to_read}."
    assert actual_already_read == expected_already_read, f"Expected {expected_already_read} books in 'Already Read', but found {actual_already_read}."


async def main():
    urls = await search_books_by_title_under_year("The Great Gatsby", 2026, limit=35)
    want_to_read, already_read = await add_books_to_reading_list(urls)
    await assert_reading_list_count(want_to_read, already_read)

asyncio.run(main())