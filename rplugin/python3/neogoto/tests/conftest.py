import json
import os

import neovim
import pytest


@pytest.fixture
def nvim_instance() -> neovim.Nvim:
    child_argv = os.environ.get('NVIM_CHILD_ARGV')
    listen_address = os.environ.get('NVIM_LISTEN_ADDRESS')
    if child_argv is None and listen_address is None:
        child_argv = '["nvim", "-u", "NONE", "--embed"]'

    if child_argv is not None:
        nvim = neovim.attach('child', argv=json.loads(child_argv))
    else:
        nvim = neovim.attach('socket', path=listen_address)

    yield nvim
