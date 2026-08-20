class Executor:
    def __init__(self, controller):
        self.controller = controller


    def run(self, actions):
        for action in actions:
            if action["action"] == "launch":
                self.controller.launch(
                    action["command"],
                    workspace=action.get("workspace"),
                    window_class=action.get("class")
                )
            elif action["action"] == "move":
                self.controller.move_window(action["address"], action["workspace"])

            


Executer = Executor
