from playwright.sync_api import expect

from src.pages.base_page import BasePage


class DashboardPage(BasePage):
    WELCOME_MESSAGE = ".welcome-message"

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/dashboard")
        expect(self.page.locator(self.WELCOME_MESSAGE)).to_be_visible(timeout=10000)
