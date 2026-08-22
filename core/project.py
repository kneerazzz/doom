from pathlib import Path, PosixPath, PurePath
import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent / "projects"

yaml.SafeDumper.add_representer(Path, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', str(data)))
yaml.SafeDumper.add_representer(PosixPath, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', str(data)))
yaml.SafeDumper.add_representer(PurePath, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', str(data)))



def load_project(project_name: str): 
    project_file = PROJECT_DIR / f"{project_name}.yaml"

    if not project_file.exists():
        return None
    
    with project_file.open("r") as file:
        project = yaml.safe_load(file)

    return project


def save_project(project_name: str, project_data: dict):
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    project_file = PROJECT_DIR / f"{project_name}.yaml"

    with project_file.open("w") as file:
        yaml.safe_dump(project_data, file, sort_keys=False)

    return project_file

