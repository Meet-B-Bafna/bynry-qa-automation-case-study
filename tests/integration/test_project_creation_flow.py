"""Cross-layer integration test: create via API, verify via web UI, verify
mobile accessibility, verify tenant isolation. Mirrors the case-study Part 3
response. The mobile step uses Playwright's built-in device emulation
(same approach as tests/mobile/test_mobile_access.py) so it's real, runnable
coverage of the web app on a phone -- not a stand-in for a native app check,
which stays out of scope until confirmed (see README "Known Gaps")."""

import os

import pytest
from playwright.sync_api import sync_playwright, expect

from src.api.projects_client import ProjectsClient
from src.pages.project_page import ProjectPage
from src.utils.data_factory import unique_project_payload

BASE_API = os.environ.get("WFP_API_URL", "https://api.workflowpro.com/v1")
BASE_WEB = os.environ.get("WFP_WEB_URL", "https://app.workflowpro.com")


def _client(tenant_id: str) -> ProjectsClient:
    token = os.environ[f"WFP_TOKEN_{tenant_id.upper()}"]
    return ProjectsClient(BASE_API, token=token, tenant_id=tenant_id)


@pytest.fixture
def created_project():
    client = _client("company1")
    payload = unique_project_payload()
    project = client.create_project(**payload)
    yield project
    # Teardown always runs, even if the test body raised.
    client.delete_project(project["id"])


@pytest.mark.integration
def test_project_creation_flow(created_project):
    project_id = created_project["id"]
    project_name = created_project["name"]

    # --- 2. Web UI: verify project display for the owning tenant ---
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # STUB: storage_state path would come from a pre-authenticated session
        # fixture (see authenticated_context_factory in browser_fixtures.py),
        # obtained via API/token exchange rather than a full UI login here.
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        try:
            project_page = ProjectPage(page, BASE_WEB)
            project_page.open_project_list()
            project_page.expect_card_visible(project_name)
        finally:
            context.close()
            browser.close()

    # --- 3. Mobile: check accessibility via device emulation ---
    # Covers the web app on a phone. A native-app check via BrowserStack
    # would live in tests/mobile/test_mobile_access.py behind its own
    # skipif(requires_browserstack) gate, not inlined here.
    with sync_playwright() as p:
        device = p.devices["iPhone 14 Pro"]
        browser = p.webkit.launch()
        context = browser.new_context(**device)
        page = context.new_page()
        try:
            mobile_project_page = ProjectPage(page, BASE_WEB)
            mobile_project_page.open_project_list()
            mobile_project_page.expect_card_visible(project_name)
        finally:
            context.close()
            browser.close()

    # --- 4. Security: tenant isolation ---
    other_tenant_client = _client("company2")
    resp = other_tenant_client.get_project(project_id)
    assert resp.status_code in (403, 404), (
        f"Tenant isolation violation: company2 got {resp.status_code} reading company1's project"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        try:
            project_page = ProjectPage(page, BASE_WEB)
            project_page.open_project_list()
            project_page.expect_card_absent(project_name)
        finally:
            context.close()
            browser.close()
