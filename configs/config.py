import os

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

# Report path used by pytest (pytest.ini will reference this path)
REPORT_PATH = os.getenv("REPORT_PATH", "artifacts/report.html")