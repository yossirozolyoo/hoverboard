import os
import subprocess
from typing import Sequence
from ..stores import BinaryStore, WebStore
from .search_path import SearchPath


class Tool:
    """
    Represents a wrapper for an executable. The executable is searched based on the directories found in
    `__search_path__`. The name of the executable is in `__tool_file_name__`, or overriden by the `file_name` argument
    in `__init__`.
    """
    def __init__(self, search_path: SearchPath):
        """
        Initializes the `Tool` instance.

        :param search_path: The search path to use when locating the tool.
        """
        self._path = search_path.find()
        if self._path is None:
            raise FileNotFoundError(f"Couldn't find tool in search path {repr(search_path)}")

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
