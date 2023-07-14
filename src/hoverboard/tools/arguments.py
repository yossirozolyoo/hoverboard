from collections import OrderedDict
from itertools import chain
from typing import Callable, Sequence, List, MutableMapping, Any, Union, Iterable
from abc import ABC, abstractmethod

RawArgumentList = Sequence[str]


class Argument(ABC):
    """
    Represents an argument in the argument list
    """

    @abstractmethod
    def compile(self) -> RawArgumentList:
        """
        Compile the argument into a sequence of `str`s, to be added to the raw arguments list.
        """
        raise NotImplementedError

    @abstractmethod
    def copy(self) -> 'Argument':
        """
        Returns a deep-copy of the argument
        """
        raise NotImplementedError

    def named_arguments(self) -> Iterable['NamedArgument']:
        """
        Returns the named arguments this argument holds. This has a default implementation that returns an empty tuple.
        """
        return tuple()


class ConstantArgument(Argument):
    """
    Represents a constant argument in the argument list.
    """

    def __init__(self, value: Any, on_compile: Union[Callable[[Any], str], str] = None):
        """
        Initialize a `NamedArgument` instance.

        :param value: The value of the argument
        :param on_compile: Used to convert the value of the argument to a `str`. If `str`, a format string used to
            convert the value to a string. If `None`, `str` is used. Otherwise, `compile` is assumed to be a function
            that converts the value of the argument to its raw value.
        """
        self._value = value
        if on_compile is None:
            self._compile = str
        elif isinstance(on_compile, str):
            self._compile = on_compile.format
        elif callable(on_compile):
            self._compile = on_compile
        else:
            raise ValueError(f'Invalid value passed to `compile`: {repr(on_compile)}')

    @property
    def value(self) -> Any:
        """
        Return the value of the argument
        """
        return self._value

    def compile(self) -> RawArgumentList:
        """
        Compile the argument into a sequence of `str`s, to be added to the raw arguments list.
        """
        return (self._compile(self._value),)

    def copy(self) -> 'ConstantArgument':
        """
        Returns a deep-copy of the argument
        """
        return ConstantArgument(self._value, self._compile)


class NamedArgument(Argument):
    """
    Represents a named argument in the argument list. The name of the argument is used when setting values from
    `ArgumentList`
    """

    def __init__(self, name: str, on_compile: Union[Callable[[Any], str], str] = None):
        """
        Initialize a `NamedArgument` instance.

        :param name: The name of the argument
        :param on_compile: Used to convert the value of the argument to a `str`. If `str`, a format string used to
            convert the value to a string. If `None`, `str` is used. Otherwise, `compile` is assumed to be a function
            that converts the value of the argument to its raw value.
        """
        self._name = name
        if on_compile is None:
            self._compile = str
        elif isinstance(on_compile, str):
            self._compile = on_compile.format
        elif callable(on_compile):
            self._compile = on_compile
        else:
            raise ValueError(f'Invalid value passed to `compile`: {repr(on_compile)}')

        self._value = None

    @property
    def name(self) -> str:
        """
        Returns the name of the argument.
        """
        return self._name

    def compile(self) -> RawArgumentList:
        """
        Compile the argument into a sequence of `str`s, to be added to the raw arguments list.
        """
        if self._value is None:
            raise KeyError(f'No value was set to {repr(self._name)}')

        return self._value

    def named_arguments(self) -> Iterable['NamedArgument']:
        """
        Returns the named arguments this argument holds. This has a default implementation that returns an empty tuple.
        """
        return (self,)

    @property
    def value(self) -> Any:
        """
        Returns the value of the named argument.
        """
        if self._value is None:
            raise KeyError('No value was set to the named argument.')

        return self._value[0]

    @value.setter
    def value(self, value: Any):
        """
        Sets the value of the named argument.

        :param value: The value to set
        """
        self._value = (value,)

    def clear(self):
        """
        Clears the value of the named argument.
        """
        self._value = None

    def copy(self) -> 'NamedArgument':
        """
        Returns a deep-copy of the argument
        """
        output = NamedArgument(self._name, self._compile)
        output._value = self._value

        return output


class TagArgument(Argument):
    """
    Represents a tag argument in the argument list.
    """

    def __init__(self, tag: str, *args: Union[Argument, str], separate_tag_and_args: bool = True,
                 required: bool = False, named_default: bool = False):
        """
        Initialize a `TagArgument` instance.

        :param tag: The tag argument to put prior to its extra arguments.
        :param args: The arguments to add after the tag. In each argument, if `str` is given it is used as a name when
            composing a `NamedArgument`.
        :param separate_tag_and_args: Whether to separate between the tag and its arguments.
        :param required: Whether the tag is required. If `True`, `KeyError` is raised when one of the named arguments
            isn't satisfied. If `False`, the tag is omitted from the argument list.
        :param named_default: Whether a string argument defaults to a `NamedArgument` or `ConstantArgument`
        """
        self._arguments = [ConstantArgument(tag)]
        for arg in args:
            if isinstance(arg, Argument):
                self._arguments.append(arg)
                continue

            if named_default:
                if not isinstance(arg, str):
                    raise TypeError(f'Invalid type of arg {repr(arg)}')

                self._arguments.append(NamedArgument(arg))
            else:
                self._arguments.append(ConstantArgument(arg))

        self._separate_tag_and_args = separate_tag_and_args
        self._required = required
        self._named = None

    @property
    def tag(self) -> str:
        """
        Returns the tag of this `TagArgument`.
        """
        tag_argument = self._arguments[0]
        assert isinstance(tag_argument, ConstantArgument)

        return tag_argument.value

    def compile(self) -> RawArgumentList:
        """
        Compile the argument into a sequence of `str`s, to be added to the raw arguments list.
        """
        try:
            return tuple(chain(*tuple(argument.compile() for argument in self._arguments)))
        except KeyError as err:
            if self._required:
                raise KeyError('Failed to resolve all named arguments in the tag.') from err
            else:
                return tuple()

    def named_arguments(self) -> Iterable['NamedArgument']:
        """
        Returns the named arguments this argument holds. This has a default implementation that returns an empty tuple.
        """
        # cached_property is introduced only in python 3.8, we need to cache locally to support 3.6
        if self._named is None:
            self._named = tuple(chain(*tuple(argument.named_arguments() for argument in self._arguments[1:])))

        return self._named

    def copy(self) -> 'TagArgument':
        """
        Returns a deep-copy of the argument
        """
        return TagArgument(self.tag, *self._arguments[1:], separate_tag_and_args=self._separate_tag_and_args,
                           required=self._required)


class ArgumentList:
    """
    Represents a template for an argument list, which can be edited using names for different elements in the template.

    Getting and setting a `NamedArgument` value is done using the `__getitem__` and `__setitem__` methods.
    """

    def __init__(self):
        """
        Initialize the `ArgumentList`.
        """
        self._arguments: List[Argument] = []
        self._namespace: MutableMapping[str, NamedArgument] = OrderedDict()

    def __getitem__(self, key: str) -> Any:
        """
        Returns the value of the named argument named `key`

        :param key: The name of the named argument to retrieve its value
        :return: The value of the named argument
        """
        return self._namespace[key].value

    def __setitem__(self, key: str, value: Any):
        """
        Sets the value of the named argument named `key`

        :param key: The name of the named argument to retrieve its value
        :param value: The value to set
        """
        self._namespace[key].value = value

    def add_argument(self, argument: Argument):
        """
        Adds an argument to the argument list.

        :param argument: The argument to add
        """
        if not isinstance(argument, Argument):
            raise TypeError(f'Invalid argument {repr(argument)}')

        self._arguments.append(argument)
        self._namespace.update((arg.name, arg) for arg in argument.named_arguments())

    def add_tag(self, tag: str, *args: Union[Argument, str], separate_tag_and_args: bool = True,
                required: bool = False, named_default: bool = False):
        """
        Add a `TagArgument`.

        :param tag: The tag argument to put prior to its extra arguments.
        :param args: The arguments to add after the tag. In each argument, if `str` is given it is used as a name when
            composing a `NamedArgument`.
        :param separate_tag_and_args: Whether to separate between the tag and its arguments.
        :param required: Whether the tag is required. If `True`, `KeyError` is raised when one of the named arguments
            isn't satisfied. If `False`, the tag is omitted from the argument list.
        :param named_default: Whether a string argument defaults to a `NamedArgument` or `ConstantArgument`
        """
        self.add_argument(TagArgument(tag, *args, separate_tag_and_args=separate_tag_and_args, required=required,
                                      named_default=named_default))

    def clear(self):
        """
        Clears the value of all the named arguments in the argument list.
        """
        for argument in self._namespace.values():
            argument.clear()

    def compile(self) -> RawArgumentList:
        """
        Compile the arguments into a sequence of `str`

        :return: The sequence of `str` represents the argument list
        """
        output = []
        for argument in self._arguments:
            output.extend(argument.compile())

        return output

    def copy(self) -> 'ArgumentList':
        """
        Copies the argument list a deep copy (up to the arguments themselves).
        """
        output = ArgumentList()
        for argument in self._arguments:
            output.add_argument(argument.copy())

        return output
