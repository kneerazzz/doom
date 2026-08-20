import json
import subprocess

try:
    from .process import get_process_cwd
except ImportError:
    from process import get_process_cwd

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

    def normal_clients(self):
        clients = self.clients()

        result = []

        for client in clients:
            workspace_id = client["workspace"]["id"]
            if workspace_id < 0:
                continue
            client["cwd"] = get_process_cwd(client["pid"])
            result.append(client)

        return result


    def scratchpad_clients(self):
        clients = self.clients()

        result = []

        for client in clients:
            workspace_id = client["workspace"]["id"]
            name = client["workspace"].get("name", "")
            if workspace_id < 0 or name.startswith("special:"):
                client["cwd"] = get_process_cwd(client["pid"])
                result.append(client)

        return result




    


if __name__ == "__main__":
    state = HyprlandState()

    print("states:\n")
    print(state.clients())

    print("workspaces: \n")
    print(state.workspaces())
