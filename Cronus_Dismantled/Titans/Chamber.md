# Council Chamber (`Titan_Council/Chamber.py`)

The **Council Chamber** is the central orchestration and deliberation engine of the Titan Council. It organizes and coordinates all 6 Titan agents, executing concurrent asynchronous workflows, enforcing safety consensus gates, and mediating autonomous recovery.

---

## 1. Technical Architecture

* **Asynchronous Concurrency**: Built with Python's native `asyncio` event loop. Leverages `asyncio.gather()` to run non-dependent Titan tasks (e.g., simultaneous Hyperion document retrieval and Coeus memory lookups) concurrently.
* **Deterministic Multi-Stage Pipeline**:
  1. **Intel Gathering**: Parallel retrieval across Hyperion (web docs) and Coeus (long-term memory).
  2. **Strategic Planning**: Prometheus generates an `ArchitecturalBlueprint`.
  3. **Safety Verification**: Themis performs static AST code checks and command safety validation.
  4. **System Execution**: Atlas executes sandboxed shell and file commands; Helios automates GUI tasks.
  5. **Memory Archival**: Coeus writes final receipts into SQLite storage.
* **Dynamic Replanning on Failure**: If any execution step fails, the Chamber immediately feeds the error context back to Prometheus to formulate a recovery plan.

---

## 2. Public API & Usage

```python
import asyncio
from Titan_Council import CouncilChamber

async def run_example():
    chamber = CouncilChamber()
    
    # Executes an autonomous multi-agent task
    result = await chamber.deliberate_and_execute(
        goal="Audit current project dependencies and verify local SQLite memory health."
    )
    print("Execution Result:", result)

asyncio.run(run_example())
```
