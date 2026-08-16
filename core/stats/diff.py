from pathlib import Path


class StateDiff:

    def __init__(self, current, desired):
        self.current = current
        self.desired = desired
    
    def find_window(self, config, used_clients):
        for client in self.current["clients"]:
            client_id = client.get("address") or id(client)
            if client_id in used_clients:
                continue

            if self.window_matches(client, config):
                return client
            
        return None

    def window_matches(self, client, config):
        client_class = client.get("class", "").lower()
        expected_class = config.get("class", "").lower()

        if client_class != expected_class:
            return False

        expected_title = config.get("title")
        if expected_title and client.get("title") != expected_title:
            return False

        expected_directory = config.get("directory")
        if expected_directory:
            actual_directory = client.get("cwd")
            if actual_directory is None:
                return False

            expected_path = Path(expected_directory).expanduser().resolve()
            actual_path = Path(actual_directory).expanduser().resolve()
            if actual_path != expected_path:
                return False

        return True
    

    def calculate(self):
        actions = []
        used_clients = set()

        for config in self.desired.targets():
            name = config["name"]
            workspace = config["workspace"]

            client = self.find_window(config, used_clients)

            if client is None:
                actions.append({
                    "action": "launch",
                    "name": name,
                    "type": config["type"],
                    "command": config["command"],
                    "workspace": workspace
                })
                continue

            used_clients.add(client.get("address") or id(client))
            
            current_workspace = client["workspace"]["id"]

            if current_workspace != workspace:
                actions.append({
                    "action": "move",
                    "name": name,
                    "type": config["type"],
                    "address": client["address"],
                    "workspace": workspace
                })
    

        return actions
    
    def terminal_matches(self, client, config):
        return self.window_matches(client, config)
    
