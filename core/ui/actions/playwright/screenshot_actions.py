import allure
from core.ui.actions.playwright.base_action import BaseAction

class ScreenshotActions(BaseAction):
    """
    Playwright-native component for capturing full-page and element screenshots.
    """

    @allure.step("Taking full page screenshot")
    def take_screenshot(self, filename: str) -> bool:
        try:
            self.page.screenshot(path=filename, full_page=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot '{filename}': {e}")
            return False

    @allure.step("Taking element screenshot")
    def take_element_screenshot(self, filename: str) -> bool:
        try:
            self.get_locator().screenshot(path=filename)
            return True
        except Exception as e:
            self.logger.error(f"Failed to capture element screenshot '{filename}': {e}")
            return False

