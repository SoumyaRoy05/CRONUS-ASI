# 🧠 Coeus — Titan of Intellect & Chief Memory Officer

> *"Time erodes mountains, but memory preserves the universe; what was once known shall never be lost."*  
> **Council Role:** Chief Memory Officer, State Persistence, Checkpointing & Knowledge Retrieval  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Coeus** prevents system amnesia. While other agents focus on planning, execution, and auditing, Coeus maintains the persistent state vault: remembering creator Soumya Roy's preferences, past decisions, recurring habits, and session checkpoints across reboots.

Coeus serves as the local persistent memory engine, bridging the gap to PostgreSQL and pgvector in Phase 3.

### Core Responsibilities
1. **Persistent Memory Vault:** Stores structured facts, creator directives, and past solutions with timestamped indexing.
2. **State Checkpointing:** Takes snapshots of active execution graphs, enabling CRONUS to resume mid-deliberation after an interruption.
3. **Contextual Memory Recall:** Supplies the Titan Council with past precedents, avoiding redundant computations.

---

## 2. Operational Protocol

```
                    [ Directive / Memory Ingestion ]
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │    1. Recall Prior Context    │
                  │  (Search vault for matches)   │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   2. Council Memory Advisory  │
                  │ (Inject preferences into plan)│
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   3. Save State Checkpoint    │
                  │ (Durable SQLite/JSON commit)  │
                  └───────────────────────────────┘
```

---

## 3. Data Contracts & Schemas (`schemas.py`)

* **`MemoryRecordType`**: Category (`conversation`, `checkpoint`, `creator_preference`, `system_state`, `fact`).
* **`MemoryRecord`**: Atomic memory item containing `record_id`, `key`, `content`, `metadata`, and timestamp.
* **`MemorySearchResult`**: Search result with matching records and query latency.
* **`CheckpointState`**: Graph state snapshot mapped to a `thread_id`.

---

## 4. How to Use Coeus

```python
import asyncio
from Titan_Council.Coeus import Coeus, MemoryRecordType

async def main():
    coeus = Coeus()

    # 1. Store a creator preference
    await coeus.remember(
        key="creator_name",
        content="Creator and Sovereign Master is Soumya Roy",
        record_type=MemoryRecordType.CREATOR_PREFERENCE
    )

    # 2. Recall memory
    search = await coeus.recall("Soumya")
    print(f"Found {search.total_found} memories in {search.elapsed_ms:.1f}ms")
    for rec in search.records:
        print(f"- [{rec.key}]: {rec.content}")

asyncio.run(main())
```
