import os
import pytest
from core.ui.playwright.driver_factory import PlaywrightDriverFactory
from core.ui.playwright.playwright_element import PlaywrightElement
from core.ui.playwright.playwright_base_page import PlaywrightBasePage
from selenium.webdriver.common.by import By


class PlaywrightSauceLoginPage(PlaywrightBasePage):
    """Demo Page Object using Playwright with the exact 3-Layer standard."""
    PAGE_PATH = "/"

    @property
    def input_username(self) -> PlaywrightElement:
        return self.element((By.ID, "user-name"), label="Username Input")

    @property
    def input_password(self) -> PlaywrightElement:
        return self.element((By.ID, "password"), label="Password Input")

    @property
    def btn_login(self) -> PlaywrightElement:
        return self.element((By.ID, "login-button"), label="Login Button")

    @property
    def txt_inventory_title(self) -> PlaywrightElement:
        return self.element((By.CLASS_NAME, "title"), label="Products Page Title")

    def login(self, username: str, password: str):
        self.input_username.type(username)
        self.input_password.type(password)
        self.btn_login.click()
        return self


def test_playwright_hybrid_engine_execution():
    # 1. Initialize Playwright engine in headless mode
    page = PlaywrightDriverFactory.create_page(browser_name="chromium", headless=True)
    try:
        # 2. Instantiate Page Object
        login_page = PlaywrightSauceLoginPage(page)
        
        # 3. Navigate
        login_page.open("https://www.saucedemo.com")
        assert "Swag Labs" in login_page.get_title()

        # 4. Perform atomic 3-layer actions
        login_page.login("standard_user", "secret_sauce")

        # 5. Verify results
        assert login_page.txt_inventory_title.is_visible() is True
        assert login_page.txt_inventory_title.get_text() == "Products"
        print("✓ Playwright 3-Layer test successfully executed and verified!")
    finally:
        PlaywrightDriverFactory.close_all()


if __name__ == "__main__":
    test_playwright_hybrid_engine_execution()
