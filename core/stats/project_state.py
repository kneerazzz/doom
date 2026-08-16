class ProjectState:
    def __init__(self, project):
        self.project = project
    
    def windows(self):
        return self.project.get("windows", {})

    def terminals(self):
        terminals = self.project.get("terminals", {})

        if "entries" not in terminals:
            return terminals

        defaults = terminals.get("defaults", {})
        entries = terminals.get("entries", {})
        resolved = {}

        for name, config in entries.items():
            terminal = defaults | (config or {})
            title_prefix = terminal.get("title_prefix")
            if "title" not in terminal and title_prefix:
                terminal["title"] = f"{title_prefix}:{name}"

            if "command" not in terminal:
                terminal["command"] = self._terminal_command(terminal)

            resolved[name] = terminal

        return resolved

    def targets(self):
        targets = []

        for name, config in self.windows().items():
            target = dict(config)
            target["name"] = name
            target["type"] = "window"
            targets.append(target)

        for name, config in self.terminals().items():
            target = dict(config)
            target["name"] = name
            target["type"] = "terminal"
            targets.append(target)

        return targets

    def _terminal_command(self, terminal):
        command = terminal.get("app", "kitty")
        title = terminal.get("title")
        directory = terminal.get("directory")

        if title:
            command = f"{command} --title {title}"
        if directory:
            command = f"{command} --working-directory {directory}"

        return command
