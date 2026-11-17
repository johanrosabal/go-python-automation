from typing import Dict, List, Optional, Any
from core.ui.actions.selenium.base_action import BaseAction


class CookieActions(BaseAction):
    """
    Handles browser cookie management operations for authentication, session inspection,
    and state validation.
    """

    def get_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves all cookies stored in the current browser session.

        Returns:
            List[Dict[str, Any]]: A list of cookie dictionaries.
        """
        self.logger.debug("Retrieving all browser cookies.")
        return self.driver.get_cookies()

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific cookie by its name.

        Args:
            name (str): The cookie name.

        Returns:
            Optional[Dict[str, Any]]: The cookie dictionary if found, otherwise None.
        """
        self.logger.debug(f"Retrieving cookie: '{name}'")
        return self.driver.get_cookie(name)

    def get_value(self, name: str) -> Optional[str]:
        """
        Retrieves the string value of a specific cookie.

        Args:
            name (str): The cookie name.

        Returns:
            Optional[str]: The cookie value, or None if the cookie does not exist.
        """
        cookie = self.get(name)
        return cookie.get("value") if cookie else None

    def add(self, name: str, value: str, path: str = "/", domain: Optional[str] = None,
            secure: bool = False, http_only: bool = False, expiry: Optional[int] = None) -> "CookieActions":
        """
        Adds a new cookie to the browser session.

        Args:
            name (str): The cookie name.
            value (str): The cookie value.
            path (str): Cookie path (default is '/').
            domain (Optional[str]): Cookie domain.
            secure (bool): Whether the cookie is HTTPS only.
            http_only (bool): Whether the cookie is HTTP only.
            expiry (Optional[int]): Expiration timestamp in seconds since epoch.

        Returns:
            CookieActions: Self for fluent chaining.
        """
        cookie_dict: Dict[str, Any] = {
            "name": name,
            "value": str(value),
            "path": path,
            "secure": secure,
            "httpOnly": http_only
        }
        if domain:
            cookie_dict["domain"] = domain
        if expiry:
            cookie_dict["expiry"] = expiry

        self.logger.info(f"Adding cookie: '{name}' with path '{path}'")
        self.driver.add_cookie(cookie_dict)
        return self

    def delete(self, name: str) -> "CookieActions":
        """
        Deletes a specific cookie by name.

        Args:
            name (str): Name of the cookie to remove.

        Returns:
            CookieActions: Self for fluent chaining.
        """
        self.logger.info(f"Deleting cookie: '{name}'")
        self.driver.delete_cookie(name)
        return self

    def delete_all(self) -> "CookieActions":
        """
        Deletes all cookies in the current browser session.

        Returns:
            CookieActions: Self for fluent chaining.
        """
        self.logger.info("Deleting all cookies in current session.")
        self.driver.delete_all_cookies()
        return self

    def has(self, name: str) -> bool:
        """
        Checks whether a cookie exists.

        Args:
            name (str): The cookie name.

        Returns:
            bool: True if the cookie exists, False otherwise.
        """
        return self.get(name) is not None

