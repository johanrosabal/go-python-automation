import allure
from typing import Any
from core.ui.actions.playwright.base_action import BaseAction
from core.utils.base64_utils import encode_base64

class SendKeysActions(BaseAction):
    """
    Playwright-native component for keyboard and text input interactions.
    """

    def __init__(self, driver_or_page: Any):
        super().__init__(driver_or_page)
        self._encrypt = False

    def encrypted(self) -> "SendKeysActions":
        """Enables base64 encryption for text in logs."""
        self._encrypt = True
        return self

    @allure.step("Typing text into element (Clear: {clear})")
    def type(self, text: str, clear: bool = True) -> "SendKeysActions":
        """Types text, optionally clearing existing content first."""
        try:
            log_text = encode_base64(text) if self._encrypt else str(text)
            self.logger.debug(f"Send Keys [{log_text}]")
            if clear:
                self.get_locator().fill(str(text), timeout=self._current_timeout)
            else:
                self.get_locator().type(str(text), timeout=self._current_timeout)
            self._encrypt = False
            return self
        except Exception as e:
            self._handle_exception(e, "type")

    @allure.step("Typing encrypted text into element")
    def type_encrypted(self, text: str, clear: bool = True) -> "SendKeysActions":
        """Enables masked logging and types text into the element."""
        return self.encrypted().type(text, clear=clear)

    @allure.step("Typing text via JavaScript (Clear: {clear})")
    def type_js(self, text: str, clear: bool = False) -> "SendKeysActions":
        """Sets element value directly via JavaScript."""
        try:
            self.get_locator().evaluate(f"""(el) => {{
                el.value = '{text}';
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}""")
            return self
        except Exception as e:
            self._handle_exception(e, "type_js")

    @allure.step("Typing text into element")
    def send_keys(self, *values) -> "SendKeysActions":
        """Types text into the element using Playwright fill."""
        text = "".join(str(v) for v in values)
        return self.type(text, clear=False)

    @allure.step("Typing text character by character")
    def type_by_character(self, text: str, delay_ms: int = 50) -> "SendKeysActions":
        """Types text with a human-like delay between keystrokes."""
        try:
            self.get_locator().type(str(text), delay=delay_ms, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "type_by_character")

    @allure.step("Clearing element text")
    def clear(self, use_js: bool = False) -> "SendKeysActions":
        """Clears the value of the input element."""
        try:
            if use_js:
                self.get_locator().evaluate("el => { el.value = ''; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }")
            else:
                self.get_locator().fill("", timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "clear")

    def clear_js(self) -> "SendKeysActions":
        """Clears input field via JavaScript dispatch."""
        return self.clear(use_js=True)

    def physical_clear(self) -> "SendKeysActions":
        """Selects all and presses Backspace."""
        try:
            self.get_locator().press("Control+A")
            self.get_locator().press("Backspace")
            return self
        except Exception as e:
            return self.clear()

    @allure.step("Pressing key: '{key_name}'")
    def press_key(self, key_name: str) -> "SendKeysActions":
        """Presses a specific keyboard key (Enter, Tab, Escape, etc.)."""
        try:
            self.get_locator().press(key_name, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "press_key")

    def press_enter(self) -> "SendKeysActions":
        return self.press_key("Enter")

    def press_tab(self) -> "SendKeysActions":
        return self.press_key("Tab")

    def press_escape(self) -> "SendKeysActions":
        return self.press_key("Escape")
