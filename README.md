# DOOM

> Local-first Linux project workspace automation.

DOOM is a personal development environment manager for Linux desktops.

The main goal is simple: after a restart, logout, or project switch, you should not have to manually reopen the same browser, editor, terminals, logs, services, workspaces, SSH sessions, Docker commands, and project directories again.

Instead, each project should describe its desired working environment once, and DOOM should restore or reconcile that environment for you.

Example target workflow:

```bash
doom start sellora
```

DOOM should inspect the current desktop, compare it with the project definition, and perform only the missing actions.

It should not blindly launch duplicate windows every time.

## What This Project Is For

Most projects have a repeated workspace layout.

For example, a project might use:

- Workspace 1 for the browser
- Workspace 2 for the editor
- Workspace 3 for terminals
- Workspace 4 for another editor, AI tool, or helper app
- Workspace 10 for music or background apps

The terminal workspace may contain several different terminals:

- A normal shell
- A web app server
- A backend server
- A log viewer
- A package/build watcher

DOOM is meant to remember and restore that setup.

Long term, DOOM should also help with common project operations:

- Git status, commit, and push flows
- Docker startup and logs
- SSH connections
- Project services
- Script generation
- Safe one-click workflows
- Local AI-assisted automation

## Core Idea

DOOM is built around state reconciliation:

```text
project definition
        +
current system state
        |
        v
     matcher
        |
        v
      planner
        |
        v
 permission check
        |
        v
     executor
```

The important idea is that DOOM should compare desired state with current state before acting.

Example:

```text
Current:
  Firefox -> workspace 1
  Code    -> workspace 4
  Kitty   -> ~/Documents/neer/doom

Desired:
  Firefox -> workspace 1
  Code    -> workspace 2
  Kitty   -> ~/Documents/neer/sellora

Plan:
  Move Code to workspace 2
  Launch Sellora terminal
```

This makes `doom start <project>` idempotent: running it twice should not create duplicate windows when the correct setup already exists.

## Current Status

DOOM is in early development.

Currently present:

- Bash CLI entry point: `doom`
- Python command entry point: `core/main.py`
- Basic command router
- YAML project loading with PyYAML
- Unified `windows` schema in project YAML files
- Example project definitions in `projects/`
- Initial Hyprland controller
- Initial Hyprland state inspection
- Process working-directory lookup through `/proc/<pid>/cwd`
- Early project/current-state/diff modules

Currently working:

```bash
python core/main.py help
python core/main.py start test
python core/main.py start sellora
```

Current limitations:

- `start` currently prints the desired project windows; it does not fully execute the plan yet.
- `status` is not implemented yet.
- `plan` is not implemented yet.
- Matching is still basic.
- Terminal identity needs stronger matching through title, role, directory, or command.
- Session save/restore is not implemented yet.
- Git, Docker, SSH, and AI automation are not implemented yet.

## Project Definition

Projects live in `projects/`.

Current schema:

```yaml
name: sellora

windows:
  browser:
    command: firefox
    class: firefox
    workspace: 1

  editor:
    command: code ~/Documents/neer/sellora
    class: code
    workspace: 2
    directory: ~/Documents/neer/sellora

  terminal:
    command: kitty --working-directory ~/Documents/neer/sellora
    class: kitty
    workspace: 3
    directory: ~/Documents/neer/sellora

  spotify:
    command: spotify
    class: spotify
    workspace: 10
```

For normal applications, matching by window class may be enough.

For terminals, class is not enough because multiple Kitty windows can be open at the same time. Terminal definitions should eventually include stable identity fields:

```yaml
server:
  command: kitty --title doom:sellora:server --working-directory ~/Documents/neer/sellora npm run dev
  class: kitty
  title: doom:sellora:server
  workspace: 3
  directory: ~/Documents/neer/sellora
  role: server
```

That gives DOOM a reliable way to detect the correct terminal later.

## Planned Commands

Near-term commands:

```bash
doom status
doom plan <project>
doom start <project>
```

`doom status` should inspect the current desktop and print the active Hyprland state:

```text
Workspace 1:
  firefox

Workspace 2:
  code ~/Documents/neer/sellora

Workspace 3:
  kitty ~/Documents/neer/sellora
  kitty ~/Documents/neer/sellora
```

`doom plan <project>` should show what DOOM would do without executing anything:

```text
Plan for sellora

Launch:
  server -> kitty on workspace 3
  logs -> kitty on workspace 3

Move:
  editor -> workspace 2
```

`doom start <project>` should later execute the approved plan.

Future commands:

```bash
doom save <project>
doom restore <project>
doom stop <project>
doom focus <project>
doom git status <project>
doom git push <project>
doom docker up <project>
doom docker logs <project>
doom ssh <target>
doom doctor
```

## Architecture

Current structure:

```text
doom/
├── README.md
├── doom
├── core/
│   ├── __init__.py
│   ├── main.py
│   ├── router.py
│   ├── project.py
│   ├── state.py
│   ├── executor.py
│   ├── permission.py
│   └── stats/
│       ├── __init__.py
│       ├── hyprland_state.py
│       ├── project_state.py
│       ├── system.py
│       ├── process.py
│       └── diff.py
├── projects/
│   ├── test.yaml
│   └── sellora.yaml
└── skills/
    └── hyprland/
        ├── __init__.py
        └── controller.py
```

Responsibilities:

- `core/main.py`: command-line entry point
- `core/router.py`: command routing
- `core/project.py`: project YAML loading
- `core/stats/hyprland_state.py`: reads Hyprland state through `hyprctl`
- `core/stats/process.py`: reads Linux process details
- `core/stats/project_state.py`: wraps desired project state
- `core/stats/system.py`: builds current system snapshots
- `core/stats/diff.py`: compares current state with desired state
- `core/permission.py`: future approval and safety layer
- `core/executor.py`: future action execution layer
- `skills/hyprland/`: Hyprland-specific control logic

## Development

Create a virtual environment:

```bash
python -m venv doom_env
source doom_env/bin/activate
```

Install dependencies:

```bash
pip install pyyaml
```

Run the CLI:

```bash
python core/main.py help
python core/main.py start test
python core/main.py start sellora
```

Or use the shell entry point:

```bash
./doom help
./doom start test
./doom start sellora
```

## Roadmap

### Phase 1 - Foundation

- Bash CLI
- Python entry point
- Command routing
- YAML project loading
- Unified project schema
- Basic project display

### Phase 2 - Desktop State

- `doom status`
- Read Hyprland clients
- Read Hyprland workspaces
- Read active window and workspace
- Read process working directories
- Normalize current window state
- Detect special workspaces

### Phase 3 - Planning

- `doom plan <project>`
- Desired state model
- Current state model
- Window matcher
- Terminal matcher
- State diff
- Action planner
- Dry-run output

### Phase 4 - Execution

- `doom start <project>` executes plans
- Launch missing windows
- Move windows to target workspaces
- Focus project workspace
- Avoid duplicate terminals
- Add approval checks for risky actions

### Phase 5 - Session Management

- `doom save <project>`
- `doom restore <project>`
- Generate project YAML from current desktop state
- Restore terminal layouts
- Restore browser/editor/workspace layout
- Restore services

### Phase 6 - Development Automation

- Git status, commit, and push helpers
- Docker start/log helpers
- SSH helpers
- Project services
- Environment variables
- Project-specific scripts
- One-click workflows

### Phase 7 - Local AI Layer

- Local model integration
- Natural-language intent parsing
- Script suggestion
- Script debugging support
- Automation generation
- Permission-aware tool calling

## Safety Model

DOOM should be deterministic and safe by default.

AI should not directly execute unrestricted shell commands.

The intended model is:

```text
natural language
      |
      v
safe intent
      |
      v
deterministic planner
      |
      v
permission check
      |
      v
executor
```

Potentially destructive actions should require explicit approval.

Examples:

- `rm`
- `git reset --hard`
- `git push --force`
- `shutdown`
- `reboot`
- Disk operations
- Package removal
- Docker volume deletion
- Production SSH commands

## Design Principles

- Local first
- Linux native
- Hyprland focused first
- Deterministic core
- State driven
- Idempotent behavior
- Safe by default
- Explicit actions
- Human-readable plans
- Modular integrations
- Optional local AI layer

## License

License: TBD.
