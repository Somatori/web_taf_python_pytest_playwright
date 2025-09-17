# e2e_tests - Playwright + Pytest TAF

#### Run tests locally

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


