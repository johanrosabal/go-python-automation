import re
from typing import Any, List, Optional, Union, Dict
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from core.ui.playwright.locator_converter import convert_selenium_locator_to_playwright
from core.utils.logger_config import setup_logger
from core.utils.action_tracer import ActionTracer


class PlaywrightElement:
    """
    Adapter implementing the UIElement interface backed natively by Playwright's Locator API.
    Provides complete API parity with Selenium's UIElement so Page Objects run unchanged.
    """

    def __init__(self, page: Page, locator: Any, label: Optional[str] = None):
        self.page = page
        self.raw_locator = locator
        self.label = label or str(locator)
        self.selector = convert_selenium_locator_to_playwright(locator)
        self._timeout = 10000  # Default ms
        self.logger = setup_logger(self.__class__.__name__)

    @property
    def locator(self) -> Locator:
        return self.page.locator(self.selector)

    def at(self, timeout_seconds: int) -> "PlaywrightElement":
        """Overrides timeout for the immediate operation."""
        self._timeout = int(timeout_seconds * 1000)
        return self

    def format(self, **kwargs) -> "PlaywrightElement":
        """Formats dynamic placeholders in selector and label."""
        formatted_raw = self.raw_locator
        if isinstance(self.raw_locator, tuple):
            by_type, val = self.raw_locator
            formatted_raw = (by_type, val.format(**kwargs))
        elif isinstance(self.raw_locator, str):
            formatted_raw = self.raw_locator.format(**kwargs)

        formatted_label = self.label.format(**kwargs) if self.label else None
        return PlaywrightElement(self.page, formatted_raw, formatted_label)

    # -------------------------------------------------------------------------
    # Core Actions & Typing
    # -------------------------------------------------------------------------
    def type(self, text: str, clear: bool = True) -> "PlaywrightElement":
        """Types text into the element using Playwright fill."""
        ActionTracer.record_action(
            action="TYPE",
            page="Playwright",
            element=self.label,
            locator=self.selector,
            duration_ms=0,
            status="PASS"
        )
        if clear:
            self.locator.fill(str(text), timeout=self._timeout)
        else:
            self.locator.type(str(text), timeout=self._timeout)
        return self

    def send_keys(self, text: str, clear: bool = True) -> "PlaywrightElement":
        return self.type(text, clear=clear)

    def type_encrypted(self, text: str) -> "PlaywrightElement":
        from core.utils.base64_utils import resolve_secret_value
        decrypted = resolve_secret_value(text)
        ActionTracer.record_action(
            action="TYPE_ENCRYPTED",
            page="Playwright",
            element=self.label,
            locator=self.selector,
            duration_ms=0,
            status="PASS"
        )
        self.locator.fill(decrypted, timeout=self._timeout)
        return self

    def clear(self) -> "PlaywrightElement":
        self.locator.fill("", timeout=self._timeout)
        return self

    def physical_clear(self) -> "PlaywrightElement":
        self.locator.click(timeout=self._timeout)
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        return self

    def press_enter(self) -> "PlaywrightElement":
        self.locator.press("Enter", timeout=self._timeout)
        return self

    def press_tab(self) -> "PlaywrightElement":
        self.locator.press("Tab", timeout=self._timeout)
        return self

    def press_escape(self) -> "PlaywrightElement":
        self.locator.press("Escape", timeout=self._timeout)
        return self

    # -------------------------------------------------------------------------
    # Mouse & Click Actions
    # -------------------------------------------------------------------------
    def click(self) -> "PlaywrightElement":
        ActionTracer.record_action(
            action="CLICK",
            page="Playwright",
            element=self.label,
            locator=self.selector,
            duration_ms=0,
            status="PASS"
        )
        self.locator.click(timeout=self._timeout)
        return self

    def double_click(self) -> "PlaywrightElement":
        self.locator.dblclick(timeout=self._timeout)
        return self

    def right_click(self) -> "PlaywrightElement":
        self.locator.click(button="right", timeout=self._timeout)
        return self

    def hover(self) -> "PlaywrightElement":
        self.locator.hover(timeout=self._timeout)
        return self

    def js_click(self) -> "PlaywrightElement":
        self.locator.dispatch_event("click")
        return self

    # -------------------------------------------------------------------------
    # Text & Reading Values
    # -------------------------------------------------------------------------
    def get_text(self) -> str:
        text = self.locator.inner_text(timeout=self._timeout)
        ActionTracer.record_action(
            action="GET_TEXT",
            page="Playwright",
            element=self.label,
            locator=self.selector,
            duration_ms=0,
            status="PASS"
        )
        return text

    def get_trimmed_text(self) -> str:
        return self.get_text().strip()

    def get_value(self) -> str:
        return self.locator.input_value(timeout=self._timeout)

    def get_attribute(self, attr_name: str) -> Optional[str]:
        return self.locator.get_attribute(attr_name, timeout=self._timeout)

    def contains_text(self, expected_text: str) -> bool:
        return expected_text in self.get_text()

    def get_int(self) -> int:
        match = re.search(r"[-+]?\d+", self.get_text())
        if not match:
            raise ValueError(f"No integer found in text: '{self.get_text()}'")
        return int(match.group(0))

    def get_float(self) -> float:
        match = re.search(r"[-+]?\d*\.\d+|\d+", self.get_text())
        if not match:
            raise ValueError(f"No float found in text: '{self.get_text()}'")
        return float(match.group(0))

    # -------------------------------------------------------------------------
    # Dropdowns & Selection
    # -------------------------------------------------------------------------
    def select_by_text(self, text: str) -> "PlaywrightElement":
        self.locator.select_option(label=text, timeout=self._timeout)
        return self

    def select_by_value(self, value: str) -> "PlaywrightElement":
        self.locator.select_option(value=value, timeout=self._timeout)
        return self

    def select_by_index(self, index: int) -> "PlaywrightElement":
        self.locator.select_option(index=index, timeout=self._timeout)
        return self

    def get_selected_text(self) -> str:
        # Reads selected option label via JS evaluation
        return str(self.locator.evaluate("el => el.options[el.selectedIndex].text"))

    # -------------------------------------------------------------------------
    # Checkboxes & Radios
    # -------------------------------------------------------------------------
    def check(self, state: bool = True) -> "PlaywrightElement":
        self.locator.set_checked(state, timeout=self._timeout)
        return self

    def select_radio(self) -> "PlaywrightElement":
        self.locator.check(timeout=self._timeout)
        return self

    def is_checked(self) -> bool:
        return self.locator.is_checked(timeout=self._timeout)

    # -------------------------------------------------------------------------
    # State Inspections & Waits
    # -------------------------------------------------------------------------
    def is_visible(self) -> bool:
        return self.locator.is_visible()

    def is_enabled(self) -> bool:
        return self.locator.is_enabled()

    def wait_visible(self, timeout_seconds: Optional[int] = None) -> "PlaywrightElement":
        timeout = int(timeout_seconds * 1000) if timeout_seconds else self._timeout
        self.locator.wait_for(state="visible", timeout=timeout)
        return self

    def wait_present(self, timeout_seconds: Optional[int] = None) -> "PlaywrightElement":
        timeout = int(timeout_seconds * 1000) if timeout_seconds else self._timeout
        self.locator.wait_for(state="attached", timeout=timeout)
        return self

    def wait_clickable(self, timeout_seconds: Optional[int] = None) -> "PlaywrightElement":
        return self.wait_visible(timeout_seconds)

    def wait_disappear(self, timeout_seconds: Optional[int] = None) -> "PlaywrightElement":
        timeout = int(timeout_seconds * 1000) if timeout_seconds else self._timeout
        self.locator.wait_for(state="hidden", timeout=timeout)
        return self

    # -------------------------------------------------------------------------
    # Scrolling & Uploads
    # -------------------------------------------------------------------------
    def scroll_to(self) -> "PlaywrightElement":
        self.locator.scroll_into_view_if_needed(timeout=self._timeout)
        return self

    def scroll_to_center(self) -> "PlaywrightElement":
        self.scroll_to()
        return self

    def upload_file(self, file_path: str) -> "PlaywrightElement":
        self.locator.set_input_files(file_path, timeout=self._timeout)
        return self
