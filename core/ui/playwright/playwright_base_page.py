from typing import Any, List, Dict, Optional, Self
from playwright.sync_api import Page
from core.ui.playwright.playwright_element import PlaywrightElement
from core.utils.logger_config import setup_logger
from core.utils.config_manager import ConfigManager


class PlaywrightBasePage:
    """
    Playwright-native BasePage implementing the framework's 3-Layer standard,
    offering exact parity with Selenium's BasePage for effortless cross-engine execution.
    """

    PAGE_PATH: Optional[str] = None

    def __init__(self, page: Optional[Page] = None):
        self.page = page
        self.logger = setup_logger(self.__class__.__name__)
        self._anchors: List[PlaywrightElement] = []

    def set_page(self, page: Page) -> Self:
        self.page = page
        return self

    def open(self, url: Optional[str] = None) -> Self:
        target_url = url
        if not target_url:
            base = ConfigManager.get("web.base_url", "")
            path = self.PAGE_PATH or ""
            target_url = f"{base.rstrip('/')}/{path.lstrip('/')}" if path else base

        self.logger.info(f"Navigating via Playwright to: {target_url}")
        self.page.goto(target_url, wait_until="domcontentloaded")
        return self

    def is_loaded(self) -> bool:
        """Evaluates whether all anchor elements on the page are visible."""
        # Inspect descriptors marked as anchor
        for attr_name in dir(self.__class__):
            val = getattr(self, attr_name, None)
            if isinstance(val, PlaywrightElement) and getattr(val, "anchor", False):
                if not val.is_visible():
                    return False
        return True

    def wait_until_loaded(self, timeout_seconds: int = 15) -> Self:
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout_seconds * 1000)
        return self

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def element(self, locator: Any, label: Optional[str] = None) -> PlaywrightElement:
        return PlaywrightElement(self.page, locator, label)

    # -------------------------------------------------------------------------
    # Cookies & Storage
    # -------------------------------------------------------------------------
    def add_cookie(self, name: str, value: str, path: str = "/") -> Self:
        self.page.context.add_cookies([{"name": name, "value": value, "url": self.page.url, "path": path}])
        return self

    def get_cookies(self) -> List[Dict[str, Any]]:
        return self.page.context.cookies()

    def clear_cookies(self) -> Self:
        self.page.context.clear_cookies()
        return self

    def clear_storage(self) -> Self:
        self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        return self
