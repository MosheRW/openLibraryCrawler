# openLibraryCrawler

A Python web automation tool that crawls [Open Library](https://openlibrary.org) to search for books by title and year, add them to a user's reading lists, verify shelf counts, and collect page performance metrics — all driven by a single YAML config file.

## What it does

For each search query defined in `options.yaml`, the crawler will:

1. Log in to Open Library with the configured account
2. Search for books matching the query, filtered to a maximum publication year
3. Add found books to the "Want to Read" or "Already Read" shelf (randomly chosen per book)
4. Assert that the reading list counts match the expected number of added books
5. Capture screenshots and page performance metrics (first paint, DOM content loaded, page load time)
6. Save a timestamped performance report to the `results/` directory

## Architecture

The project follows the **Page Object Model** pattern and is fully async (Python `asyncio` + Playwright).

```
openLibraryCrawler/
├── main.py                          # Entry point
├── options.yaml                     # Runtime configuration (credentials + queries)
├── options.example.yaml             # Configuration template
│
├── helpers/                         # Cross-cutting infrastructure
│   ├── browser.py                   # Singleton Playwright browser instance
│   ├── configs.py                   # Config data classes (Account, Settings, Query)
│   ├── logger.py                    # Performance metrics collector & JSON reporter
│   ├── results.py                   # Timestamped results directory manager
│   ├── screenshots_taker.py         # Screenshot capture handler
│   └── report_generator.py          # HTML report generator (Chart.js, dark theme)
│
├── pages/                           # Page Object Model layer
│   ├── auth_page.py                 # Login automation
│   └── inheriting_pages/
│       ├── base_page.py             # Shared page utilities (login, screenshots)
│       ├── home_page.py             # Search query execution
│       ├── search_results_page.py   # Result parsing, pagination, performance capture
│       ├── book_page.py             # "Add to shelf" interactions
│       └── profile_page.py          # Reading list count retrieval & shelf clearing
│
├── methods/                         # Business logic / workflow orchestration
│   ├── orchestrator.py              # Main workflow coordinator
│   ├── search_books_by_title_under_year.py
│   ├── add_books_to_reading_list.py
│   ├── assert_reading_list_count.py
│   └── measure_page_performance.py
│
├── utils/
│   └── book.py                      # Book data model (JSON, XML, CSV, HTML, Markdown, YAML export)
│
└── results/                         # Generated output (gitignored)
    └── <timestamp>/
        ├── performance_report.json
        └── screenshots/
```

## Requirements

- Python 3.8+
- A free [Open Library](https://openlibrary.org/account/create) account

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure credentials and queries

```bash
cp options.example.yaml options.yaml
```

Edit `options.yaml`:

```yaml
account:
  email: "your@email.com"
  username: "your_username"
  password: "your_password"

queries:
  - query: "python programming"
    max_year: 2024
    limit: 10
  - query: "data science"
    max_year: 2023
    limit: 5

settings:
  headless: true                  # Set to false to watch the browser
  output_format: "json"
  output_directory: "results"
  initialize_book_shelves: true   # Clear all shelves before each run
  print_info: true
  save_results: true
  log_level: "INFO"
  log_file: "app.log"
```

> **Note:** `options.yaml` contains plaintext credentials — keep it out of version control. It is already listed in `.gitignore`.

> **`.env` file:** Alternatively, copy `.env.example` to `.env` and fill in your credentials. Values in `.env` override `options.yaml`.

> **CI/CD:** Credentials can be supplied via environment variables instead of (or to override) `options.yaml`: `OL_EMAIL`, `OL_USERNAME`, `OL_PASSWORD`.

## Usage

```bash
python main.py
```

## Docker

```bash
# Build
docker build -t openlibrary-crawler .

# Run — credentials via .env, results persisted to host
docker run --env-file .env -v "$(pwd)/results:/app/results" openlibrary-crawler
```

Results land in `results/<timestamp>/` on the host after the run.

The crawler will authenticate, run all configured queries, and write output to `results/<timestamp>/`.

## Output

| File | Description |
|------|-------------|
| `results/<timestamp>/performance_report.json` | Page load metrics (first paint, DOM ready, load time) per query |
| `results/<timestamp>/report.html` | Interactive HTML report with charts, screenshot gallery, and sortable metrics table |
| `results/<timestamp>/screenshots/` | Screenshots captured during search and book interactions |

## Configuration reference

| Key | Type | Description |
|-----|------|-------------|
| `account.email` | string | Open Library login email |
| `account.username` | string | Open Library username |
| `account.password` | string | Open Library password |
| `queries[].query` | string | Book search term |
| `queries[].max_year` | int | Only include books published on or before this year |
| `queries[].limit` | int | Maximum number of books to process per query |
| `settings.headless` | bool | Run browser without a visible window |
| `settings.initialize_book_shelves` | bool | Clear all shelves before starting |
| `settings.save_results` | bool | Write screenshots and performance report to disk |
| `settings.thresholds.search_results_ms` | int | Max acceptable load time (ms) for the search results page (default: `3000`) |
| `settings.thresholds.book_ms` | int | Max acceptable load time (ms) for individual book pages (default: `2500`) |
| `settings.thresholds.profile_ms` | int | Max acceptable load time (ms) for the user profile page (default: `2000`) |