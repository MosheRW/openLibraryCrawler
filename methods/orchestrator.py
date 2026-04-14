
from helpers.configs import Config
from helpers.logger import print_error, print_info
from helpers.screenshots_taker import ScreenshotsTaker
from methods.add_books_to_reading_list import add_books_to_reading_list
from methods.assert_reading_list_count import assert_reading_list_count
from methods.search_books_by_title_under_year import search_books_by_title_under_year
from pages.inheriting_pages.profile_page import ProfilePage

# Instantiated here to warm up the singleton before page objects use it,
# ensuring the same Results directory is referenced throughout the run.
screenshotsTaker = ScreenshotsTaker()


async def orchestrator():
    config = Config()

    if len(config.queries) == 0:
        raise ValueError("No queries found in configuration.")

    profile_page = await ProfilePage.create()

    if config.settings.initialize_book_shelves:
        await profile_page.get_want_and_already_read_quantities("before_initial")
        await profile_page.remove_all_books_from_shelves()

    # Counts accumulate across all queries: assert_reading_list_count checks the
    # total shelf state after each query, not just the books added by that query.
    want_to_read_prev, already_read_prev = await profile_page.get_want_and_already_read_quantities("initial")

    errors = []
    for query in config.queries:
        try:
            print_info(
                f"Query: {query.query}, Max Year: {query.max_year}, Limit: {query.limit}")

            urls = await search_books_by_title_under_year(query.query, query.max_year, query.limit)
            print_info(
                f"Found {len(urls)} books matching criteria for query '{query.query}'")

            want_to_read, already_read = await add_books_to_reading_list(urls, query.shelf)
            want_to_read_prev += want_to_read
            already_read_prev += already_read
            await assert_reading_list_count(want_to_read_prev, already_read_prev, query.query)
        except Exception as e:
            print_error(f"Error processing query '{query.query}': {e}")
            errors.append((query.query, str(e)))

    if errors:
        raise Exception(f"Errors occurred during processing:\n" +
                        "\n".join([f"Query: {q}, Error: {err}" for q, err in errors]))
