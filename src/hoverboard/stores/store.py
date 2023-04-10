import os
import tempfile
import uuid
from typing import IO


_stores = {}


class BinaryStore:
    """
    Represents a binary store on the disk.
    """
    def __init__(self, path: str = None, name: str = None):
        """
        Initializes the `BinaryStore` instance.

        :param path: The path the store is in. `None` for a temporary path.
        :param name: The name to give to the store. `None` for no registration
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

    def store(self, name: str) -> 'BinaryStore':
        """
        Create an inner store to this store.

        :param name: The inner store name
        :return: The created store
        """
        if self._name is not None:
            store_name = f'{self._name}:{name}'
            if store_name in _stores:
                return _stores[store_name]
        else:
            store_name = None

        store_path = os.path.join(self._path, name)
        if not os.path.isdir(store_path):
            os.mkdir(store_path)

        if self._name is None:
            return BinaryStore(store_path)
        else:
            return BinaryStore(store_path, store_name)

    @staticmethod
    def get(name: str) ->'BinaryStore':
        """
        Get a previously opened store.

        :param name: The name of the opened store.
        :return: The store.
        """
        return _stores[name]
