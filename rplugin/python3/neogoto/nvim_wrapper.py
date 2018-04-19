import pathlib

import neovim


class NvimWrapper:
    def __init__(self, nvim: neovim.Nvim):
        self._nvim = nvim

    @property
    def current_path(self) -> pathlib.Path:
        file_path = self._nvim.call('expand', '%:p')
        return pathlib.Path(file_path)

    @property
    def current_pos(self) -> str:
        file_path = self.current_path
        lnum, col = self._nvim.call('getcurpos')[1:3]
        return "{}:{}:{}".format(file_path, lnum, col)

    def set_var(self, name, value):
        self._nvim.vars[name] = value

    def get_var(self, name):
        return self._nvim.vars.get(name, None)

    def goto_file(self, file_path: pathlib.Path):
        if file_path:
            file_path_str = str(file_path)
            if file_path_str != self._nvim.call('expand', '%:p'):
                self._nvim.command("normal! m`")
                self._nvim.command('e {}'.format(file_path_str))
        else:
            self.print_message("Unknown path: {}".format(file_path))

    def print_message(self, msg: str):
        self._nvim.command('echo \'{}\''.format(msg))

    def echom(self, msg: str):
        self._nvim.command('echom \"{}\"'.format(msg))
