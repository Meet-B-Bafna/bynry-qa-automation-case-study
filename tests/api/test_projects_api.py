"""API-only CRUD + tenant-isolation coverage for the Projects endpoint.
Kept separate from UI tests so API contract regressions are caught fast,
without spinning up a browser."""

import os

import pytest

from src.api.projects_client import ProjectsClient
from src.utils.data_factory import unique_project_payload

API_URL = os.environ.get("WFP_API_URL", "https://api.workflowpro.com/v1")


def _client(tenant_id: str) -> ProjectsClient:
    token = os.environ[f"WFP_TOKEN_{tenant_id.upper()}"]
    return ProjectsClient(API_URL, token=token, tenant_id=tenant_id)


@pytest.fixture
def project_for_company1():
    client = _client("company1")
    payload = unique_project_payload()
    project = client.create_project(**payload)
    yield client, project
    client.delete_project(project["id"])


@pytest.mark.api
def test_create_project_returns_expected_fields(project_for_company1):
    _, project = project_for_company1
    assert "id" in project
    assert project["status"] == "active"


@pytest.mark.api
def test_owning_tenant_can_read_project(project_for_company1):
    client, project = project_for_company1
    resp = client.get_project(project["id"])
    assert resp.status_code == 200
    assert resp.json()["id"] == project["id"]


@pytest.mark.api
def test_other_tenant_cannot_read_project(project_for_company1):
    _, project = project_for_company1
    other_tenant_client = _client("company2")
    resp = other_tenant_client.get_project(project["id"])
    assert resp.status_code in (403, 404), (
        f"Tenant isolation violation: company2 got {resp.status_code} "
        f"reading company1's project"
    )
