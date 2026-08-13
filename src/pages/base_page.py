"""Shared Page Object behavior: every page object inherits from this so waits,
navigation, and failure diagnostics are consistent across the whole suite."""

from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")

    def wait_visible(self, selector: str, timeout: int = 10000):
        """State-based wait wrapper. Prefer this (or expect() directly in tests)
        over fixed sleeps or wait_for_load_state('networkidle')."""
        locator = self.page.locator(selector)
        expect(locator).to_be_visible(timeout=timeout)
        return locator

    def screenshot_on_failure(self, name: str):
        """Called from a pytest hook (see conftest.py) so every failing test
        leaves a screenshot behind in reports/, without every test needing to
        remember to take one manually."""
        self.page.screenshot(path=f"reports/{name}.png", full_page=True)
