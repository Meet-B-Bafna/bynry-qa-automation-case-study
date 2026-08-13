"""Generates test data payloads with unique identifiers so parallel workers
(pytest-xdist) never collide on the same name/slug."""

import uuid


def unique_project_payload(prefix: str = "Test Project", description: str = "QA automation test"):
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"{prefix} {suffix}",
        "description": description,
        "team_members": [],
    }
