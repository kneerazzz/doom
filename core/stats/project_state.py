class ProjectState:
    def __init__(self, project):
        self.project = project
    
    def windows(self):
        return self.project.get("windows", {})
