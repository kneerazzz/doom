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
python core/main.py status
python core/main.py plan sellora
```

Current limitations:

- `start` currently prints the desired project windows; it does not fully execute the plan yet.
- `status` requires a running Hyprland session with `hyprctl`.
- `plan` requires a running Hyprland session because it compares against current windows.
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
    command: brave-browser
    class: brave-browser
    workspace: 1

  editor:
    command: code ~/Documents/neer/sellora
    class: code
    workspace: 2
    directory: ~/Documents/neer/sellora

  spotify:
    command: spotify
    class: spotify
    workspace: 10

terminals:
  defaults:
    app: kitty
    class: kitty
    workspace: 3
    directory: ~/Documents/neer/sellora
    title_prefix: doom:sellora

  entries:
    shell: {}
    server: {}
    logs: {}
    packages: {}
```

For normal applications, matching by window class may be enough.

For terminals, class is not enough because multiple Kitty windows can be open at the same time. Terminal definitions should include stable identity fields:

```yaml
terminals:
  defaults:
    app: kitty
    class: kitty
    workspace: 3
    directory: ~/Documents/neer/sellora
    title_prefix: doom:sellora

  entries:
    server:
      title: doom:sellora:server
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
python core/main.py status
python core/main.py plan sellora
```

Or use the shell entry point:

```bash
./doom help
./doom start test
./doom start sellora
./doom status
./doom plan sellora
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

# Local AI Architecture

The AI layer is intended to make DOOM easier to control and more capable, not to turn it into an unrestricted AI coding agent.

The core idea is:

> **AI understands intent. DOOM decides and executes actions.**

The deterministic DOOM engine remains responsible for:

* State inspection
* Matching
* Planning
* Validation
* Permissions
* Execution
* Verification

The local model sits above that system and translates natural-language requests into structured DOOM operations.

For example, instead of manually running several commands:

```text
Start Sellora.

Open the project environment,
start the required services,
open the backend terminal,
open the frontend terminal,
and put everything in the correct workspaces.
```

The AI should understand the request and map it to DOOM's existing capabilities.

Conceptually:

```text
                    User
                      |
                      v
              Natural Language
                      |
                      v
                 Local AI
                      |
              Intent / Action
                      |
                      v
              DOOM Core Engine
                      |
        ┌─────────────┼─────────────┐
        v             v             v
      State         Planner      Permissions
        |             |             |
        └─────────────┼─────────────┘
                      |
                      v
                   Executor
                      |
                      v
                  Linux System
```

The AI should **not bypass the planner or executor**.

---

# What the AI Is Responsible For

The AI layer can eventually handle tasks such as:

### Intent Understanding

Convert natural language into structured operations.

For example:

```text
"Start my Sellora environment."
```

could become an internal intent similar to:

```text
project = sellora
operation = start
```

Another request:

```text
"Open the backend terminal for Sellora."
```

could become:

```text
project = sellora
role = backend
operation = open
```

The exact internal representation can evolve as DOOM's action system becomes more mature.

---

### Project-Aware Assistance

The AI can use the project's existing definition and DOOM's current state to understand the environment.

For example:

```text
User:
Why isn't my Sellora backend running?

AI:
The Sellora backend terminal exists, but the expected
server process is not running.
```

The AI can then request a deterministic DOOM operation rather than inventing an arbitrary shell command.

---

### Automation Orchestration

The AI can combine existing DOOM capabilities into higher-level workflows.

For example:

```text
"Prepare Sellora for development."
```

could involve:

```text
1. Check current project state
2. Start required services
3. Restore project windows
4. Open required terminals
5. Start approved development processes
6. Verify the resulting state
```

The AI determines the user's intent and helps select the required operations.

DOOM remains responsible for executing those operations.

---

### Diagnostics

The AI can inspect structured information produced by DOOM and explain problems.

For example:

```text
Current:

Postgres      -> running
Redis         -> running
Backend       -> stopped
Frontend      -> running

User:
What's wrong?

AI:
The backend is the only missing service.
The project environment otherwise matches the expected state.
```

This is much safer and more useful than having an AI blindly execute commands until something appears to work.

---

# AI Should Work Through Capabilities

Rather than giving the AI unrestricted shell access, DOOM should expose controlled capabilities.

For example:

```text
project.start
project.stop
project.status
project.plan

window.list
window.launch
window.move
window.close

terminal.open
terminal.list

service.start
service.stop
service.status

docker.up
docker.down
docker.logs

git.status
git.diff
git.commit
git.push

ssh.connect
```

The AI can request one of these capabilities.

DOOM then validates and executes it.

```text
AI
 |
 | request: docker.up(project="sellora")
 v
DOOM
 |
 | validate
 v
Permission Layer
 |
 | approved
 v
Executor
 |
 v
Docker
```

This gives DOOM a clear boundary between:

```text
AI reasoning
```

and:

```text
system execution
```

---

# AI Should Not Have Unrestricted Shell Access

DOOM should avoid an architecture where the model simply receives:

```text
run_shell(command)
```

and can generate arbitrary commands such as:

```bash
rm -rf ...
```

or:

```bash
git push --force
```

The preferred architecture is capability-based.

Instead of:

```text
AI -> arbitrary shell command
```

DOOM should use:

```text
AI
 ↓
Structured intent
 ↓
Known DOOM capability
 ↓
Planner
 ↓
Permission check
 ↓
Executor
```

This makes the system easier to reason about, audit, and debug.

---

# AI and the Deterministic Core

The deterministic core should remain usable without AI.

For example:

```bash
doom plan sellora
doom start sellora
doom status
```

should continue to work normally.

AI is an additional interface on top of DOOM.

That means:

```text
             ┌──────────────────┐
             │   Natural Language│
             └────────┬─────────┘
                      │
                      v
                ┌───────────┐
                │ Local AI  │
                └─────┬─────┘
                      │
                      v
             ┌──────────────────┐
             │  DOOM Core API  │
             └────────┬─────────┘
                      │
          ┌───────────┼───────────┐
          v           v           v
       State       Planner    Permission
          │           │           │
          └───────────┼───────────┘
                      v
                  Executor
```

The AI can therefore be replaced, disabled, or upgraded without changing the fundamental automation engine.

---

# Phase 7 — Local AI Layer

The AI layer will be introduced only after the deterministic automation system is sufficiently mature.

### Intent and Interaction

* [ ] Local model integration
* [ ] Natural-language project commands
* [ ] Convert user requests into structured intents
* [ ] Project-aware conversations
* [ ] Context-aware status explanations
* [ ] Natural-language `plan` requests
* [ ] Natural-language `status` queries

### Capability Interface

* [ ] Define a controlled DOOM capability API
* [ ] Allow AI to request known operations
* [ ] Validate AI-generated structured actions
* [ ] Prevent direct unrestricted shell execution
* [ ] Add capability-specific permissions
* [ ] Log AI-requested operations

### Project Intelligence

* [ ] Understand project definitions
* [ ] Understand project roles
* [ ] Understand terminal identities
* [ ] Understand services and dependencies
* [ ] Explain why an environment differs from its desired state
* [ ] Suggest corrective actions through the planner

### Automation

* [ ] Combine existing capabilities into workflows
* [ ] Allow natural-language project preparation
* [ ] Support multi-step approved workflows
* [ ] Detect failed actions
* [ ] Re-check system state after execution
* [ ] Explain failures and missing dependencies

### Local Intelligence

* [ ] Local model support
* [ ] Local project context
* [ ] Optional local embeddings/RAG where useful
* [ ] Persistent project knowledge
* [ ] Tool/capability selection
* [ ] Context-aware automation

The AI layer should remain optional.

DOOM's fundamental state reconciliation and execution system should not depend on a cloud AI provider.

---

# Safety Model

DOOM should be deterministic and safe by default.

The AI should never be treated as an authority to directly execute arbitrary system commands.

The intended model is:

```text
Natural Language
       |
       v
Local AI
       |
       v
Structured Intent
       |
       v
Known DOOM Capability
       |
       v
Deterministic Planner
       |
       v
Permission Check
       |
       v
Executor
       |
       v
Verification
```

Potentially destructive actions should require explicit approval.

Examples include:

```text
rm
git reset --hard
git push --force
shutdown
reboot
disk operations
package removal
Docker volume deletion
production SSH commands
```

The important distinction is that the AI can **request** an operation, but the AI does not get to decide that the operation is safe.

DOOM's permission layer makes that decision.

---

# Long-Term Architecture

The long-term goal is for DOOM to become a local development-environment automation platform rather than simply a window launcher.

A project could eventually describe an entire development environment:

```yaml
name: sellora

workspace:
  browser:
    workspace: 1

  editor:
    workspace: 2

  development:
    workspace: 3

services:
  - postgres
  - redis
  - ollama

terminals:
  - role: shell
  - role: backend
  - role: frontend
  - role: worker
  - role: logs

docker:
  compose: docker-compose.yml

git:
  repository: ~/Documents/neer/sellora

ssh:
  - target: development-server
```

DOOM could then reconcile multiple parts of the development environment:

```text
                         PROJECT
                            |
          ┌─────────────────┼─────────────────┐
          |                 |                 |
          v                 v                 v
       Desktop           Services           Tools
          |                 |                 |
          v                 v                 v
      Hyprland           Docker              Git
      Windows            Redis               SSH
      Terminals          Postgres            Scripts
      Workspaces         Ollama              etc.
          |                 |                 |
          └─────────────────┼─────────────────┘
                            |
                            v
                         Verify
```

The local AI layer sits above this system as an intelligent interface:

```text
                     User
                       |
                       v
                  Local AI
                       |
              Understand Intent
                       |
                       v
                 DOOM Core
                       |
       ┌───────────────┼───────────────┐
       v               v               v
     State           Plan          Permissions
       |               |               |
       └───────────────┼───────────────┘
                       v
                    Execute
                       |
                       v
                    Verify
```

The key design principle is:

> **AI should make DOOM easier to control, not make DOOM less deterministic.**

The AI interprets what the user wants.
DOOM determines what needs to change.
The permission layer determines what is allowed.
The executor performs the approved operation.
The state system verifies the result.

That separation is what keeps the system predictable while still allowing DOOM to become significantly more powerful over time.


## License

License: TBD.
