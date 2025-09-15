import pytest
import os
from playwright.sync_api import sync_playwright
from configs.config import BROWSER, HEADED, SLOW_MO, BASE_URL, REPORT_PATH

@pytest.fixture(scope="function")
def page():
    """
    Provides a Playwright `page` object for every test function.

    Uses the sync_playwright() context manager to start/stop Playwright cleanly.
    Default behaviour (from configs/config.py): Chromium + headed mode.
    You can override with env vars:
      HEADED=false  -> run headless
      BROWSER=chromium|firefox|webkit
      SLOW_MO=50    -> slow down actions for debugging
    """
    with sync_playwright() as p:
        # p.chromium / p.firefox / p.webkit
        browser_launcher = getattr(p, BROWSER)
        browser = browser_launcher.launch(headless=not HEADED, slow_mo=SLOW_MO)
        context = browser.new_context()
        page = context.new_page()
        # optional: set viewport / timeout etc here if desired
        yield page
        # teardown
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
