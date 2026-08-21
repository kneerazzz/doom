import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

try:
    from executor import Executor
    from project import load_project, save_project as save_project_file
    from stats.diff import StateDiff
    from stats.hyprland_state import HyprlandState
    from stats.project_state import ProjectState
except ImportError:
    from core.executor import Executor
    from core.project import load_project, save_project as save_project_file
    from core.stats.diff import StateDiff
    from core.stats.hyprland_state import HyprlandState
    from core.stats.project_state import ProjectState

PROJECT_DIR = PROJECT_ROOT / "projects"


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
    scratchpad_clients = _read_scratchpad_clients()
    if clients is None:
        return 1

    grouped = {}
    for client in clients:
        workspace_id = client["workspace"]["id"]
        grouped.setdefault(workspace_id, []).append(client)

    print()
    print("Current Hyprland State")
    print()

    if not grouped and not scratchpad_clients:
        print("No windows found.")
        return 0

    if grouped:
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

    if scratchpad_clients:
        print("Special / Scratchpad Workspaces:")
        special_grouped = {}
        for client in scratchpad_clients:
            name = client["workspace"].get("name", "special")
            special_grouped.setdefault(name, []).append(client)

        for name, sp_clients in sorted(special_grouped.items()):
            print(f"  {name}:")
            for client in sp_clients:
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


def _read_scratchpad_clients():
    try:
        return HyprlandState().scratchpad_clients()
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


def save_project_session(project_name: str):
    clients = _read_normal_clients()
    if not clients:
        print("No open windows found to save.")
        return 1

    windows = {}
    terminals_entries = {}
    terminal_defaults = {}

    terminal_classes = {"kitty", "alacritty", "foot", "gnome-terminal", "wezterm"}

    for idx, client in enumerate(clients):
        w_class = client.get("class", "unknown").lower()
        title = client.get("title", "")
        cwd = client.get("cwd")
        workspace = client["workspace"]["id"]

        is_terminal = w_class in terminal_classes or "doom:" in title

        if is_terminal:
            if not terminal_defaults:
                terminal_defaults = {
                    "app": w_class or "kitty",
                    "class": w_class or "kitty",
                    "workspace": workspace,
                    "title_prefix": f"doom:{project_name}"
                }
                if cwd:
                    terminal_defaults["directory"] = cwd

            entry_name = f"term_{idx + 1}"
            if title and f"doom:{project_name}:" in title:
                entry_name = title.split(f"doom:{project_name}:")[-1]

            entry_cfg = {}
            if cwd and cwd != terminal_defaults.get("directory"):
                entry_cfg["directory"] = cwd

            terminals_entries[entry_name] = entry_cfg
        else:
            app_name = w_class
            if app_name in windows:
                app_name = f"{w_class}_{idx + 1}"

            command = w_class
            if cwd and "code" in w_class:
                command = f"code {cwd}"

            win_cfg = {
                "command": command,
                "class": w_class,
                "workspace": workspace
            }
            if cwd:
                win_cfg["directory"] = cwd

            windows[app_name] = win_cfg

    project_data = {
        "name": project_name,
        "windows": windows
    }

    if terminals_entries:
        project_data["terminals"] = {
            "defaults": terminal_defaults,
            "entries": terminals_entries
        }

    saved_path = save_project_file(project_name, project_data)
    print()
    print(f"Saved session snapshot to `{saved_path}`")
    print()
    return 0


def stop_project(project_name: str):
    project = _load_project_or_error(project_name)
    if project is None:
        return 1

    clients = _read_normal_clients() or []
    scratchpad = _read_scratchpad_clients() or []
    all_clients = clients + scratchpad

    if not all_clients:
        print("No open windows to stop.")
        return 0

    desired = ProjectState(project)
    diff = StateDiff({"clients": all_clients}, desired)

    matched_addresses = set()
    matched_names = []

    for target_config in desired.targets():
        matched_client = diff.find_window(target_config, matched_addresses)
        if matched_client and "address" in matched_client:
            address = matched_client["address"]
            matched_addresses.add(address)
            matched_names.append((target_config["name"], address, matched_client.get("class", "window")))

    if not matched_names:
        print(f"No running windows found matching project `{project_name}`.")
        return 0

    print()
    print(f"Stopping DOOM project: `{project_name}`")
    print()

    controller = HyprlandController()
    stopped_count = 0
    for name, address, w_class in matched_names:
        try:
            controller.close_window(address)
            print(f"  Stopped {name} ({w_class} at {address})")
            stopped_count += 1
        except Exception as err:
            print(f"  Could not close {name} ({address}): {err}")

    print()
    print(f"Successfully stopped {stopped_count} window(s) for `{project_name}`.")
    print()
    return 0


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
    elif command == "save":
        if argument is None:
            print("Usage: doom save <project>")
            return 1
        return save_project_session(argument)
    elif command == "stop":
        if argument is None:
            print("Usage: doom stop <project>")
            return 1
        return stop_project(argument)
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

