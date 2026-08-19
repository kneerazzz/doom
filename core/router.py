import subprocess
import sys
from pathlib import Path
from executor import Executor
from project import load_project
from stats.diff import StateDiff
from stats.hyprland_state import HyprlandState
from stats.project_state import ProjectState

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = PROJECT_ROOT / "projects"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skills.hyprland.controller import HyprlandController



def show_help():
    print()
    print("DOOM - Local Linux Automation")
    print()
    print("Usage:")
    print("    doom <command>")
    print()
    print("Commands:")
    print("    start <project>      Start a project environment")
    print("    plan  <project>      Show actions needed for a project")
    print("    stop                 Stop a project environment")
    print("    save                 Save current session")
    print("    restore              Restore previous session")
    print("    status               Show current desktop state")
    print("    run                  Execute an approved action")
    print("    learn                Create a new automation")
    print()


def _load_project_or_error(project_name: str):
    project = load_project(project_name)

    if project is None:
        print(f"Project: `{project_name}` does not exist.")
        return None

    if "windows" not in project and "terminals" not in project:
        print("Project file needs at least one of: `windows`, `terminals`.")
        return None

    return project


def start_project(project_name: str):
    project = _load_project_or_error(project_name)
    if project is None:
        return 1

    controller = HyprlandController()
    try:
        initial_active_window = HyprlandState().active_window()
    except Exception:
        initial_active_window = None

    clients = _read_normal_clients()
    if clients is None:
        return 1

    desired = ProjectState(project)
    current = {"clients": clients}
    actions = StateDiff(current, desired).calculate()

    print()
    print(f"Starting DOOM project: `{project['name']}`")

    _print_plan(project["name"], actions)

    if not actions:
        return 0

    try:
        Executor(controller).run(actions)
    except Exception as error:
        print(f"Could not execute plan: {error}")
        return 1
    finally:
        if initial_active_window and isinstance(initial_active_window, dict) and "address" in initial_active_window:
            try:
                controller.focus_window(initial_active_window["address"])
            except Exception:
                pass

    return 0



def show_status():
    clients = _read_normal_clients()
    if clients is None:
        return 1

    grouped = {}

    for client in clients:
        workspace = client["workspace"]["id"]
        grouped.setdefault(workspace, []).append(client)

    print()
    print("Current Hyprland State")
    print()

    if not grouped:
        print("No normal windows found.")
        return 0

    for workspace, workspace_clients in sorted(grouped.items()):
        print(f"Workspace {workspace}:")

        for client in workspace_clients:
            window_class = client.get("class", "unknown")
            title = client.get("title", "")
            cwd = client.get("cwd")

            details = window_class
            if title:
                details = f"{details} - {title}"
            if cwd:
                details = f"{details} ({cwd})"

            print(f"    {details}")

        print()

    return 0


def _print_plan(project_name: str, actions: list[dict]):
    print()
    print(f"Plan for {project_name}")
    print()

    if not actions:
        print("No actions needed.")
        return

    launch_actions = [action for action in actions if action["action"] == "launch"]
    move_actions = [action for action in actions if action["action"] == "move"]

    if launch_actions:
        print("Launch:")
        for action in launch_actions:
            label = f"{action['type']}:{action['name']}"
            print(
                f"    {label} -> {action['command']} "
                f"on workspace {action['workspace']}"
            )
        print()

    if move_actions:
        print("Move:")
        for action in move_actions:
            label = f"{action['type']}:{action['name']}"
            print(f"    {label} -> workspace {action['workspace']}")
        print()


def plan_project(project_name: str):
    project = _load_project_or_error(project_name)
    if project is None:
        return 1

    clients = _read_normal_clients()
    if clients is None:
        return 1

    current = {"clients": clients}
    desired = ProjectState(project)
    actions = StateDiff(current, desired).calculate()
    _print_plan(project["name"], actions)
    return 0


def _read_normal_clients():
    try:
        return HyprlandState().normal_clients()
    except FileNotFoundError:
        print("Could not read Hyprland state: `hyprctl` was not found.")
        return None
    except subprocess.CalledProcessError as error:
        message = (
            error.stderr.strip()
            if error.stderr
            else f"`hyprctl -j {error.cmd[-1]}` failed with exit code {error.returncode}."
        )
        print(f"Could not read Hyprland state: {message}")
        return None
    except Exception as error:
        print(f"Could not read Hyprland state: {error}")
        return None


def route(command: str, argument: str | None = None):
    if command == "start":
        if argument is None:
            print("Usage: doom start <project>")
            return 1
        return start_project(argument)
    elif command == "plan":
        if argument is None:
            print("Usage: doom plan <project>")
            return 1
        return plan_project(argument)
    elif command == "status":
        if argument is not None:
            print("Usage: doom status")
            return 1
        return show_status()
    elif command == "help":
        show_help()
        return 0
    print(f"Unknown command: '{command}'")
    return 1
