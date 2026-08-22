from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PROJECT_ROOT / "projects"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

try:
    from stats.hyprland_state import HyprlandState
except ImportError:
    from core.stats.hyprland_state import HyprlandState


def list_projects():
    if not PROJECT_DIR.exists():
        return []
    return sorted([f.stem for f in PROJECT_DIR.glob("*.yaml")])


def render_dashboard():
    projects = list_projects()
    
    # Try to get active window / workspace info
    active_ws = "Unknown"
    active_win = "None"
    try:
        ws_info = HyprlandState().active_workspace()
        win_info = HyprlandState().active_window()
        if ws_info and isinstance(ws_info, dict):
            active_ws = str(ws_info.get("id", "Unknown"))
        if win_info and isinstance(win_info, dict):
            active_win = win_info.get("class", "None")
    except Exception:
        pass

    lines = []
    lines.append("┌─────────────────────────────────────────────────────────────┐")
    lines.append("│                     DOOM AUTOMATION                         │")
    lines.append("│            Local Linux Workspace Reconciler                 │")
    lines.append("├─────────────────────────────────────────────────────────────┤")
    
    lines.append("│ Configured Projects:                                        │")
    if projects:
        for p in projects:
            lines.append(f"│   • {p:<53} │")
    else:
        lines.append("│   (No projects found in projects/)                          │")

    lines.append("├─────────────────────────────────────────────────────────────┤")
    lines.append(f"│ Desktop State: Workspace {active_ws:<2} | Active App: {active_win:<19} │")
    lines.append("├─────────────────────────────────────────────────────────────┤")
    lines.append("│ Commands:                                                   │")
    lines.append("│   [1] Start a project   (doom start <project>)              │")
    lines.append("│   [2] Plan project      (doom plan <project>)               │")
    lines.append("│   [3] Show status       (doom status)                       │")
    lines.append("│   [4] Save session      (doom save <project>)               │")
    lines.append("│   [5] Stop project      (doom stop <project>)               │")
    lines.append("│   [q] Quit                                                  │")
    lines.append("└─────────────────────────────────────────────────────────────┘")

    return "\n".join(lines)


def interactive_dashboard(router_func):
    while True:
        # Clear screen for clean TUI re-rendering
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()

        print(render_dashboard())
        print()

        projects = list_projects()
        default_proj = projects[0] if projects else "sellora"

        try:
            choice = input("DOOM > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting DOOM.")
            return 0

        if not choice:
            continue

        if choice.lower() in ("q", "quit", "exit"):
            print("Exiting DOOM. Goodbye!")
            return 0

        if choice == "1":
            proj = input(f"Project to start (default '{default_proj}'): ").strip() or default_proj
            router_func("start", proj)
            input("\nPress Enter to return to menu...")
        elif choice == "2":
            proj = input(f"Project to plan (default '{default_proj}'): ").strip() or default_proj
            router_func("plan", proj)
            input("\nPress Enter to return to menu...")
        elif choice == "3":
            router_func("status")
            input("\nPress Enter to return to menu...")
        elif choice == "4":
            proj = input(f"Project to save (default '{default_proj}'): ").strip() or default_proj
            router_func("save", proj)
            input("\nPress Enter to return to menu...")
        elif choice == "5":
            proj = input(f"Project to stop (default '{default_proj}'): ").strip() or default_proj
            router_func("stop", proj)
            input("\nPress Enter to return to menu...")
        else:
            parts = choice.split(maxsplit=1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            router_func(cmd, arg)
            input("\nPress Enter to return to menu...")


if __name__ == "__main__":
    print(render_dashboard())

