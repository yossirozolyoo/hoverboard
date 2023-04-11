import subprocess
from typing import Sequence, Union
from .search_path import SearchPath


class Tool:
    """
    Represents a wrapper for an executable. The executable is searched based on the directories found in
    `__search_path__`. The name of the executable is in `__tool_file_name__`, or overriden by the `file_name` argument
    in `__init__`.
    """
    def __init__(self, path: str = None, search_path: SearchPath = None):
        """
        Initializes the `Tool` instance.

        :param path: The path the tool resides in
        :param search_path: The search path to use when locating the tool.
        """
        self._path = path

        if search_path is None:
            self._search_path = SearchPath()
        else:
            self._search_path = search_path

    @property
    def search_path(self) -> SearchPath:
        """
        Returns the search path the tool is found in.

        :return: The search path the tool is found in.
        """
        return self._search_path

    @property
    def path(self) -> Union[str, None]:
        """
        Returns the found path of the tool.

        :return: The found path of the tool.
        """
        if self._path is None:
            self._path = self._search_path.find()

        return self._path

    def run(self, arguments: Sequence[str] = None, **kwargs) -> subprocess.CompletedProcess:
        """
        Runs the tools.

        :param arguments: A sequence of strings passed to the process as arguments.
        :param kwargs: Keyword arguments to pass to `subprocess.run`
        :return: The returned `subprocess.CompletedProcess`
        """
        path = self.path
        if path is None:
            raise FileNotFoundError(f"Couldn't find tool in search path {repr(self._search_path)}")

        if arguments is None:
            arguments = [path]
        else:
            arguments = [path, *arguments]

        run_arguments = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE
        }
        run_arguments.update(kwargs)

        return subprocess.run(arguments, **run_arguments)
