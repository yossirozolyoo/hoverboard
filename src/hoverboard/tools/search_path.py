import os
from abc import ABC, abstractmethod
from typing import Union, Sequence, List
from ..stores import BinaryStore, WebStore


FileNames = Union[str, Sequence[str]]


class SearchPathEntry(ABC):
    """
    Represents a search path entry.
    """
    @abstractmethod
    def find(self) -> Union[str, None]:
        """
        Finds the element.

        :return: The found path if found, `None` if not found.
        """
        pass


class DirectoryEntry(SearchPathEntry):
    """
    Represents a directory in the search path entry.
    """
    def __init__(self, directory_path: str, name: FileNames):
        """
        Initialize the `DirectoryEntry` instance

        :param directory_path: The path of the directory
        :param name: If `str` is given, the name of the file to find. If sequence of `str` is give, multiple names to
            find, ordered by the search order.
        """
        self._path = directory_path
        if isinstance(name, str):
            self._names = (name,)
        else:
            self._names = tuple(name)

    def __repr__(self) -> str:
        """
        Returns a string representation of the search path entry.

        :return: The string representation of the search path entry.
        """
        if len(self._names) == 1:
            return f'Directory({self._path}, name={repr(self._names[0])})'
        else:
            return f'Directory({self._path}, names={self._names})'

    def find(self) -> Union[str, None]:
        """
        Find the file inside the given directory.

        :return: The found path. `None` if not found.
        """
        for name in self._names:
            file_path = os.path.join(self._path, name)
            if os.path.isfile(file_path):
                return file_path


class WebEntry(SearchPathEntry):
    """
    Represents a web path in the search path entry.
    """
    def __init__(self, url: str, name: str = None, store: BinaryStore = None):
        """
        Initialize the `DirectoryEntry` instance

        :param url: The url to download
        :param name: The name to use for the file. `None` for name extraction from the URL
        :param store: The store to download the file to. `None` for temporary store
        """
        self._url = url
        self._name = name
        self._store = store

    def __repr__(self) -> str:
        """
        Returns a string representation of the search path entry.

        :return: The string representation of the search path entry.
        """
        if self._name is None:
            return f'Web({self._url})'
        else:
            return f'Web({self._url}, name={self._name})'

    def find(self) -> Union[str, None]:
        """
        Find the file inside the given directory.

        :return: The found path. `None` if not found.
        """
        return WebStore.get(self._url, self._name, self._store)


class SearchPath:
    """
    Represents a tool search path
    """
    def __init__(self, default_file_name: Union[str, FileNames] = None):
        """
        Initializes a `SearchPath` instance.

        :param default_file_name: The default file name to give to each entry in the search path.
        """
        self._entries: List[SearchPathEntry] = []
        self._default_file_name = default_file_name

    def __repr__(self) -> str:
        """
        Returns a string representation of the search path

        :return: The string representation of the search path
        """
        return repr(self._entries)

    @property
    def default_file_name(self) -> Union[None, FileNames]:
        """
        Returns the default file name used when adding a directory to the search path.

        :return: The default file name used when adding a directory to the search path.
        """
        return self._default_file_name

    @default_file_name.setter
    def default_file_name(self, value: Union[None, FileNames]):
        """
        Sets the default file name used when adding a directory to the search path.

        :param value: The value to set
        """
        self._default_file_name = value

    def find(self) -> Union[str, None]:
        """
        Finds the file path in the search path.

        :return: The file path if found, `None` if not
        """
        for entry in self._entries:
            result = entry.find()
            if result is not None:
                return result

    def add_directory(self, path: str, file_name: FileNames = None):
        """
        Adds a directory entry to the search path.

        :param path: The path of the directory to add
        :param file_name: If `str` is given, the name of the file to find. If sequence of `str` is given, multiple names
            to find, ordered by the search order. If `None`, `default_search_path` is used.
        """
        if file_name is None:
            if self._default_file_name is None:
                raise ValueError('file_name cannot be None when no default file name is supplied.')

            file_name = self._default_file_name

        self._entries.append(DirectoryEntry(path, file_name))

    def add_store(self, store_name: str, file_name: FileNames = None):
        """
        Adds a store search path entry to the search path.

        :param store_name: The name of the store to add
        :param file_name: If `str` is given, the name of the file to find. If sequence of `str` is given, multiple names
            to find, ordered by the search order. If `None`, `default_search_path` is used.
        """
        try:
            store = BinaryStore.get(store_name)
        except KeyError:
            # No store exists with given name.
            return

        self.add_directory(store.path, file_name)

    def add_system_path(self, file_name: FileNames = None):
        """
        Adds the system path to the search path.

        :param file_name: If `str` is given, the name of the file to find. If sequence of `str` is given, multiple names
            to find, ordered by the search order. If `None`, `default_search_path` is used.
        """
        for directory in os.get_exec_path():
            self.add_directory(directory, file_name)

    def add_web_path(self, url: str, name: str = None, store: BinaryStore = None):
        """
        Adds a web path to the search path.

        :param url: The url to download
        :param name: The name to use for the file. None for name extraction from the URL.
        :param store: The store to download the file to. `None` for temporary store
        """
        self._entries.append(WebEntry(url, name, store))
