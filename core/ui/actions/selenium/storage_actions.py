import json
from typing import Any, Dict, List, Optional
from core.ui.actions.selenium.base_action import BaseAction


class WebStorageArea:
    """
    Helper class encapsulating operations for either localStorage or sessionStorage.
    """

    def __init__(self, driver, storage_type: str, logger):
        self.driver = driver
        self.storage_type = storage_type  # 'localStorage' or 'sessionStorage'
        self.logger = logger

    def get(self, key: str) -> Optional[str]:
        """
        Retrieves a raw string item from storage.
        """
        script = f"return window.{self.storage_type}.getItem(arguments[0]);"
        return self.driver.execute_script(script, key)

    def get_json(self, key: str) -> Optional[Any]:
        """
        Retrieves and parses a JSON item from storage.
        """
        raw = self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception as e:
            self.logger.warning(f"Could not parse storage key '{key}' as JSON: {e}")
            return raw

    def set(self, key: str, value: Any) -> "WebStorageArea":
        """
        Sets a key-value pair. If value is a dict or list, it is automatically serialized to JSON.
        """
        if isinstance(value, (dict, list)):
            val_str = json.dumps(value)
        else:
            val_str = str(value)
        
        script = f"window.{self.storage_type}.setItem(arguments[0], arguments[1]);"
        self.driver.execute_script(script, key, val_str)
        return self

    def remove(self, key: str) -> "WebStorageArea":
        """
        Removes a specific item from storage.
        """
        script = f"window.{self.storage_type}.removeItem(arguments[0]);"
        self.driver.execute_script(script, key)
        return self

    def clear(self) -> "WebStorageArea":
        """
        Clears all items in this storage area.
        """
        script = f"window.{self.storage_type}.clear();"
        self.driver.execute_script(script)
        return self

    def has(self, key: str) -> bool:
        """
        Checks if a key exists in storage.
        """
        return self.get(key) is not None

    def length(self) -> int:
        """
        Returns the number of stored keys.
        """
        script = f"return window.{self.storage_type}.length;"
        return int(self.driver.execute_script(script) or 0)

    def all(self) -> Dict[str, str]:
        """
        Returns all key-value pairs from this storage area.
        """
        script = f"""
            var items = {{}};
            for (var i = 0; i < window.{self.storage_type}.length; i++) {{
                var k = window.{self.storage_type}.key(i);
                items[k] = window.{self.storage_type}.getItem(k);
            }}
            return items;
        """
        return self.driver.execute_script(script) or {}


class StorageActions(BaseAction):
    """
    Manages browser HTML5 Web Storage (localStorage and sessionStorage).
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.local = WebStorageArea(driver, "localStorage", self.logger)
        self.session = WebStorageArea(driver, "sessionStorage", self.logger)

    def clear_all(self) -> "StorageActions":
        """
        Clears both localStorage and sessionStorage in one call.

        Returns:
            StorageActions: Self for fluent chaining.
        """
        self.logger.info("Clearing both localStorage and sessionStorage.")
        self.local.clear()
        self.session.clear()
        return self

