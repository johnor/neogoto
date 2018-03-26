import os
import pathlib

import pytest
import neovim
from neogoto import NvimWrapper, iterate_parents, get_switch_file


@pytest.fixture
def nvim_wrapper(nvim_instance) -> NvimWrapper:
    yield NvimWrapper(nvim_instance)


@pytest.fixture
def basic_fs(fs):
    fs.create_file("/data/repo_root/Include/lib1/lib1_file1.h")
    fs.create_file("/data/repo_root/Source/lib1/lib1_file1.cpp")
    fs.create_file("/data/repo_root/Include/lib1/lib1_file2.hpp")
    fs.create_file("/data/repo_root/Source/lib1/lib1_file2.cpp")

    fs.create_file("/data/repo_root/Source/lib2/lib2_file1.h")
    fs.create_file("/data/repo_root/Source/lib2/lib2_file1.cpp")

    fs.create_file("/data/repo_root/UnitTest/lib2/Testlib2_file1.cpp")


@pytest.fixture
def header_mapping(basic_fs):
    mapping = {
        'dirs': ['Include', 'Impl'],
        'endings': ['h', 'hpp'],
    }
    return mapping


@pytest.fixture
def unittest_mapping(basic_fs):
    mapping = {
        'dirs': ['UnitTest'],
        'endings': ['cpp'],
        'prefix': 'Test',
    }
    return mapping


def test_filesystem(basic_fs):
    assert os.path.isfile("/data/repo_root/Include/lib1/lib1_file1.h")


def test_set_mapping(nvim_wrapper):
    nvim_wrapper._nvim.command('let g:neoswitch_mapping = {"to_source": [["Include", "Source"]] }')

    expected_mapping = {
        'to_source': [
            ['Include', 'Source']
        ]
    }
    actual_mapping = nvim_wrapper.get_var("neoswitch_mapping")
    assert expected_mapping == actual_mapping


def test_iterate_parents():
    path = pathlib.Path("/folder1/folder2/folder3/file.cpp")
    result = list(iterate_parents(path))

    assert [(pathlib.Path("/folder1/folder2/folder3"), pathlib.Path(".")),
            (pathlib.Path("/folder1/folder2/"), pathlib.Path(".")),
            (pathlib.Path("/folder1/"), pathlib.Path("folder3")),
            (pathlib.Path("/"), pathlib.Path("folder2/folder3")),
            ] == result


def test_get_switch_file_same_dir(header_mapping):
    header = get_switch_file(pathlib.Path("/data/repo_root/Source/lib2/lib2_file1.cpp"), header_mapping)
    assert pathlib.Path("/data/repo_root/Source/lib2/lib2_file1.h") == header


def test_get_switch_file_with_different_dir(header_mapping):
    header = get_switch_file(pathlib.Path("/data/repo_root/Source/lib1/lib1_file1.cpp"), header_mapping)
    assert pathlib.Path("/data/repo_root/Include/lib1/lib1_file1.h") == header

    header = get_switch_file(pathlib.Path("/data/repo_root/Source/lib1/lib1_file2.cpp"), header_mapping)
    assert pathlib.Path("/data/repo_root/Include/lib1/lib1_file2.hpp") == header


def test_get_switch_file_unittest(unittest_mapping):
    header = get_switch_file(pathlib.Path("/data/repo_root/Source/lib2/lib2_file1.cpp"), unittest_mapping)
    assert pathlib.Path("/data/repo_root/UnitTest/lib2/Testlib2_file1.cpp") == header

