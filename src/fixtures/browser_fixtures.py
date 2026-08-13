"""Browser/page fixtures. Parametrize `browser_type_name` (e.g. via
pytest.mark.parametrize or a CLI flag wired in conftest.py) to run the same
test across chromium/firefox/webkit."""

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        try:
            yield page
        finally:
            # Always tears down, even if an assertion in the test raised --
            # prevents orphaned browser processes from piling up in CI.
            context.close()
            browser.close()


@pytest.fixture
def authenticated_context_factory():
    """Returns a factory for creating a browser context pre-authenticated for
    a given tenant, via a stored storage_state rather than repeating full UI
    login in every integration test."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()

        def _make(storage_state_path: str):
            return browser.new_context(
                viewport={"width": 1280, "height": 800},
                storage_state=storage_state_path,
            )

        yield _make
        browser.close()
