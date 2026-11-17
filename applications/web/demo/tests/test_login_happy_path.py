import pytest
import allure
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
class TestLoginHappyPath(BaseTest):
    """
    Test Suite for SauceDemo Login Happy Path & Session Lifecycle.
    """

    @test_case(id="CT-LOGIN-001")
    def test_valid_login_standard_user(self):
        """
        Scenario: Standard user authenticates successfully and lands on Inventory Page.
        """
        expected = self.get_expected_for_test()
        role = self.test_data.get("role", "standard")
        username = self.get_username(role)
        password = self.get_password(role)

        with allure.step("1. Navigate to Login Page and verify load state"):
            login_page = self.app.login_page.open()
            assert login_page.is_loaded(), "Login page failed to load anchor elements"

        with allure.step(f"2. Submit credentials for role '{role}' ({username})"):
            login_page.login(username=username, password=password)

        with allure.step("3. Synchronize with Inventory Page load"):
            inventory_page = self.app.inventory_page
            inventory_page.wait_until_loaded()

        with allure.step("4. Verify redirection URL and Inventory page title"):
            actual_url = self.driver.current_url
            expected_url_part = expected.get("expected_url_contains", "inventory.html")
            assert (
                expected_url_part in actual_url
            ), f"Expected URL to contain '{expected_url_part}', but got '{actual_url}'"

            actual_title = inventory_page.get_header_title()
            expected_title = expected.get("inventory_title", "Products")
            assert (
                actual_title == expected_title
            ), f"Expected page header '{expected_title}', but got '{actual_title}'"
            self.pause(seconds=4)

    @test_case(id="CT-LOGIN-002")
    @pytest.mark.usefixtures("as_standard_user")
    def test_logout_returns_to_login_page(self):
        """
        Scenario: Authenticated user logs out via sidebar menu and returns to Login Page.
        Uses precondition fixture 'as_standard_user' to guarantee authenticated session on Inventory.
        """
        expected = self.get_expected_for_test()

        with allure.step("1. Open sidebar and trigger logout flow"):
            self.app.inventory_page.logout()

        with allure.step("2. Verify return to Login Page and check element readiness"):
            login_page = self.app.login_page
            assert (
                login_page.is_loaded()
            ), "Login Page did not reload anchor elements after logout"
            assert (
                login_page.is_login_button_visible()
            ), "Login button is not visible after logout"
            expected_url_part = expected.get("expected_url_contains", "saucedemo.com")
            assert (
                expected_url_part in self.driver.current_url
            ), f"Expected URL to contain '{expected_url_part}' after logout, but got '{self.driver.current_url}'"

    @test_case(id="CT-LOGIN-003")
    def test_dynamic_credentials_from_footer(self):
        """
        Scenario: Authenticate dynamically using credentials parsed directly from the page footer.
        """
        expected = self.get_expected_for_test()
        user_index = self.test_data.get("user_index", 0)

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()
            assert (
                login_page.is_credentials_panel_visible()
            ), "Accepted credentials panel is not visible on Login Page"

        with allure.step(
            f"2. Dynamically authenticate using parsed credential index {user_index}"
        ):
            login_page.login_using_page_listed_credential(user_index=user_index)

        with allure.step("3. Synchronize and verify Inventory Page"):
            inventory_page = self.app.inventory_page
            inventory_page.wait_until_loaded()
            actual_title = inventory_page.get_header_title()
            expected_title = expected.get("inventory_title", "Products")
            assert (
                actual_title == expected_title
            ), f"Expected page header '{expected_title}', but got '{actual_title}'"
