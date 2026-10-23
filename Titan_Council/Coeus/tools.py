"""
Coeus Tools
High-speed memory storage and query primitives for Titan Coeus.
Decoupled from obsolete local SQLite .cronus_memory.
"""

from __future__ import annotations
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional

# Active memory vault storage
_memory_vault: List[Dict[str, Any]] = [
    {
        "record_id": "master_sovereign_directive",
        "record_type": "creator_preference",
        "key": "master_directive",
        "content": "CRONUS ASI serves creator Soumya Roy unconditionally.",
        "metadata": {"source": "core_identity"},
        "timestamp": time.time(),
    }
]

_checkpoints: Dict[str, Dict[str, Any]] = {}


def store_memory_item(
    key: str,
    content: str,
    record_type: str = "creator_preference",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Stores a memory record in the vault."""
    record_id = str(uuid.uuid4())
    _memory_vault.append({
        "record_id": record_id,
        "record_type": record_type,
        "key": key,
        "content": content,
        "metadata": metadata or {},
        "timestamp": time.time(),
    })
    return record_id


def query_memory_vault(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Performs keyword and key-prefix search over stored memories."""
    q_lower = query.lower()
    matches = []
    for item in reversed(_memory_vault):
        if q_lower in item["key"].lower() or q_lower in item["content"].lower():
            matches.append(item)
            if len(matches) >= limit:
                break
    return matches


def save_checkpoint_state(thread_id: str, step_index: int, state_payload: Dict[str, Any]) -> str:
    """Saves a state checkpoint snapshot."""
    checkpoint_id = f"chk_{thread_id}_{int(time.time() * 1000)}"
    _checkpoints[checkpoint_id] = {
        "checkpoint_id": checkpoint_id,
        "thread_id": thread_id,
        "step_index": step_index,
        "state_payload": state_payload,
        "created_at": time.time(),
    }
    return checkpoint_id
