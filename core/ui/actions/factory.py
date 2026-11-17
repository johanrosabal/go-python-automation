import os
from typing import Any, Type

class ActionFactory:
    """
    Factory responsible for dynamically resolving and instantiating UI Action classes
    based on the active automation engine (Selenium or Playwright).
    """

    @staticmethod
    def detect_engine(driver_or_page: Any = None) -> str:
        """
        Detects whether the current session is running under 'playwright' or 'selenium'.
        Checks the driver instance attributes, then falls back to the ENGINE env variable.
        """
        if driver_or_page is not None:
            if getattr(driver_or_page, "is_playwright_shim", False) or hasattr(driver_or_page, "page"):
                return "playwright"
            from playwright.sync_api import Page
            if isinstance(driver_or_page, Page):
                return "playwright"

        return os.getenv("ENGINE", "selenium").lower()

    @classmethod
    def create(cls, action_name: str, driver_or_page: Any, **kwargs):
        """
        Instantiates the native action class for the given engine.
        
        Args:
            action_name: Lowercase action name (e.g. 'click', 'send_keys', 'cookies')
            driver_or_page: Active WebDriver or Playwright Page instance
        """
        engine = cls.detect_engine(driver_or_page)
        
        if engine == "playwright":
            import core.ui.actions.playwright as pw_actions
            action_map = {
                "click": pw_actions.ClickActions,
                "send_keys": pw_actions.SendKeysActions,
                "scroll": pw_actions.ScrollActions,
                "cookies": pw_actions.CookieActions,
                "storage": pw_actions.StorageActions,
                "script": pw_actions.ScriptActions,
                "diagnostics": pw_actions.DiagnosticsActions,
                "elements": pw_actions.ElementsActions,
                "dropdown": pw_actions.DropdownActions,
                "select": pw_actions.DropdownActions,
                "navigation": pw_actions.NavigationActions,
                "screenshot": pw_actions.ScreenshotActions,
                "get_text": pw_actions.GetTextActions,
                "window": pw_actions.SwitchWindowsActions,
                "frame": pw_actions.FrameActions,
                "alert": pw_actions.AlertActions,
                "radio": pw_actions.RadioActions,
                "check": pw_actions.CheckActions,
                "table": pw_actions.TableActions,
                "upload": pw_actions.UploadActions,
            }
            target_cls = action_map.get(action_name.lower())
            if target_cls:
                return target_cls(driver_or_page)

        # Fallback to Selenium native actions
        import core.ui.actions.selenium as se_actions
        action_map = {
            "click": se_actions.ClickActions,
            "send_keys": se_actions.SendKeysActions,
            "scroll": se_actions.ScrollActions,
            "cookies": se_actions.CookieActions,
            "storage": se_actions.StorageActions,
            "script": se_actions.ScriptActions,
            "diagnostics": se_actions.DiagnosticsActions,
            "elements": se_actions.ElementsActions,
            "dropdown": se_actions.DropdownActions,
            "select": se_actions.DropdownActions,
            "navigation": se_actions.NavigationActions,
            "screenshot": se_actions.ScreenshotActions,
            "window": se_actions.SwitchWindowsActions,
            "frame": se_actions.FrameActions,
            "alert": se_actions.AlertActions,
            "radio": se_actions.RadioActions,
            "check": se_actions.CheckActions,
            "table": se_actions.TableActions,
            "upload": se_actions.UploadActions,
            "get_text": se_actions.GetTextActions,
        }
        target_cls = action_map.get(action_name.lower(), se_actions.BaseAction)
        return target_cls(driver_or_page)
