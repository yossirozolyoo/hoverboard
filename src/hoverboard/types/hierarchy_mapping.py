from typing import Union, MutableMapping, Any, Iterable, Tuple, Generator, \
    Iterator
from collections import abc


OtherMapping = MutableMapping[str, Any]
KVPair = Tuple[str, Any]
Items = Iterable[KVPair]


def find_parent(obj: Any, path: str) -> Tuple[Any, str]:
    """
    Finds the parent of the object directed by path.

    :param obj: The root object
    :param path: The path under `obj`
    :return: The parent of the object directed by `path`
    """
    while '.' in path:
        member, path = path.split('.', 1)
        obj = getattr(obj, member)

    return obj, path


def get_value_at(obj: Any, path: str) -> Any:
    """
    Returns the value at the given Python object path.

    :param obj: The parent object
    :param path: The path inside `obj` to retrieve the value from.
    :return: The retrieved value.
    """
    obj, member = find_parent(obj, path)
    return getattr(obj, member)


def set_value_at(obj: Any, path: str, value: Any):
    """
    Sets the given value at the given Python object path.

    :param obj: The parent object
    :param path: The path inside `obj` to set
    :param value: The value to set
    """
    obj, member = find_parent(obj, path)
    setattr(obj, member, value)


def del_value_at(obj: Any, path: str):
    """
    Deletes the value directed by `path` under `obj`..
    :param obj: The root object.
    :param path: The path under `obj`
    """
    obj, member = find_parent(obj, path)
    delattr(obj, member)


class HierarchyMapping(abc.MutableMapping):
    """
    A mapping that supports hierarchy in keys. For example, after creating a
    `HierarchyMapping` from the following code:
    ```
    hm = HierarchyMapping({
        'outer': {
            'inner': 'hello'
        }
    })
    ```

    One can access inner elements:
    ```
    assert hm['outer.inner'] == 'hello'
    assert hm['outer.inner.__class__'] == str
    ```
    """
    def __init__(self, data: Union[OtherMapping, Items] = None):
        """
        Initialize the `HierarchyMapping` instance.

        :param data:
            The data to initialize the `HierarchyMapping` instance with.
        """
        self._data = {}
        super().__init__()

        if data is not None:
            if isinstance(data, abc.Mapping):
                data = data.items()

            for key, value in data:
                self[key] = value

    def __repr__(self) -> str:
        """
        Returns a string representation of the HierarchyMapping

        :return: A string representation of the HierarchyMapping
        """
        return repr(self._data)

    def _keys(self) -> Generator[str, None, None]:
        """
        Return a generator that yields the HierarchyMapping's keys.

        :return: The generator
        """

        for member, value in self._data.items():
            if isinstance(value, HierarchyMapping):
                for key in value._keys():
                    yield f'{member}.{key}'
            else:
                yield member

    def __iter__(self) -> Iterator[str]:
        """
        Iterates over the keys of HierarchyMapping

        :return: An iterable that yields the mapping keys
        """
        return iter(self._keys())

    def __len__(self) -> int:
        """
        Returns the number of entries under this HierarchyMapping.

        :return: The number of entries under this HierarchyMapping.
        """
        length = 0
        for member, value in self._data.items():
            if isinstance(value, HierarchyMapping):
                length += len(value)
            else:
                length += 1

        return length

    def __contains__(self, item: str) -> bool:
        """
        Returns whether a given key is in the mapping

        :param item: The item path
        :return: Whether it exists or not
        """
        if '.' in item:
            member_name, inner_path = item.split('.', 1)
            try:
                member = self._data[member_name]
            except KeyError:
                return False

            return \
                isinstance(member, HierarchyMapping) and \
                inner_path in member

        else:
            return item in self._data

    def __getitem__(self, key: str) -> Any:
        """
        Returns the value at given hierarchy.

        :param key: The path inside the mapping to retrieve
        :return: The found value
        """
        try:
            return get_value_at(self, key.replace('-', '_'))
        except AttributeError as err:
            raise KeyError(str(err)) from err

    def __setitem__(self, key: str, value: Any):
        """
        Sets the value at given hierarchy.

        :param key: The path inside the mapping to set
        :param value: The value to set
        """
        key = key.replace('-', '_')
        try:
            set_value_at(self, key, value)
        except AttributeError as err:
            # Create the path if it does not exist
            parent = self
            while '.' in key:
                member_name, key = key.split('.', 1)
                try:
                    member = parent._data[member_name]
                except KeyError:
                    member = HierarchyMapping()
                    parent._data[member_name] = member
                    parent = member
                    continue

                if not isinstance(member, HierarchyMapping):
                    # Creating a path under objects other than
                    # HierarchyMapping isn't supported
                    raise KeyError('Creating a path under objects other '
                                   'than HierarchyMapping isn\'t '
                                   'supported') from err

                parent = member

            setattr(parent, key, value)

    def __delitem__(self, key: str):
        """
        Deletes the value at given hierarchy.

        :param key: The path inside the mapping to delete
        """
        try:
            del_value_at(self, key.replace('-', '_'))
        except AttributeError as err:
            raise KeyError(str(err)) from err

    def __getattr__(self, item: str) -> Any:
        """
        Returns the value a given mapping item.

        :param item: The item to retrieve
        :return: The found value
        """
        try:
            return self._data[item]
        except KeyError as err:
            raise AttributeError(f'Member {repr(item)} doesn\'t exists ' + \
                                 f'under {repr(self)}') from err

    def __setattr__(self, item: str, value: Any):
        """
        Sets the value of given mapping item.

        :param item: The item to set
        :param value: The value to set
        """
        if item == '_data':
            super().__setattr__(item, value)
            return

        if isinstance(value, abc.Mapping):
            value = HierarchyMapping(value)

        try:
            self._data[item] = value
        except KeyError as err:
            raise AttributeError(f'Member {repr(item)} doesn\'t exists ' + \
                                 f'under {repr(self)}') from err

    def __delattr__(self, item: str):
        """
        Deletes an attribute from the mapping.

        :param item: The attribute to delete
        """
        try:
            del self._data[item]
        except KeyError as err:
            raise AttributeError(f'Member {repr(item)} doesn\'t exists ' + \
                                 f'under {repr(self)}') from err

    def copy(self) -> 'HierarchyMapping':
        """
        Deep-copies this HierarchyMapping.

        :return: The deep copy
        """
        return HierarchyMapping(self)
