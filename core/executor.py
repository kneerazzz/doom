class Executor:
    def __init__(self, controller):
        self.controller = controller


    def run(self, actions):
        for action in actions:
            if action["action"] == "launch":
                self.controller.focus_workspace(action["workspace"])
                self.controller.launch(action["command"])
            elif action["action"] == "move":
                self.controller.move_window(action["workspace"], action["address"])


Executer = Executor
