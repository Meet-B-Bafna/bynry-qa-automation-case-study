"""Corrected version of the originally-flaky login tests (see case-study
Part 1 for the full root-cause analysis). Key fixes: state-based waits via
expect(), explicit navigation wait instead of racing the click, optional 2FA
handling, and guaranteed browser cleanup via the browser_page fixture."""

import os

import pytest
from playwright.sync_api import expect

from src.pages.login_page import LoginPage
from src.pages.project_page import ProjectPage

BASE_URL = os.environ.get("WFP_BASE_URL", "https://app.workflowpro.com")


@pytest.mark.ui
@pytest.mark.smoke
def test_user_login(browser_page):
    login_page = LoginPage(browser_page, BASE_URL)
    login_page.login("admin@company1.com", os.environ["WFP_TEST_PASSWORD"])
    expect(browser_page).to_have_url(f"{BASE_URL}/dashboard")


@pytest.mark.ui
def test_invalid_password_shows_error(browser_page):
    login_page = LoginPage(browser_page, BASE_URL)
    login_page.goto("/login")
    browser_page.fill(login_page.EMAIL_INPUT, "admin@company1.com")
    browser_page.fill(login_page.PASSWORD_INPUT, "wrong-password")
    browser_page.click(login_page.LOGIN_BUTTON)
    login_page.expect_login_error()
    expect(browser_page).not_to_have_url(f"{BASE_URL}/dashboard")


@pytest.mark.ui
def test_multi_tenant_access(browser_page):
    login_page = LoginPage(browser_page, BASE_URL)
    login_page.login("user@company2.com", os.environ["WFP_TEST_PASSWORD"])

    project_page = ProjectPage(browser_page, BASE_URL)
    project_page.open_project_list()
    project_page.expect_all_cards_belong_to("Company2")
