from pathlib import Path


class StateDiff:

    def __init__(self, current, desired):
        self.current = current
        self.desired = desired
    
    def find_window(self, window_class):
        for client in self.current["clients"]:
            if client["class"] == window_class:
                return client
            
        return None
    

    def calculate(self):
        actions = []

        for name, config in self.desired.windows().items():

            window_class = config["class"]
            workspace = config["workspace"]

            client = self.find_window(window_class)

            if client is None:
                actions.append({
                    "action": "launch",
                    "name": name,
                    "command": config["command"],
                    "workspace": workspace
                })
                continue
            
            current_workspace = client["workspace"]["id"]

            if current_workspace != workspace:
                actions.append({
                    "action": "move",
                    "name": name,
                    "address": client["address"],
                    "workspace": workspace
                })
    

        return actions
    
    def terminal_matches(self, client, config):
        if client["class"] != config["class"]:
            return False
        
        expected_directory = Path(
            config["directory"]
        ).expanduser().resolve()

        actual_directory = client.get("cwd")
        if actual_directory is None:
            return False
        return actual_directory == expected_directory
    
