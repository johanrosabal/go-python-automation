from abc import abstractmethod
from core.ui.actions.contracts.base_action_contract import BaseActionContract

class SendKeysActionsContract(BaseActionContract):
    """
    Contract defining all standard keyboard and text operations across engines.
    """

    @abstractmethod
    def send_keys(self, *values) -> "SendKeysActionsContract":
        """Types text into the target element."""
        pass

    @abstractmethod
    def type(self, text: str, clear: bool = True) -> "SendKeysActionsContract":
        """Types text, optionally clearing existing content first."""
        pass

    @abstractmethod
    def clear(self) -> "SendKeysActionsContract":
        """Clears the value of the target element."""
        pass

