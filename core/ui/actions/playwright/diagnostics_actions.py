import allure
from typing import List, Dict, Any
from core.ui.actions.playwright.base_action import BaseAction

class DiagnosticsActions(BaseAction):
    """
    Playwright-native component for browser console errors, page errors, and diagnostics.
    """

    def __init__(self, driver_or_page: Any):
        super().__init__(driver_or_page)
        self._console_logs: List[Dict[str, str]] = []
        self._page_errors: List[str] = []
        self._attach_listeners()

    def _attach_listeners(self):
        try:
            self.page.on("console", lambda msg: self._console_logs.append({
                "type": msg.type,
                "text": msg.text,
                "location": str(msg.location)
            }))
            self.page.on("pageerror", lambda err: self._page_errors.append(str(err)))
        except Exception:
            pass

    @allure.step("Getting browser console logs")
    def get_console_logs(self) -> List[Dict[str, str]]:
        return list(self._console_logs)

    @allure.step("Getting browser errors")
    def get_errors(self) -> List[Dict[str, str]]:
        return [entry for entry in self._console_logs if entry["type"] in ("error", "warning")]

    @allure.step("Asserting no severe console errors")
    def assert_no_severe_errors(self, allowed_patterns: List[str] = None):
        allowed = allowed_patterns or []
        errors = self.get_errors() + [{"type": "pageerror", "text": e} for e in self._page_errors]
        severe = []
        for err in errors:
            msg = err.get("text", "")
            if any(p.lower() in msg.lower() for p in allowed):
                continue
            if err.get("type") in ("error", "pageerror"):
                severe.append(msg)

        assert not severe, f"Found {len(severe)} severe console errors: {severe}"

