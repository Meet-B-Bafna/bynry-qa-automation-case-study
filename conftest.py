"""Root conftest -- pulls in the shared fixture modules and adds a
failure-screenshot hook so every failing UI test leaves a screenshot in
reports/ without each test needing to remember to take one."""

import pytest

pytest_plugins = [
    "src.fixtures.browser_fixtures",
    "src.fixtures.auth_fixtures",
]


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="company1",
        help="Environment/tenant config to use, matches config/environments/<name>.yaml",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("browser_page")
        if page is not None:
            try:
                page.screenshot(path=f"reports/{item.name}-failure.png", full_page=True)
            except Exception:
                pass  # best-effort diagnostics, never fail the test *harder* on cleanup
