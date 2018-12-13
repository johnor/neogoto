import json
import os

import pynvim
import pytest


@pytest.fixture
def nvim_instance() -> pynvim.Nvim:
    child_argv = os.environ.get('NVIM_CHILD_ARGV')
    listen_address = os.environ.get('NVIM_LISTEN_ADDRESS')
    if child_argv is None and listen_address is None:
        child_argv = '["nvim", "-u", "NONE", "--embed"]'

    if child_argv is not None:
        nvim = pynvim.attach('child', argv=json.loads(child_argv))
    else:
        nvim = pynvim.attach('socket', path=listen_address)

    nvim.command('set noswapfile')

    yield nvim
