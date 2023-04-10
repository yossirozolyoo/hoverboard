from typing import Callable, Any


class ObjectFactory:
    """
    An object factory implementation.
    """
    def __init__(self):
        """
        Initialize the `ObjectFactory` instance.
        """
        self._builders = {}

    def register(self, key: str, builder: Callable):
        """
        Register a new builder under this `ObjectFactory`.
        :param key: The key that represents the builder
        :param builder: The builder that creates the object.
        """
        self._builders[key] = builder

    def create(self, key, *args, **kwargs) -> Any:
        """
        Create an object based on the given builder key.

        :param key: The key to use
        :param args: The positional arguments to pass to the builder.
        :param kwargs: The keyword arguments to pass to the builder.
        :return: The created object
        """
        builder = self._builders.get(key)
        if builder is None:
            raise ValueError(key)

        return builder(*args, **kwargs)
