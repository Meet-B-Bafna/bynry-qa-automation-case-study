"""Login page object, including optional 2FA handling.

ASSUMPTION: 2FA behavior was not specified by the case study. This assumes
automation accounts are provisioned with a fixed/mock OTP for test purposes.
In a real engagement I would first ask whether automation accounts can have
2FA disabled entirely, or whether a service-account/API-token auth path
exists that bypasses UI login for setup (see README "Known Gaps").
"""

import os

from playwright.sync_api import expect

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    OTP_INPUT = "#otp-code"
    OTP_SUBMIT = "#otp-submit-btn"
    WELCOME_MESSAGE = ".welcome-message"

    def login(self, email: str, password: str) -> None:
        self.goto("/login")

        email_input = self.page.locator(self.EMAIL_INPUT)
        expect(email_input).to_be_visible()
        email_input.fill(email)
        self.page.fill(self.PASSWORD_INPUT, password)
        self.page.click(self.LOGIN_BUTTON)

        self._handle_optional_2fa()

        self.page.wait_for_url(f"{self.base_url}/dashboard", timeout=15000)
        expect(self.page.locator(self.WELCOME_MESSAGE)).to_be_visible(timeout=10000)

    def _handle_optional_2fa(self) -> None:
        otp_input = self.page.locator(self.OTP_INPUT)
        # Short existence check for an *optional* step -- not a substitute for
        # expect() on required elements, which is used everywhere else.
        if otp_input.is_visible(timeout=3000):
            otp_input.fill(os.environ["WFP_TEST_OTP"])
            self.page.click(self.OTP_SUBMIT)

    def expect_login_error(self) -> None:
        expect(self.page.locator(".login-error")).to_be_visible(timeout=5000)
