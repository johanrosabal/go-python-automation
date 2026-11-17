import allure
from core.ui.actions.playwright.base_action import BaseAction

class NavigationActions(BaseAction):
    """
    Playwright-native component for browser-level navigation operations.
    """

    @allure.step("Navigating to URL: '{url}'")
    def to(self, url: str) -> "NavigationActions":
        try:
            self.logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until="domcontentloaded", timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "navigate_to")

    @allure.step("Opening URL: '{url}'")
    def open(self, url: str, wait_for_load: bool = True) -> "NavigationActions":
        """Directly navigates to the provided URL."""
        return self.to(url)

    def go(self, url: str, base_url: str = None) -> "NavigationActions":
        """Navigates to a concatenated URL and waits for the page to load."""
        if base_url is None:
            from core.utils.config_manager import ConfigManager
            base_url = ConfigManager.get("web.base_url", "")
        full_url = str(base_url).rstrip('/') + '/' + str(url).lstrip('/')
        return self.to(full_url)

    @allure.step("Refreshing page")
    def refresh(self) -> "NavigationActions":
        try:
            self.page.reload(wait_until="domcontentloaded")
            return self
        except Exception as e:
            self._handle_exception(e, "refresh")

    @allure.step("Navigating back")
    def back(self) -> "NavigationActions":
        try:
            self.page.go_back(wait_until="domcontentloaded")
            return self
        except Exception as e:
            self._handle_exception(e, "back")

    @allure.step("Navigating forward")
    def forward(self) -> "NavigationActions":
        try:
            self.page.go_forward(wait_until="domcontentloaded")
            return self
        except Exception as e:
            self._handle_exception(e, "forward")

    def get_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    @allure.step("Waiting for URL to contain: '{partial_url}'")
    def wait_url_contains(self, partial_url: str, timeout: int = None) -> "NavigationActions":
        try:
            import re
            t = (timeout * 1000) if timeout else self._current_timeout
            self.page.wait_for_url(re.compile(re.escape(partial_url)), timeout=t)
            return self
        except Exception as e:
            self._handle_exception(e, "wait_url_contains")

    @allure.step("Waiting for URL to match pattern: '{pattern}'")
    def wait_url_matches(self, pattern: str) -> "NavigationActions":
        try:
            import re
            self.page.wait_for_url(re.compile(pattern), timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "wait_url_matches")
