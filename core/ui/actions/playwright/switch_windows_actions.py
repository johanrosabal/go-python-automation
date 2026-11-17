import allure
from typing import Any, List
from core.ui.actions.playwright.base_action import BaseAction

class SwitchWindowsActions(BaseAction):
    """
    Playwright-native component for browser window and tab management.

    Handles switching between multiple windows/tabs, opening and closing pages,
    and adjusting zoom levels using Playwright's Page Context.
    """

    def __init__(self, driver_or_page: Any):
        super().__init__(driver_or_page)
        self._original_page = self.page

    def get_current_handle(self) -> str:
        """
        Retrieves the handle ID of the currently focused page.

        Returns:
            str: Identifier for current page.
        """
        pages = self.page.context.pages
        try:
            idx = pages.index(self.page)
            return f"page_{idx}"
        except ValueError:
            return "page_0"

    def get_original_handle(self) -> str:
        """
        Retrieves the identifier of the original page during action initialization.

        Returns:
            str: Original page handle.
        """
        return "page_0"

    @allure.step("Switching to tab index {index}")
    def to_tab(self, index: int) -> "SwitchWindowsActions":
        """Alias for tab()."""
        return self.tab(index)

    def tab(self, index: int) -> "SwitchWindowsActions":
        """
        Switches focus to a browser tab by its index.

        Args:
            index (int): Zero-based tab index.

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        pages = self.page.context.pages
        if 0 <= index < len(pages):
            target = pages[index]
            target.bring_to_front()
            self.page = target
            if self._shim:
                self._shim.page = target
            self.logger.info(f"Switched to tab index {index}")
        else:
            self.logger.error(f"Tab index {index} out of bounds (Total tabs: {len(pages)})")
        return self

    @allure.step("Finding and switching to a new window")
    def switch_to_new(self) -> "SwitchWindowsActions":
        """Alias for find_new()."""
        return self.find_new()

    def find_new(self) -> "SwitchWindowsActions":
        """
        Switches focus to the first window that is not the original one.

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        pages = self.page.context.pages
        for p in pages:
            if p != self._original_page:
                p.bring_to_front()
                self.page = p
                if self._shim:
                    self._shim.page = p
                self.logger.info("Switched to newly opened tab/window")
                break
        return self

    @allure.step("Opening a new blank tab")
    def open_new(self) -> "SwitchWindowsActions":
        """
        Opens a new blank tab and automatically switches focus to it.

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        try:
            new_p = self.page.context.new_page()
            new_p.bring_to_front()
            self.page = new_p
            if self._shim:
                self._shim.page = new_p
            self.logger.info("Opened and switched to a new blank tab")
        except Exception as e:
            self._handle_exception(e, "open_new")
        return self

    @allure.step("Closing current tab and returning focus")
    def close_current(self) -> "SwitchWindowsActions":
        """Alias for close()."""
        return self.close()

    def close(self) -> "SwitchWindowsActions":
        """
        Closes the currently focused window and switches focus back to the original or first available tab.

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        try:
            closing_page = self.page
            closing_page.close()
            remaining = self.page.context.pages
            if self._original_page in remaining:
                self.page = self._original_page
            elif remaining:
                self.page = remaining[0]
            self.page.bring_to_front()
            if self._shim:
                self._shim.page = self.page
            self.logger.info("Closed tab and restored focus")
        except Exception as e:
            self._handle_exception(e, "close")
        return self

    def switch_to_main(self) -> "SwitchWindowsActions":
        """
        Switches focus to the first tab in the context.

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        return self.tab(0)

    @allure.step("Setting page zoom to {percentage}%")
    def set_zoom_level(self, percentage: int) -> "SwitchWindowsActions":
        """
        Adjusts the zoom level of the current page via JavaScript.

        Args:
            percentage (int): Target zoom percentage (e.g. 75, 100, 150).

        Returns:
            SwitchWindowsActions: The current instance for method chaining.
        """
        try:
            self.logger.info(f"Setting page zoom to {percentage}%")
            self.page.evaluate(f"() => {{ document.body.style.zoom='{percentage}%'; }}")
        except Exception as e:
            self._handle_exception(e, "set_zoom_level")
        return self

    def get_handles(self) -> List[str]:
        """
        Retrieves identifiers for all active pages in the browser context.

        Returns:
            List[str]: List of handle identifiers.
        """
        return [f"page_{i}" for i in range(len(self.page.context.pages))]

