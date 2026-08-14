class SystemState:

    def __init__(self, hyprland):
        self.hyprland = hyprland


    def snapshot(self):
        return {
            "clients": self.hyprland.clients(),
            "workspaces": self.hyprland.workspaces(),
            "active_window": self.hyprland.active_window(),
            "active_workspace": self.hyprland.active_workspace()
        }
