"""Small wait utilities for cases the Playwright expect() API doesn't cover
directly (e.g., polling an API for eventual consistency after a UI action)."""

import time
from typing import Callable


def poll_until(condition: Callable[[], bool], timeout: float = 10.0, interval: float = 0.5) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False
