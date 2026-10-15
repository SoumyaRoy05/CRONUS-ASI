"""
Coeus Schemas (Pydantic V2)
Persistent memory records, state checkpoints, and contextual search results.
"""

from __future__ import annotations
from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryRecordType(str, Enum):
    CONVERSATION = "conversation"
    CHECKPOINT = "checkpoint"
    CREATOR_PREFERENCE = "creator_preference"
    SYSTEM_STATE = "system_state"
    FACT = "fact"


class MemoryRecord(BaseModel):
    """An atomic persistent memory record stored in Coeus vault."""
    record_id: str = Field(description="Unique UUID or key hash")
    record_type: MemoryRecordType = Field(description="Category of memory stored")
    key: str = Field(description="Searchable identifier or keyword")
    content: str = Field(description="Content text or serialized state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary contextual tags")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of creation")
    relevance_score: float = Field(default=1.0, description="Match score if returned by query")


class MemorySearchResult(BaseModel):
    """Result of a memory recall query."""
    query: str = Field(description="Original search query")
    records: List[MemoryRecord] = Field(default_factory=list, description="Retrieved matching records")
    total_found: int = Field(default=0, description="Count of matched items")
    search_strategy: str = Field(default="exact_and_lexical", description="Retrieval algorithm used")
    elapsed_ms: float = Field(default=0.0, description="Query execution time in milliseconds")


class CheckpointState(BaseModel):
    """Stateful checkpoint snapshot for LangGraph or agent session persistence."""
    checkpoint_id: str = Field(description="Unique checkpoint identifier")
    thread_id: str = Field(default="cronus_main", description="Session thread ID")
    step_index: int = Field(default=0, description="Step index within execution graph")
    state_payload: Dict[str, Any] = Field(default_factory=dict, description="State dictionary")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
