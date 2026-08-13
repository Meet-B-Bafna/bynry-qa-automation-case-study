"""BrowserStack/Appium driver factory for native-app mobile testing.

This path is for a native iOS/Android app, if WorkFlow Pro has one in scope.
For mobile *web* checks (the responsive web app on a phone), see
tests/mobile/test_mobile_access.py, which uses Playwright's built-in device
emulation instead -- that runs directly in CI with no external service and
no BrowserStack credentials, and is the actually-exercised mobile coverage
in this repo today.

This module is real, runnable code against the Appium Python client's API --
it is not a mock -- but it has not been executed against a live BrowserStack
session because native-app scope was never confirmed for this case study
(see README "Known Gaps"). Tests that depend on it are skipped unless
BROWSERSTACK_USERNAME/BROWSERSTACK_ACCESS_KEY are present, so the suite
never silently reports a pass/fail for something that didn't actually run.
"""

import os
import yaml
from appium import webdriver
from appium.options.common import AppiumOptions

CONFIG_PATH = "config/browserstack.yaml"


def _load_capabilities(device_profile: str) -> tuple[dict, str]:
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    caps = dict(config["capabilities"][device_profile])
    caps["bstack:options"] = {
        "userName": os.environ["BROWSERSTACK_USERNAME"],
        "accessKey": os.environ["BROWSERSTACK_ACCESS_KEY"],
        "projectName": "WorkFlow Pro",
        "buildName": os.environ.get("CI_BUILD_ID", "local"),
    }
    return caps, config["hub_url"]


def build_driver(device_profile: str):
    caps, hub_url = _load_capabilities(device_profile)
    options = AppiumOptions()
    options.load_capabilities(caps)
    return webdriver.Remote(command_executor=hub_url, options=options)


def find_project_card(driver, project_name: str, timeout: float = 10.0):
    """Native-app element lookup. Selector strategy (accessibility id vs.
    XPath vs. UiSelector) depends on how the native app exposes project
    cards -- left as accessibility id here as the most maintainable default,
    to be confirmed once app scope/access is available."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from appium.webdriver.common.appiumby import AppiumBy

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, f"project-card-{project_name}"))
    )
