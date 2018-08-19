from pathlib import Path

import pytest

from neogoto import Neogoto


THIS_DIR = Path(__file__).parent
PLUGIN_DIR = THIS_DIR.parent.parent.parent.parent / 'plugin'
TEST_FILE_STRUCTURE_ROOT = THIS_DIR / 'root'


@pytest.fixture
def plugin(nvim_instance) -> Neogoto:
    yield Neogoto(nvim_instance)


def test_switch_split_right(nvim_instance, plugin):
    nvim_instance.command('edit {}'.format(TEST_FILE_STRUCTURE_ROOT / 'lib1' / 'Include' / 'lib1file.h'))

    plugin.goto_switch_split_right(args=None)

    assert len(nvim_instance.windows) == 2
    assert nvim_instance.current.line == 'lib1/Source/lib1file.cpp'

    nvim_instance.command('wincmd h')
    assert nvim_instance.current.line == 'lib1/Include/lib1file.h'


def test_switch_right(nvim_instance, plugin):
    nvim_instance.command('wincmd v')
    nvim_instance.command('edit {}'.format(TEST_FILE_STRUCTURE_ROOT / 'lib1' / 'Include' / 'lib1file.h'))

    plugin.goto_switch_right(args=None)

    assert len(nvim_instance.windows) == 2
    assert nvim_instance.current.line == 'lib1/Source/lib1file.cpp'

    nvim_instance.command('wincmd h')
    assert nvim_instance.current.line == 'lib1/Include/lib1file.h'


def test_switch_split_left(nvim_instance, plugin):
    nvim_instance.command('edit {}'.format(TEST_FILE_STRUCTURE_ROOT / 'lib1' / 'Include' / 'lib1file.h'))

    plugin.goto_switch_split_left(args=None)

    assert len(nvim_instance.windows) == 2
    assert nvim_instance.current.line == 'lib1/Source/lib1file.cpp'

    nvim_instance.command('wincmd l')
    assert nvim_instance.current.line == 'lib1/Include/lib1file.h'


def test_switch_left(nvim_instance, plugin):
    nvim_instance.command('wincmd v | wincmd l')
    nvim_instance.command('edit {}'.format(TEST_FILE_STRUCTURE_ROOT / 'lib1' / 'Include' / 'lib1file.h'))

    plugin.goto_switch_left(args=None)

    assert len(nvim_instance.windows) == 2
    assert nvim_instance.current.line == 'lib1/Source/lib1file.cpp'

    nvim_instance.command('wincmd l')
    assert nvim_instance.current.line == 'lib1/Include/lib1file.h'



