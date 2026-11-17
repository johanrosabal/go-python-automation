import re
import allure
from typing import List, Optional
from core.ui.actions.playwright.base_action import BaseAction

class GetTextActions(BaseAction):
    """
    Playwright-native component for retrieving and validating text and values from UI elements.
    """

    @allure.step("Getting text from element")
    def get_text(self) -> str:
        try:
            return self.get_locator().inner_text(timeout=self._current_timeout)
        except Exception as e:
            self._handle_exception(e, "get_text")

    def text(self) -> str:
        return self.get_text()

    @allure.step("Getting trimmed text from element")
    def get_trimmed_text(self) -> str:
        val = self.get_text()
        return val.strip() if val else ""

    def trimmed(self) -> str:
        return self.get_trimmed_text()

    @allure.step("Getting attribute {attribute} from element")
    def attribute(self, attribute: str) -> Optional[str]:
        try:
            if attribute == "value":
                return self.get_locator().input_value(timeout=self._current_timeout)
            return self.get_locator().get_attribute(attribute, timeout=self._current_timeout)
        except Exception as e:
            self._handle_exception(e, "attribute")

    def value(self) -> str:
        return self.attribute("value") or ""

    @allure.step("Checking if element contains text '{expected_text}'")
    def contains(self, expected_text: str) -> bool:
        val = self.get_text()
        return expected_text in val if val else False

    @allure.step("Waiting until element text is exactly '{expected_text}'")
    def wait_until_is(self, expected_text: str) -> "GetTextActions":
        try:
            self.page.locator(self._selector, has_text=expected_text).wait_for(
                state="visible", timeout=self._current_timeout
            )
            return self
        except Exception as e:
            self._handle_exception(e, "wait_until_is")

    @allure.step("Checking if element matches regex pattern '{pattern}'")
    def matches_regex(self, pattern: str) -> bool:
        val = self.get_text()
        return bool(re.match(pattern, val)) if val else False

    @allure.step("Checking if element is empty")
    def is_empty(self) -> bool:
        val = self.trimmed()
        return not val

    def inner_html(self) -> str:
        return self.get_locator().inner_html(timeout=self._current_timeout)

    def outer_html(self) -> str:
        return self.get_locator().evaluate("el => el.outerHTML")

    def text_content(self) -> str:
        return self.get_locator().text_content(timeout=self._current_timeout) or ""

    def get_int(self) -> int:
        val = self.get_text()
        nums = re.findall(r'\d+', val)
        return int(nums[0]) if nums else 0

    def get_float(self) -> float:
        val = self.get_text()
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", val)
        return float(nums[0]) if nums else 0.0

    def all_texts(self) -> List[str]:
        try:
            return self.get_locator().all_inner_texts()
        except Exception as e:
            self._handle_exception(e, "all_texts")

