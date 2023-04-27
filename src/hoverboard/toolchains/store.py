from . import toolchain as t
from .installation_database import DefaultInstallationDatabase, InstallationDatabase
from ..tools import register as register_tool, Tool
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

    # Register the toolchain
    _load_tool_from_database(metadata['name'], DefaultInstallationDatabase)


def uninstall(name: str):
    """
    Uninstall a previously installed toolchain.

    :param name: The toolchain name
    """
    DefaultInstallationDatabase.uninstall(name)
    if name in toolchains:
        del toolchains[name]


def _load_tool_from_database(name: str, db: InstallationDatabase) -> 't.Toolchain':
    """
    Loads a tool from the installation database

    :param name: The name of the tool
    :param db: The installation database
    :return: The loaded tool
    """
    # Load the toolchain
    toolchain = db.load(name, types)

    # Register it
    if 'register-tools' in toolchain.metadata:
        register_tools = toolchain.metadata['register-tools']
    else:
        register_tools = True
    register(toolchain, register_tools=register_tools)

    return toolchain


def get_toolchain(name: str) -> 't.Toolchain':
    """
    Get a registered toolchain. Raises `KeyError` if the toolchain wasn't registered before.

    :param name: The name of the toolchain
    :return: The found Toolchain instance.
    """
    if name in toolchains:
        return toolchains[name]

    for installation_database in dbs:
        if name in installation_database.installed:
            return _load_tool_from_database(name, installation_database)

    raise KeyError(f"Couldn't find a registered toolchain named {repr(name)}")


def get_tool(name: str) -> Tool:
    """
    Finds a tool under one of the registered toolchains.

    :param name: The name of the tool
    :return: The found tool
    """
    # Find in loaded toolchains
    for toolchain in toolchains.values():
        for tool_name, tool in toolchain.items():
            if tool_name == name:
                return tool

    # Find in installed toolchains
    for installation_database in dbs:
        for name, metadata in installation_database.installed.items():
            if name in metadata['tools']:
                toolchain = _load_tool_from_database(name, installation_database)
                return toolchain[name]

    raise KeyError(f'Tool {repr(name)} isn\'t registered under any toolchain')
