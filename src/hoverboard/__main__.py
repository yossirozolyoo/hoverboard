from .toolchains.store import types, DefaultInstallationDatabase
from functools import partial
import argparse
import sys


LIST_LIMITS = {
    'name': 15,
    'type': 15,
    'path': 40,
    'tools': 30
}


def _prepare_list_item(content: any, max_length: int) -> str:
    """
    Prepare an item to fit in a table cell

    :param content: The content to fit, if it isn't a `str`, it will be `repr`ed
    :param max_length: The maximum length of the representation of the item.
    :return: The `str` representation of the item, truncated if needed.
    """
    output = content if isinstance(content, str) else repr(content)
    if len(output) > max_length:
        output = output[:max_length - 3] + '...'

    return output


def _install_toolchain(toolchain_type: str, args: argparse.Namespace):
    """
    The implementation for the 'install' command, for a given toolchain

    :param toolchain_type: The type of the toolchain, as a string, to store in the metadata
    :param args: The user supplied arguments
    """
    types[toolchain_type].install(DefaultInstallationDatabase, args.uri, name=args.name)


def _list(args: argparse.Namespace):
    """
    The implementation for the 'list' command.

    :param args: The user supplied arguments
    """
    # Prepare the table
    rows = []
    for name, metadata in DefaultInstallationDatabase.installed.items():
        toolchain_type = metadata['type'] if 'type' in metadata else ''
        path = metadata['path'] if 'path' in metadata else ''
        tools = ', '.join(metadata['tools'].top_level.keys())
        rows.append((
            _prepare_list_item(name, LIST_LIMITS['name']),
            _prepare_list_item(toolchain_type, LIST_LIMITS['type']),
            _prepare_list_item(path, LIST_LIMITS['path']),
            _prepare_list_item(tools, LIST_LIMITS['tools'])
        ))

    rows.insert(0, ('Name', 'Type', 'Path', 'Tools'))
    lengths = tuple(len(max(column, key=len)) for column in zip(*rows))
    rows.insert(1, tuple('-' * column_length for column_length in lengths))

    # Print the table
    for row in rows:
        row = ' | '.join(('{: ^' + str(column_length) + '}').format(column) for column, column_length in zip(row, lengths))
        print(row)


def main():
    """
    Main entry point of hoverboard, exposes an interface to manage installed toolchains and stores
    """
    parser = argparse.ArgumentParser(description='Manage hoverboard toolchains')
    subparsers = parser.add_subparsers()

    # 'install' command
    install_subparser = subparsers.add_parser('install', help='Install a toolchain')
    install_subparsers = install_subparser.add_subparsers(title='Toolchains')

    for name in types:
        toolchain_subparser = install_subparsers.add_parser(name)
        toolchain_subparser.add_argument('uri', help='A path to the compressed toolchain, or a download link to it.')
        toolchain_subparser.add_argument('-n', '--name',
                                         help='The name to give to the toolchain. Defaults to the toolchain\'s type')
        toolchain_subparser.set_defaults(operation=partial(_install_toolchain, name))

    # 'list' command
    list_subparser = subparsers.add_parser('list', help='List installed toolchains')
    list_subparser.set_defaults(operation=_list)

    # Parse arguments
    args = parser.parse_args()
    try:
        operation = args.operation
    except AttributeError:
        parser.print_usage()
        sys.exit(-1)

    result = operation(args)
    if result is None:
        sys.exit(0)
    else:
        sys.exit(result)


if '__main__' == __name__:
    main()
