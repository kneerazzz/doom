import subprocess


class HyprlandController:
    def dispatch(self, lua: str):
        result = subprocess.run(
            ["hyprctl", "dispatch", lua],
            capture_output = True,
            text = True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Hyprland dispatch failed \n:{result.stderr}"
            )
        return result.stdout.strip()
    
    def focus_workspace(self, workspace: int | str):
        return self.dispatch(
            f'hl.dsp.focus({{workspace = "{workspace}"}})'
        )

    def focus_window(self, address: str):
        address_target = address if str(address).startswith("address:") else f"address:{address}"
        return self.dispatch(
            f'hl.dsp.focus({{window = "{address_target}"}})'
        )

    
    def eval(self, lua: str):
        result = subprocess.run(
            ["hyprctl", "eval", lua],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Hyprland eval failed:\n{result.stderr}"
            )
        return result.stdout.strip()

    def set_window_rule(self, window_class: str, workspace: int | str):
        lua_code = f'hl.window_rule({{match = {{class = "(?i)^{window_class}$"}}, workspace = "{workspace} silent"}})'
        return self.eval(lua_code)


    def launch(self, application: str, workspace: int | str | None = None, window_class: str | None = None):
        if workspace is not None and window_class:
            self.set_window_rule(window_class, workspace)

        if workspace is not None:
            return self.dispatch(
                f'hl.dsp.exec_cmd("[workspace {workspace} silent] {application}")'
            )
        return subprocess.Popen(
            application,
            shell=True
        )




    def move_window(self, address: str, workspace: int):
        return self.dispatch(
            f'hl.dsp.window.move({{workspace = "{workspace}", window = "address:{address}", follow = false}})'
        )

    def close_window(self, address: str):
        address_target = address if str(address).startswith("address:") else f"address:{address}"
        return self.dispatch(
            f'hl.dsp.window.close({{window = "{address_target}"}})'
        )



if __name__ == "__main__":
    controller = HyprlandController()

    controller.focus_workspace(3)
    controller.launch('kitty')
    controller.move_window("0x123456", 5)

