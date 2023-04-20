from . import toolchain as t
from .installation_database import DefaultInstallationDatabase
from ..tools import register as register_tool
from ..types import HierarchyMapping
from typing import Callable

LoadToolchain = Callable[[HierarchyMapping], 't.Toolchain']

toolchains = {}
dbs = [DefaultInstallationDatabase]


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


def install(path: str, metadata: HierarchyMapping):
    """
    Install a toolchain from path. If `path` is a directory, the toolchain is installed as is. If `path` is a
    compressed file, it is decompressed into the `InstallationDatabase` storage.

    :param path: The path to the tool
    :param metadata: The toolchain's metadata. Must contain its name.
    """
    DefaultInstallationDatabase.install(path, metadata)


def get(name: str, load: LoadToolchain = None, register_tools: bool = True) -> 't.Toolchain':
    """
    Get a registered toolchain. Raises `KeyError` if the toolchain wasn't registered before.

    If `load` is supplied, then the toolchain is searched in known `InstallationDatabase`s.

    :param name: The name of the toolchain
    :param load: A function that receives the toolchain's metadata and returns the toolchain object from it.
    :param register_tools: If a toolchain is loaded from disk, whether to register its tools
    :return: The found Toolchain instance.
    """
    if name in toolchains:
        return toolchains[name]

    if load is not None:
        for installation_database in dbs:
            if name in installation_database.installed:
                toolchain = installation_database.installed[name]
                register(toolchain, register_tools)
                return toolchain

    raise KeyError(f"Couldn't find a registered toolchain named {repr(name)}")
