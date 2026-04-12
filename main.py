from helpers.logger import Logger, print_error
from helpers.report_generator import generate_report
from methods.orchestrator import orchestrator
from helpers.browser import Browser
from helpers.results import Results

import asyncio


async def main():
    browser = Browser.get_instance()
    logger = Logger()
    try:
        await orchestrator()
    except Exception as e:
        # The finally block below always runs cleanup, so the exception is
        # caught here to allow save_logs() and generate_report() to complete
        # even on a failed run. A partial report is better than no report.
        print_error(f"An error occurred: {e}")

    finally:
        await browser.close()
        logger.save_logs()
        generate_report(Results().results_path)

asyncio.run(main())
