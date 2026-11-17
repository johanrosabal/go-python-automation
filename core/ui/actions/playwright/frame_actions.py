import allure
from typing import Any
from core.ui.actions.playwright.base_action import BaseAction
from core.ui.playwright.locator_converter import convert_selenium_locator_to_playwright

class FrameActions(BaseAction):
    """
    Playwright-native component for Frame and IFrame navigation and focus management.

    Handles switching contexts between the main document and nested frames.
    """

    def __init__(self, driver_or_page: Any):
        super().__init__(driver_or_page)
        self._current_frame = None

    def switch_to(self, locator: Any) -> "FrameActions":
        """
        Switches the focus to a specified frame or iframe.

        Args:
            locator: The Selenium tuple (By, value) or CSS/XPath string.

        Returns:
            FrameActions: The current instance for method chaining.
        """
        try:
            selector = convert_selenium_locator_to_playwright(locator)
            self.logger.info(f"Switching context to frame: '{selector}'")
            self._current_frame = self.page.frame_locator(selector)
            return self
        except Exception as e:
            self._handle_exception(e, "switch_to")

    def switch_to_parent(self) -> "FrameActions":
        """
        Switches focus to the parent frame or back to the main document.

        Returns:
            FrameActions: The current instance for method chaining.
        """
        self.logger.info("Switching back to parent frame context")
        self._current_frame = None
        return self

    def switch_to_default(self) -> "FrameActions":
        """
        Switches focus back to the main top-level document.

        Returns:
            FrameActions: The current instance for method chaining.
        """
        self.logger.info("Switching back to default content (main page)")
        self._current_frame = None
        return self

