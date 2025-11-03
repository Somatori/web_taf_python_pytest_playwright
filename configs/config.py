import os

# Try to load a local .env automatically for convenience in dev.
# This ensures environment variables from .env are available when this module is imported.
try:
    from dotenv import load_dotenv  # python-dotenv
    load_dotenv()  # loads .env from repo root if present
except Exception:
    # python-dotenv not installed or failed; continue and rely on real env vars
    pass

# Base URL of the site under test
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/")

# Browser choice: 'chromium', 'firefox', 'webkit'
BROWSER = os.getenv("BROWSER", "chromium")

# Headed mode by default (True). Override via env var: HEADED=false
HEADED = os.getenv("HEADED", "true").lower() in ("1", "true", "yes")

# Slow motion (ms) for debugging; default 0. Set env var SLOW_MO=50 to slow actions.
try:
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))
except ValueError:
    SLOW_MO = 0

# Video recording controls
# KEEP_VIDEOS: if true, keep videos for all tests; otherwise keep only failed tests
KEEP_VIDEOS = os.getenv("KEEP_VIDEOS", "false").lower() in ("1", "true", "yes")

# Default directory where Playwright writes videos (overridable)
VIDEO_DIR = os.getenv("VIDEO_DIR", "artifacts/videos")

# Browser viewport / window size (width x height)
try:
    BROWSER_WIDTH = int(os.getenv("BROWSER_WIDTH", "1280"))
except ValueError:
    BROWSER_WIDTH = 1280

try:
    BROWSER_HEIGHT = int(os.getenv("BROWSER_HEIGHT", "720"))
except ValueError:
    BROWSER_HEIGHT = 720

# Default recorded video size (defaults to video size for consistency)
try:
    VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", str(BROWSER_WIDTH)))
except ValueError:
    VIDEO_WIDTH = BROWSER_WIDTH

try:
    VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", str(BROWSER_HEIGHT)))
except ValueError:
    VIDEO_HEIGHT = BROWSER_HEIGHT

# Tracing controls (Playwright trace)
# KEEP_TRACES: if true, keep traces for all runs; otherwise keep only failed tests
KEEP_TRACES = os.getenv("KEEP_TRACES", "false").lower() in ("1", "true", "yes")

# Directory to store trace zip files
TRACE_DIR = os.getenv("TRACE_DIR", "artifacts/traces")

# Whether to capture snapshots & screenshots in the trace (both recommended)
TRACE_SNAPSHOTS = os.getenv("TRACE_SNAPSHOTS", "true").lower() in ("1", "true", "yes")
TRACE_SCREENSHOTS = os.getenv("TRACE_SCREENSHOTS", "true").lower() in ("1", "true", "yes")
