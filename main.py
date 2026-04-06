from helpers.logger import print_error, print_info
from methods.orchestrator import orchestrator
from methods.search_books_by_title_under_year import search_books_by_title_under_year
from methods.add_books_to_reading_list import add_books_to_reading_list
from methods.assert_reading_list_count import assert_reading_list_count
from pages.inheriting_pages.profile_page import ProfilePage
from helpers.browser import Browser

import asyncio


async def main():
    browser = Browser.get_instance()

    try:
        await orchestrator()
    except Exception as e:
        print_error(f"An error occurred: {e}")

    finally:
        await browser.close()

asyncio.run(main())
