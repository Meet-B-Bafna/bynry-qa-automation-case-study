"""Fixtures that resolve credentials/tokens per role x tenant, backed by
config/roles.yaml and config/environments/*.yaml."""

import os
import pytest

from src.utils.tenant_context import TenantContext


@pytest.fixture
def tenant_context(request):
    env_name = request.config.getoption("--env")
    return TenantContext.load(env_name)


@pytest.fixture
def api_token(tenant_context):
    env_var = f"WFP_TOKEN_{tenant_context.tenant_id.upper()}"
    return os.environ[env_var]
