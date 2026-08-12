# DOOM

> Local Linux automation and development environment manager.

DOOM is a local-first Linux automation project for restoring development environments on a Linux desktop.

The goal is to stop manually rebuilding the same setup after every restart or project switch: terminals, editors, browsers, workspaces, services, and project directories should eventually be described once and reconciled automatically.

Example target workflow:

```bash
doom start sellora
```

Eventually, that command should inspect the current desktop state, compare it with the desired project state, and perform only the missing actions.

## Vision

DOOM is being built around state reconciliation:

```text
desired project state
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
     executor
```

Instead of blindly launching every application again, DOOM should detect what already exists.

For example:

```text
Current:
  Firefox -> workspace 1
  VS Code -> special workspace
  Kitty   -> ~/Documents/neer/doom

Desired:
  Firefox -> workspace 1
  VS Code -> workspace 2
  Kitty   -> ~/Documents/neer/sellora

Plan:
  Move VS Code to workspace 2
  Launch Sellora terminal
```

## Current Status

DOOM is in early development.

Currently present:

- Bash CLI entry point: `doom`
- Python command entry point: `core/main.py`
- Basic command router
- YAML project loading with PyYAML
- Example project definitions in `projects/`
- Initial Hyprland controller
- Initial Hyprland state inspection code
- Initial process inspection through `/proc/<pid>/cwd`
- Early project/current-state/diff modules

Known current gaps:

- The project YAML schema is not unified yet.
- `doom start test` works with the current router.
- `doom start sellora` currently fails because `sellora.yaml` uses a newer `windows` schema while the router expects `workspaces` and `applications`.
- Some state/diff modules are architectural drafts and are not fully runnable yet.
- Matching, planning, execution, session save, and session restore are not complete yet.

## Project Structure

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

## Core Concepts

### Project

A project describes a development environment.

It may eventually include:

- Applications
- Workspaces
- Terminals
- Working directories
- Commands
- Services
- Browser sessions
- Git repositories
- SSH connections
- Environment variables

### Desired State

The desired state describes what should exist when a project is active.

Example:

```yaml
editor:
  type: application
  command: code
  class: code
  workspace: 2
```

### Current State

The current state describes what is actually running on the machine.

DOOM is expected to collect this from:

- Hyprland
- Linux processes
- The filesystem
- Git
- SSH
- System services

### Matching

Matching decides whether an existing system object satisfies a desired project object.

For terminals, class alone is not enough. Multiple Kitty windows may exist, so DOOM should also compare workspace, working directory, and project identity.

### Planning

The planner should convert state differences into explicit actions.

Examples:

```text
LaunchApplication firefox
MoveWindow 0x1234 -> workspace 2
OpenTerminal ~/Documents/neer/sellora
```

### Execution

The executor should perform approved actions through integration layers such as Hyprland, Git, SSH, Docker, or shell commands.

## Hyprland Integration

DOOM currently targets Hyprland.

Hyprland-specific logic should stay inside:

```text
skills/hyprland/
```

The rest of the system should use a controller abstraction instead of directly depending on Hyprland command details.

Current integration ideas include:

- Switching workspaces
- Launching applications
- Reading clients with `hyprctl -j clients`
- Reading workspaces with `hyprctl -j workspaces`
- Reading active window and workspace state
- Moving windows between workspaces

## Commands

Current CLI shape:

```bash
doom help
doom start <project>
doom stop <project>
doom save <project>
doom restore <project>
doom status <project>
doom run <action>
doom learn
```

Currently implemented:

```bash
python core/main.py help
python core/main.py start test
```

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
```

Or use the shell entry point:

```bash
./doom help
./doom start test
```

## Design Principles

- Local first
- Linux native
- Deterministic core
- State driven
- Idempotent behavior
- Safe by default
- Explicit actions
- Modular integrations
- Optional AI layer

## AI Direction

AI is not the foundation of DOOM.

The deterministic automation engine should work first. A local model can later translate natural language into safe DOOM intents.

Example:

```text
"Start Sellora"
```

could become:

```json
{
  "intent": "start_project",
  "project": "sellora"
}
```

DOOM should then handle the state inspection, planning, permission checks, and execution deterministically.

## Roadmap

### Phase 1 - Foundation

- Bash CLI
- Python entry point
- Command routing
- YAML project loading
- Hyprland controller

### Phase 2 - Desktop State

- Read Hyprland clients
- Read Hyprland workspaces
- Read active window
- Read active workspace
- Read Linux process information
- Detect special workspaces
- Normalize window state

### Phase 3 - Reconciliation

- Unified project schema
- Desired state model
- Current state model
- Window matcher
- Terminal matcher
- State diff
- Action planner
- Action executor
- Idempotent `doom start`

### Phase 4 - Session Management

- `doom save`
- `doom restore`
- Terminal restoration
- Browser restoration
- Workspace restoration
- Service restoration

### Phase 5 - Development Automation

- Git integration
- SSH integration
- Docker integration
- Project services
- Environment variables
- Project-specific scripts

### Phase 6 - AI

- Local model integration
- Intent parser
- Tool calling
- Natural-language project startup
- Permission system
- Automation generation

## Safety Model

DOOM should not execute unrestricted AI-generated shell commands.

The intended model is:

```text
intent -> planner -> validated actions -> permission check -> executor
```

Potentially destructive operations should require explicit approval.

Examples:

- `rm`
- `git reset --hard`
- `git push --force`
- `shutdown`
- `reboot`
- Disk operations
- Package removal

## License

License: TBD.
