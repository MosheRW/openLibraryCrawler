
from pages.inheriting_pages.home_page import HomePage


async def search_books_by_title_under_year(title: str, year: int, limit: int = 5) -> list[str]:
    home_page = await HomePage.create()
    search_results_page = await home_page.search_books_by_title_under_year(
        title, year)
    return await search_results_page.get_books_urls(limit)
