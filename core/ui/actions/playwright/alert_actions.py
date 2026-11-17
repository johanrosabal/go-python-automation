import time
import allure
from typing import Any
from core.ui.actions.playwright.base_action import BaseAction

class AlertActions(BaseAction):
    """
    Playwright-native component for handling browser dialogs (Alert, Confirm, Prompt).

    Provides parity with Selenium AlertActions by supporting accept, dismiss,
    retrieving dialog text, and typing prompt values.
    """

    def __init__(self, driver_or_page: Any):
        super().__init__(driver_or_page)
        self._dialog_messages = []
        self._prompt_text = ""
        self._action_mode = "accept"  # 'accept' or 'dismiss'
        self._setup_dialog_listener()

    def _setup_dialog_listener(self):
        """Attaches an auto-handling listener to the active Playwright page."""
        def handle_dialog(dialog):
            self._dialog_messages.append(dialog.message)
            self.logger.info(f"Captured Playwright dialog [{dialog.type}]: '{dialog.message}'")
            if self._action_mode == "dismiss":
                dialog.dismiss()
            else:
                if self._prompt_text:
                    dialog.accept(self._prompt_text)
                else:
                    dialog.accept()

        self.page.on("dialog", handle_dialog)

    def wait_presence(self, timeout: int = 10) -> "AlertActions":
        """
        Wait briefly for potential asynchronous dialog emission.

        Args:
            timeout (int): Maximum time in seconds.

        Returns:
            AlertActions: The current instance for method chaining.
        """
        time.sleep(0.3)
        return self

    @allure.step("Accepting browser alert")
    def accept(self) -> "AlertActions":
        """
        Sets dialog handler to accept next alert (Clicks OK).

        Returns:
            AlertActions: The current instance for method chaining.
        """
        self._action_mode = "accept"
        self.logger.info("Configured Playwright dialog handler to accept")
        return self

    @allure.step("Dismissing browser alert")
    def dismiss(self) -> "AlertActions":
        """
        Sets dialog handler to dismiss next alert (Clicks Cancel).

        Returns:
            AlertActions: The current instance for method chaining.
        """
        self._action_mode = "dismiss"
        self.logger.info("Configured Playwright dialog handler to dismiss")
        return self

    def get_text(self) -> str:
        """
        Retrieves the text message displayed in the most recent dialog.

        Returns:
            str: The alert message.
        """
        if self._dialog_messages:
            return self._dialog_messages[-1]
        return ""

    @allure.step("Typing '{text}' into prompt")
    def type(self, text: str) -> "AlertActions":
        """
        Sets prompt text to be entered upon dialog submission.

        Args:
            text (str): The text to enter.

        Returns:
            AlertActions: The current instance for method chaining.
        """
        self._prompt_text = text
        self.logger.info(f"Configured Playwright prompt response text: '{text}'")
        return self

