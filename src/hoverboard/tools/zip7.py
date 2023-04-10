import os
from .tool import Tool
from typing import Sequence, Union
from .errors import ToolRuntimeError


class Zip7(Tool):
    __tool_file_name__ = '7zr.exe'
    __search_path__ = (
        'system-path',
        'web:https://www.7-zip.org/a/7zr.exe'
    )

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
