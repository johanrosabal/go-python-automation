"""
Legacy BasePage Compatibility Adapter.
Provides exact 1:1 API parity with the legacy BasePage class, allowing un-modified
legacy Page Objects to execute transparently on the modern dual-engine framework.
"""
from typing import Optional
from core.ui.common.base_app import BaseApp
from core.ui.adapters.legacy.actions import (
    LegacyClick,
    LegacySendKeys,
    LegacyGetText,
    LegacyNavigation,
    LegacyScreenshot,
    LegacyDropdown,
    LegacyCheckbox,
    LegacyRadio,
    LegacyTable,
    LegacyAlert,
    LegacyFrame,
    LegacySwitchWindow,
    LegacyUploadFile,
    LegacyElement,
    LegacyScroll,
    LegacyElementHighlighter,
    LegacyVerifyLocators,
)
from core.utils.logger_config import setup_logger

logger = setup_logger("LegacyBasePage")


class BasePage:
    """
    Drop-in compatibility base class for legacy Page Objects.
    Emulates the old BasePage methods and delegates to the modern runtime.
    """
    def __init__(self, driver=None):
        self._driver = driver or BaseApp.get_driver()
        self.driver = self._driver
        self._name = self.__class__.__name__
        self.relative = ""

    def get_driver(self):
        return self.driver or BaseApp.get_driver()

    def navigation(self) -> LegacyNavigation:
        return LegacyNavigation(self.get_driver())

    def click(self) -> LegacyClick:
        return LegacyClick(self.get_driver())

    def send_keys(self) -> LegacySendKeys:
        return LegacySendKeys(self.get_driver())

    def get_text(self) -> LegacyGetText:
        return LegacyGetText(self.get_driver())

    def screenshot(self) -> LegacyScreenshot:
        return LegacyScreenshot(self.get_driver())

    def dropdown(self) -> LegacyDropdown:
        return LegacyDropdown(self.get_driver())

    def checkbox(self) -> LegacyCheckbox:
        return LegacyCheckbox(self.get_driver())

    def radio(self) -> LegacyRadio:
        return LegacyRadio(self.get_driver())

    def table(self) -> LegacyTable:
        return LegacyTable(self.get_driver())

    def alert(self) -> LegacyAlert:
        return LegacyAlert(self.get_driver())

    def frame(self) -> LegacyFrame:
        return LegacyFrame(self.get_driver())

    def switch_window(self) -> LegacySwitchWindow:
        return LegacySwitchWindow(self.get_driver())

    def upload_file(self) -> LegacyUploadFile:
        return LegacyUploadFile(self.get_driver())

    def scroll(self) -> LegacyScroll:
        return LegacyScroll(self.get_driver())

    def highlight_element(self) -> LegacyElementHighlighter:
        return LegacyElementHighlighter(self.get_driver())

    def element(self) -> LegacyElement:
        return LegacyElement(self.get_driver())

    def verify_locators(self) -> LegacyVerifyLocators:
        return LegacyVerifyLocators(self.get_driver())

