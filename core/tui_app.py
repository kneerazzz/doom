import io
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
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, ListView, ListItem, Label, Button, RichLog
    from textual.containers import Container, Horizontal, Vertical
    from textual.binding import Binding
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

try:
    from stats.hyprland_state import HyprlandState
except ImportError:
    from core.stats.hyprland_state import HyprlandState


def list_projects():
    if not PROJECT_DIR.exists():
        return []
    return sorted([f.stem for f in PROJECT_DIR.glob("*.yaml")])


if HAS_TEXTUAL:
    class DoomApp(App):
        CSS = """
        Screen {
            layout: vertical;
            background: $surface;
        }

        #top-banner {
            height: 3;
            background: $primary-background;
            color: $text;
            content-align: center middle;
            text-style: bold;
            border-bottom: heavy $primary;
        }

        #main-container {
            layout: horizontal;
            height: 1fr;
        }

        #sidebar {
            width: 30;
            border-right: solid $primary;
            padding: 1;
        }

        #sidebar-title {
            text-style: bold;
            color: $accent;
            margin-bottom: 1;
        }

        #project-list {
            height: 1fr;
            border: panel $primary;
        }

        #content-pane {
            width: 1fr;
            padding: 1;
            layout: vertical;
        }

        #action-bar {
            height: 3;
            margin-bottom: 1;
        }

        #action-bar Button {
            margin-right: 1;
        }

        #log-view {
            height: 1fr;
            border: panel $accent;
            background: $background;
        }
        """

        BINDINGS = [
            Binding("s", "start_proj", "Start", show=True),
            Binding("p", "plan_proj", "Plan", show=True),
            Binding("d", "show_status", "Status", show=True),
            Binding("v", "save_proj", "Save", show=True),
            Binding("x", "stop_proj", "Stop", show=True),
            Binding("q", "quit", "Quit", show=True),
        ]

        def __init__(self, router_func=None):
            super().__init__()
            self.router_func = router_func

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Label("⚡ DOOM AUTOMATION - Local Linux Workspace Reconciler", id="top-banner")
            
            with Container(id="main-container"):
                with Vertical(id="sidebar"):
                    yield Label("Projects", id="sidebar-title")
                    projects = list_projects()
                    items = [ListItem(Label(p), id=f"proj-{p}") for p in projects]
                    yield ListView(*items, id="project-list")

                with Vertical(id="content-pane"):
                    with Horizontal(id="action-bar"):
                        yield Button("Start (s)", id="btn-start", variant="success")
                        yield Button("Plan (p)", id="btn-plan", variant="primary")
                        yield Button("Status (d)", id="btn-status", variant="info")
                        yield Button("Save (v)", id="btn-save", variant="warning")
                        yield Button("Stop (x)", id="btn-stop", variant="error")
                    
                    yield RichLog(id="log-view", highlight=True, markup=True)

            yield Footer()

        def on_mount(self) -> None:
            log = self.query_one(RichLog)
            log.write("[bold green]DOOM Interactive TUI Loaded.[/bold green]")
            log.write("Use [bold yellow]Arrow Keys[/bold yellow] to select a project, or press keys/buttons to run actions.")
            self.action_show_status()

        def _get_selected_project(self) -> str:
            project_list = self.query_one("#project-list", ListView)
            if project_list.highlighted_child:
                label = project_list.highlighted_child.query_one(Label)
                return str(label.renderable)
            projects = list_projects()
            return projects[0] if projects else "sellora"

        def _run_captured_command(self, cmd: str, arg: str | None = None):
            log = self.query_one(RichLog)
            if not self.router_func:
                log.write(f"[red]No router attached to execute '{cmd} {arg or ''}'[/red]")
                return

            log.write(f"\n[bold cyan]> Executing: doom {cmd} {arg or ''}[/bold cyan]\n")

            # Capture stdout
            old_stdout = sys.stdout
            buffer = io.StringIO()
            sys.stdout = buffer
            try:
                self.router_func(cmd, arg)
            except Exception as err:
                buffer.write(f"Error: {err}\n")
            finally:
                sys.stdout = old_stdout

            output = buffer.getvalue()
            for line in output.splitlines():
                log.write(line)

        def action_start_proj(self) -> None:
            proj = self._get_selected_project()
            self._run_captured_command("start", proj)

        def action_plan_proj(self) -> None:
            proj = self._get_selected_project()
            self._run_captured_command("plan", proj)

        def action_show_status(self) -> None:
            self._run_captured_command("status")

        def action_save_proj(self) -> None:
            proj = self._get_selected_project()
            self._run_captured_command("save", proj)

        def action_stop_proj(self) -> None:
            proj = self._get_selected_project()
            self._run_captured_command("stop", proj)

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "btn-start":
                self.action_start_proj()
            elif event.button.id == "btn-plan":
                self.action_plan_proj()
            elif event.button.id == "btn-status":
                self.action_show_status()
            elif event.button.id == "btn-save":
                self.action_save_proj()
            elif event.button.id == "btn-stop":
                self.action_stop_proj()


def run_tui_app(router_func=None):
    if not HAS_TEXTUAL:
        print("Textual library not found. Falling back to CLI.")
        return 1
    app = DoomApp(router_func=router_func)
    app.run()
    return 0


if __name__ == "__main__":
    run_tui_app()
