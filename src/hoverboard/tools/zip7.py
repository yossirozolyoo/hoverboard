import os
from .tool import Tool
from typing import Sequence, Union
from .errors import ToolRuntimeError
from ..types import HierarchyMapping


class Zip7(Tool):
    """
    Wraps the 7zr binary.
    """
    __metadata__ = {
        'name': '7-Zip'
    }

    def __init__(self, path: str = None, download_link: str = None, metadata: HierarchyMapping = None):
        """
        Initializes the `Zip7` instance. Finds the binary on the disk, and can possibly download it if `download_link`
        is supplied.

        :param path: The local path of 7zr.
        :param download_link: The download link for the 7zr to use if no version was found in the system path.
        :param metadata: Additional metadata to add to the tool's metadata
        """
        super().__init__(path=path, metadata=metadata)
        self.search_path.add_system_path('7zr.exe')

        if download_link is not None:
            self.search_path.add_web_path(download_link)

    def compress(self, output_archive: str, files: Union[Sequence[str], str], compress_type='7z'):
        """
        Compress files using 7-Zip.

        :param output_archive: The output archive path
        :param files: The files to add to the archive
        :param compress_type: The type of compression to use
        """
        if isinstance(files, str):
            files = (files, )

        results = self.run([
            'a',
            '-y',
            f'-t{compress_type}',
            output_archive,
            *files])

        if results.returncode != 0:
            if os.path.isfile(output_archive):
                os.unlink(output_archive)

            raise ToolRuntimeError(f'Creating archive failed with output: {repr(results.stderr)}')

    def extract(self, archive: str, output_dir: str, compression_type: str = None):
        """
        Extract an archive using 7-Zip.

        :param archive: The archive to extract
        :param output_dir: The directory to extract to
        :param compression_type: The type of the compressions of the archive
        """
        arguments = [
            'e',
            '-y',
            f'-o{output_dir}',
        ]

        if compression_type is not None:
            arguments.append(f'-t{compression_type}')

        arguments.append(archive)

        results = self.run(arguments)
        if results.returncode != 0:
            raise ToolRuntimeError(f'Extracting archive failed with output: {repr(results.stderr)}')
