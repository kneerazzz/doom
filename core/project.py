from pathlib import Path
import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent / "projects"


def load_project(project_name: str): 
    project_file = PROJECT_DIR / f"{project_name}.yaml"

    if not project_file.exists():
        return None
    
    with project_file.open("r") as file:
        project = yaml.safe_load(file)
    
    
    return project
