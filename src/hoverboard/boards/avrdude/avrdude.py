import os.path

from typing import Union
from ...toolchains.toolchain import Toolchain
from ...toolchains.store import implementation, install
from ...tools import LocalTool


@implementation('avrdude')
class AVRDudeToolchain(Toolchain):
    """
    The toolchain that contains avrdude.
    """
    __metadata__ = {
        'name': 'avrdude'
    }

    @staticmethod
    def _extract_version_from_path(path: str) -> Union[None, str]:
        """
        Extracts the avrdude version from the archive path.

        :param path: The archive path
        :return: The version if found, None if not.
        """
        if path.startswith('http://') or path.startswith('https://'):
            url = path
            if '?' in url:
                url, _ = url.rsplit('?', 1)

            _, filename = url.rsplit('/', 1)

        else:
            filename = os.path.basename(path)

        for element in filename.split('-'):
            if not element.startswith('v'):
                continue

            element = element[1:]

            valid_version = True
            for version_element in element.split('.'):
                if not version_element.isdigit():
                    valid_version = False

            if valid_version:
                return element

    @classmethod
    def install(cls, path: str, version: str = None):
        """
        Install the toolchain from path.

        :param path: The path to the compressed archive of the toolchain.
        :param version: The version of the toolchain. If `None`, extracted from the file name.
        """
        # Extract version from filename if needed
        if version is None:
            version = cls._extract_version_from_path(path)

        install(path, {
            'name': 'avrdude',
            'version': version,
            'tools': {
                'avrdude': {
                    'type': 'avrdude',
                    'path': 'avrdude.exe',
                    'version': version
                }
            }
        })


@AVRDudeToolchain.tool('avrdude')
class AVRDude(LocalTool):
    """
    Wraps the command "avrdude".
    """
    pass
