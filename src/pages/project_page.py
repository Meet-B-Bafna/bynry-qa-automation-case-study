from playwright.sync_api import expect

from src.pages.base_page import BasePage


class ProjectPage(BasePage):
    PROJECT_LIST = ".project-list"
    PROJECT_CARD = ".project-card"

    def open_project_list(self) -> None:
        self.goto("/projects")
        expect(self.page.locator(self.PROJECT_LIST)).to_be_visible(timeout=10000)

    def get_all_cards(self):
        cards = self.page.locator(self.PROJECT_CARD)
        expect(cards.first).to_be_visible(timeout=10000)
        return cards

    def get_card_by_name(self, name: str):
        return self.page.locator(f"{self.PROJECT_CARD}:has-text('{name}')")

    def expect_card_visible(self, name: str, timeout: int = 10000) -> None:
        expect(self.get_card_by_name(name)).to_be_visible(timeout=timeout)

    def expect_card_absent(self, name: str) -> None:
        """Used for tenant-isolation checks: the card must never appear,
        not just 'not currently visible'."""
        expect(self.get_card_by_name(name)).to_have_count(0)

    def expect_all_cards_belong_to(self, tenant_label: str) -> None:
        cards = self.get_all_cards()
        for i in range(cards.count()):
            expect(cards.nth(i)).to_contain_text(tenant_label)
