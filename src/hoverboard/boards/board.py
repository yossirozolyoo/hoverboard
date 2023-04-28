class Board:
    """
    Represents a programmable board.
    """
    def __init__(self, name: str):
        """
        Initialize a `Board` instance.

        :param name: The name of the board
        """
        self._name = name

    @property
    def name(self) -> str:
        """
        The name of the board
        """
        return self._name
