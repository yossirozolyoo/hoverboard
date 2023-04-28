import subprocess
from typing import Sequence, Union
from .search_path import SearchPath
from ..types import HierarchyMapping


TOOL_DEFAULT_CONFIG = HierarchyMapping({
    'name': None,
    'version': '0.0.0.0'
})


class Tool:
    """
    Represents a wrapper for an executable. The executable is searched based on the directories found in
    `__search_path__`. The name of the executable is in `__tool_file_name__`, or overriden by the `file_name` argument
    in `__init__`.
    """
    __metadata__ = {}

    def __init__(self, metadata: HierarchyMapping = None):
        """
        Initializes the `Tool` instance.

        :param metadata: metadata to override __metadata__.
        """
        self._metadata = TOOL_DEFAULT_CONFIG.copy()
        self._metadata.update(self.__metadata__)
        if metadata is not None:
            self._metadata.update(metadata)

        if self._metadata['name'] is None:
            raise ValueError('Missing "name" from tool\'s metadata')

    @property
    def name(self) -> str:
        """
        Returns the name of the tool.

        :return: The name of the tool.
        """
        return self._metadata['name']

    @property
    def metadata(self) -> HierarchyMapping:
        """
        Returns the tool's metadata

        :return: The tool's metadata
        """
        return self._metadata

    @classmethod
    def create(cls, metadata: HierarchyMapping) -> 'Tool':
        """
        Create an instance of the tool.

        :param metadata: Metadata of the tool.
        :return: The created instance.
        """
        if 'params' in metadata:
            return cls(**metadata.params, metadata=metadata)
        else:
            return cls(metadata=metadata)
