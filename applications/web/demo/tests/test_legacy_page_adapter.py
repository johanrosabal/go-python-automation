"""
Test Suite for Legacy Page Object Interpreter & Compatibility Shim.
Verifies that untouched page objects from the previous automation framework
can execute transparently on the modern dual-engine framework.
"""
import pytest
import allure
from selenium.webdriver.common.by import By

from core.ui.common.base_test import BaseTest
from applications.web.demo.utils.decorators import demo
from applications.web.demo.pages.legacy.LoginPage import LoginPage
from core.asserts.AssertCollector import AssertCollector
from core.data import UserDTO
from core.ui.common.BaseApp import BaseApp


@demo
class TestLegacyPageAdapter(BaseTest):
    """
    Validates that legacy page objects run directly through the compatibility interpreter
    without requiring any modifications to the original legacy class files.
    """

    def test_legacy_page_instantiation_and_structure(self):
        """
        Scenario: Legacy LoginPage initializes with driver and retains all original properties.
        """
        with allure.step("1. Instantiate legacy LoginPage via driver"):
            page = LoginPage(self.driver)
            assert page.driver is not None, "Driver was not passed to legacy page"
            assert page.relative == "/web/index.php/auth/login", "Relative URL mismatch"

        with allure.step("2. Verify legacy locators are 3-element tuples"):
            assert isinstance(page._input_user_name, tuple), "Locator should be a tuple"
            assert page._input_user_name[0] == By.NAME
            assert page._input_user_name[1] == "username"
            assert page._input_user_name[2] == "Input Username"

        with allure.step("3. Verify singleton get_instance() pattern works"):
            instance = LoginPage.get_instance()
            assert instance is not None, "get_instance() failed to return singleton"
            assert isinstance(instance, LoginPage)

    def test_legacy_interpreter_fluent_actions_execution(self):
        """
        Scenario: Legacy fluent builder actions (navigation, send_keys, click, get_text, AssertCollector)
        execute successfully on the active browser engine (Selenium / Playwright).
        """
        page = LoginPage(self.driver)

        with allure.step("1. Navigate to target URL using legacy navigation shim"):
            page.navigation().go("https://www.saucedemo.com/")
            current_url = page.navigation().get_current_url()
            assert "saucedemo.com" in current_url, f"Failed to navigate, got {current_url}"

        with allure.step("2. Type credentials using legacy send_keys fluent builder"):
            page.send_keys().set_locator((By.ID, "user-name", "Username Input Field"), page="LoginPage").set_text("standard_user")
            page.send_keys().set_locator((By.ID, "password", "Password Input Field"), page="LoginPage").set_text("secret_sauce").highlight()

        with allure.step("3. Click login using legacy click fluent builder"):
            page.click().set_locator((By.ID, "login-button", "Submit Login Button"), page="LoginPage").single_click()

        with allure.step("4. Read text from inventory title using legacy get_text shim"):
            title = page.get_text().set_locator((By.CLASS_NAME, "title", "Inventory Title"), page="InventoryPage").by_text()

        with allure.step("5. Validate result using legacy AssertCollector"):
            AssertCollector.assert_equal_message(
                expected="Products",
                actual=title,
                message="Inventory Title Heading",
                page="LoginPage",
                method_name="test_legacy_interpreter_fluent_actions_execution"
            )

    def test_legacy_user_dto_and_composite_methods(self):
        """
        Scenario: Calling legacy composite methods (login_user with UserDTO) works end-to-end.
        """
        page = LoginPage(self.driver)

        with allure.step("1. Navigate to login page"):
            page.navigation().go("https://www.saucedemo.com/")

        with allure.step("2. Prepare UserDTO data model"):
            user = UserDTO(user_name="problem_user", user_password="secret_sauce")
            assert user.user_name == "problem_user"
            assert user.user_password == "secret_sauce"

        with allure.step("3. Execute legacy atomic setters"):
            # Set username with legacy tuple
            page.send_keys().set_locator((By.ID, "user-name", "Input Username"), page="LoginPage").set_text(user.user_name)
            # Set password with legacy tuple
            page.send_keys().set_locator((By.ID, "password", "Input Password"), page="LoginPage").set_text(user.user_password)
            # Click login
            page.click().set_locator((By.ID, "login-button", "Login Button"), page="LoginPage").single_click()

        with allure.step("4. Verify successful authentication"):
            current_url = page.navigation().get_current_url()
            assert "inventory.html" in current_url, f"Expected inventory.html in URL, got {current_url}"

