from abc import abstractmethod
from typing import Any
from core.ui.actions.contracts.base_action_contract import BaseActionContract

class ClickActionsContract(BaseActionContract):
    """
    Contract defining all standard mouse and click operations across engines.
    """

    @abstractmethod
    def click(self) -> "ClickActionsContract":
        """Performs a standard click."""
        pass

    @abstractmethod
    def double_click(self) -> "ClickActionsContract":
        """Performs a double-click."""
        pass

    @abstractmethod
    def right_click(self) -> "ClickActionsContract":
        """Performs a right (context) click."""
        pass

    @abstractmethod
    def hover(self) -> "ClickActionsContract":
        """Hovers over the target element."""
        pass

    @abstractmethod
    def drag_and_drop(self, target_locator: Any) -> "ClickActionsContract":
        """Drags the element onto the destination element."""
        pass

