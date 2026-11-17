import allure
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
class TestLoginSecurity(BaseTest):
    """
    Test Suite for SauceDemo Security & Input Masking.
    """

    @test_case(id="CT-LOGIN-014")
    def test_password_input_is_masked(self):
        """
        Scenario: Password input has HTML attribute type='password' to mask characters.
        """
        expected = self.get_expected_for_test()
        expected_type = expected.get("password_field_type", "password")

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Retrieve HTML input type attribute of password field"):
            actual_type = login_page.get_password_field_type()

        with allure.step("3. Verify password field masks input characters"):
            assert actual_type == expected_type, (
                f"Expected password field type='{expected_type}', but got '{actual_type}'"
            )

    @test_case(id="CT-LOGIN-015")
    def test_login_submit_via_enter_key(self):
        """
        Scenario: Submitting login form by pressing ENTER on password field successfully authenticates.
        """
        expected = self.get_expected_for_test()
        role = self.test_data.get("role", "standard")
        username = self.get_username(role)
        password = self.get_password(role)

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step(f"2. Fill credentials for role '{role}' and submit via ENTER key"):
            login_page.set_username(username).set_password(password).submit_with_enter()

        with allure.step("3. Synchronize with Inventory Page and verify landing"):
            inventory_page = self.app.inventory_page
            inventory_page.wait_until_loaded()
            expected_url_part = expected.get("expected_url_contains", "inventory.html")
            assert expected_url_part in self.driver.current_url, (
                f"Expected URL to contain '{expected_url_part}', but got '{self.driver.current_url}'"
            )

