from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar('T', bound='BaseActionContract')

class BaseActionContract(ABC):
    """
    Abstract contract defining the common lifecycle and configuration
    for any UI Action implementation (Selenium, Playwright, Appium, etc.).
    """

    @abstractmethod
    def at(self: T, timeout_seconds: int) -> T:
        """Sets a temporary timeout for the immediate next action."""
        pass

    @abstractmethod
    def set_locator(self: T, locator: Any) -> T:
        """Binds a locator (tuple or string) to the action instance."""
        pass

