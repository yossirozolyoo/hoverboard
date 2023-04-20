from ..toolchain import Toolchain
from ..store import implementation
from ..typing import Metadata


@implementation('avrdude')
class AVRDudeToolchain(Toolchain):
    """
    The toolchain that contains avrdude.
    """
    def __init__(self, metadata: Metadata):
        """
        Initialize an `AVRDudeToolchain` instance.

        :param metadata: The metadata of the toolchain.
        """
        super().__init__(metadata=metadata)
