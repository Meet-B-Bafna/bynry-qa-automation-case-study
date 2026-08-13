"""Registers the --env CLI option and re-exports shared fixtures so
tests/**/conftest.py (or a root conftest.py) can pull them in with a single
`from src.fixtures.conftest import *`-style import, or pytest_plugins."""

import pytest

pytest_plugins = [
    "src.fixtures.browser_fixtures",
    "src.fixtures.auth_fixtures",
]


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="company1",
        help="Environment/tenant config to use, matches config/environments/<name>.yaml",
    )
