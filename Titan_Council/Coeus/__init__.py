"""
Coeus Module - Titan Council
Titan of Intellect, Deep Memory, and Knowledge Retrieval.
"""

from .schemas import (
    MemoryRecord,
    MemoryRecordType,
    MemorySearchResult,
    CheckpointState,
)
from .prompts import COEUS_SYSTEM_PROMPT, COEUS_DELIBERATION_PROMPT
from .tools import (
    store_memory_item,
    query_memory_vault,
    save_checkpoint_state,
)
from .agent import Coeus

__all__ = [
    "Coeus",
    "MemoryRecord",
    "MemoryRecordType",
    "MemorySearchResult",
    "CheckpointState",
    "COEUS_SYSTEM_PROMPT",
    "COEUS_DELIBERATION_PROMPT",
    "store_memory_item",
    "query_memory_vault",
    "save_checkpoint_state",
]
