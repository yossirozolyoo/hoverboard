from .toolchain import Toolchain, Metadata


toolchains = {}


def register(name: str, toolchain: Toolchain):
    """
    Register a toolchain

    :param name: The name of the toolchain
    :param toolchain: The toolchain
    """
    toolchains[name] = toolchain


def get(name: str) -> Toolchain:
    """
    Get a registered toolchain. Raises `KeyError` if toolchain wasn't registered before.

    :param name: The name of the toolchain
    :return: The found Toolchain instance.
    """
    return toolchains[name]
