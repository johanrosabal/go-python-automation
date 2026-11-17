import allure
from typing import Any
from core.ui.actions.playwright.base_action import BaseAction

class ScriptActions(BaseAction):
    """
    Playwright-native component for JavaScript execution and Promise evaluation.
    """

    @allure.step("Executing JavaScript in page")
    def execute(self, script: str, *args) -> Any:
        """Executes JavaScript code in the browser context."""
        try:
            return self.page.evaluate(script, *args) if args else self.page.evaluate(script)
        except Exception as e:
            self._handle_exception(e, "execute_script")

    @allure.step("Evaluating JavaScript Promise in page")
    def eval_promise(self, promise_js: str, *args) -> Any:
        """Evaluates an async JavaScript Promise."""
        return self.execute(promise_js, *args)

    @allure.step("Setting attribute via JavaScript")
    def set_attribute(self, attr_name: str, value: str) -> "ScriptActions":
        """Sets an HTML attribute directly on the element via JavaScript."""
        self.get_locator().evaluate(f"(el, val) => el.setAttribute('{attr_name}', val)", value)
        return self

    @allure.step("Removing attribute via JavaScript")
    def remove_attribute(self, attr_name: str) -> "ScriptActions":
        """Removes an HTML attribute from the element via JavaScript."""
        self.get_locator().evaluate(f"(el) => el.removeAttribute('{attr_name}')")
        return self

    @allure.step("Dispatching custom DOM event")
    def dispatch_event(self, event_name: str) -> "ScriptActions":
        """Dispatches an event on the element."""
        self.get_locator().dispatch_event(event_name)
        return self

