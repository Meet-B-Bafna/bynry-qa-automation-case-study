"""Base API client: owns the HTTP session, injects tenant/auth headers, and
centralizes retry/backoff for transient errors so individual test files never
build raw requests by hand."""

import time

import requests


class BaseAPIClient:
    def __init__(self, base_url: str, token: str, tenant_id: str, max_retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "X-Tenant-ID": tenant_id,
            }
        )

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        last_exc = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.request(method, url, timeout=kwargs.pop("timeout", 10), **kwargs)
                # Only retry on transient server-side errors, never on 4xx --
                # a 4xx is a real bug/expected-denial, not flakiness.
                if resp.status_code >= 500 and attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return resp
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
        raise last_exc

    def get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)
