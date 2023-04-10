from abc import ABC, abstractmethod
from typing import Mapping
from ..types import HierarchyMapping


Metadata = Mapping[str, str]


class Toolchain(ABC):
    """
    Represents an existing toolchain.
    """
    def __init__(self, metadata: Metadata = None):
        """
        Initializes the `Toolchain` instance.

        :param metadata: The metadata of the toolchain
        """
        self._metadata = HierarchyMapping(metadata)

    @property
    def metadata(self) -> HierarchyMapping:
        """
        Returns the metadata of the toolchain

        :return: The metadata of the toolchain
        """
        return self._metadata.copy()

    @staticmethod
    @abstractmethod
    def create(metadata: Metadata) -> 'Toolchain':
        """
        Create an instance of the toolchain using the given metadata.

        :param metadata: The toolchain's metadata
        :return: The created instance.
        """
        pass
