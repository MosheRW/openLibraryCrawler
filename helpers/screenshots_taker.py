from playwright.async_api import Page

def screenshots_path():
    from pathlib import Path
    path = Path("screenshots")
    path.mkdir(parents=True, exist_ok=True)
    return path


async def take_screenshot(page: Page, name: str):
    path = screenshots_path() / f"{name}.png"
    await page.screenshot(path=path)
    print(f"Screenshot saved to: {path}")
