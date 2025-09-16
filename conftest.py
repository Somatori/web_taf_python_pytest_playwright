import pytest
import os
import re
import shutil
from playwright.sync_api import sync_playwright
from configs.config import BROWSER, HEADED, SLOW_MO, BASE_URL, REPORT_PATH
from model.user import User


def _safe_test_name(nodeid: str) -> str:
    # create a filesystem-safe name based on pytest nodeid
    name = nodeid.replace("::", "__")
    name = re.sub(r'[^0-9A-Za-z._-]+', '_', name)
    return name


# Ensure pytest attaches test reports to node for later inspection in fixtures
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # attach the report object to the test item for later access
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="function")
def page(request):
    """
    Playwright page fixture that records video to artifacts/videos.

    Behavior:
      - by default keeps videos only for failed tests
      - set env KEEP_VIDEOS=true to keep videos for all tests
      - set env VIDEO_DIR to change the directory (default: artifacts/videos)
      - record size is 1280x720 (configurable in code)
    """
    VIDEO_DIR = os.getenv("VIDEO_DIR", "artifacts/videos")
    os.makedirs(VIDEO_DIR, exist_ok=True)

    keep_videos_all = os.getenv("KEEP_VIDEOS", "true").lower() in ("1", "true", "yes")

    with sync_playwright() as p:
        browser_launcher = getattr(p, BROWSER)
        browser = browser_launcher.launch(headless=not HEADED, slow_mo=SLOW_MO)
        # instruct Playwright to store per-page video in VIDEO_DIR
        context = browser.new_context(record_video_dir=VIDEO_DIR, record_video_size={"width": 1280, "height": 720})
        page = context.new_page()

        yield page

        # ---- teardown: flush & handle video ----
        try:
            # Close the page to flush the video file
            try:
                page.close()
            except Exception:
                pass

            # Attempt to retrieve the recorded video path (Playwright provides this)
            video_path = None
            try:
                vid = page.video
                if vid:
                    # .path() returns the path to the recorded webm file
                    video_path = vid.path()
            except Exception:
                video_path = None

            # Decide whether to keep the video based on test result or env override
            test_failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed

            if video_path and os.path.exists(video_path):
                safe_name = _safe_test_name(request.node.nodeid) + ".webm"
                dest = os.path.join(VIDEO_DIR, safe_name)

                if keep_videos_all or test_failed:
                    # move the produced video to a nicer file name
                    try:
                        # If dest exists, overwrite it
                        if os.path.exists(dest):
                            os.remove(dest)
                        shutil.move(video_path, dest)
                    except Exception:
                        # if move fails, leave the original file
                        pass
                else:
                    # test passed and KEEP_VIDEOS not set -> remove temporary video to save space
                    try:
                        os.remove(video_path)
                    except Exception:
                        pass

                # Attempt to remove the parent directory if it's empty (Playwright places the file in a directory)
                try:
                    parent = os.path.dirname(video_path)
                    if parent and os.path.isdir(parent):
                        os.rmdir(parent)
                except Exception:
                    pass

        finally:
            # close context and browser
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
