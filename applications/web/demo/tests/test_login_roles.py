import allure
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
class TestLoginRoles(BaseTest):
    """
    Test Suite for SauceDemo Credential Roles & Account Statuses.
    """

    @test_case(id="CT-LOGIN-004")
    def test_locked_out_user_error(self):
        """
        Scenario: Locked out user receives rejection error banner and cannot access application.
        """
        expected = self.get_expected_for_test()
        role = self.test_data.get("role", "locked")
        username = self.get_username(role)
        password = self.get_password(role)
        expected_message = self.config.get(expected.get("error_key"))

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()
            assert login_page.is_loaded(), "Login page anchor elements not loaded"

        with allure.step(f"2. Attempt login with locked role '{role}' ({username})"):
            login_page.login(username=username, password=password)

        with allure.step("3. Verify error alert banner and message text"):
            assert login_page.is_error_message_visible(), (
                "Error banner did not appear for locked_out_user"
            )
            actual_message = login_page.get_error_message()
            assert actual_message == expected_message, (
                f"Expected error '{expected_message}', but got '{actual_message}'"
            )

    @test_case(id="CT-LOGIN-005")
    def test_problem_user_login(self):
        """
        Scenario: User with known asset issues authenticates and lands on Inventory.
        """
        expected = self.get_expected_for_test()
        role = self.test_data.get("role", "problem")
        username = self.get_username(role)
        password = self.get_password(role)

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step(f"2. Submit credentials for role '{role}' ({username})"):
            login_page.login(username=username, password=password)

        with allure.step("3. Synchronize with Inventory Page and verify access"):
            inventory_page = self.app.inventory_page
            inventory_page.wait_until_loaded()
            expected_url_part = expected.get("expected_url_contains", "inventory.html")
            assert expected_url_part in self.driver.current_url, (
                f"Expected URL to contain '{expected_url_part}', but got '{self.driver.current_url}'"
            )

    @test_case(id="CT-LOGIN-006")
    def test_performance_glitch_user_login(self):
        """
        Scenario: User with simulated network latency completes authentication within SLA.
        """
        expected = self.get_expected_for_test()
        role = self.test_data.get("role", "performance")
        username = self.get_username(role)
        password = self.get_password(role)
        max_sla_seconds = expected.get("max_wait_seconds", 15)

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step(f"2. Submit credentials for latency role '{role}' ({username})"):
            login_page.login(username=username, password=password)

        with allure.step(f"3. Wait for Inventory Page to load within SLA ({max_sla_seconds}s)"):
            inventory_page = self.app.inventory_page
            inventory_page.wait_until_loaded(timeout=max_sla_seconds)
            expected_url_part = expected.get("expected_url_contains", "inventory.html")
            assert expected_url_part in self.driver.current_url, (
                f"Expected URL to contain '{expected_url_part}', but got '{self.driver.current_url}'"
            )

