import allure
from core.ui.actions.playwright.base_action import BaseAction

class ScrollActions(BaseAction):
    """
    Playwright-native component for viewport and element scrolling operations.
    """

    @allure.step("Scrolling element into view")
    def scroll_to_element(self) -> "ScrollActions":
        """Scrolls the element into the viewport if needed."""
        try:
            self.logger.info(f"Scrolling to element: {self._selector}")
            self.get_locator().scroll_into_view_if_needed(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "scroll_to_element")

    @allure.step("Scrolling to top of the page")
    def scroll_to_top(self) -> "ScrollActions":
        """Scrolls to the top of the browser page."""
        try:
            self.page.evaluate("window.scrollTo(0, 0)")
            return self
        except Exception as e:
            self._handle_exception(e, "scroll_to_top")

    @allure.step("Scrolling to bottom of the page")
    def scroll_to_bottom(self) -> "ScrollActions":
        """Scrolls to the bottom of the browser page."""
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            return self
        except Exception as e:
            self._handle_exception(e, "scroll_to_bottom")

    @allure.step("Scrolling by pixel offset")
    def scroll_by(self, x: int, y: int) -> "ScrollActions":
        """Scrolls the viewport by horizontal and vertical pixel offsets."""
        try:
            self.page.evaluate(f"window.scrollBy({x}, {y})")
            return self
        except Exception as e:
            self._handle_exception(e, "scroll_by")

