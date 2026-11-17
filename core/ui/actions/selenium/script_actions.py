from typing import Any, List, Optional
from core.ui.actions.selenium.base_action import BaseAction


class ScriptActions(BaseAction):
    """
    Provides clean, expressive JavaScript execution and asynchronous promise handling
    within the browser context.
    """

    def execute(self, script: str, *args: Any) -> Any:
        """
        Executes synchronous JavaScript in the context of the currently selected frame or window.

        Args:
            script (str): The JavaScript snippet to execute.
            *args (Any): Arguments accessible via 'arguments[0]', 'arguments[1]', etc.

        Returns:
            Any: The return value from the JavaScript execution.
        """
        self.logger.debug(f"Executing JavaScript: {script[:100]}... with {len(args)} args")
        return self.driver.execute_script(script, *args)

    def execute_async(self, script: str, *args: Any) -> Any:
        """
        Executes an asynchronous piece of JavaScript in the context of the currently selected frame or window.
        The last argument in the script must be invoked as a callback to signal completion.

        Args:
            script (str): The asynchronous JavaScript snippet.
            *args (Any): Arguments passed to the script.

        Returns:
            Any: The value passed to the callback function.
        """
        self.logger.debug(f"Executing Async JavaScript: {script[:100]}... with {len(args)} args")
        return self.driver.execute_async_script(script, *args)

    def eval_promise(self, promise_script: str, timeout_seconds: int = 15) -> Any:
        """
        Evaluates a JavaScript Promise expression and awaits its resolution.

        Args:
            promise_script (str): JavaScript expression returning a Promise.
            timeout_seconds (int): Maximum time in seconds to wait for resolution.

        Returns:
            Any: The resolved Promise value.
        """
        async_wrapper = f"""
            var callback = arguments[arguments.length - 1];
            Promise.resolve({promise_script})
                .then(function(result) {{ callback({{status: 'resolved', data: result}}); }})
                .catch(function(err) {{ callback({{status: 'rejected', error: String(err)}}); }});
        """
        prev_timeout = self.driver.timeouts.script if hasattr(self.driver, "timeouts") else 15
        try:
            self.driver.set_script_timeout(timeout_seconds)
            res = self.driver.execute_async_script(async_wrapper)
            if isinstance(res, dict) and res.get("status") == "rejected":
                raise RuntimeError(f"JavaScript Promise rejected: {res.get('error')}")
            return res.get("data") if isinstance(res, dict) else res
        finally:
            self.driver.set_script_timeout(prev_timeout if isinstance(prev_timeout, (int, float)) else 15)

    def get_document_ready_state(self) -> str:
        """
        Returns document.readyState ('loading', 'interactive', 'complete').
        """
        return str(self.execute("return document.readyState;"))

    def wait_for_document_ready(self, timeout: int = 15) -> bool:
        """
        Polls until document.readyState === 'complete'.
        """
        import time
        start = time.time()
        while time.time() - start < timeout:
            if self.get_document_ready_state() == "complete":
                return True
            time.sleep(0.2)
        return False

