from typing import Self, Dict, Any, List
from core.ui.common.base_page import BasePage
from core.ui.common.find_by import find_by
import allure


class LoginPage(BasePage):
    """
    Comprehensive 3-Layer Page Object Model for the SauceDemo Login Page.

    Built by inspecting the live DOM via the Selenium MCP server, covering:
      - Branding & layout containers (`lbl_brand_logo`, `cnt_login_wrapper`, `frm_login`)
      - Authentication inputs with placeholders, values, and dynamic validation icons (`input_username`, `input_password`, `ico_field_error`)
      - Interactive error banner & dismiss button (`cnt_error_banner`, `msg_error`, `btn_dismiss_error`)
      - Reference credentials & password panels (`cnt_credentials_panel`, `hdr_accepted_usernames`, `txt_accepted_usernames`, `hdr_password_info`, `txt_password_info`)
    """

    PAGE_PATH = "/"

    # =========================================================================
    # LAYER 1: Declarative Locators (Prefix + Label + Anchor)
    # =========================================================================

    # --- Branding & Structural Containers ---
    lbl_brand_logo = find_by(
        class_name="login_logo", label="Swag Labs Brand Logo", anchor=True
    )
    cnt_login_wrapper = find_by(
        css="[data-test='login-container']", label="Main Login Wrapper Container"
    )
    frm_login = find_by(css="form[aria-label='Login']", label="Login Form Container")

    # --- Form Inputs & Submit Action ---
    input_username = find_by(id="user-name", label="Username Input Field", anchor=True)
    input_password = find_by(id="password", label="Password Input Field")
    btn_login = find_by(id="login-button", label="Login Submit Button", anchor=True)

    # --- Dynamic & Static Field Validation Icons (Appear on validation failure) ---
    ico_username_error = find_by(
        css="#user-name ~ svg.error_icon", label="Username Field Error X-Icon"
    )
    ico_password_error = find_by(
        css="#password ~ svg.error_icon", label="Password Field Error X-Icon"
    )
    ico_field_error = find_by(
        css="#{field_id} ~ svg.error_icon",
        label="Field '{field_id}' Error X-Icon",
    )

    # --- Error Alert Banner & Dismiss Action ---
    cnt_error_banner = find_by(
        css=".error-message-container.error", label="Error Banner Container"
    )
    msg_error = find_by(css="[data-test='error']", label="Login Error Alert Message")
    btn_dismiss_error = find_by(
        css="[data-test='error-button']", label="Dismiss Error Banner Button"
    )

    # --- Reference Credentials & Password Info Panels (Footer) ---
    cnt_credentials_panel = find_by(
        css="[data-test='login-credentials-container']",
        label="Credentials Footer Container",
    )
    hdr_accepted_usernames = find_by(
        css="[data-test='login-credentials'] > h4", label="Accepted Usernames Header"
    )
    txt_accepted_usernames = find_by(
        css="[data-test='login-credentials']", label="Accepted Usernames Block"
    )
    hdr_password_info = find_by(
        css="[data-test='login-password'] > h4", label="Password Info Header"
    )
    txt_password_info = find_by(
        css="[data-test='login-password']", label="Password Info Block"
    )

    # =========================================================================
    # LAYER 2: Granular Atomic Methods (Setters, Getters, Clicks & Checks)
    # =========================================================================

    # --- Branding & Containers ---
    def get_brand_logo_text(self) -> str:
        """Returns the main header brand logo text ('Swag Labs')."""
        return self.lbl_brand_logo.get_trimmed_text()

    def is_brand_logo_visible(self) -> bool:
        """Checks if the Swag Labs header logo is visible."""
        return self.lbl_brand_logo.is_visible()

    def is_login_form_visible(self) -> bool:
        """Checks if the login form container is visible."""
        return self.frm_login.is_visible()

    # --- Username Input Atomic Methods ---
    @allure.step("Setting username: {username}")
    def set_username(self, username: str) -> Self:
        """Clears and types the username into the username input field."""
        self.input_username.type(username, clear=True)
        return self

    def clear_username(self) -> Self:
        """Clears the username input field."""
        self.input_username.clear()
        return self

    def get_username(self) -> str:
        """Retrieves the current text value inside the username input field."""
        return self.input_username.get_value()

    def get_username_placeholder(self) -> str:
        """Retrieves the placeholder attribute of the username input ('Username')."""
        return self.input_username.get_attribute("placeholder")

    def is_username_highlighted_as_error(self) -> bool:
        """Checks if the username input has the 'error' CSS validation class applied."""
        classes = self.input_username.get_attribute("class") or ""
        return "error" in classes.split()

    def is_username_error_icon_visible(self) -> bool:
        """Checks if the red circle-xmark SVG icon next to username is visible."""
        return self.ico_username_error.is_visible()

    # --- Password Input Atomic Methods ---
    @allure.step("Setting password")
    def set_password(self, password: str) -> Self:
        """Clears and types the password (masked in logs) into the password input field."""
        self.input_password.type_encrypted(password, clear=True)
        return self

    def clear_password(self) -> Self:
        """Clears the password input field."""
        self.input_password.clear()
        return self

    def get_password(self) -> str:
        """Retrieves the current value inside the password input field."""
        return self.input_password.get_value()

    def get_password_placeholder(self) -> str:
        """Retrieves the placeholder attribute of the password input ('Password')."""
        return self.input_password.get_attribute("placeholder")

    def get_password_field_type(self) -> str:
        """Retrieves the HTML input type of the password field (verifies masking via 'password')."""
        return self.input_password.get_attribute("type")

    def is_password_highlighted_as_error(self) -> bool:
        """Checks if the password input has the 'error' CSS validation class applied."""
        classes = self.input_password.get_attribute("class") or ""
        return "error" in classes.split()

    def is_password_error_icon_visible(self) -> bool:
        """Checks if the red circle-xmark SVG icon next to password is visible."""
        return self.ico_password_error.is_visible()

    # --- Dynamic Field Validation Icon Check ---
    def is_field_error_icon_visible(self, field_id: str) -> bool:
        """Checks if the validation SVG icon is visible for a specific input ID ('user-name' or 'password')."""
        return self.ico_field_error.format(field_id=field_id).is_visible()

    # --- Login Submit Button Atomic Methods ---
    @allure.step("Clicking Login button")
    def click_login(self) -> Self:
        """Clicks the Login submit button."""
        self.btn_login.click()
        return self

    @allure.step("Submitting login via ENTER key on password field")
    def submit_with_enter(self) -> Self:
        """Submits the login form by pressing ENTER on the password input."""
        self.input_password.press_enter()
        return self

    def get_login_button_text(self) -> str:
        """Retrieves the visible label ('value' attribute) of the Login submit button."""
        return self.btn_login.get_value()

    def is_login_button_enabled(self) -> bool:
        """Checks if the Login submit button is enabled."""
        return self.btn_login.is_enabled()

    def is_login_button_visible(self) -> bool:
        """Checks if the Login submit button is visible."""
        return self.btn_login.is_visible()

    # --- Error Alert Banner Atomic Methods ---
    def get_error_message(self) -> str:
        """Waits for the error banner to appear and returns its text."""
        return self.msg_error.wait_visible().get_trimmed_text()

    def is_error_message_visible(self) -> bool:
        """Checks if the error alert message banner is currently visible."""
        return self.msg_error.is_visible()

    def is_error_message_not_visible(self) -> bool:
        """Checks if the error alert message banner is absent or hidden."""
        return self.msg_error.is_not_visible()

    @allure.step("Clicking the 'X' button to dismiss the login error message")
    def click_dismiss_error(self) -> Self:
        """Clicks the 'X' button inside the error banner and waits for the banner to disappear."""
        self.btn_dismiss_error.click()
        self.msg_error.wait_disappear()
        return self

    # --- Reference Credentials & Password Footer Panel Atomic Methods ---
    def is_credentials_panel_visible(self) -> bool:
        """Checks if the bottom reference credentials container is visible."""
        return self.cnt_credentials_panel.is_visible()

    def get_accepted_usernames_header(self) -> str:
        """Returns the header title of the accepted usernames section ('Accepted usernames are:')."""
        return self.hdr_accepted_usernames.get_trimmed_text()

    def get_accepted_usernames_list(self) -> List[str]:
        """
        Extracts and parses the list of accepted usernames displayed on the page
        (excluding the '<h4>Accepted usernames are:</h4>' header line).
        """
        raw_text = self.txt_accepted_usernames.get_trimmed_text()
        header = self.get_accepted_usernames_header()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return [line for line in lines if line != header]

    def get_password_info_header(self) -> str:
        """Returns the header title of the password hint section ('Password for all users:')."""
        return self.hdr_password_info.get_trimmed_text()

    def get_public_password_hint(self) -> str:
        """
        Extracts the shared password string ('secret_sauce') displayed in the
        bottom password info box (excluding the '<h4>Password for all users:</h4>' header).
        """
        raw_text = self.txt_password_info.get_trimmed_text()
        header = self.get_password_info_header()
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        remaining = [line for line in lines if line != header]
        return remaining[0] if remaining else ""

    # =========================================================================
    # LAYER 3: Composite Business / Form Methods (Orchestrating Layer 2 ONLY)
    # =========================================================================

    @allure.step("Logging in with username '{username}'")
    def login(self, username: str = None, password: str = None) -> Self:
        """
        Performs the standard login flow by chaining Layer 2 atomic methods.
        Falls back to environment YAML defaults (`self.username`, `self.password`) when omitted.
        """
        user = username if username is not None else self.username
        pwd = password if password is not None else self.password
        return self.set_username(user).set_password(pwd).click_login()

    @allure.step("Logging in with JSON/dict payload")
    def login_with_data(self, data: Dict[str, Any]) -> Self:
        """
        Populates the login form automatically via `BasePage.fill_form(data)`
        (which delegates to `set_username` and `set_password`) and clicks Login.
        """
        return self.fill_form(data).click_login()

    @allure.step(
        "Logging in dynamically using the N-th username listed on the page (index={user_index})"
    )
    def login_using_page_listed_credential(self, user_index: int = 0) -> Self:
        """
        Reads the accepted usernames and password directly from the Login page's
        bottom reference panel (Layer 2 getters) and logs in with them.
        """
        usernames = self.get_accepted_usernames_list()
        password = self.get_public_password_hint()
        selected_user = usernames[user_index]
        return self.set_username(selected_user).set_password(password).click_login()

    @allure.step("Clearing both login form fields")
    def clear_login_form(self) -> Self:
        """Clears both username and password fields using Layer 2 atomic methods."""
        return self.clear_username().clear_password()

    def has_full_validation_error_state(self) -> bool:
        """
        Verifies that a failed login triggered the complete UI validation state:
        1. Error banner is visible
        2. Both inputs have the 'error' CSS class
        3. Both red circle-xmark SVG icons are visible
        """
        return (
            self.is_error_message_visible()
            and self.is_username_highlighted_as_error()
            and self.is_password_highlighted_as_error()
            and self.is_username_error_icon_visible()
            and self.is_password_error_icon_visible()
        )
