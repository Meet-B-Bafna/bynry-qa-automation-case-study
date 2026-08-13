"""Role-based permission tests, data-driven from config/roles.yaml so adding
a new role or permission doesn't require new test functions -- only a config
change (unless the UI/API contract for that action changes)."""

import os
import yaml
import pytest
from playwright.sync_api import expect

from src.pages.login_page import LoginPage

BASE_URL = os.environ.get("WFP_BASE_URL", "https://app.workflowpro.com")

with open("config/roles.yaml") as f:
    ROLES = yaml.safe_load(f)

# UI control selector for each gated action -- would be filled in against the
# real DOM; kept as a mapping so it's a one-place update if selectors change.
ACTION_SELECTORS = {
    "create_project": "#create-project-btn",
    "delete_project": "#delete-project-btn",
    "invite_team_member": "#invite-member-btn",
    "manage_billing": "#billing-settings-link",
}


@pytest.mark.ui
@pytest.mark.parametrize("role", ["admin", "manager", "employee"])
def test_role_sees_only_permitted_controls(browser_page, role):
    email = f"{role}@company1.com"
    login_page = LoginPage(browser_page, BASE_URL)
    login_page.login(email, os.environ["WFP_TEST_PASSWORD"])

    allowed = set(ROLES[role]["can"])
    for action, selector in ACTION_SELECTORS.items():
        control = browser_page.locator(selector)
        if action in allowed:
            expect(control).to_be_visible(timeout=5000)
        else:
            expect(control).to_have_count(0)
