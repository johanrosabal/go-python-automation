import allure
from typing import Optional, List
from core.ui.actions.playwright.base_action import BaseAction

class ElementsActions(BaseAction):
    """
    Playwright-native component for element state inspection and presence/visibility checks.
    """

    def is_visible(self) -> bool:
        """Returns True if the element is visible in the DOM."""
        try:
            return self.get_locator().is_visible(timeout=self._current_timeout)
        except Exception:
            return False

    def is_not_visible(self) -> bool:
        """Returns True if the element is not visible or detached."""
        return not self.is_visible()

    def is_enabled(self) -> bool:
        """Returns True if the element is enabled."""
        try:
            return self.get_locator().is_enabled(timeout=self._current_timeout)
        except Exception:
            return False

    def is_selected(self) -> bool:
        """Checks if the element is checked/selected."""
        try:
            return self.get_locator().is_checked(timeout=self._current_timeout)
        except Exception:
            return False

    def is_clickable(self) -> bool:
        """Playwright checks enabled and visible for clickability."""
        return self.is_visible() and self.is_enabled()

    def is_enabled_js(self) -> bool:
        return self.is_enabled()

    @allure.step("Waiting for element to be visible")
    def wait_visible(self, timeout: int = None) -> "ElementsActions":
        """Explicitly waits for the element to reach visible state."""
        t = (timeout * 1000) if timeout else self._current_timeout
        try:
            self.get_locator().wait_for(state="visible", timeout=t)
            self.logger.info(f"Element '{self._selector}' is now visible.")
            return self
        except Exception as e:
            self._handle_exception(e, "wait_visible")

    @allure.step("Waiting for element to disappear")
    def wait_disappear(self, timeout: int = None) -> "ElementsActions":
        """Explicitly waits for the element to become hidden or detached."""
        t = (timeout * 1000) if timeout else self._current_timeout
        try:
            self.get_locator().wait_for(state="hidden", timeout=t)
            self.logger.info(f"Element '{self._selector}' has disappeared.")
            return self
        except Exception as e:
            self._handle_exception(e, "wait_disappear")

    @allure.step("Waiting for element to be present in DOM")
    def wait_present(self, timeout: int = None) -> bool:
        t = (timeout * 1000) if timeout else self._current_timeout
        try:
            self.get_locator().wait_for(state="attached", timeout=t)
            return True
        except Exception:
            return False

    @allure.step("Waiting for element to be clickable")
    def wait_clickable(self, timeout: int = None) -> bool:
        t = (timeout * 1000) if timeout else self._current_timeout
        try:
            self.get_locator().wait_for(state="visible", timeout=t)
            return self.is_enabled()
        except Exception:
            return False

    def get_text(self) -> str:
        """Returns the inner text of the element."""
        return self.get_locator().inner_text(timeout=self._current_timeout)

    def get_trimmed_text(self) -> str:
        """Returns the stripped inner text."""
        return self.get_text().strip()

    def get_attribute(self, attr_name: str) -> Optional[str]:
        """Returns the value of the specified HTML attribute."""
        if attr_name == "value":
            return self.get_locator().input_value(timeout=self._current_timeout)
        return self.get_locator().get_attribute(attr_name, timeout=self._current_timeout)

    def get_css_value(self, property_name: str) -> str:
        return self.get_locator().evaluate(f"el => window.getComputedStyle(el).getPropertyValue('{property_name}')")

    def wait_for_text(self, text: str, timeout: int = None) -> bool:
        t = (timeout * 1000) if timeout else self._current_timeout
        try:
            import re
            self.page.locator(self._selector, has_text=text).wait_for(state="visible", timeout=t)
            return True
        except Exception:
            return False

    def wait_for_page_load(self, timeout: int = 30) -> "ElementsActions":
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout * 1000)
        except Exception:
            pass
        return self

    def wait_for_js_completion(self, timeout: int = 20) -> "ElementsActions":
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        except Exception:
            pass
        return self

    def count(self) -> int:
        """Returns the number of matching elements."""
        return self.get_locator().count()
