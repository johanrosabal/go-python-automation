import allure
from typing import Any, Optional, TypeVar
from playwright.sync_api import Page, Locator
from core.ui.playwright.locator_converter import convert_selenium_locator_to_playwright
from core.utils.logger_config import setup_logger

T = TypeVar('T', bound='BaseAction')

class BaseAction:
    """
    Foundational base class for all Playwright UI action components.
    
    Provides direct access to Playwright's Page and Locator primitives,
    native auto-waiting, dynamic timeouts, and standardized logging.
    """
    def __init__(self, driver_or_page: Any):
        """
        Initializes the Playwright BaseAction.
        Accepts either a Playwright Page instance or a PlaywrightWebDriverShim.
        """
        if hasattr(driver_or_page, "page"):
            self.page: Page = driver_or_page.page
            self._shim = driver_or_page
        elif isinstance(driver_or_page, Page):
            self.page: Page = driver_or_page
            self._shim = None
        else:
            # Fallback if raw driver passed
            self.page = getattr(driver_or_page, "page", driver_or_page)
            self._shim = driver_or_page

        self.default_timeout = 10000  # 10s in milliseconds
        self._current_timeout = self.default_timeout
        self._locator = None
        self._selector = None
        self._is_shadow = False
        self.logger = setup_logger(self.__class__.__name__)

    @property
    def driver(self):
        """Returns the underlying shim or page for compatibility."""
        return self._shim or self.page

    def at(self: T, timeout_seconds: int) -> T:
        """Sets a temporary timeout (in seconds) for the immediate next operation."""
        self._current_timeout = int(timeout_seconds * 1000)
        return self

    def shadow(self: T, is_shadow: bool = True) -> T:
        """Enables Shadow DOM searching (Playwright pierces open shadow roots by default)."""
        self._is_shadow = is_shadow
        return self

    def set_locator(self: T, locator: Any) -> T:
        """Sets the locator (Selenium tuple or Playwright selector string)."""
        self._locator = locator
        self._selector = convert_selenium_locator_to_playwright(locator)
        return self

    def get_locator(self) -> Locator:
        """Returns the active Playwright Locator for the configured selector."""
        if not self._selector:
            raise ValueError(f"No locator set on {self.__class__.__name__}. Call set_locator() first.")
        return self.page.locator(self._selector)

    def _handle_exception(self, e: Exception, action_name: str):
        """Standardized exception logger and re-raiser."""
        msg = f"Failed to perform Playwright action '{action_name}' on selector '{self._selector}': {e}"
        self.logger.error(msg)
        raise e

