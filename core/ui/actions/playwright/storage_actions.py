import json
import allure
from typing import Any, Dict, Optional
from core.ui.actions.playwright.base_action import BaseAction

class StorageActions(BaseAction):
    """
    Playwright-native component for managing HTML5 localStorage & sessionStorage.
    """

    # --- localStorage ---
    @allure.step("Setting localStorage item '{key}'")
    def set_local(self, key: str, value: Any) -> "StorageActions":
        str_val = json.dumps(value) if not isinstance(value, str) else value
        self.page.evaluate(f"(key, val) => window.localStorage.setItem(key, val)", [key, str_val])
        return self

    @allure.step("Getting localStorage item '{key}'")
    def get_local(self, key: str) -> Optional[str]:
        return self.page.evaluate(f"(key) => window.localStorage.getItem(key)", key)

    def get_local_json(self, key: str) -> Optional[Any]:
        val = self.get_local(key)
        if val is None:
            return None
        try:
            return json.loads(val)
        except Exception:
            return val

    @allure.step("Removing localStorage item '{key}'")
    def remove_local(self, key: str) -> "StorageActions":
        self.page.evaluate(f"(key) => window.localStorage.removeItem(key)", key)
        return self

    @allure.step("Clearing all localStorage")
    def clear_local(self) -> "StorageActions":
        self.page.evaluate("() => window.localStorage.clear()")
        return self

    # --- sessionStorage ---
    @allure.step("Setting sessionStorage item '{key}'")
    def set_session(self, key: str, value: Any) -> "StorageActions":
        str_val = json.dumps(value) if not isinstance(value, str) else value
        self.page.evaluate(f"(key, val) => window.sessionStorage.setItem(key, val)", [key, str_val])
        return self

    @allure.step("Getting sessionStorage item '{key}'")
    def get_session(self, key: str) -> Optional[str]:
        return self.page.evaluate(f"(key) => window.sessionStorage.getItem(key)", key)

    @allure.step("Clearing all sessionStorage")
    def clear_session(self) -> "StorageActions":
        self.page.evaluate("() => window.sessionStorage.clear()")
        return self

    @allure.step("Clearing both local and session storage")
    def clear_all(self) -> "StorageActions":
        self.clear_local()
        self.clear_session()
        return self

