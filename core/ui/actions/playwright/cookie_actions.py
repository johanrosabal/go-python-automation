import allure
from typing import List, Dict, Optional, Any
from core.ui.actions.playwright.base_action import BaseAction

class CookieActions(BaseAction):
    """
    Playwright-native component for browser cookie management via BrowserContext.
    """

    @allure.step("Getting all cookies")
    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieves all cookies stored in the current BrowserContext."""
        try:
            return self.page.context.cookies()
        except Exception as e:
            self._handle_exception(e, "get_all_cookies")

    @allure.step("Getting cookie: '{name}'")
    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Finds a cookie by its name."""
        cookies = self.get_all()
        for c in cookies:
            if c.get("name") == name:
                return c
        return None

    def get_value(self, name: str) -> Optional[str]:
        """Returns the string value of a cookie, or None if not present."""
        cookie = self.get(name)
        return cookie.get("value") if cookie else None

    def has(self, name: str) -> bool:
        """Checks whether a cookie exists."""
        return self.get(name) is not None

    @allure.step("Adding cookie: '{name}'")
    def add(self, name: str, value: str, path: str = "/", domain: Optional[str] = None, secure: bool = False, http_only: bool = False) -> "CookieActions":
        """Adds a cookie to the current BrowserContext."""
        try:
            cookie_dict = {
                "name": name,
                "value": value,
                "path": path,
                "secure": secure,
                "httpOnly": http_only,
                "url": self.page.url
            }
            if domain:
                cookie_dict["domain"] = domain
            self.page.context.add_cookies([cookie_dict])
            self.logger.info(f"Added cookie '{name}' with value '{value}'")
            return self
        except Exception as e:
            self._handle_exception(e, "add_cookie")

    @allure.step("Deleting cookie: '{name}'")
    def delete(self, name: str) -> "CookieActions":
        """Deletes a cookie by name from the current BrowserContext."""
        try:
            cookies = [c for c in self.get_all() if c.get("name") != name]
            self.page.context.clear_cookies()
            if cookies:
                self.page.context.add_cookies(cookies)
            self.logger.info(f"Deleted cookie '{name}'")
            return self
        except Exception as e:
            self._handle_exception(e, "delete_cookie")

    @allure.step("Deleting all cookies")
    def delete_all(self) -> "CookieActions":
        """Clears all cookies from the active BrowserContext."""
        try:
            self.page.context.clear_cookies()
            self.logger.info("Cleared all cookies from BrowserContext.")
            return self
        except Exception as e:
            self._handle_exception(e, "delete_all_cookies")

