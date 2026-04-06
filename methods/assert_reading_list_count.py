from helpers.logger import print_info
from pages.inheriting_pages.profile_page import ProfilePage


async def assert_reading_list_count(expected_want_to_read: int, expected_already_read: int, title: str | None = None):
    profile_page = await ProfilePage.create()
    actual_want_to_read, actual_already_read = await profile_page.get_want_and_already_read_quantities(title)
    assert actual_want_to_read == expected_want_to_read and actual_already_read == expected_already_read, f"Expected {expected_want_to_read} books in 'Want to Read' and {expected_already_read} books in 'Already Read', but found {actual_want_to_read} and {actual_already_read}."
    print_info(
        f"Assertion passed: {actual_want_to_read} books in 'Want to Read' and {actual_already_read} books in 'Already Read' as expected.")
