from typing import Any, Dict, List, Optional
from core.ui.actions.selenium.base_action import BaseAction


class DiagnosticsActions(BaseAction):
    """
    Captures browser runtime diagnostics, JavaScript exceptions, console errors,
    and unhandled promise rejections.
    """

    def get_browser_logs(self, log_type: str = "browser") -> List[Dict[str, Any]]:
        """
        Retrieves raw browser log entries (supported on Chromium and Edge).

        Args:
            log_type (str): Type of log ('browser', 'driver', 'client'). Default 'browser'.

        Returns:
            List[Dict[str, Any]]: List of log entry dictionaries.
        """
        try:
            available_types = self.driver.log_types
            if log_type in available_types:
                return self.driver.get_log(log_type)
        except Exception as e:
            self.logger.debug(f"get_log not supported or failed on this driver: {e}")
        return []

    def get_console_errors(self) -> List[Dict[str, Any]]:
        """
        Retrieves all SEVERE or ERROR console log messages recorded during the session.

        Returns:
            List[Dict[str, Any]]: List of error logs with level, message, and timestamp.
        """
        logs = self.get_browser_logs("browser")
        errors = [entry for entry in logs if entry.get("level") in ("SEVERE", "ERROR")]
        if errors:
            self.logger.warning(f"Found {len(errors)} SEVERE/ERROR console logs.")
        return errors

    def get_console_warnings(self) -> List[Dict[str, Any]]:
        """
        Retrieves all WARNING console log messages.

        Returns:
            List[Dict[str, Any]]: List of warning logs.
        """
        logs = self.get_browser_logs("browser")
        return [entry for entry in logs if entry.get("level") == "WARNING"]

    def assert_no_severe_errors(self, allowed_patterns: Optional[List[str]] = None) -> "DiagnosticsActions":
        """
        Asserts that no SEVERE JavaScript errors occurred in the browser console.
        Optionally ignores known or benign error substrings.

        Args:
            allowed_patterns (Optional[List[str]]): List of substrings to ignore (e.g. ['favicon.ico']).

        Raises:
            AssertionError: If unexpected severe errors are detected.

        Returns:
            DiagnosticsActions: Self for fluent chaining.
        """
        allowed = allowed_patterns or []
        errors = self.get_console_errors()
        filtered = []
        for err in errors:
            msg = err.get("message", "")
            if not any(pat in msg for pat in allowed):
                filtered.append(msg)

        if filtered:
            joined_errors = "\n  - ".join(filtered)
            raise AssertionError(
                f"Severe browser console errors detected ({len(filtered)} total):\n  - {joined_errors}"
            )
        return self

