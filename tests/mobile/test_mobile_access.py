"""Mobile coverage for the web app, using Playwright's built-in device
emulation (viewport, user agent, touch) -- this is real, runnable code that
needs no external service and no BrowserStack account, and directly covers
the case-study requirement 'check project is accessible on mobile' for the
responsive web app.

A second, BrowserStack-backed suite lower in this file targets a native app
if that's ever in scope; those tests are skipped (not run, not faked) unless
BrowserStack credentials are configured, so the suite is always honest about
what actually executed.
"""

import os

import pytest
from playwright.sync_api import sync_playwright, expect

from src.pages.login_page import LoginPage
from src.pages.project_page import ProjectPage

BASE_URL = os.environ.get("WFP_BASE_URL", "https://app.workflowpro.com")

# (device name, engine) -- webkit for iOS devices matches real Safari
# rendering more closely than chromium's iOS emulation.
MOBILE_DEVICES = [
    ("iPhone 14 Pro", "webkit"),
    ("Pixel 7", "chromium"),
]


@pytest.mark.mobile
@pytest.mark.parametrize("device_name,engine", MOBILE_DEVICES, ids=[d[0] for d in MOBILE_DEVICES])
def test_project_list_renders_on_mobile(device_name, engine):
    with sync_playwright() as p:
        device = p.devices[device_name]
        browser = getattr(p, engine).launch()
        context = browser.new_context(**device)
        page = context.new_page()
        try:
            login_page = LoginPage(page, BASE_URL)
            login_page.login("admin@company1.com", os.environ["WFP_TEST_PASSWORD"])

            project_page = ProjectPage(page, BASE_URL)
            project_page.open_project_list()
            expect(page.locator(project_page.PROJECT_LIST)).to_be_visible(timeout=10000)
        finally:
            context.close()
            browser.close()


@pytest.mark.mobile
@pytest.mark.parametrize("device_name,engine", MOBILE_DEVICES, ids=[d[0] for d in MOBILE_DEVICES])
def test_login_form_usable_on_mobile_viewport(device_name, engine):
    """Guards against a common mobile-responsive regression: form controls
    present but not actually interactable (off-screen, zero-size, covered by
    a sticky header) at phone viewport widths."""
    with sync_playwright() as p:
        device = p.devices[device_name]
        browser = getattr(p, engine).launch()
        context = browser.new_context(**device)
        page = context.new_page()
        try:
            login_page = LoginPage(page, BASE_URL)
            login_page.goto("/login")
            email_input = page.locator(login_page.EMAIL_INPUT)
            expect(email_input).to_be_visible(timeout=10000)
            expect(email_input).to_be_in_viewport()
        finally:
            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# Native app (BrowserStack App Automate), if in scope -- see module docstring.
# ---------------------------------------------------------------------------

requires_browserstack = pytest.mark.skipif(
    not (os.environ.get("BROWSERSTACK_USERNAME") and os.environ.get("BROWSERSTACK_ACCESS_KEY")),
    reason=(
        "Requires BROWSERSTACK_USERNAME/BROWSERSTACK_ACCESS_KEY, and native-app "
        "scope has not been confirmed for this project (see README 'Known Gaps'). "
        "Skipped rather than run against a guess."
    ),
)


@pytest.mark.mobile
@requires_browserstack
@pytest.mark.parametrize("device_profile", ["android_pixel_7", "ios_iphone_14"])
def test_project_visible_in_native_app(device_profile):
    from src.mobile.browserstack_driver import build_driver, find_project_card

    driver = build_driver(device_profile)
    try:
        card = find_project_card(driver, project_name="Test Project", timeout=10)
        assert card is not None
    finally:
        driver.quit()
