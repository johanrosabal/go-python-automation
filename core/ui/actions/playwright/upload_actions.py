import os
import allure
from core.ui.actions.playwright.base_action import BaseAction

class UploadActions(BaseAction):
    """
    Playwright-native component for handling file upload interactions.

    Provides a clean interface for interacting with <input type='file'> elements,
    automatically resolving absolute paths and utilizing Playwright's native set_input_files.
    """

    @allure.step("Uploading file '{file_path}'")
    def upload_file(self, file_path: str) -> "UploadActions":
        """
        Uploads a file by setting its file path on the target file input element.

        Args:
            file_path (str): The path to the file to upload.

        Returns:
            UploadActions: The current instance for method chaining.
        """
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                raise FileNotFoundError(f"File not found: {abs_path}")

            self.logger.info(f"Uploading file '{abs_path}' to element '{self._selector}'")
            self.get_locator().set_input_files(abs_path, timeout=self._current_timeout)
            return self
        except Exception as e:
            self._handle_exception(e, "upload_file")

