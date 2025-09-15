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