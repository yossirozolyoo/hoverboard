import os
import json
from ..types import HierarchyMapping
from ..stores import WebStore, BinaryStore, default
from .errors import ToolchainDecompressionFailed


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

    def _load_db(self):
        """
        Load the DB from disk if not loaded already.
        """
        if self._installed_db is None:
            if self._store.isfile('installations.json'):
                with self._store.open(INSTALLATIONS_FILE) as file_obj:
                    deserialized = json.load(file_obj)
                    self._installed_db = HierarchyMapping.deserialize(deserialized)
            else:
                self._installed_db = HierarchyMapping()

    @property
    def installed(self) -> HierarchyMapping:
        """
        Return the installed toolchains.

        :return: A mapping between the installed package name to the package matadata, including a 'path' key with the
            package location.
        """
        self._load_db()
        return self._installed_db.copy()

    def install(self, path: str, metadata: HierarchyMapping, **kwargs):
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

        # Handle path
        if path.startswith('http://') or path.startswith('https://'):
            store = WebStore.decompress(path, store=self._store.store(), **kwargs)
            if store is None:
                raise ToolchainDecompressionFailed(f'Failed to download and decompress {repr(path)}')

            path = store.path

        if os.path.isfile(path):
            store = self._store.store()
            if store.decompress(path, **kwargs) is None:
                raise ToolchainDecompressionFailed(f'Failed to decompress {repr(path)}')

            path = store.path

        else:
            if not os.path.isdir(path):
                raise ValueError(f'Invalid path {repr(path)}')

        metadata['path'] = path
        self._load_db()
        self._installed_db[metadata['name']] = metadata

        with self._store.open(INSTALLATIONS_FILE, 'w') as file_obj:
            json.dump(self._installed_db.serialize(), file_obj)


DefaultInstallationDatabase = InstallationDatabase(default.store('toolchains'))
