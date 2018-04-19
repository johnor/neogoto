import pathlib
import neovim
import os

from .nvim_wrapper import NvimWrapper


DEFAULT_MAPPING = {
    'header': {
        'dirs': ['Include', 'include', 'Impl', 'impl'],
        'endings': ['hpp', 'h'],
    },
    'source': {
        'dirs': ['Source', 'source', 'src'],
        'endings': ['cpp', 'c'],
    },
    'test': {
        'dirs': ['UnitTest', 'UnitTests', 'test'],
        'endings': ['cpp', 'c'],
        'prefix': 'Test',
    },
}


# path: /folder1/folder2/folder3/file.cpp
# ->
# (/folder1/folder2/folder3, .)
# (/folder1/folder2/,        .)
# (/folder1/,                folder3)
# (/,                        folder2/folder3)
def iterate_parents(path: pathlib.Path) -> tuple:
    folder = path.parent
    parts = folder.parts

    for ix in range(len(parts)):
        ix_from_end = len(parts) - ix
        beginning = parts[:ix_from_end]
        ending = parts[ix_from_end+1:]
        yield pathlib.Path(*beginning), pathlib.Path(*ending)


def _debug(nvim: NvimWrapper, msg: str):
    if nvim:
        nvim.echom(msg)


def get_switch_file(file_path: pathlib.Path,
                    mapping: dict,
                    nvim: NvimWrapper) -> pathlib.Path:
    filename = os.path.basename(str(file_path))
    filename_root, filename_ext = os.path.splitext(filename)

    mapping_dirs = ['.'] + mapping.get('dirs', [])
    mapping_endings = mapping.get('endings', [])

    _debug(nvim, "mapping_dirs {}".format(mapping_dirs))

    for parent, sub_dir in iterate_parents(file_path):
        for folder in mapping_dirs:
            new_folder = parent / folder  # type: pathlib.Path
            if new_folder.is_dir():
                _debug(nvim, "Found valid dir {}".format(new_folder))
                for ending in mapping_endings:
                    prefix = mapping.get('prefix', '')
                    new_filename = prefix + filename_root + '.' + ending
                    header_path = new_folder / sub_dir / new_filename  # type: pathlib.Path
                    _debug(nvim, "Trying file {}".format(header_path))

                    if header_path.is_file():
                        _debug(nvim, "Found matching file {}".format(header_path))
                        return header_path
    return None


@neovim.plugin
class Neogoto:
    def __init__(self, nvim):
        self._nvim = NvimWrapper(nvim)

    @neovim.command(name='NeogotoHeader', sync=True, nargs='?')
    def goto_header(self, args):
        mapping = DEFAULT_MAPPING.get('header')
        self._goto(mapping, args)

    @neovim.command(name='NeogotoSource', sync=True, nargs='?')
    def goto_source(self, args):
        mapping = DEFAULT_MAPPING.get('source')
        self._goto(mapping, args)

    @neovim.command(name='NeogotoTest', sync=True, nargs='?')
    def goto_test(self, args):
        mapping = DEFAULT_MAPPING.get('test')
        self._goto(mapping, args)

    def _goto(self, mapping, args):
        nvim_debug = None
        if args and args[0] == 'debug':
            nvim_debug = self._nvim

        current_path = self._nvim.current_path

        new_file = get_switch_file(current_path, mapping, nvim_debug)
        self._nvim.goto_file(new_file)