from .toolchain import Toolchain


toolchains = {}


def register(toolchain: Toolchain):
    """
    Register a toolchain

    :param toolchain: The toolchain
    """
    toolchains[toolchain.name] = toolchain


def get(name: str) -> Toolchain:
    """
    Get a registered toolchain. Raises `KeyError` if the toolchain wasn't registered before.

    :param name: The name of the toolchain
    :return: The found Toolchain instance.
    """
    return toolchains[name]
