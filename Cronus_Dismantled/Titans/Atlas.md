# Atlas: Titan of Endurance & System Execution (`Titan_Council/Atlas/`)

Atlas is the muscle and operational executor of the Titan Council. Named after the Titan who holds up the celestial spheres, Atlas interfaces directly with the operating system, executing commands and manipulating the filesystem under strict containment policies.

---

## 1. Core Responsibilities

* **Sandboxed Command Execution**: Runs PowerShell and cmd processes with strict execution timeouts and output stream capture.
* **Contained File System I/O**: Performs read, write, append, directory listing, and file deletion operations within permitted workspace boundaries.
* **Process Lifecycle Supervision**: Monitors long-running processes and prevents orphaned background tasks.
* **Structured Output Logging**: Encapsulates stdout, stderr, execution duration, and exit codes in `ExecutionResult` schemas.

---

## 2. Data Schemas (`schemas.py`)

```python
class ExecutionResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    command_executed: str
    error_message: Optional[str]
```

---

## 3. Public API

```python
from Titan_Council.Atlas import Atlas

executor = Atlas()

# Run a PowerShell command
res = executor.run_shell("Get-Process | Select-Object -First 5")
print(f"Command Exited {res.exit_code}:\n{res.stdout}")

# Secure file creation
executor.manage_file(
    operation="write",
    target_path="D:/Codes/CRONUS-ASI/scratch_output.txt",
    content="Atlas system execution verified."
)
```
