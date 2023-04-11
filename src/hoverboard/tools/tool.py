import os
import hashlib
import subprocess
import shutil
from urllib3 import Retry, PoolManager
from urllib3.exceptions import HTTPError
from typing import Sequence, Union
from ..stores import BinaryStore, default


http = PoolManager(retries=Retry(connect=5, read=2, redirect=5))


def _generate_search_path(user_search_path: Sequence[str]) -> Sequence[str]:
    """
    Generates a search path from a user search path.

    :param user_search_path: The user search path
    :return: The search paths
    """
    search_path = []
    for entry in user_search_path:
        if entry.startswith('stores:'):
            _, store_name = entry.split('stores:', 1)
            try:
                store = BinaryStore.get(store_name)
            except KeyError:
                # Store doesn't exist
                continue

            search_path.append(store.path)

        elif entry.startswith('web:'):
            search_path.append(entry)

        elif entry == 'system-path':
            for directory in os.get_exec_path():
                if os.path.isdir(directory):
                    search_path.append(directory)

        elif os.path.isdir(entry):
            search_path.append(entry)

    return search_path


def _handle_web(url: str, file_name: str) -> Union[str, None]:
    """
    Download a file from web or used a cached version of it.

    :param url: The url to download
    :param file_name: The file name to use for the download
    :return: Either the file path, or `None` in case of an error.
    """
    download_store_name = hashlib.sha256(url.encode()).hexdigest()
    download_store = default.store(download_store_name)

    # Check if file was downloaded previously
    if download_store.isfile(file_name):
        return download_store.get_path(file_name)

    # Download the file
    try:
        with http.request('GET', url, preload_content=False) as response:
            if response.status != 200:
                # Server couldn't return the file
                return None

            with download_store.open(file_name, 'wb') as file_obj:
                shutil.copyfileobj(response, file_obj)

    except HTTPError:
        return None

    # Download finished, return the file path
    return download_store.get_path(file_name)


def _find(search_paths: Sequence[str], file_name: str):
    """
    Find a file in a sequence of paths. Raises `FileNotFoundError` if not found.

    :param search_paths: The paths to look for the file in
    :param file_name: The file_name
    :return: The path of the found file.
    """
    for path in search_paths:
        if path.startswith('web:'):
            _, url = path.split('web:', 1)

            found_path = _handle_web(url, file_name)
            if found_path is not None:
                return found_path

        else:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                return file_path

    raise FileNotFoundError(f"Couldn't find {repr(file_name)} in search paths {repr(search_paths)}")


class Tool:
    """
    Represents a wrapper for an executable. The executable is searched based on the directories found in
    `__search_path__`. The name of the executable is in `__tool_file_name__`, or overriden by the `file_name` argument
    in `__init__`.
    """
    __search_path__ = (
        'stores:default',
        'system-path'
    )
    __tool_file_name__ = None

    def __init__(self, file_name: str = None, search_path: Union[str, Sequence[str]] = None):
        """
        Initializes the `Tool` instance.

        :param file_name: The file name to find when searching for the tool. This argument overrides the
            `__tool_file_name__` field of the `Tool` class.
        :param search_path: The search path to use when searching the file. This argument overrides the
            `__search_path__` field of the `Tool` class. If this is not None, can be either a `str` for a single search
            path, or a sequence of `str` for multiple paths.
        """
        if file_name is None:
            file_name = self.__tool_file_name__

        if file_name is None:
            raise ValueError('Missing file_name param from constructor')

        if search_path is None:
            search_path = self.__search_path__

        if isinstance(search_path, str):
            search_path = (search_path, )

        self._path = _find(_generate_search_path(search_path), file_name)

    def run(self, arguments: Sequence[str] = None, **kwargs) -> subprocess.CompletedProcess:
        """
        Runs the tools.

        :param arguments: A sequence of strings passed to the process as arguments.
        :param kwargs: Keyword arguments to pass to `subprocess.run`
        :return: The returned `subprocess.CompletedProcess`
        """
        if arguments is None:
            arguments = [self._path]
        else:
            arguments = [self._path, *arguments]

        run_arguments = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE
        }
        run_arguments.update(kwargs)

        return subprocess.run(arguments, **run_arguments)
