from helpers.logger import print_error, print_info
from pages.inheriting_pages.book_page import BookPage

import random


async def add_books_to_reading_list(urls: list[str]):
    """
    Adds books to the user's reading list by randomly assigning them to either the "Want to Read" or "Already Read" shelf.
    It iterates through the provided list of book URLs, navigates to each book's page, and attempts to add it to one of the shelves.
    If a book is already in one shelf, it skips adding it to the other and adjusts the counters accordingly.
    The function returns the total count of books added to each shelf.
    """
    want_to_read = already_read = 0
    if not urls:
        return want_to_read, already_read

    book_page = await BookPage.create(urls[0])
    for index, url in enumerate(urls):
        if index > 0:
            book_page.book_url = url
            await book_page.navigate()

        # Random shelf assignment exercises both "Want to Read" and "Already Read"
        # code paths in a single run. Runs are intentionally non-reproducible.
        if random.choice([True, False]):
            res = await book_page.set_book_as_want_to_read()
            if res == 0:
                print_error(f"Failed to add {url} to 'Want to Read' shelf, skipping counter.")
            else:
                want_to_read += 1
                # If the book was already in the "Already Read" shelf, it decreases the "Already Read" counter after it moved to "Want to Read" shelf
                if res == -1:
                    print_info(
                        f"Book at {url} was already in 'Already Read' shelf, skipping addition.")
                    already_read -= 1
        else:
            res = await book_page.set_book_as_already_read()
            if res == 0:
                print_error(f"Failed to add {url} to 'Already Read' shelf, skipping counter.")
            else:
                already_read += 1
                # If the book was already in the "Want to Read" shelf, it decreases the "Want to Read" counter after it moved to "Already Read" shelf
                if res == -1:
                    print_info(
                        f"Book at {url} was already in 'Want to Read' shelf, skipping addition.")
                    want_to_read -= 1

    return want_to_read, already_read
