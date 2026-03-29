from pages.book_page import BookPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from pages.search_results_page import SearchResultsPage
import time


if __name__ == "__main__":
    home_page = HomePage()
    home_page.take_screenshot("home_page")

    search_results_page = home_page.search_books_by_title_under_year(
        "The Great Gatsby", 2026)

    books = search_results_page.get_books_urls(limit=35)
    
    
    profile_page = ProfilePage()
    print("Want to Read quantity:", profile_page.get_want_to_read_quantity())
    print("Currently Reading quantity:", profile_page.get_currently_reading_quantity())
    print("Already Read quantity:", profile_page.get_already_read_quantity())
