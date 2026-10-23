# CRONUS Database Engine (PostgreSQL 18 Architecture)

The **Database** engine (`Database/`) provides 24/7 persistent memory, dialogue turn history, user preferences, and multi-agent Titan Council execution tracking via local **PostgreSQL 18**.

---

## 1. Engine Specifications

* **Server Engine**: PostgreSQL 18.6 (64-bit Windows Service: `postgresql-x64-18`)
* **Database Name**: `Cronus_DB`
* **Driver**: `asyncpg==0.32.0` (asynchronous, high-throughput binary protocol)
* **Connection Pooling**: `asyncpg.create_pool(min_size=1, max_size=10)`
* **Latency**: Under 1ms query round-trip time on `localhost:5432`
* **Circuit-Breaker Protection**: If the PostgreSQL service is ever stopped or offline, the database client catches the exception, logs a warning, and allows CRONUS to continue talking in RAM with **zero crashes**.

---

## 2. Database Schema (Public Schema in `Cronus_DB`)

| Table Name | Primary Key | Key Columns | Purpose |
| :--- | :--- | :--- | :--- |
| **`conversations`** | `session_id` (UUID) | `started_at`, `ended_at`, `total_turns`, `summary` | Tracks high-level voice/chat sessions |
| **`dialogue_turns`** | `turn_id` (BigSerial) | `session_id`, `user_prompt`, `cleaned_speech_response`, `model_used`, `ear_latency_ms`, `brain_latency_ms`, `mouth_latency_ms` | Complete conversational audit log written by `Brain.think()` |
| **`user_preferences`** | `key` (VarChar) | `value`, `category`, `metadata` (JSONB), `updated_at` | Long-term user facts, identity directives, and custom settings |
| **`semantic_vault`** | `id` (UUID) | `content`, `category`, `tags` (Array), `embedding` (Float8[]), `metadata` (JSONB) | Semantic vector knowledge vault for cross-session continuity |
| **`titan_blueprints`** | `blueprint_id` (UUID) | `goal`, `rationale`, `planner_model`, `total_steps`, `status`, `fallback_strategy`, `raw_json` | Prometheus master architectural plans |
| **`titan_task_steps`** | `step_id` (UUID) | `blueprint_id`, `step_number`, `title`, `action_type`, `command_payload`, `status`, `exit_code`, `stdout`, `stderr` | Atlas & Helios step-by-step execution logs |
| **`titan_security_audits`**| `audit_id` (UUID) | `step_id`, `target_name`, `command_or_code`, `verdict`, `score`, `violations` (JSONB), `summary` | Themis AST syntax & safety verification audits |

---

## 3. Public API (`Database/`)

```python
import asyncio
from Database import (
    is_db_connected,
    set_user_preference,
    get_user_preference,
    log_dialogue_turn,
    get_recent_dialogue_turns,
    save_blueprint_record,
    save_task_step_record,
    save_security_audit_record,
)

async def example():
    # 1. Health check
    if await is_db_connected():
        print("Cronus_DB is active and healthy.")

    # 2. Set user preference
    await set_user_preference("creator", "Soumya Roy", category="identity")

    # 3. Retrieve recent speech history
    recent = await get_recent_dialogue_turns(limit=5)
    for turn in recent:
        print(f"User: {turn['user_prompt']} -> CRONUS: {turn['cleaned_speech_response']}")

asyncio.run(example())
```
