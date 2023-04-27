import pytest
import importlib
import os
from hoverboard.stores import BinaryStore, WebStore
from hoverboard.toolchains import install, uninstall, get_toolchain, store as store_module
from hoverboard.boards.avrdude import avrdude as avrdude_module

AVRDUDE_URL = 'https://github.com/mariusgreuel/avrdude/releases/download/v7.1-windows/' \
              'avrdude-v7.1-windows-windows-x64.zip'


def _install_and_uninstall(path: str):
    """
    Test an installation and uninstallation of a package

    :param path: The package path to pass to `install`
    """
    install(path, {
        'name': 'avrdude',
        'version': '7.1',
        'tools': {
            'avrdude': {
                'path': 'avrdude.exe',
                'version': '7.1'
            }
        }
    })

    # Check that the toolchain is available right after installation
    avrdude = get_toolchain('avrdude')
    assert isinstance(avrdude, avrdude_module.AVRDudeToolchain), 'Failed to determine toolchain type correctly'

    # Check that the toolchain is available on fresh start (reloading `store` and `avrdude` is good enough)
    importlib.reload(store_module)
    importlib.reload(avrdude_module)
    avrdude = get_toolchain('avrdude')
    assert isinstance(avrdude, avrdude_module.AVRDudeToolchain), 'Failed to determine toolchain type correctly'

    # Check uninstallation
    uninstall('avrdude')
    if os.path.isdir(path):
        assert os.path.exists(avrdude.metadata['path']), 'Uninstalled local package and directory deleted'
    else:
        assert not os.path.exists(avrdude.metadata['path']), 'Uninstalled package and directory still exists'

    with pytest.raises(KeyError):
        get_toolchain('avrdude')


def test_toolchain_install_web():
    """
    Test the function `install` for a web path
    """
    _install_and_uninstall(AVRDUDE_URL)


def test_toolchain_install_local_archive():
    """
    Test the function `install` for a local archive path
    """
    # Local
    local_path = WebStore.get(AVRDUDE_URL)
    _install_and_uninstall(local_path)
    os.unlink(local_path)


def test_toolchain_install_local_directory():
    """
    Test the function `install` for a local archive path
    """
    local_path = WebStore.decompress(AVRDUDE_URL)
    assert local_path is not None, 'Failed to decompress avrdude'

    _install_and_uninstall(local_path.path)
    assert os.path.exists(local_path.path), 'Local toolchain was deleted after uninstall'


def test_toolchain_install_bad_path():
    """
    Test the function `install` for a local archive path
    """
    bad_store = BinaryStore()
    bad_archive = bad_store.get_path('abc.zip')
    assert not os.path.exists(bad_archive)

    with pytest.raises(ValueError):
        install(bad_archive, {
            'name': 'abc',
            'version': '1.0',
            'tools': []
        })
