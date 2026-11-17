import allure
from typing import List
from core.ui.actions.playwright.base_action import BaseAction

class DropdownActions(BaseAction):
    """
    Playwright-native component for HTML <select> dropdown interactions.
    """

    @allure.step("Selecting dropdown option by visible text: '{text}'")
    def select_by_text(self, text: str) -> "DropdownActions":
        try:
            self.get_locator().select_option(label=text, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "select_by_text")

    @allure.step("Selecting dropdown option by value: '{value}'")
    def select_by_value(self, value: str) -> "DropdownActions":
        try:
            self.get_locator().select_option(value=value, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "select_by_value")

    @allure.step("Selecting dropdown option by index: '{index}'")
    def select_by_index(self, index: int) -> "DropdownActions":
        try:
            self.get_locator().select_option(index=index, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "select_by_index")

    def get_selected_text(self) -> str:
        """Returns the currently selected visible text."""
        return self.get_locator().evaluate("el => el.options[el.selectedIndex].text")

    def get_dropdown_options(self) -> List[str]:
        """Returns all option texts from the dropdown."""
        return self.get_locator().evaluate("el => Array.from(el.options).map(o => o.text)")

