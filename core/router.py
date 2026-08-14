from pathlib import Path
from project import load_project

PROJECT_DIR = Path(__file__).resolve().parent.parent / "projects"



def show_help():
    print()
    print("DOOM - Local Linux Automation")
    print()
    print("Usage:")
    print("    doom <command>")
    print()
    print("Commands:")
    print("    start       Start a project environment")
    print("    stop        Stop a project environment")
    print("    save        Save current session")
    print("    restore     Restore previous session")
    print("    status      Show current state")
    print("    run         Execute an approved action")
    print("    learn       Create a new automation")
    print()


def start_project(project_name: str): 
    project = load_project(project_name)

    if project is None:
        print(f"Project: `{project_name}` does not exist.")
        return 1
    print()
    print(f"Starting DOOM project: `{project['name']}`")
    print()

    windows = project.get("windows")
    if windows is None:
        print("Project file is missing required `windows` section.")
        return 1

    print("Windows:")

    for name, window in windows.items():
        command = window.get("command")
        workspace = window.get("workspace")
        directory = window.get("directory")
        details = f"{command} -> workspace {workspace}"
        if directory:
            details = f"{details} ({directory})"
        print(f"    {name}: {details}")


    return 0

def route(command: str, argument: str | None = None):
    if command == "start":
        if argument is None:
            print("Usage: doom start <project>")
            return 1
        return start_project(argument)
    elif command == "help":
        show_help()
        return 0
    print(f"Unknown command: '{command}'")
    return 1



def show_status():
    hyprland = HyprlandState()
    clients = hyprland.normal_clients()
    
    grouped = {}

    for client in clients:
        workspace = client["workspace"]["id"]
        grouped.setdefault(workspace, []).append(client)

    for workspace, clients in sorted(grouped.items()):
        print(f"Workspace: {workspace}")

        for client in clients:
            print(f"    {client['class']} {client.get('title', '')} {client.get('cwd', '')}")
