"""
Coeus Tools
Local persistent memory storage, SQLite state vault, and query primitives.
"""

from __future__ import annotations
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_root_dir = Path(__file__).resolve().parents[2]
_storage_dir = _root_dir / ".cronus_memory"
_storage_dir.mkdir(parents=True, exist_ok=True)
_db_path = _storage_dir / "coeus_vault.sqlite"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            record_id TEXT PRIMARY KEY,
            record_type TEXT,
            key TEXT,
            content TEXT,
            metadata TEXT,
            timestamp REAL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS checkpoints (
            checkpoint_id TEXT PRIMARY KEY,
            thread_id TEXT,
            step_index INTEGER,
            state_payload TEXT,
            created_at REAL
        )
        """
    )
    conn.commit()
    return conn


def store_memory_item(
    key: str,
    content: str,
    record_type: str = "creator_preference",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Stores a memory record in the persistent vault."""
    record_id = str(uuid.uuid4())
    meta_json = json.dumps(metadata or {})
    ts = time.time()

    conn = _get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, record_type, key, content, meta_json, ts),
            )
        return record_id
    finally:
        conn.close()


def query_memory_vault(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Performs keyword and key-prefix search over stored memories."""
    conn = _get_connection()
    q_pattern = f"%{query}%"
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT record_id, record_type, key, content, metadata, timestamp
            FROM memories
            WHERE key LIKE ? OR content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (q_pattern, q_pattern, limit),
        )
        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                "record_id": r[0],
                "record_type": r[1],
                "key": r[2],
                "content": r[3],
                "metadata": json.loads(r[4]),
                "timestamp": r[5],
            })
        return results
    finally:
        conn.close()


def save_checkpoint_state(thread_id: str, step_index: int, state_payload: Dict[str, Any]) -> str:
    """Saves a state checkpoint snapshot."""
    checkpoint_id = f"chk_{thread_id}_{int(time.time() * 1000)}"
    conn = _get_connection()
    try:
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?, ?, ?)",
                (checkpoint_id, thread_id, step_index, json.dumps(state_payload), time.time()),
            )
        return checkpoint_id
    finally:
        conn.close()
