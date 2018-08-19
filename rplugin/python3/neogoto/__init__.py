import pathlib
import queue

import neovim
import os

from .nvim_wrapper import NvimWrapper


DEFAULT_MAPPING = {
    'header': {
        'dirs': ['Include', 'include', 'Impl', 'impl'],
        'endings': ['hpp', 'h'],
        'switch': 'source',
    },
    'source': {
        'dirs': ['Source', 'source', 'src'],
        'endings': ['cpp', 'c'],
        'switch': 'header',
    },
    'test': {
        'dirs': [
            'UnitTest', 'UnitTests', 'test', 'UnitTest/Source',
            'UnitTests/Source'
        ],
        'endings': ['cpp', 'c'],
        'prefix': 'Test',
        'switch': 'source',
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
                    nvim: NvimWrapper=None) -> pathlib.Path:
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


# Tries to figure out the mapping for a file
# A mapping is given a higher score if a prefix is set for a mapping and matches
# This makes it possible to figure out if a file is a unit tests or not
def get_current_mapping(file_path: pathlib.Path, full_mapping: dict) -> dict:
    mapping_candidates = queue.PriorityQueue()
    filename = file_path.name
    for key, mapping in full_mapping.items():
        endings = tuple(mapping.get('endings', []))
        if filename.endswith(endings):
            score = 1
            prefix = mapping.get('prefix')
            if prefix:
                if filename.startswith(prefix):
                    score += 1
                else:
                    score -= 1
            mapping_candidates.put((-score, mapping))
    return mapping_candidates.get()[1] if not mapping_candidates.empty() else None


def get_switch_mapping(file_path: pathlib.Path, full_mapping: dict):
    current_mapping = get_current_mapping(file_path, full_mapping)
    if current_mapping:
        switch_type = current_mapping.get('switch', 'source')
        return full_mapping.get(switch_type)
    return None


@neovim.plugin
class Neogoto:
    def __init__(self, nvim):
        self._nvim = NvimWrapper(nvim)

    @neovim.command(name='NeogotoHeader', sync=True, nargs='?')
    def goto_header(self, args):
        mapping = DEFAULT_MAPPING.get('header')
        self._goto(mapping, nvim_debug=self._get_debug(args))

    @neovim.command(name='NeogotoSource', sync=True, nargs='?')
    def goto_source(self, args):
        mapping = DEFAULT_MAPPING.get('source')
        self._goto(mapping, nvim_debug=self._get_debug(args))

    @neovim.command(name='NeogotoTest', sync=True, nargs='?')
    def goto_test(self, args):
        mapping = DEFAULT_MAPPING.get('test')
        self._goto(mapping, nvim_debug=self._get_debug(args))

    @neovim.command(name='NeogotoSwitch', sync=True, nargs='?')
    def goto_switch(self, args):
        self._switch(args, precmd=None)

    @neovim.command(name='NeogotoSwitchSplitLeft', sync=True, nargs='?')
    def goto_switch_split_left(self, args):
        precmd = 'let cursplitright=&splitright | set nosplitright | vsplit | if cursplitright | set splitright | endif'
        self._switch(args, precmd)

    @neovim.command(name='NeogotoSwitchLeft', sync=True, nargs='?')
    def goto_switch_left(self, args):
        precmd = 'wincmd h'
        self._switch(args, precmd)

    @neovim.command(name='NeogotoSwitchSplitRight', sync=True, nargs='?')
    def goto_switch_split_right(self, args):
        precmd = 'let cursplitright=&splitright | set nosplitright | vsplit | wincmd l | if cursplitright | set splitright | endif'
        self._switch(args, precmd)

    @neovim.command(name='NeogotoSwitchRight', sync=True, nargs='?')
    def goto_switch_right(self, args):
        precmd = 'wincmd l'
        self._switch(args, precmd)

    def _switch(self, args, precmd=None):
        current_path = self._nvim.current_path
        mapping = get_switch_mapping(current_path, DEFAULT_MAPPING)
        if mapping:
            self._goto(mapping, precmd=precmd, nvim_debug=self._get_debug(args))
        else:
            self._nvim.print_message("Could not find mapping for current file")

    def _get_debug(self, args):
        nvim_debug = None
        if args and args[0] == 'debug':
            nvim_debug = self._nvim
        return nvim_debug

    def _goto(self, mapping, nvim_debug=None, precmd=None):
        current_path = self._nvim.current_path
        new_file = get_switch_file(current_path, mapping, nvim_debug)

        if new_file:
            if precmd:
                self._nvim.command(precmd)
            self._nvim.goto_file(new_file)
        else:
            self._nvim.print_message("Could not find a file to switch to")

