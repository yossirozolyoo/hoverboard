import os
import tempfile
import uuid
import zipfile
from typing import IO


_stores = {}


class BinaryStore:
    """
    Represents a binary store on the disk.
    """
    def __init__(self, name: str = None, path: str = None):
        """
        Initializes the `BinaryStore` instance.

        :param name: The name to give to the store. `None` for no registration
        :param path: The path the store is in. `None` for a temporary path.
            of the store.
        """
        if path is None:
            path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
            os.mkdir(path)
        else:
            if not os.path.isdir(path):
                raise FileNotFoundError(path)

        self._path = path
        self._name = name

        if name is not None:
            if name in _stores:
                raise KeyError(f'The name {repr(name)} is already taken')

            _stores[name] = self

    @property
    def path(self) -> str:
        """
        Returns the path on disk of the binary store.

        :return: The path on disk of the binary store.
        """
        return self._path

    def open(self, file: str, *args, **kwargs) -> IO:
        """
        Open a file in the store using `open` and return a stream.

        :param file: The relative path inside the store
        :param args: Positional arguments to pass to `open`
        :param kwargs: Keyword arguments to pass to `open`
        :return: The opened stream.
        """
        return open(os.path.join(self._path, file), *args, **kwargs)

    def store(self, name: str = None) -> 'BinaryStore':
        """
        Create an inner store to this store.

        :param name: The inner store name. If `None`, a random GUID is generated as its name and the store won't be
            registered.
        :return: The created store
        """
        if self._name is not None and name is not None:
            store_name = f'{self._name}:{name}'
            if store_name in _stores:
                return _stores[store_name]
        else:
            store_name = None

        store_path = None
        if name is None:
            succeeded = False
            while not succeeded:
                store_path = os.path.join(self._path, str(uuid.uuid4()))
                if not os.path.exists(store_path):
                    os.mkdir(store_path)
                    succeeded = True

        else:
            store_path = os.path.join(self._path, name)
            if not os.path.isdir(store_path):
                os.mkdir(store_path)

        if self._name is None:
            return BinaryStore(path=store_path)
        else:
            return BinaryStore(name=store_name, path=store_path)

    @staticmethod
    def get(name: str) -> 'BinaryStore':
        """
        Get a previously opened store.

        :param name: The name of the opened store.
        :return: The store.
        """
        return _stores[name]

    def get_path(self, name: str) -> str:
        """
        Returns a full path for a file in the store.

        :param name: The relative path of the file in the store
        :return: The path on disk.
        """
        return os.path.join(self._path, name)

    def isfile(self, file_name: str) -> bool:
        """
        Checks if a given name exists, and is a file.

        :param file_name: The file name
        :return: Whether it exists or not.
        """
        return os.path.isfile(os.path.join(self._path, file_name))

    def unzip(self, archive_path: str, **kwargs):
        """
        Unzip a zip file to the store.

        :param archive_path: The path to the archive.
        :param kwargs: Additional keyword arguments to pass to `zipfile.ZipFile.extractall`
        """
        archive = zipfile.ZipFile(archive_path)
        archive.extractall(self._path, **kwargs)

    def decompress(self, compressed: str, compression: str = None, **kwargs):
        """
        Decompress a compressed file using a known compression.

        :param compressed: The path to the compressed file
        :param compression: The compression used in the file
        :param kwargs: Additional keyword arguments to the decompression method.
        """
        if compression is None:
            if os.path.extsep not in compressed:
                raise ValueError(f'Compression not specified')

            _, compression = compressed.rsplit(os.extsep, 1)

        if compression == 'zip':
            self.unzip(compressed, **kwargs)
        else:
            raise ValueError(f'Unsupported compression {repr(compression)}')
