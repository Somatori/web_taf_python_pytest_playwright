A small, generic end-to-end Test Automation Framework (TAF) for web UI testing using **Python**, **pytest**, and **Playwright (sync API)**.  
The project implements the **Page Object Model (POM)** and is designed to be easy to use, extend, run locally and in CI.

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

HTML report is generated at `artifacts/report.html` (`pytest.ini` sets this).

## Record video:

Video is generated at `artifacts/videos` if the test is failed (by default).
Set env `KEEP_VIDEOS=true` to keep videos for all tests.

## Trace tests

Tracing is generated at `artifacts/traces` if the test is failed (by default).

To view the trace run:
playwright show-trace artifacts/traces/<your-trace-file>.zip
OR
python -m playwright show-trace artifacts/traces/<your-trace-file>.zip

To view the last trace:
ls -1 artifacts/traces/\*.zip | tail -n1 | xargs playwright show-trace

## Continuous Integration (GitHub Actions)

This project uses [GitHub Actions](https://docs.github.com/en/actions) to run automated tests on every push and pull request.

- Workflow file: `.github/workflows/ci.yml`
- Runs on **Ubuntu latest** with Python 3.11
- Installs dependencies, Playwright browsers, and executes the full pytest suite
- Uploads pytest HTML reports, videos, and Playwright traces as build artifacts

### CI Behavior

- All tests are executed in CI (no fail-fast by default).
- If a test fails, artifacts (videos, traces, HTML report) are available in the GitHub Actions run for debugging.
- Secrets (like `SAUCE_USERNAME` and `SAUCE_PASSWORD`) can be added to the repository’s **Settings > Secrets and variables > Actions** for secure usage in tests.

### Local vs CI

- Locally: run `pytest` (optionally `pytest --headed` to see the browser).
- In CI: tests run in headless mode by default, artifacts are stored automatically.

## Test markers

Pytest markers are used to group and run subsets of tests quickly.

Registered markers:

- `smoke` — fast, high-level smoke tests that exercise critical paths.
- `sanity` — slightly broader sanity checks that validate core functionality.

Marking tests:

```py
import pytest

@pytest.mark.smoke
def test_example(page, credentials):
    ...
```

Running tests by a marker:

```bash
pytest -q -m smoke
```
