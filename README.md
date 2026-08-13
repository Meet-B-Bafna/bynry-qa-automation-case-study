# WorkFlow Pro — QA Automation Framework

Test automation framework for **WorkFlow Pro**, a multi-tenant B2B project
management SaaS platform. Covers web UI (Chrome/Firefox/Safari via Playwright),
mobile (Playwright device emulation for the web app, plus an optional
BrowserStack/Appium path for a native app), and API (pytest + requests) testing,
with explicit multi-tenant isolation and role-based permission coverage.

> Built as part of the Bynry QA Automation Engineering Intern take-home case study.
> See `TEST_PLAN.md` for scenario coverage and the case-study response doc for the
> full written reasoning (flaky-test root-cause analysis, framework design rationale,
> and stated assumptions).

## Stack

- **UI**: Playwright (Python, sync API)
- **API**: `requests` + pytest
- **Mobile (web)**: Playwright's built-in device emulation — real, runnable, no external service required
- **Mobile (native app, optional)**: Appium via BrowserStack App Automate — skipped unless credentials are configured and app scope is confirmed
- **Test runner**: pytest, parallelized with `pytest-xdist` (`-n auto` by default), flaky-retry via `pytest-rerunfailures` (`--reruns 1`)
- **Reporting**: Allure (`allure-pytest`)
- **CI**: GitHub Actions (`.github/workflows/pipeline.yml`)

## Project Structure

```
.
├── config/
│   ├── environments/         # per-tenant base URLs, tenant IDs
│   │   ├── company1.yaml
│   │   ├── company2.yaml
│   │   └── staging.yaml
│   ├── roles.yaml             # permission matrix: Admin / Manager / Employee
│   └── browserstack.yaml      # device/browser capability matrix
├── src/
│   ├── pages/                 # Page Object Model
│   ├── api/                   # API client layer
│   ├── mobile/                # BrowserStack/Appium driver (native-app path, optional)
│   ├── utils/                 # test data factory, tenant context, wait helpers
│   └── fixtures/              # shared pytest fixtures
├── tests/
│   ├── ui/                    # web UI tests
│   ├── api/                   # API-only tests
│   ├── integration/           # cross-layer API+UI+mobile+security tests
│   └── mobile/                # mobile-web (device emulation) + gated native-app tests
├── .github/workflows/pipeline.yml   # GitHub Actions workflow
├── reports/                   # Allure results output (gitignored contents)
├── pytest.ini
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps chromium firefox webkit
```

## Configuration

Copy `.env.example` to `.env` (not committed) and set:

```
WFP_TEST_PASSWORD=...
WFP_TEST_OTP=...
WFP_TOKEN_COMPANY1=...
WFP_TOKEN_COMPANY2=...
BROWSERSTACK_USERNAME=...
BROWSERSTACK_ACCESS_KEY=...
```

Environment/tenant selection (base URLs, tenant IDs) lives in
`config/environments/*.yaml` — select which one to use with `--env`:

```bash
pytest --env=company1
```

## Running Tests

```bash
# Full suite, default environment
pytest

# Just the UI suite, headed, single worker (debugging)
pytest tests/ui -k "not mobile" --headed -n0

# API only
pytest tests/api

# Cross-layer integration + tenant isolation
pytest tests/integration

# Mobile web checks (device emulation, no external service needed)
pytest tests/mobile

# Native-app mobile checks only run if BrowserStack creds are set;
# otherwise they report as skipped, not passed/failed.
BROWSERSTACK_USERNAME=... BROWSERSTACK_ACCESS_KEY=... pytest tests/mobile -k native_app

# Parallel workers are on by default (-n auto in pytest.ini); override explicitly if needed
pytest -n4

# With Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## Design Notes

- **Page Object Model** (`src/pages`): every page exposes behavior (`login()`,
  `get_project_card()`), never raw selectors, so UI changes are a one-file fix.
- **API client layer** (`src/api`): centralizes auth header injection
  (`Authorization`, `X-Tenant-ID`) and retry/backoff for transient errors, so
  tests never build requests by hand.
- **TenantContext** (`src/utils/tenant_context.py`): single source of truth for
  which tenant/environment a test run targets — nothing is hardcoded per test file.
- **Waits**: state-based (`expect(...).to_be_visible()`, `wait_for_url()`)
  everywhere, never fixed `sleep()` or `wait_for_load_state("networkidle")` as a
  primary sync mechanism (see case-study Part 1 for why).
- **Test data**: created and torn down via the API layer in fixtures, with a
  unique suffix per test run so parallel workers never collide.

## Known Gaps / Open Questions

See "Missing Requirements" in the case-study response doc — notably: whether a
dedicated sandbox tenant exists, 2FA handling for automation accounts (currently
assumes a fixed test OTP — see `src/pages/login_page.py`), whether a native
mobile app is even in scope (mobile-web coverage via Playwright emulation is
in place either way; the native-app path in `src/mobile/browserstack_driver.py`
is real code but unexercised and its tests are skipped until credentials and
scope are confirmed), and CI parallelism limits on the BrowserStack plan.
