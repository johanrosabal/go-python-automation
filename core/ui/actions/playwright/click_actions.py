import allure
from typing import Any
from core.ui.actions.playwright.base_action import BaseAction
from core.ui.playwright.locator_converter import convert_selenium_locator_to_playwright

class ClickActions(BaseAction):
    """
    Playwright-native component for handling all click and mouse interactions.
    Leverages Playwright's built-in actionability checks and auto-waiting.
    """

    @allure.step("Clicking on element")
    def click(self) -> "ClickActions":
        """Performs a standard click with Playwright's auto-wait."""
        try:
            self.logger.info(f"Clicking on element: {self._selector}")
            self.get_locator().click(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "click")

    @allure.step("Clicking on element")
    def single_click(self) -> "ClickActions":
        """Alias for click()."""
        return self.click()

    @allure.step("Double clicking on element")
    def double_click(self) -> "ClickActions":
        """Performs a double-click on the element."""
        try:
            self.logger.info(f"Double clicking on: {self._selector}")
            self.get_locator().dblclick(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "double_click")

    @allure.step("Right clicking on element")
    def right_click(self) -> "ClickActions":
        """Performs a context (right) click on the element."""
        try:
            self.logger.info(f"Right clicking on: {self._selector}")
            self.get_locator().click(button="right", timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "right_click")

    @allure.step("Hovering over element")
    def hover(self) -> "ClickActions":
        """Hovers the mouse pointer over the element."""
        try:
            self.logger.info(f"Hovering over: {self._selector}")
            self.get_locator().hover(timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "hover")

    @allure.step("Clicking and holding on element")
    def click_and_hold(self) -> "ClickActions":
        """Dispatches mouse down over the element."""
        try:
            box = self.get_locator().bounding_box(timeout=self._current_timeout)
            if box:
                self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                self.page.mouse.down()
            return self
        except Exception as e:
            self._handle_exception(e, "click_and_hold")

    @allure.step("Releasing mouse button")
    def release_mouse(self) -> "ClickActions":
        """Dispatches mouse up."""
        try:
            self.page.mouse.up()
            return self
        except Exception as e:
            self._handle_exception(e, "release_mouse")

    @allure.step("Dragging element to target")
    def drag_and_drop(self, target_locator: Any) -> "ClickActions":
        """Drags the current element onto a destination locator."""
        try:
            target_sel = convert_selenium_locator_to_playwright(target_locator)
            self.logger.info(f"Dragging {self._selector} to {target_sel}")
            target_loc = self.page.locator(target_sel)
            self.get_locator().drag_to(target_loc, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "drag_and_drop")

