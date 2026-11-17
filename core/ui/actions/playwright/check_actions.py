import allure
from core.ui.actions.playwright.base_action import BaseAction

class CheckActions(BaseAction):
    """
    Playwright-native specialized actions for interacting with Checkboxes.
    
    Provides high-level methods to ensure a checkbox reaches a specific toggle state,
    handling state verification automatically using Playwright's native check/uncheck primitives.
    """

    @allure.step("Setting checkbox state to {state}")
    def check(self, state: bool = True) -> "CheckActions":
        """
        Sets the checkbox to the desired state (checked or unchecked).

        Args:
            state (bool): True to check, False to uncheck.

        Returns:
            CheckActions: The current instance for method chaining.
        """
        try:
            loc = self.get_locator()
            self.logger.info(f"Setting checkbox state for selector '{self._selector}' to {state}")
            if state:
                loc.check(timeout=self._current_timeout)
            else:
                loc.uncheck(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "check")

    @allure.step("Checking selection state")
    def is_checked(self) -> bool:
        """
        Checks if the element is currently selected/checked.

        Returns:
            bool: True if the element is checked, False otherwise.
        """
        try:
            return self.get_locator().is_checked(timeout=self._current_timeout)
        except Exception as e:
            self._handle_exception(e, "is_checked")

