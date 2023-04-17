from . import toolchain as t
from ..tools import register as register_tool


toolchains = {}


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


def get(name: str) -> 't.Toolchain':
    """
    Get a registered toolchain. Raises `KeyError` if the toolchain wasn't registered before.

    :param name: The name of the toolchain
    :return: The found Toolchain instance.
    """
    return toolchains[name]
