from ..types import ObjectFactory
from .toolchain import Toolchain, Metadata
from typing import Type


factory = ObjectFactory()


def register(name: str, toolchain: Type[Toolchain]):
    """
    Register a toolchain

    :param name: The name of the toolchain
    :param toolchain: The toolchain
    """
    factory.register(name, toolchain.create)


def new(toolchain: str, metadata: Metadata) -> Toolchain:
    """
    Create a toolchain instance

    :param toolchain: The toolchain name to create instance of it
    :param metadata: The metadata used to create the toolchain instance
    :return: The created Toolchain instance.
    """
    return factory.create(toolchain, metadata)
