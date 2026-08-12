import json
import subprocess

class HyprlandState:
    

    def _query(self, command: str):
        result = subprocess.run(
            ["hyprctl", "-j", command],
            capture_output = True,
            text = True,
            check = True
        )
        return json.loads(result.stdout)

    def clients(self):
        return self._query("clients")

    def workspaces(self):
        return self._query("workspaces")

    def active_window(self):
        return self._query("activewindow")
    
    def active_workspace(self):
        return self._query("activeworkspace")

    


if __name__ == "__main__":
    state = HyprlandState()

    print("states:\n")
    print(state.clients())

    print("workspaces: \n")
    print(state.workspaces())