from . import store
from .typing import Metadata
from collections.abc import Mapping
from ..types import HierarchyMapping
from ..tools import Tool
from ..stores import BinaryStore
from typing import Union, Iterable, Tuple, Iterator, Mapping as MappingT


Other = Union[MappingT[str, Tool], Iterable[Tuple[str, Tool]]]


DEFAULT_METADATA = {
    'name': None,
    'version': '0.0.0.0',
    'tools': {}
}


class Toolchain(MappingT, Mapping):
    """
    Represents a toolchain.
    """
    __metadata__ = {}

    def __init__(self, metadata: Metadata = None, path: Union[str, BinaryStore] = None, register: bool = True):
        """
        Initializes the `Toolchain` instance.

        :param metadata: The metadata of the toolchain, overrides __metadata__
        """
        super().__init__()

        # Init metadata
        self._metadata = HierarchyMapping(self.__metadata__)
        if metadata is not None:
            self._metadata.update(metadata)

        if self._metadata.name is None:
            raise ValueError('Missing section "name" in metadata')

        # Init tools
        if path is None:
            if 'path' in self._metadata:
                path = self._metadata['path']
            else:
                path = None

        if isinstance(path, str):
            path = BinaryStore(name=self._metadata.name, path=path)

        # Init tools
        self._tools = HierarchyMapping()
        for tool_name, tool_metadata in self._metadata.tools.top_level.items():
            tool_metadata = tool_metadata.copy()
            if 'path' not in tool_metadata:
                raise ValueError(f"'path' not in {repr(tool_name)} metadata")

            if path is not None:
                tool_metadata['path'] = path.get_path(tool_metadata['path'])

            if 'name' not in tool_metadata:
                tool_metadata['name'] = tool_name

            if 'base-class' in tool_metadata:
                base_class = tool_metadata['base-class']
            else:
                base_class = Tool

            self._tools[tool_name] = base_class.create(tool_metadata)

        # Register
        if register:
            store.register(self)

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

    @property
    def name(self) -> str:
        """
        Returns the toolchain's name

        :return: The toolchain's name
        """
        return self._metadata['name']
