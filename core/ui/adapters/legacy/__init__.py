"""
Legacy Adapter Package.
Houses backward-compatibility classes and interpreters for migrating older Page Objects.
"""
from core.ui.adapters.legacy.legacy_base_page import BasePage as LegacyBasePage
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

__all__ = [
    "LegacyBasePage",
    "LegacyClick",
    "LegacySendKeys",
    "LegacyGetText",
    "LegacyNavigation",
    "LegacyScreenshot",
    "LegacyDropdown",
    "LegacyCheckbox",
    "LegacyRadio",
    "LegacyTable",
    "LegacyAlert",
    "LegacyFrame",
    "LegacySwitchWindow",
    "LegacyUploadFile",
    "LegacyElement",
    "LegacyScroll",
    "LegacyElementHighlighter",
    "LegacyVerifyLocators",
]

