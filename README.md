A small, generic end-to-end Test Automation Framework (TAF) for web UI testing using **Python**, **pytest**, and **Playwright (sync API)**.  
The project implements the **Page Object Model (POM)** and is designed to be easy to use, extend and run locally. 

**KEY POINTS / FEATURES**
- Language: **Python**
- Test runner: **pytest**
- Browser automation: **Playwright (Chromium only, sync API)**
- Design: **Page Object** Model (`pages/`), simple dataclasses in `model/`
- Headed mode by default (can be toggled to headless)
- Per-test isolation using fresh browser contexts (fast and independent tests)
- Video recording and Playwright **tracing** support (kept on failures by default)
- HTML test report generated at `artifacts/report.html`
- No credentials stored in source — uses environment variables / `.env` for local convenience

## Activate venv:
source .venv/bin/activate

## Run the full suite (headed by default):
pytest -q

## Run headless:
export HEADED=false
pytest -q

## Run a single test file:
pytest tests/test_checkout.py -q

## Enable slow-motion for debugging:
export SLOW_MO=50
pytest tests/test_login.py -q

## Report:
HTML report is generated at artifacts/report.html (pytest.ini sets this).

## Record video:
Video is generated at artifacts/videos if the test is failed (by default).
Set env KEEP_VIDEOS=true to keep videos for all tests.

## Trace tests
Tracing is generated at artifacts/traces if the test is failed (by default).

To view the trace run:
playwright show-trace artifacts/traces/<your-trace-file>.zip
OR
python -m playwright show-trace artifacts/traces/<your-trace-file>.zip

To view the last trace:
ls -1 artifacts/traces/*.zip | tail -n1 | xargs playwright show-trace