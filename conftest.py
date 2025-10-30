import pytest
import os
import re
import shutil
from playwright.sync_api import sync_playwright
from model.user import User


# Try to import centralized config values, but fall back to safe defaults
try:
    from configs import config as cfg
except Exception:
    cfg = None

def _cfg(attr, default):
    if cfg is None:
        return default
    return getattr(cfg, attr, default)

# Config values (with sensible fallbacks)
BROWSER = _cfg("BROWSER", "chromium")
HEADED = _cfg("HEADED", True)
SLOW_MO = _cfg("SLOW_MO", 0)
KEEP_VIDEOS = _cfg("KEEP_VIDEOS", False)
VIDEO_DIR = _cfg("VIDEO_DIR", "artifacts/videos")
VIDEO_WIDTH = _cfg("VIDEO_WIDTH", 1280)
VIDEO_HEIGHT = _cfg("VIDEO_HEIGHT", 720)

KEEP_TRACES = _cfg("KEEP_TRACES", False)
TRACE_DIR = _cfg("TRACE_DIR", "artifacts/traces")
TRACE_SNAPSHOTS = _cfg("TRACE_SNAPSHOTS", True)
TRACE_SCREENSHOTS = _cfg("TRACE_SCREENSHOTS", True)


# Create a filesystem-safe trace/video filename
def _safe_test_name(nodeid: str) -> str:
    name = nodeid.replace("::", "__")
    name = re.sub(r'[^0-9A-Za-z._-]+', '_', name)
    return name


# Start Playwright once per session
@pytest.fixture(scope="session")
def playwright_session():
    p = sync_playwright().start()
    yield p
    try:
        p.stop()
    except Exception:
        pass


# Launch browser once per session (reused across tests)
@pytest.fixture(scope="session")
def browser(playwright_session):
    browser_launcher = getattr(playwright_session, BROWSER)
    browser = browser_launcher.launch(headless=not HEADED, slow_mo=SLOW_MO)
    yield browser
    try:
        browser.close()
    except Exception:
        pass


# Ensure pytest attaches test reports (traces/videos) to node for later inspection in fixtures
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# Per-test context + page fixture (isolated)
@pytest.fixture(scope="function")
def page(request, browser):
    """
    Provides a fresh context + page per test while reusing the session browser process.

    Benefits:
      - Tests are isolated (fresh context)
      - Much faster than launching a browser per test because the browser process is reused
    """
    # ensure dirs exist
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(TRACE_DIR, exist_ok=True)

    # Create a fresh context for this test (isolation)
    context = browser.new_context(
        record_video_dir=VIDEO_DIR,
        record_video_size={"width": int(VIDEO_WIDTH), "height": int(VIDEO_HEIGHT)},
    )

    # Start tracing on this context
    try:
        context.tracing.start(
            screenshots=bool(TRACE_SCREENSHOTS),
            snapshots=bool(TRACE_SNAPSHOTS),
            sources=True,
        )
    except Exception:
        # tracing may not be available on some setups - don't fail tests
        pass

    page = context.new_page()

    yield page

    # Teardown: stop tracing, handle trace/video retention, then close context
    try:
        # close page to flush video
        try:
            page.close()
        except Exception:
            pass

        # stop tracing and write zip file
        trace_path = None
        try:
            safe_name = _safe_test_name(request.node.nodeid)
            tmp_trace = os.path.join(TRACE_DIR, safe_name + ".zip")
            try:
                context.tracing.stop(path=tmp_trace)
                trace_path = tmp_trace
            except Exception:
                trace_path = None
        except Exception:
            trace_path = None

        # video handling: Playwright stores a video file per-page in a temp folder
        video_path = None
        try:
            vid = page.video
            if vid:
                video_path = vid.path()
        except Exception:
            video_path = None

        test_failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed

        # Keep or delete trace
        if trace_path and os.path.exists(trace_path):
            if KEEP_TRACES or test_failed:
                pass  # keep it as written
            else:
                try:
                    os.remove(trace_path)
                except Exception:
                    pass

        # Keep or move video
        if video_path and os.path.exists(video_path):
            safe_vid_dest = os.path.join(VIDEO_DIR, _safe_test_name(request.node.nodeid) + ".webm")
            if KEEP_VIDEOS or test_failed:
                try:
                    if os.path.exists(safe_vid_dest):
                        os.remove(safe_vid_dest)
                    shutil.move(video_path, safe_vid_dest)
                except Exception:
                    pass
            else:
                try:
                    os.remove(video_path)
                except Exception:
                    pass

        # attempt cleanup of intermediate directories
        try:
            parent_v = os.path.dirname(video_path) if video_path else None
            if parent_v and os.path.isdir(parent_v):
                os.rmdir(parent_v)
        except Exception:
            pass

    finally:
        try:
            context.close()
        except Exception:
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
