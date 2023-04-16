from abc import abstractmethod
from collections.abc import Mapping
from ..types import HierarchyMapping
from ..tools import Tool
from typing import Union, Iterable, Tuple, Iterator, Mapping as MappingT

Metadata = MappingT[str, str]
Other = Union[MappingT[str, Tool], Iterable[Tuple[str, Tool]]]


class Toolchain(MappingT, Mapping):
    """
    Represents a toolchain.
    """
    def __init__(self, tools: Other, metadata: Metadata = None):
        """
        Initializes the `Toolchain` instance.

        :param tools: The tools in the toolchain
        :param metadata: The metadata of the toolchain
        """
        super().__init__()
        self._tools = HierarchyMapping(tools)
        self._metadata = HierarchyMapping(metadata)

    def __iter__(self) -> Iterator[str]:
        """
        Returns the tool names under this toolchain.

        :return: The tool names under this toolchain.
        """
        return iter(self._tools)

    def __getitem__(self, key: str) -> Tool:
        """
        Get a tool by name

        :param key: The tool name
        :return: The tool
        """
        return self._tools[key]

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolchain

        :return: The number of tools in the toolchain
        """
        return len(self._tools)

    @property
    def metadata(self) -> HierarchyMapping:
        """
        Returns the metadata of the toolchain

        :return: The metadata of the toolchain
        """
        return self._metadata.copy()
