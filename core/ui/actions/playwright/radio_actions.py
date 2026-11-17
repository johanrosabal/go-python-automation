import allure
from core.ui.actions.playwright.base_action import BaseAction

class RadioActions(BaseAction):
    """
    Playwright-native specialized actions for interacting with Radio Buttons.

    Provides high-level methods to ensure a radio button is selected,
    handling the current state check automatically.
    """

    @allure.step("Selecting radio button")
    def select_radio(self) -> "RadioActions":
        """
        Selects the radio button if not already selected.

        Returns:
            RadioActions: The current instance for method chaining.
        """
        try:
            loc = self.get_locator()
            self.logger.info(f"Selecting radio button: {self._selector}")
            if not loc.is_checked(timeout=self._current_timeout):
                loc.check(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "select_radio")

    def is_selected(self) -> bool:
        """
        Checks if the radio button is currently selected.

        Returns:
            bool: True if selected, False otherwise.
        """
        try:
            return self.get_locator().is_checked(timeout=self._current_timeout)
        except Exception as e:
            self._handle_exception(e, "is_selected")

