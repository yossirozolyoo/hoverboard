from . import toolchain as t
from .installation_database import DefaultInstallationDatabase
from ..tools import register as register_tool
from ..types import HierarchyMapping
from typing import Callable, Type, Mapping, Any

LoadToolchain = Callable[[HierarchyMapping], 't.Toolchain']
ToolchainImplementation = Type['t.Toolchain']

toolchains = {}
dbs = [DefaultInstallationDatabase]
types = {}


def register_implementation(name: str, cls: ToolchainImplementation):
    """
    Register an implementation under a given name.

    :param name: The name of the implementation
    :param cls: The implementation
    """
    if name in types:
        raise KeyError(f'Implementation {repr(name)} already exists')

    types[name] = cls


def implementation(name: str) -> Callable[[ToolchainImplementation], ToolchainImplementation]:
    """
    Returns a decorator that registers an implementation with a given name.

    :param name: The name of the implementation
    :return: A decorator that should wrap the implementation
    """
    def hook(cls: ToolchainImplementation) -> ToolchainImplementation:
        f"""
        Wraps an implementation of a toolchain to register it under the name {repr(name)}.

        :param cls: The implementation of the toolchain
        :return: The same implementation of the toolchain
        """
        register_implementation(name, cls)
        return cls

    return hook


def register(toolchain: 't.Toolchain', register_tools: bool = True):
    """
    Register a toolchain

    :param toolchain: The toolchain
    :param register_tools: Whether to register the toolchain tools.
    """
    toolchains[toolchain.name] = toolchain
    if register_tools:
        for tool in toolchain.values():
            register_tool(tool)


def install(path: str, metadata: Mapping[str, Any]):
    """
    Install a toolchain from path. If `path` is a directory, the toolchain is installed as is. If `path` is a
    compressed file, it is decompressed into the `InstallationDatabase` storage.

    :param path: The path to the tool
    :param metadata: The toolchain's metadata. Must contain its name.
    """
    DefaultInstallationDatabase.install(path, metadata)


def uninstall(name: str):
    """
    Uninstall a previously installed toolchain.

    :param name: The toolchain name
    """
    DefaultInstallationDatabase.uninstall(name)


def get(name: str) -> 't.Toolchain':
    """
    Get a registered toolchain. Raises `KeyError` if the toolchain wasn't registered before.

    :param name: The name of the toolchain
    :return: The found Toolchain instance.
    """
    if name in toolchains:
        return toolchains[name]

    for installation_database in dbs:
        if name in installation_database.installed:
            metadata = installation_database.installed[name]

            if 'register-tools' in metadata:
                register_tools = metadata['register-tools']
            else:
                register_tools = True

            if 'type' in metadata:
                toolchain_type_name = metadata['type']
                if toolchain_type_name not in types:
                    raise KeyError(f'Unknown toolchain type {repr(toolchain_type_name)}')

                toolchain_type = types[toolchain_type_name]
            elif metadata['name'] in types:
                toolchain_type_name = metadata['name']
                if toolchain_type_name not in types:
                    raise KeyError(f'Missing toolchain type for {repr(toolchain_type_name)}')

                toolchain_type = types[toolchain_type_name]
            else:
                toolchain_type = t.Toolchain

            toolchain = toolchain_type(metadata=metadata)
            register(toolchain, register_tools)

            return toolchain

    raise KeyError(f"Couldn't find a registered toolchain named {repr(name)}")
