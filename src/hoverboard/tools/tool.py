import os
import subprocess
from typing import Sequence, Union
from ..stores import BinaryStore, WebStore


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

            found_path = WebStore.get(url, file_name)
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
    __manifest__ = {}

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
