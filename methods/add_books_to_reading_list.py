from helpers.logger import print_info
from pages.inheriting_pages.book_page import BookPage

import random


async def add_books_to_reading_list(urls: list[str]):
    want_to_read = already_read = 0
    if not urls:
        return want_to_read, already_read

    book_page = await BookPage.create(urls[0])
    for index, url in enumerate(urls):
        if index > 0:
            book_page.book_url = url
            await book_page.navigate()

        if random.choice([True, False]):
            res = await book_page.set_book_as_want_to_read()
            want_to_read += 1
            if res == -1:
                print_info(
                    f"Book at {url} was already in 'Already Read' shelf, skipping addition.")
                already_read -= 1
        else:
            res = await book_page.set_book_as_already_read()
            already_read += 1
            if res == -1:
                print_info(
                    f"Book at {url} was already in 'Want to Read' shelf, skipping addition.")
                want_to_read -= 1

    return want_to_read, already_read
