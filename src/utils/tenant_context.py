"""Single source of truth for which tenant/environment a test targets.
Loaded once per test session from config/environments/<env>.yaml, resolved
via the --env CLI flag registered in conftest.py."""

from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_DIR = Path("config/environments")


@dataclass
class TenantContext:
    tenant_id: str
    display_name: str
    base_url: str
    api_url: str
    accounts: dict

    @classmethod
    def load(cls, env_name: str) -> "TenantContext":
        path = CONFIG_DIR / f"{env_name}.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"No environment config at {path}. "
                f"Available: {[p.stem for p in CONFIG_DIR.glob('*.yaml')]}"
            )
        data = yaml.safe_load(path.read_text())
        return cls(
            tenant_id=data["tenant_id"],
            display_name=data["display_name"],
            base_url=data["base_url"],
            api_url=data["api_url"],
            accounts=data["accounts"],
        )
