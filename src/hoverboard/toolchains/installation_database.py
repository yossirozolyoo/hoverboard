import os
import json
from .typing import Metadata
from ..types import HierarchyMapping
from ..stores import WebStore, BinaryStore, default
from .errors import ToolchainDecompressionFailed
from typing import Mapping, Any, Callable
from . import toolchain

INSTALLATIONS_FILE = 'installations.json'


class InstallationDatabase:
    """
    Represents an installation database for toolchains.
    """

    def __init__(self, store: BinaryStore):
        """
        Initialize an `InstallationDatabase` instance.

        :param store: The binary store to store installations on.
        """
        self._store = store
        self._installed_db = None
        self._types = {}

    def _load_db(self):
        """
        Load the DB from disk if not loaded already.
        """
        if self._installed_db is None:
            if self._store.isfile('installations.json'):
                with self._store.open(INSTALLATIONS_FILE) as file_obj:
                    deserialized = json.load(file_obj)
                    self._installed_db = {
                        metadata['name']: HierarchyMapping.deserialize(metadata) for metadata in deserialized
                    }

            else:
                self._installed_db = {}

    def _dump_db(self):
        """
        Dump the database to the disk.
        """
        with self._store.open(INSTALLATIONS_FILE, 'w') as file_obj:
            serialized = list(metadata.serialize() for metadata in self._installed_db.values())
            json.dump(serialized, file_obj)

    @property
    def installed(self) -> Mapping[str, Metadata]:
        """
        Return the installed toolchains.

        :return: A mapping between the installed package name to the package matadata, including a 'path' key with the
            package location.
        """
        self._load_db()
        return {
            key: value.copy() for key, value in self._installed_db.items()
        }

    def install(self, path: str, metadata: Mapping[str, Any], **kwargs):
        """
        Install a toolchain from path. If `path` is a directory, the toolchain is installed as is. If `path` is a
        compressed file (local or in the web), it is decompressed into the `InstallationDatabase` storage.

        :param path: The path to the tool. If url, `path` must begin with either 'http://' or 'https://'
        :param metadata: The toolchain's metadata. Must contain its name.
        :param compression: The compression to use if decompressing the file
        :param kwargs: Additional keyword arguments to pass to the function `decompress`.
        """
        if 'name' not in metadata:
            raise ValueError('Missing "name" from metadata')

        metadata = HierarchyMapping(metadata)

        # Handle path
        if path.startswith('http://') or path.startswith('https://'):
            store = WebStore.decompress(path, store=self._store.store(), **kwargs)
            if store is None:
                raise ToolchainDecompressionFailed(f'Failed to download and decompress {repr(path)}')

            path = store.path

        if os.path.isfile(path):
            store = self._store.store()
            store.decompress(path, **kwargs)

            path = store.path

        else:
            if not os.path.isdir(path):
                raise ValueError(f'Invalid path {repr(path)}')

        metadata['path'] = path
        self._load_db()
        self._installed_db[metadata['name']] = metadata

        self._dump_db()

    def uninstall(self, name: str):
        """
        Uninstall a previously installed toolchain.

        :param name: The toolchain name
        """
        metadata = self.installed[name]
        if os.path.abspath(metadata['path']).startswith(os.path.abspath(self._store.path)):
            BinaryStore(path=metadata['path']).delete()

        del self._installed_db[name]
        self._dump_db()

    def load(self, name: str,
             types: Mapping[str, Callable[[HierarchyMapping], 'toolchain.Toolchain']]) -> 'toolchain.Toolchain':
        """
        Loads an installed toolchain

        :param name: The name of the toolchain to load
        :param types: The types that can be used to create `Toolchain` instances
        :return: The loaded toolchain
        """
        metadata = self.installed[name]

        if 'type' in metadata:
            toolchain_type_name = metadata['type']
            if toolchain_type_name not in types:
                raise KeyError(f'Unknown toolchain type {repr(toolchain_type_name)}')

            toolchain_type = types[toolchain_type_name]
        elif metadata['name'] in types:
            toolchain_type = types[metadata['name']]
        else:
            toolchain_type = toolchain.Toolchain

        return toolchain_type(metadata=metadata)


DefaultInstallationDatabase = InstallationDatabase(default.store('toolchains'))
