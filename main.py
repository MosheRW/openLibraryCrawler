from pages.inheriting_pages.book_page import BookPage
from pages.inheriting_pages.home_page import HomePage
from pages.inheriting_pages.profile_page import ProfilePage
from helpers.browser import Browser

import random
import asyncio


async def search_books_by_title_under_year(title: str, year: int, limit: int = 5) -> list[str]:
    home_page = await HomePage.create()
    search_results_page = await home_page.search_books_by_title_under_year(
        title, year)
    return await search_results_page.get_books_urls(limit)


async def add_books_to_reading_list(urls: list[str]):
    want_to_read = already_read = 0
    if not urls:
        return want_to_read, already_read

    # Reuse a single browser page and just navigate it to each next book URL.
    book_page = await BookPage.create(urls[0])
    for index, url in enumerate(urls):
        if index > 0:
            book_page.book_url = url
            await book_page.navigate()

        if random.choice([True, False]):
            await book_page.set_book_as_want_to_read()
            want_to_read += 1
        else:
            await book_page.set_book_as_already_read()
            already_read += 1

    return want_to_read, already_read


async def assert_reading_list_count(expected_want_to_read: int, expected_already_read: int):
    profile_page = await ProfilePage.create()
    actual_want_to_read = await profile_page.get_want_to_read_quantity()
    actual_already_read = await profile_page.get_already_read_quantity()

    assert actual_want_to_read == expected_want_to_read, f"Expected {expected_want_to_read} books in 'Want to Read', but found {actual_want_to_read}."
    assert actual_already_read == expected_already_read, f"Expected {expected_already_read} books in 'Already Read', but found {actual_already_read}."


async def main():
    browser = Browser.get_instance()

    try:
        urls = await search_books_by_title_under_year("The Great Gatsby", 2026, limit=5)
        want_to_read, already_read = await add_books_to_reading_list(urls)
        await assert_reading_list_count(want_to_read, already_read)
        print(
            f"Test passed: {want_to_read} books added to 'Want to Read' and {already_read} books added to 'Already Read'.")
    finally:
        await browser.close()

asyncio.run(main())
