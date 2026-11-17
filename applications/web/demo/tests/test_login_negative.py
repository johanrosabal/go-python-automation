import allure
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
class TestLoginNegative(BaseTest):
    """
    Test Suite for SauceDemo Negative Authentication & Missing Fields.
    """

    @test_case(id="CT-LOGIN-007")
    def test_login_empty_username(self):
        """
        Scenario: Submitting login with empty username displays required field error.
        """
        expected = self.get_expected_for_test()
        username = self.test_data.get("username", "")
        password = self.test_data.get("password", self.password)
        expected_msg = self.config.get(expected.get("error_key"))

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Leave username blank, enter password and click Login"):
            login_page.set_username(username).set_password(password).click_login()

        with allure.step("3. Verify username required validation error message"):
            assert login_page.is_error_message_visible(), "Error message banner is not visible"
            actual_msg = login_page.get_error_message()
            assert actual_msg == expected_msg, (
                f"Expected '{expected_msg}', but got '{actual_msg}'"
            )

    @test_case(id="CT-LOGIN-008")
    def test_login_empty_password(self):
        """
        Scenario: Submitting login with valid username and empty password displays required error.
        """
        expected = self.get_expected_for_test()
        username = self.test_data.get("username", self.username)
        password = self.test_data.get("password", "")
        expected_msg = self.config.get(expected.get("error_key"))

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Enter username, leave password blank and click Login"):
            login_page.set_username(username).set_password(password).click_login()

        with allure.step("3. Verify password required validation error message"):
            assert login_page.is_error_message_visible(), "Error message banner is not visible"
            actual_msg = login_page.get_error_message()
            assert actual_msg == expected_msg, (
                f"Expected '{expected_msg}', but got '{actual_msg}'"
            )

    @test_case(id="CT-LOGIN-009")
    def test_login_both_fields_empty(self):
        """
        Scenario: Submitting with both fields empty displays username required error first.
        """
        expected = self.get_expected_for_test()
        expected_msg = self.config.get(expected.get("error_key"))

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Click Login button directly with both fields empty"):
            login_page.click_login()

        with allure.step("3. Verify error message prioritizes username required"):
            assert login_page.is_error_message_visible(), "Error message banner is not visible"
            actual_msg = login_page.get_error_message()
            assert actual_msg == expected_msg, (
                f"Expected '{expected_msg}', but got '{actual_msg}'"
            )

    @test_case(id="CT-LOGIN-010")
    def test_login_unregistered_credentials(self):
        """
        Scenario: Submitting unregistered credentials displays credentials mismatch error.
        """
        expected = self.get_expected_for_test()
        username = self.test_data.get("username", "invalid_user")
        password = self.test_data.get("password", "wrong_password")
        expected_msg = self.config.get(expected.get("error_key"))

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step(f"2. Submit unregistered credentials ('{username}')"):
            login_page.set_username(username).set_password(password).click_login()

        with allure.step("3. Verify mismatch error alert banner"):
            assert login_page.is_error_message_visible(), "Error message banner is not visible"
            actual_msg = login_page.get_error_message()
            assert actual_msg == expected_msg, (
                f"Expected '{expected_msg}', but got '{actual_msg}'"
            )

