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
        'dirs': ['UnitTest', 'test'],
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


def get_switch_file(file_path: pathlib.Path, mapping: dict) -> pathlib.Path:
    filename = os.path.basename(str(file_path))
    filename_root, filename_ext = os.path.splitext(filename)

    mapping_dirs = ['.'] + mapping.get('dirs', [])
    mapping_endings = mapping.get('endings', [])

    for parent, sub_dir in iterate_parents(file_path):
        for folder in mapping_dirs:
            new_folder = parent / folder  # type: pathlib.Path
            if new_folder.is_dir():
                for ending in mapping_endings:
                    prefix = mapping.get('prefix', '')
                    new_filename = prefix + filename_root + '.' + ending
                    header_path = new_folder / sub_dir / new_filename  # type: pathlib.Path

                    if header_path.is_file():
                        return header_path
    return None


@neovim.plugin
class Neogoto:
    def __init__(self, nvim):
        self._nvim = NvimWrapper(nvim)

    @neovim.command(name='NeogotoHeader', sync=True)
    def goto_header(self):
        mapping = DEFAULT_MAPPING.get('header')
        current_path = self._nvim.current_path

        new_file = get_switch_file(current_path, mapping)
        self._nvim.goto_file(str(new_file))

    @neovim.command(name='NeogotoSource', sync=True)
    def goto_source(self):
        mapping = DEFAULT_MAPPING.get('source')
        current_path = self._nvim.current_path

        new_file = get_switch_file(current_path, mapping)
        self._nvim.goto_file(str(new_file))

    @neovim.command(name='NeogotoTest', sync=True)
    def goto_test(self):
        mapping = DEFAULT_MAPPING.get('test')
        current_path = self._nvim.current_path

        new_file = get_switch_file(current_path, mapping)
        self._nvim.goto_file(str(new_file))
