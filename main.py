from helpers.logger import Logger, print_error
from methods.orchestrator import orchestrator
from helpers.browser import Browser

import asyncio


async def main():
    browser = Browser.get_instance()
    logger = Logger()
    try:
        await orchestrator()
    except Exception as e:
        print_error(f"An error occurred: {e}")

    finally:
        await browser.close()
        logger.save_logs()

asyncio.run(main())
