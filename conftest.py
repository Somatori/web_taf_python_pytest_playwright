import pytest
import os
import re
import shutil
import subprocess
import time
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
BROWSER_WIDTH = _cfg("BROWSER_WIDTH", 1280)
BROWSER_HEIGHT = _cfg("BROWSER_HEIGHT", 720)
HEADED = _cfg("HEADED", True)
SLOW_MO = _cfg("SLOW_MO", 0)
KEEP_VIDEOS = _cfg("KEEP_VIDEOS", False)

# base directories (from config / env)
BASE_VIDEO_DIR = _cfg("VIDEO_DIR", "artifacts/videos")
BASE_TRACE_DIR = _cfg("TRACE_DIR", "artifacts/traces")

# Determine pytest-xdist worker id (if running under pytest-xdist)
# xdist sets PYTEST_XDIST_WORKER (e.g. "gw0", "gw1"); fall back to "gw0" for single-process runs.
WORKER_ID = os.getenv("PYTEST_XDIST_WORKER") or os.getenv("PYTEST_WORKER") or "gw0"

# Per-worker directories to avoid collisions between parallel pytest workers
VIDEO_DIR = os.path.join(BASE_VIDEO_DIR, WORKER_ID)
TRACE_DIR = os.path.join(BASE_TRACE_DIR, WORKER_ID)

# Video size defaults to browser size for consistency
VIDEO_WIDTH = _cfg("VIDEO_WIDTH", BROWSER_WIDTH) 
VIDEO_HEIGHT = _cfg("VIDEO_HEIGHT", BROWSER_HEIGHT)

KEEP_TRACES = _cfg("KEEP_TRACES", False)
TRACE_SNAPSHOTS = _cfg("TRACE_SNAPSHOTS", True)
TRACE_SCREENSHOTS = _cfg("TRACE_SCREENSHOTS", True)


# Create a filesystem-safe trace/video filename
def _safe_test_name(nodeid: str) -> str:
    name = nodeid.replace("::", "__")
    name = re.sub(r'[^0-9A-Za-z._-]+', '_', name)
    return name


def pytest_sessionstart(session):
    """
    Clean up previous Allure raw results before the test session starts.
    This removes the 'artifacts/allure-results' directory if present and
    creates an empty directory so the current run starts fresh.
    """
    try:
        results_dir = os.path.join(os.getcwd(), "artifacts", "allure-results")
        if os.path.isdir(results_dir):
            try:
                shutil.rmtree(results_dir)
                print(f"Removed existing Allure results directory: {results_dir}")
            except Exception as e:
                print(f"Warning: failed to remove {results_dir}: {e}")
        # recreate empty directory so later steps can write into it
        os.makedirs(results_dir, exist_ok=True)
    except Exception as e:
        print("Warning: pytest_sessionstart cleanup failed:", e)


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

    # Build launch args (set native window size in headed mode)
    launch_args = []
    try:
        if HEADED:
            launch_args.append(f"--window-size={int(BROWSER_WIDTH)},{int(BROWSER_HEIGHT)}")
    except Exception:
        # fallback: ignore malformed values
        launch_args = []

    # Pass args only if non-empty (Playwright accepts None)
    browser = browser_launcher.launch(
        headless=not HEADED,
        slow_mo=SLOW_MO,
        args=launch_args or None,
    )
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
        viewport={"width": int(BROWSER_WIDTH), "height": int(BROWSER_HEIGHT)},
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

    # Teardown: stop tracing, handle trace/video retention, attach to Allure if requested, then close context
    try:
        # Attempt guarded import of allure for attaching artifacts (if installed)
        try:
            import allure
            from allure_commons.types import AttachmentType
        except Exception:
            allure = None
            AttachmentType = None

        # close page to flush page-level resources
        try:
            page.close()
        except Exception:
            pass

        # stop tracing and write zip file (if tracing was started)
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

        # video handling: get the video file path (Playwright gives us a path,
        # but the file may be finalized only after context.close())
        video_path = None
        try:
            vid = page.video
            if vid:
                video_path = vid.path()
        except Exception:
            video_path = None

        # compute test result (failed or not)
        test_failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed

        # Now close the context — this is important: Playwright finalizes videos on context close
        try:
            context.close()
        except Exception:
            # If context.close fails, continue; we still try to attach/move files
            pass

        # Helper: wait for a file to become non-zero and stable for a short time
        def _wait_for_file_stable(path, timeout_sec=10, stable_for=0.5):
            """
            Wait until `path` exists, its size > 0, and size doesn't change for `stable_for` seconds.
            Returns True if file is stable and non-empty before timeout, False otherwise.
            """
            if not path:
                return False
            start = time.time()
            last_size = -1
            last_change_time = time.time()
            while True:
                try:
                    st = os.stat(path)
                    size = st.st_size
                except Exception:
                    size = -1

                now = time.time()
                if size > 0:
                    if size != last_size:
                        last_change_time = now
                        last_size = size
                    else:
                        # size unchanged since last check
                        if now - last_change_time >= stable_for:
                            return True
                # timeout
                if now - start > timeout_sec:
                    return size > 0
                time.sleep(0.25)

        # If there is a video path, wait until it's fully written (or timeout)
        if video_path:
            # If the video lives in a temporary folder Playwright created, it will be finalized after context.close()
            ok = _wait_for_file_stable(video_path, timeout_sec=15, stable_for=0.5)
            if not ok:
                print(f"WARNING: video file {video_path} did not stabilize within timeout; proceeding anyway.")

        # Best-effort attach: copy attachments into allure-results and then attach those copies.
        if allure and test_failed:
            allure_results_dir = os.getenv("ALLURE_RESULTS_DIR", "artifacts/allure-results")
            os.makedirs(allure_results_dir, exist_ok=True)

            def _copy_and_attach(src_path: str, dest_name: str, attach_name: str, mime_or_type):
                try:
                    if not src_path or not os.path.exists(src_path):
                        print(f"DEBUG: source not found for attach: {src_path}")
                        return False

                    dest_path = os.path.join(allure_results_dir, dest_name)
                    # copy the file into allure-results to make sure it's available to the reporter
                    shutil.copy2(src_path, dest_path)
                    print(f"DEBUG: copied {src_path} -> {dest_path}")

                    try:
                        if AttachmentType is not None and hasattr(AttachmentType, mime_or_type):
                            atype = getattr(AttachmentType, mime_or_type)
                            allure.attach.file(dest_path, name=attach_name, attachment_type=atype)
                        else:
                            fallback = "application/octet-stream"
                            if mime_or_type.lower() == "webm":
                                fallback = "video/webm"
                            elif mime_or_type.lower() == "zip":
                                fallback = "application/zip"
                            allure.attach.file(dest_path, name=attach_name, attachment_type=fallback)
                        print(f"DEBUG: attached {attach_name} -> {dest_path}")
                        return True
                    except Exception as e:
                        print("DEBUG: allure.attach.file failed:", e)
                        return False
                except Exception as e:
                    print("DEBUG: copy_and_attach failed:", e)
                    return False

            # Attach video
            if video_path:
                dest_video_name = f"{_safe_test_name(request.node.nodeid)}_video.webm"
                _copy_and_attach(video_path, dest_video_name, "video", "WEBM")

            # Attach trace
            if trace_path:
                dest_trace_name = f"{_safe_test_name(request.node.nodeid)}_trace.zip"
                _copy_and_attach(trace_path, dest_trace_name, "trace", "ZIP")

        # Keep or delete trace
        if trace_path and os.path.exists(trace_path):
            if KEEP_TRACES or test_failed:
                pass
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
                # only attempt rmdir if directory empty
                try:
                    os.rmdir(parent_v)
                except Exception:
                    pass
        except Exception:
            pass

    finally:
        # ensure context is closed (if not already)
        try:
            # if context still open, close it (safe no-op if already closed)
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


# Optional: automatically generate Allure HTML after pytest run when requested.
# Usage: set environment variable ALLURE_AUTO_GENERATE=1 before running pytest and ensure the 'allure' CLI is installed.
def _has_any_attachments(allure_results_dir: str, videos_dir: str) -> bool:
    """
    Quickly check if any likely attachment files exist in allure results or videos dir.
    Returns True if we find at least one candidate attachment file (.webm, .mp4, .zip).
    """
    try:
        for root_dir in (allure_results_dir, videos_dir):
            if not os.path.isdir(root_dir):
                continue
            for fn in os.listdir(root_dir):
                if fn.lower().endswith((".webm", ".mp4", ".zip")):
                    return True
        return False
    except Exception:
        # If something unexpected happens, be conservative and say attachments may exist.
        return True


def _wait_for_attachments_to_settle(allure_results_dir: str, videos_dir: str, max_wait_seconds: int = 10):
    """
    Wait until files in videos_dir / allure_results_dir have stable sizes or until timeout.
    Returns True if we observed at least one non-zero attachment and it stabilized, False otherwise.

    Optimization: if no candidate attachment files are present at all, return False immediately
    (skip waiting).
    """
    # Quick early-exit: if there are no attachments at all, skip waiting.
    if not _has_any_attachments(allure_results_dir, videos_dir):
        # No attachments to wait for
        return False

    start = time.time()
    seen_nonzero = False
    prev_sizes = {}

    while True:
        any_changing = False
        seen_nonzero = False

        for root_dir in (videos_dir, allure_results_dir):
            if not os.path.isdir(root_dir):
                continue
            for fn in os.listdir(root_dir):
                if fn.lower().endswith((".webm", ".mp4", ".zip")):
                    path = os.path.join(root_dir, fn)
                    try:
                        st = os.stat(path)
                        size = st.st_size
                    except Exception:
                        size = -1

                    if size > 0:
                        seen_nonzero = True

                    prev = prev_sizes.get(path)
                    if prev is None:
                        prev_sizes[path] = size
                        any_changing = True
                    else:
                        if size != prev:
                            any_changing = True
                            prev_sizes[path] = size

        if seen_nonzero and not any_changing:
            return True

        elapsed = time.time() - start
        if elapsed >= max_wait_seconds:
            return seen_nonzero

        time.sleep(0.5)


def pytest_sessionfinish(session, exitstatus):
    """
    Auto-generate Allure HTML report (if enabled) *only in the pytest controller process*.
    Avoid running this inside pytest-xdist workers to prevent concurrent generation collisions.
    """
    try:
        # If running under pytest-xdist worker, skip HTML generation here.
        if os.getenv("PYTEST_XDIST_WORKER") or os.getenv("PYTEST_WORKER"):
            return

        auto = os.getenv("ALLURE_AUTO_GENERATE", "0").lower() in ("1", "true", "yes")
        if not auto:
            return

        allure_cmd = shutil.which("allure")
        if not allure_cmd:
            print("ALLURE_AUTO_GENERATE is set but 'allure' CLI was not found in PATH. Skipping report generation.")
            return

        result_dir = os.getenv("ALLURE_RESULTS_DIR", "artifacts/allure-results")
        videos_dir = os.getenv("VIDEO_DIR", "artifacts/videos")
        report_dir = os.getenv("ALLURE_REPORT_DIR", "artifacts/allure-report")

        # If there are no candidate attachment files at all, skip waiting and generate immediately.
        if not _has_any_attachments(result_dir, videos_dir):
            print(" No attachments found; skipping attachment-stability wait and generating Allure report now.")
        else:
            # Wait for attachments to settle (so generated report picks them up)
            print(f" Allure auto-generation requested. Waiting up to 10s for attachments to settle...")
            ok = _wait_for_attachments_to_settle(result_dir, videos_dir, max_wait_seconds=10)
            if not ok:
                print("Warning: no non-empty attachments detected or attachments still changing after timeout; proceeding to generate report anyway.")

        print(f"Generating Allure report from {result_dir} -> {report_dir} ...")
        try:
            subprocess.run([allure_cmd, "generate", result_dir, "-o", report_dir, "--clean"], check=True)
            print(f"Allure report generated: {report_dir}/index.html")
        except subprocess.CalledProcessError as e:
            print("Allure CLI failed to generate report:", e)
    except Exception as e:
        print("Unexpected error when trying to auto-generate Allure report:", e)
