import re
import allure
from core.ui.common.base_component import BaseComponent
from core.ui.common.find_by import find_by


class SidebarComponent(BaseComponent):
    """
    Reusable Component representing the SauceDemo Burger Sidebar Menu.
    """

    button_side_menu = find_by(id="react-burger-menu-btn", label="Burger Side Menu Button")
    link_logout = find_by(id="logout_sidebar_link", label="Logout Sidebar Link")

    @allure.step("Opening sidebar menu")
    def open_menu(self) -> "SidebarComponent":
        """Opens the burger menu and waits for the logout link to become clickable."""
        self.button_side_menu.click()
        self.link_logout.wait_clickable()
        return self

    @allure.step("Logging out via sidebar menu")
    def logout(self):
        """Performs the logout sequence via the sidebar menu and waits for base URL redirect."""
        self.logger.info("Performing logout via SidebarComponent")
        self.open_menu()
        self.link_logout.click()

        expected_url = self.base_url.rstrip("/")
        self.navigation.wait_url_matches(rf"^{re.escape(expected_url)}/?$")

        from applications.web.demo.pages.login_page import LoginPage
        return LoginPage()

