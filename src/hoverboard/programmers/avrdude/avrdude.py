import os.path
from collections import OrderedDict
from typing import Union
from hoverboard.toolchains.toolchain import Toolchain
from hoverboard.toolchains.store import implementation, install
from hoverboard.tools import LocalTool
from hoverboard.stores import BinaryStore


AVRDUDE_FILE_FORMATS = {
    'hex': 'i',
    'raw': 'r'
}


class AVRDudeRuntimeError(RuntimeError):
    pass


class AVRDudeTarget:
    """
    Represents a target configuration settings, used to build the AVRDude command line.
    """

    def __init__(self, avrdude: 'AVRDude', part: str, programmer: str, port: str, config_file: str = None,
                 baudrate: int = None):
        """
        Initialize the `TargetConfiguration` instance.

        :param part: The target part number.
        :param programmer: The programmer to use
        :param config_file: The config file to pass to avrdude. If not supplied, no config file will be passed to
            avrdude.
        :param baudrate: The baudrate to use while communicating with the programmer.
        """
        self._tags = OrderedDict()
        self._avrdude = avrdude
        self.programmer = programmer
        self.part = part
        self.port = port
        self.config_file = config_file
        self.baudrate = baudrate

    @property
    def config_file(self) -> Union[str, None]:
        """
        The config file passed to avrdude. `None` if not passed.
        """
        if 'config' in self._tags:
            return self._tags['config'][1]

    @config_file.setter
    def config_file(self, value: Union[str, None]):
        """
        Sets the config file passed to avrdude. `None` if not passed.
        :param value: The value to set.
        """
        if value is None:
            if 'config' in self._tags:
                del self._tags['config']
        else:
            self._tags['config'] = ('-C', value)

    @property
    def baudrate(self) -> Union[str, None]:
        """
        The baudrate passed to avrdude. `None` if not passed.
        """
        if 'baudrate' in self._tags:
            return self._tags['baudrate'][1]

    @baudrate.setter
    def baudrate(self, value: Union[str, None]):
        """
        Sets the baudrate passed to avrdude. `None` if not passed.
        :param value: The value to set.
        """
        if value is None:
            if 'baudrate' in self._tags:
                del self._tags['baudrate']
        else:
            self._tags['baudrate'] = ('-b', value)

    @property
    def programmer(self) -> str:
        """
        The programmer passed to avrdude
        """
        return self._tags['programmer'][1]

    @programmer.setter
    def programmer(self, value: str):
        """
        Sets the programmer passed to avrdude.
        :param value: The value to set.
        """
        self._tags['programmer'] = ('-c', value)

    @property
    def port(self) -> str:
        """
        The port passed to avrdude
        """
        return self._tags['port'][1]

    @port.setter
    def port(self, value: str):
        """
        Sets the port passed to avrdude.
        :param value: The value to set.
        """
        self._tags['port'] = ('-P', value)

    @property
    def part(self) -> str:
        """
        The part passed to avrdude
        """
        return self._tags['port'][1]

    @part.setter
    def part(self, value: str):
        """
        Sets the part passed to avrdude.
        :param value: The value to set.
        """
        self._tags['part'] = ('-p', value)

    def _run(self, memory_type: str, operation: str, file: str, operation_format: str = None):
        """
        Run avrdude with the set tags, performing the requested operation.

        :param memory_type: The memory type to read from
        :param operation: The operation to perform on said memory type
        :param file: The file path to perform the operation on
        :param operation_format: The format of the operation
        """
        args = self._avrdude.argument_list.copy()

        # Add the configured tags
        for tag in self._tags.values():
            args.add_tag(*tag)

        # Add the current operation
        operation = f'{memory_type}:{operation}:{file}'
        if operation_format:
            operation += f':{operation_format}'

        args.add_tag('-U', operation)

        # Run
        results = self._avrdude.run(args.compile())
        if results.returncode != 0:
            raise AVRDudeRuntimeError(results.stdout)

    def read(self, memory_type: str, path: str = None):
        """
        Read data from a device. If `output_file` is passed, the data is written to the path in it. If it is not passed,
        the data will be returned from the function as a buffer.

        :param memory_type: The memory to read. Differs between chips, e.g., 'flash', 'eeprom', 'lfuse'.
        :param path: The path of the file to read the memory to. `None` for a `bytes` object to be returned.
        :return: `None` if path is not `None`. Otherwise the read buffer as `bytes`.
        """
        if path is None:
            store = BinaryStore()
            try:
                self.read(memory_type, store.get_path('output.bin'))
                with store.open('output.bin', 'rb') as file_obj:
                    return file_obj.read()
            finally:
                store.delete()

        self._run(memory_type, 'r', path, 'r')

    def program(self, memory_type: str, data: Union[str, bytes], file_type: str = None):
        """
        Program data to a device. If `str` is passed in `data`, `data` will be interpreted as a path to read the
        content from. Otherwise, `data` will be treated as a bytes-like object and be programmed.

        If `data` is treated as a path, `file_type` will be used to determine how to program the given file. If 'hex',
        the file will be treated as an intel-hex file. If 'raw', the file will be treated as a raw binary file. If None,
        the file type will be inferred from the suffix of the file name - '.hex' for intel-hex files, any other suffix
        for raw binary file.

        :param memory_type: The memory to read. Differs between chips, e.g., 'flash', 'eeprom', 'lfuse'.
        :param data: If `str` is given, `data` will be interpreted as a path to the file to program. Otherwise, `data`
            will be treated as a bytes-like object, and its content will be programmed.
        :param file_type: The given file type when `data` is interpreted as a path. Pass `None` to infer from the
            suffix.
        """
        if not isinstance(data, str):
            store = BinaryStore()
            try:
                with store.open('data.bin', 'wb') as file_obj:
                    file_obj.write(data)
                return self.program(memory_type, file_obj.name, 'raw')
            finally:
                store.delete()

        if file_type is None:
            file_type = 'hex' if data.endswith('.hex') else 'raw'

        if file_type not in AVRDUDE_FILE_FORMATS:
            raise ValueError(f'Invalid format {repr(file_type)}')

        self._run(memory_type, 'w', data, AVRDUDE_FILE_FORMATS[file_type])


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

    def create_target(self, part: str, programmer: str, port: str, baudrate: int = None, config_file: str = None) -> AVRDudeTarget:
        """
        Initialize a `TargetConfiguration` instance.

        :param part: The target part number.
        :param programmer: The programmer to use
        :param port: The serial port to communicate with the programmer.
        :param baudrate: The baudrate to use while communicating with the programmer.
        :param config_file: The config file to pass to avrdude. If not supplied, no config file will be passed to
            avrdude.
        :return: The created `AVRDudeTarget` instance
        """
        return AVRDudeTarget(self, part, programmer, port, config_file, baudrate)

    def create_arduino_target(self, port: str, model: str = 'uno', config_file: str = None) -> AVRDudeTarget:
        """
        Creates an arduino target
        :param port: The port the arduino is connected to
        :param model: The model of the arduino
        :param config_file: The config file to pass to avrdude. If not supplied, no config file will be passed to
            avrdude.
        :return: The created `AVRDudeTarget` instance
        """
        lower_model = model.lower()
        if lower_model == 'uno':
            return self.create_target('m328p', 'arduino', port, 115200, config_file)
        else:
            raise ValueError(f'Unsupported arduino model {repr(model)}')
