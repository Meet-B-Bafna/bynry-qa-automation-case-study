"""Placeholder for a token-exchange auth client.

ASSUMPTION: the case study did not describe a token/auth endpoint, so this
assumes tenant API tokens are provisioned out-of-band (e.g., CI secrets) for
test accounts, rather than obtained through a login call. If WorkFlow Pro
exposes a POST /auth/token endpoint, this is where it would be implemented.
"""

import os


def get_tenant_token(tenant_id: str) -> str:
    env_var = f"WFP_TOKEN_{tenant_id.upper()}"
    try:
        return os.environ[env_var]
    except KeyError as exc:
        raise RuntimeError(
            f"No API token configured for tenant '{tenant_id}'. "
            f"Set the {env_var} environment variable."
        ) from exc
