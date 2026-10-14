# 🛠️ Atlas — Titan of Endurance & Chief Engineer

> *"Let the architects dream the sky; I shall bear its weight upon my shoulders and forge it into steel."*  
> **Council Role:** Chief Systems Engineer, Tool Executor, Shell & File I/O Specialist  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Atlas** represents the physical embodiment of execution. While Prometheus envisions the architecture and Themis audits the quality, Atlas carries the celestial sphere of physical implementation: writing code, manipulating files, executing shell commands, and configuring runtime environments.

Atlas converts theoretical `TaskStep` directives from Prometheus into concrete, verifiable reality with zero hallucination.

### Core Responsibilities
1. **Asynchronous Shell Execution:** Runs shell commands, test scripts, and build processes non-blockingly with timeouts and stream capture (`stdout`, `stderr`, `exit_code`).
2. **Deterministic Filesystem Operations:** Handles file creation, atomic writes, line-level patching, and directory tree management.
3. **Hardware & Environment Telemetry:** Gathers runtime telemetry (OS version, Python executable, CUDA availability, GPU device name).
4. **Council Execution Deliberation:** Participates in the Titan Council chamber, assessing whether proposed blueprints are physically feasible given workspace constraints.

---

## 2. Operational Protocol: The Execution Cycle

Atlas executes tasks through a deterministic, four-stage loop:

```
                  [ TaskStep from Prometheus ]
                               │
                               ▼
               ┌───────────────────────────────┐
               │    1. Feasibility Analysis    │
               │ (Check paths, tools & env)   │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │     2. Tool Dispatching       │
               │ (Shell / File I/O / Patch)    │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │   3. Telemetry & Stream Log   │
               │ (Capture stdout, stderr, code)│
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │ 4. StepExecutionResult Return │
               │ (Output to Council / Themis)  │
               └───────────────────────────────┘
```

1. **Feasibility Analysis:** Verifies that required directories exist, dependencies are satisfied, and inputs are well-formed.
2. **Tool Dispatching:** Dispatches actions to asynchronous subprocesses or filesystem handlers.
3. **Telemetry Capture:** Measures execution duration in milliseconds, captures output streams, and checks exit codes.
4. **Result Packaging:** Packages output into a deterministic `StepExecutionResult` for audit by Themis.

---

## 3. Data Contracts & Schemas (`schemas.py`)

Atlas enforces strict **Pydantic V2** schemas for all execution actions:

### `ToolActionType` (Enum)
* `SHELL_COMMAND`: Subprocess execution.
* `WRITE_FILE`: Creating or overwriting files with parent directory creation.
* `READ_FILE`: Safe reading of workspace files.
* `PATCH_FILE`: Surgical snippet replacement.
* `INSPECT_ENV`: Hardware and runtime telemetry check.
* `LIST_DIR`: Directory inventory.

### `ToolAction`
The atomic instruction sent to Atlas:
* `action_type` (*ToolActionType*): Category of tool operation.
* `command` (*Optional[str]*): Command string if shell action.
* `file_path` (*Optional[str]*): Target filesystem path.
* `content` (*Optional[str]*): Text content to write.
* `target_snippet` (*Optional[str]*): Exact snippet to replace during patching.
* `replacement_snippet` (*Optional[str]*): Replacement text.
* `timeout_seconds` (*float*): Execution timeout (default: `30.0s`).

### `StepExecutionResult`
The outcome of executing a single step:
* `step_id` (*int*): Step index.
* `title` (*str*): Step description.
* `action_type` (*str*): Action performed.
* `status` (*str*): `SUCCESS`, `FAILED`, `BLOCKED`, or `SKIPPED`.
* `stdout` (*str*): Standard output text.
* `stderr` (*str*): Standard error text.
* `exit_code` (*int*): Process return code (`0` = success).
* `error_message` (*Optional[str]*): Detailed failure message if unsuccessful.
* `execution_time_ms` (*float*): Execution duration in milliseconds.
* `artifacts_created` (*List[str]*): File paths created or modified.

### `ExecutionSummary`
Consolidated report across a multi-step blueprint execution.

---

## 4. Internal Architecture & File Layout

```text
Titan_Council/Atlas/
├── __init__.py      # Clean public API exposing Atlas, schemas, and tools
├── schemas.py       # Pydantic V2 execution schemas
├── prompts.py       # Atlas persona, execution principles, and deliberation prompts
├── tools.py         # Async shell runner, file I/O primitives, and telemetry inspection
├── agent.py         # Atlas agent class with async dispatch and council debate
└── README.md        # This technical documentation file
```

---

## 5. Tool Primitives (`tools.py`)

* **`async_run_command(command, cwd, timeout)`:** Uses `asyncio.create_subprocess_shell` with strict timeouts, non-blocking stream capture, and automatic UTF-8 decoding.
* **`write_file(file_path, content, overwrite)`:** Writes text safely, creating missing parent folders automatically.
* **`patch_file(file_path, target, replacement)`:** Performs exact, single-occurrence text replacement without destructive overwrites.
* **`inspect_environment()`:** Returns active OS, Python version, CUDA readiness, and GPU device details (`NVIDIA GeForce RTX 5060`).

---

## 6. How to Use Atlas

### Instantiation
```python
from Titan_Council.Atlas import Atlas, ToolAction, ToolActionType

atlas = Atlas()
```

### Executing a Shell Action Asynchronously
```python
import asyncio

async def run_step():
    action = ToolAction(
        action_type=ToolActionType.SHELL_COMMAND,
        command="python -c \"print('Atlas executing verified command')\"",
        timeout_seconds=15.0
    )
    result = await atlas.execute_action(action)
    print(f"Status: {result.status} | Exit Code: {result.exit_code} ({result.execution_time_ms:.1f}ms)")
    print(f"Output: {result.stdout.strip()}")

asyncio.run(run_step())
```

### Participating in Council Deliberation
```python
# Atlas reviews a proposal from Prometheus
proposal = "Deploy LangGraph AsyncPostgresSaver connecting Subgraph 1 to Subgraph 3"
deliberation = atlas.deliberate_sync(proposal)
print(deliberation)
```
