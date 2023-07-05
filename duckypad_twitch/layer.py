import abc
import logging

logger = logging.getLogger(__name__)


class ILayer(abc.ABC):
    """Abstract Base Class for Layers"""

    def __init__(self, duckypad):
        self.logger = logger.getChild(self.__class__.__name__)
        self._duckypad = duckypad

    @abc.abstractmethod
    def identifier():
        """a unique identifier for each class"""

    @property
    @abc.abstractmethod
    def state(self):
        """retrieve/update the states of a class"""

    @abc.abstractmethod
    def reset_states():
        """reset states for a class"""
