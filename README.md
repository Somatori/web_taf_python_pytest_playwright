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
- HTML test report generated (2 types of reports are available)
- No credentials stored in source — uses environment variables / `.env` for local convenience
- Running tests in parallel
- Integration with CI/CD (**GitHub Actions**)

## Activate venv:

```bash
source .venv/bin/activate
```

## Run the full suite (headed by default):

```bash
pytest
```

## Run headless:

```bash
export HEADED=false
pytest
```

## Run a single test file:

```bash
pytest tests/test_checkout.py
```

## Enable slow-motion for debugging:

```bash
export SLOW_MO=50
pytest tests/test_login.py
```

## Running tests in parallel

The `pytest-xdist` package is used to run tests in parallel (multiple worker processes).

```bash
pytest -n 2
```

## Reports:

A simple HTML report is generated at `artifacts/report.html`.

Running tests with report generation:

```bash
pytest -q --html=artifacts/report.html --self-contained-html
```

**Note:** this html-report can be generated only if tests are not run in parallel.

## Reporting with Allure

The **Allure** is used for rich HTML reports (attachments, history, etc).

Running tests with report generation:

```bash
# [optionally ] remove previous artifacts:
rm -rf artifacts/allure-results artifacts/allure-report artifacts/videos artifacts/traces

# initial attempt
ALLURE_AUTO_GENERATE=1 RUN_ATTEMPT=1 ALLURE_RESULTS_DIR=artifacts/allure-results/attempt_1 VIDEO_DIR=artifacts/videos pytest --alluredir=artifacts/allure-results/attempt_1

# [optionally] re-run failed tests
RUN_ATTEMPT=2 ALLURE_RESULTS_DIR=artifacts/allure-results/attempt_2 VIDEO_DIR=artifacts/videos pytest --last-failed --alluredir=artifacts/allure-results/attempt_2

# [optionally, if used both attempts] merge Allure results from both attempts into one report
mkdir -p artifacts/allure-results/merged
cp -a artifacts/allure-results/attempt_1/. artifacts/allure-results/merged/ || true
cp -a artifacts/allure-results/attempt_2/. artifacts/allure-results/merged/ || true
allure generate artifacts/allure-results/merged -o artifacts/allure-report --clean
```

Opening the generated report:

```bash
allure open artifacts/allure-report
```

## Record video:

Video is generated at `artifacts/videos` if the test is failed (by default).
Set env `KEEP_VIDEOS=true` to keep videos for all tests.

## Trace tests

Tracing is generated at `artifacts/traces` if the test is failed (by default).

To view the trace run:

```bash
playwright show-trace artifacts/traces/<your-trace-file>.zip
# or
python -m playwright show-trace artifacts/traces/<your-trace-file>.zip
```

## Continuous Integration (GitHub Actions)

This project uses [GitHub Actions](https://docs.github.com/en/actions) to run automated tests on every push and pull request.

- Workflow file: `.github/workflows/ci.yml`
- Runs on **Ubuntu latest** with Python 3.11
- Installs dependencies, Playwright browsers, and executes the full pytest suite
- Uploads Allure report, videos, and traces as build artifacts
- Fails the job if the tests are failed

### CI Behavior

- All tests are executed in CI (no fail-fast by default).
- If a test fails, artifacts (videos, traces) are available in the GitHub Actions run for debugging.
- Secrets (like `SAUCE_USERNAME` and `SAUCE_PASSWORD`) can be added to the repository’s **Settings > Secrets and variables > Actions** for secure usage in tests.
- The Allure report is generates as an artifact.
- The last Allure report is available here: https://somatori.github.io/web_taf_python_pytest_playwright/

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
