import allure
from core.ui.common.base_test import BaseTest
from core.utils.decorators import test_case
from applications.web.demo.utils.decorators import demo


@demo
class TestLoginValidationUx(BaseTest):
    """
    Test Suite for SauceDemo UI Validation UX & Error Recovery.
    """

    @test_case(id="CT-LOGIN-011")
    def test_login_error_visual_feedback(self):
        """
        Scenario: Failed login sets error CSS classes on inputs and displays SVG warning icons.
        """
        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Trigger validation failure by submitting empty form"):
            login_page.click_login()

        with allure.step("3. Verify visual error indicators on form inputs"):
            assert login_page.is_username_highlighted_as_error(), (
                "Username input missing 'error' CSS validation class"
            )
            assert login_page.is_password_highlighted_as_error(), (
                "Password input missing 'error' CSS validation class"
            )
            assert login_page.is_username_error_icon_visible(), (
                "Username error SVG icon is not visible"
            )
            assert login_page.is_password_error_icon_visible(), (
                "Password error SVG icon is not visible"
            )

    @test_case(id="CT-LOGIN-012")
    def test_dismiss_error_banner(self):
        """
        Scenario: Clicking the dismiss 'X' button removes the error message banner.
        """
        username = self.test_data.get("username", "bad_user")
        password = self.test_data.get("password", "bad_password")

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step("2. Trigger error banner by submitting invalid credentials"):
            login_page.set_username(username).set_password(password).click_login()
            assert login_page.is_error_message_visible(), "Error banner failed to display"

        with allure.step("3. Click dismiss 'X' button on error banner"):
            login_page.click_dismiss_error()

        with allure.step("4. Verify error banner has disappeared"):
            assert login_page.is_error_message_not_visible(), (
                "Error banner is still visible after clicking dismiss button"
            )

    @test_case(id="CT-LOGIN-013")
    def test_clear_login_form_inputs(self):
        """
        Scenario: Clearing login form inputs resets their values to empty strings.
        """
        sample_user = self.test_data.get("username", "sample_user")
        sample_pass = self.test_data.get("password", "sample_password")

        with allure.step("1. Navigate to Login Page"):
            login_page = self.app.login_page.open()

        with allure.step(f"2. Fill form inputs with '{sample_user}'"):
            login_page.set_username(sample_user).set_password(sample_pass)
            assert login_page.get_username() == sample_user, "Username was not populated"

        with allure.step("3. Call clear_login_form() atomic sequence"):
            login_page.clear_login_form()

        with allure.step("4. Assert input fields are completely cleared"):
            actual_user = login_page.get_username()
            actual_pass = login_page.get_password()
            assert actual_user == "", f"Expected empty username, but got '{actual_user}'"
            assert actual_pass == "", f"Expected empty password, but got '{actual_pass}'"

