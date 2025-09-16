import pytest
import os
from playwright.sync_api import sync_playwright
from configs.config import BROWSER, HEADED, SLOW_MO, BASE_URL, REPORT_PATH
from model.user import User

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


# If you installed python-dotenv for local convenience, auto-load .env (safe because .env is in .gitignore)
try:
    from dotenv import load_dotenv
    # load .env from repo root if present (no-op if not)
    load_dotenv()
except Exception:
    # dotenv not installed or failed — that's fine; we'll rely on env vars
    pass

@pytest.fixture(scope="session")
def credentials():
    """
    Provide user credentials read from environment variables.

    Required env vars:
      - SAUCE_USERNAME
      - SAUCE_PASSWORD

    Usage in tests: add 'credentials' parameter and use credentials.username, credentials.password
    """
    username = os.getenv("SAUCE_USERNAME")
    password = os.getenv("SAUCE_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing credentials: set SAUCE_USERNAME and SAUCE_PASSWORD environment variables. "
            "You can create a local .env file (not committed) from .env.example for convenience."
        )

    return User(username=username, password=password)
