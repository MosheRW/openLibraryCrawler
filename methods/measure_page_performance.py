from playwright.async_api import Page


async def measure_page_performance(page: Page, url: str, threshold: int) -> dict:

    metrics = await page.evaluate(
        """
        () => {
            const navigationEntry = performance.getEntriesByType("navigation")[0];
            const paintEntries = performance.getEntriesByType("paint");
            const firstPaintEntry = paintEntries.find((entry) => entry.name === "first-paint");

            if (navigationEntry) {
                return {
                    first_paint_ms: firstPaintEntry ? Math.round(firstPaintEntry.startTime) : 0,
                    dom_content_loaded_ms: Math.round(navigationEntry.domContentLoadedEventEnd),
                    load_time_ms: Math.round(navigationEntry.loadEventEnd),
                };
            }

            const timing = performance.timing;
            const navigationStart = timing.navigationStart;

            return {
                first_paint_ms: firstPaintEntry ? Math.round(firstPaintEntry.startTime) : 0,
                dom_content_loaded_ms: timing.domContentLoadedEventEnd - navigationStart,
                load_time_ms: timing.loadEventEnd - navigationStart,
            };
        }
        """
    )

    return {
        "url": url,
        "first_paint_ms": metrics["first_paint_ms"],
        "dom_content_loaded_ms": metrics["dom_content_loaded_ms"],
        "load_time_ms": metrics["load_time_ms"],
        "is_within_threshold": metrics["load_time_ms"] <= threshold,
    }
