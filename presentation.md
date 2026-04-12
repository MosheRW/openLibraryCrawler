# OpenLibrary Crawler
### Web Automation & Performance Testing with Python + Playwright

---

## Slide 1 — What Is OpenLibrary?

- Free, open-source digital library run by the **Internet Archive**
- 25 million+ book records, community-edited (wiki-style)
- Unique among book sites: **free digital lending**, open API (no key required), open-source codebase
- Reading-list UI (Want to Read / Currently Reading / Already Read) that is not fully covered by the API alone — making it an interesting automation target

---

## Slide 2 — Project Goal

Automate the full book-management lifecycle and measure real site performance:

1. Authenticate as a real user
2. Search books by title + publication year
3. Add books to reading shelves
4. Assert shelf counts match expectations
5. Measure page load performance (First Paint, DCL, Load Time)
6. Generate an interactive HTML report

**Tech stack:** Python 3.10+ · Playwright (async) · asyncio · PyYAML · Chart.js

---

## Slide 3 — Architecture: Page Object Model

```
main.py
  └── orchestrator()
        ├── ProfilePage       ← shelf management & assertions
        ├── HomePage          ← search input
        ├── SearchResultsPage ← result parsing + pagination
        └── BookPage          ← "Add to shelf" actions

All pages inherit BasePage → login via AuthPage
```

**Patterns used:**

| Pattern | Where |
|---------|-------|
| Page Object Model | One class per page, selectors isolated inside it |
| Singleton | Browser, Logger, Config, Results — one instance per run |
| Factory Method | `PageClass.create()` handles async initialization |

---

## Slide 4 — Core Workflow

```
options.yaml
  ↓
Config (singleton) — credentials + queries + settings
  ↓
ProfilePage.create() → login → navigate to profile
  ↓ (optional) clear shelves
  ↓
For each Query:
  search_books_by_title_under_year()  → list of URLs
  add_books_to_reading_list(urls)     → (want_count, read_count)
  assert_reading_list_count(expected) → pass / AssertionError
  ↓
logger.save_logs() → performance_report.json
generate_report()  → report.html
```

Shelf counts **accumulate across queries** — each assertion checks the total shelf state, not just the books from that query.

---

## Slide 5 — Performance Monitoring

Metrics collected via the browser's **JS Performance API** on every page navigation:

| Metric | Source |
|--------|--------|
| `first_paint_ms` | `performance.getEntriesByType("paint")` |
| `dom_content_loaded_ms` | `PerformanceNavigationTiming.domContentLoadedEventEnd` |
| `load_time_ms` | `PerformanceNavigationTiming.loadEventEnd` |
| `is_within_threshold` | compared against configurable per-page limit |

Per-page thresholds: BookPage 2500 ms · ProfilePage 2000 ms · SearchResultsPage 5000 ms

**Output:** JSON log → deduplicated by `(url, page)` key → interactive HTML report with Chart.js doughnut + bar charts, screenshot gallery, sortable table.

---

## Slide 6 — Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Playwright over Selenium | Native async, built-in auto-wait, faster, modern API |
| Singleton Browser | One tab reused across all pages — no context switching overhead |
| `create()` factory on each page | Async `__init__` is not valid in Python; factory encapsulates setup |
| Book model with 6 export formats | JSON / XML / CSV / YAML / HTML / Markdown for downstream flexibility |
| YAML config (not CLI args) | Nested queries + credentials are cleaner in YAML than as flags |
| `ReadingStatus` Enum | Replaces a fragile `bool \| str` return type with explicit states |

---

## Slide 7 — Interesting Engineering Challenges

1. **Stale UI during bulk shelf clearing**
   OpenLibrary's "remove" button stops responding after ~5 successive removals.
   Fix: reload the page every `ITERATIONS_BEFORE_RELOAD` operations to reset the DOM.

2. **Shelf button has three states**
   Unset / set to this shelf / set to a different shelf.
   Modelled with a `ReadingStatus` Enum (`SUCCESS=1`, `FAILURE=0`, `NOT_SUCCESS=-1`).

3. **Login has no reliable post-login DOM signal**
   OpenLibrary redirects to `/people/<username>/books` but no element appears synchronously.
   Current approach: `wait_for_timeout(5000)`. Documented as tech debt; correct fix is `wait_for_url`.

4. **Cumulative shelf counts across queries**
   Each assertion checks total shelf state, so counters carry over between queries in the orchestrator.

5. **Duplicate performance entries**
   `BookPage.navigate()` and `is_book_marked_as()` both log metrics for the same URL.
   Fix: deduplicate by `(url, page)` key in the report generator.

---

## Slide 8 — Report Output

Generated `report.html` is a **self-contained file** (no server needed):

- KPI cards: total pages measured, pass/fail count, average load time
- Doughnut chart — pass rate (Chart.js)
- Bar chart — load times per page, colour-coded by threshold
- Screenshot gallery — every step captured
- Sortable table — all performance measurements

**Output structure:**
```
results/20240412143022/
  ├── performance_report.json
  ├── report.html
  └── screenshots/
      ├── profile_page_quantities.png
      └── python_programming/
          ├── want_to_read_001.png
          └── ...
```

---

## Slide 9 — OpenLibrary vs. Similar Sites

| Feature | OpenLibrary | Goodreads | LibraryThing | Google Books |
|---------|-------------|-----------|--------------|--------------|
| Owner | Internet Archive (nonprofit) | Amazon | TinyCat | Google |
| API | Free, no key | Deprecated (2020) | Key required | Key + quota |
| Open source | Yes | No | Partial | No |
| Digital lending | Yes | No | No | Preview only |
| Community editing | Yes (wiki) | No | Yes | No |
| Open data | Yes (CC0 dump) | No | No | No |
| Automatable? | Yes — UI + API | Very limited | Yes (key) | Yes (quota) |

**Why OpenLibrary for this project:** Only major book site that is simultaneously open-source, API-key-free, has digital lending, and imposes no rate limits for educational use.

---

## Slide 10 — Future Improvements

1. Replace `wait_for_timeout(5000)` post-login with `wait_for_url()` — eliminates flakiness
2. Add a `shelf` field to `Query` config — removes random shelf assignment, makes runs reproducible
3. Parallel query execution with `asyncio.gather()` + a `Page` pool
4. Retry decorator for flaky book-add and navigation operations
5. Fix `report_generator.py` gallery — change `glob("*.png")` to `glob("**/*.png")` so book screenshots appear
6. Persist results to SQLite for trend analysis across runs
7. Docker + CI integration — run on every commit, track performance regressions over time
