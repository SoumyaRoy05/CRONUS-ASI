# Coeus: Titan of Intellect & Memory Persistence (`Titan_Council/Coeus/`)

Coeus is the keeper of memory and cross-session knowledge. Named after the Titan of intellect and inquisitive mind, Coeus maintains CRONUS's local SQLite database vault, logging conversational journals and persisting key-value facts across system reboots.

---

## 1. Core Responsibilities

* **SQLite Memory Vault**: Manages an embedded, thread-safe database located at `.cronus_memory/coeus_vault.sqlite`.
* **Structured Tag Indexing**: Stores records with domain tags (e.g., `user_preference`, `system_config`, `titan_receipt`) for sub-millisecond retrieval.
* **Session Journaling**: Automatically logs conversational events, timestamps, and tool outputs into an audit trail.
* **Cross-Session Continuity**: Ensures that user instructions, project states, and environmental configurations persist indefinitely.

---

## 2. Data Schemas (`schemas.py`)

```python
class MemoryRecord(BaseModel):
    key: str
    value: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str

class SessionJournal(BaseModel):
    session_id: str
    event_type: str
    details: str
    timestamp: str
```

---

## 3. Database Schema

```sql
CREATE TABLE IF NOT EXISTS memories (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Public API

```python
from Titan_Council.Coeus import Coeus

vault = Coeus()

# Persist knowledge
vault.remember(
    key="preferred_code_editor",
    val="VS Code / Antigravity IDE",
    category="user_preference",
    tags=["ide", "developer_tools"]
)

# Recall memory
entry = vault.recall("preferred_code_editor")
print(f"Memory [{entry.key}]: {entry.value}")
```
