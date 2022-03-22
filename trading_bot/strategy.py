import logging

from abc import ABC, abstractmethod
from pandas import DataFrame

logger = logging.getLogger(__name__)


class Strategy(ABC):
    """Abstract Strategy class. Define required interface for all
    strategies. Strategy need to folow CEST. C - conditions,
    E - entry, S - stop loss, T - target profit.

    Attributes:
        df(DataFrame): Exchange data.
        entry(float): Order entry value.
        stop_loss(float): Order stop loss value.
        target(float): Order target profit value.

    Methods:
    start():
        Starts strategy setup.
    _is_condition_met():
        Check if strategy conditions are met.
    _set_entry():
        Sets entry value in strategy setup.
    _set_stop_loss():
        Sets stop loss value in strategy setup.
    _set_target():
        Sets target profit value in strategy setup.
    get_entry():
        Gets entry value in strategy setup.
    get_stop_loss():
        Gets stop loss value in strategy setup.
    get_target():
        Gets target profit value in strategy setup.
    is_setup_ready():
        Check if strategy setup is ready. We have our CEST.
    """

    def __init__(self, df: DataFrame) -> None:
        """Params:
            df(DataFrame): Exchange data"""

        self.df = df
        self.entry = None
        self.stop_loss = None
        self.target = None

    def start(self) -> None:
        """Starts strategy setup."""
        if (self._is_condition_met()):
            self._set_entry()
            self._set_stop_loss()
            self._set_target()

    @abstractmethod
    def _is_condition_met(self) -> bool:
        """Check if strategy conditions are met.
        
        Returns:
            bool: True if conditions met. False otherwise.
        """
        pass

    @abstractmethod
    def _set_entry(self) -> None:
        """Sets entry value in strategy setup."""
        pass

    @abstractmethod
    def _set_stop_loss(self) -> None:
        """Sets stop loss value in strategy setup."""
        pass

    @abstractmethod
    def _set_target(self) -> None:
        """Sets target profit value in strategy setup."""
        pass

    def get_entry(self) -> float:
        """Gets entry value in strategy setup.

        Returns:
            float: Entry value.
        """
        return self.entry

    def get_stop_loss(self) -> float:
        """Gets stop loss value in strategy setup.

        Returns:
            float: Stop loss value.
        """
        return self.stop_loss

    def get_target(self) -> float:
        """Gets target profit value in strategy setup.

        Returns:
            float: Target profit value.
        """
        return self.target

    def is_setup_ready(self) -> bool:
        """Check if strategy setup is ready. We have our CEST.

        Returns:
            bool: True if setup ready. False otherwise.
        """
        if (self.entry != None and
            self.stop_loss != None and
            self.target != None):
            return True
        
        return False

