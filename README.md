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
