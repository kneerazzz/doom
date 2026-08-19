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
    
    def focus_workspace(self, workspace: int):
        return self.dispatch(
            f'hl.dsp.focus({{workspace = "{workspace}"}})'
        )
    
    def launch(self, application: str, workspace: int | str | None = None):
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


if __name__ == "__main__":
    controller = HyprlandController()

    controller.focus_workspace(3)
    controller.launch('kitty')
    controller.move_window("0x123456", 5)

