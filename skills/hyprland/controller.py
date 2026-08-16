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
    
    def launch(self, application: str):
        return subprocess.Popen(
            application,
            shell=True
            #f'hl.dsp.exec_cmd("{application}")'
        )
    def move_window(self, address: str, workspace: int):
        return self.dispatch(
            f'hl.dsp.movetoworkspacesilent({{workspace = "{workspace}", window = "{address}"}})'
        )

if __name__ == "__main__":
    controller = HyprlandController()

    controller.workspace(3)
    controller.launch('kitty')
    controller.move_window(5, '')
