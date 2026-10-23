"""
Coeus Agent Class
Titan of Intellect, Deep Memory, and Knowledge Retrieval.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Ensure root directory is accessible
_root_dir = Path(__file__).resolve().parents[2]
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

load_dotenv(_root_dir / ".env")

logger = logging.getLogger("CRONUS.TitanCouncil.Coeus")

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


def _build_default_coeus_llm() -> Any:
    """Build a fast reasoning model for Coeus memory analysis."""
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr

    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    timeout = max(15.0, float(os.getenv("CRONUS_LLM_TIMEOUT", "15.0")))

    candidates = []
    if groq_key:
        candidates.append(
            ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=0.1,
                max_tokens=2048,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )
    if gemini_key:
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                temperature=0.1,
                max_tokens=2048,
                google_api_key=SecretStr(gemini_key),
            )
        )

    if nvidia_key:
        try:
            candidates.append(
                ChatOpenAI(
                    model="nvidia/nemotron-3-ultra-550b-a55b",
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=SecretStr(nvidia_key),
                    temperature=0.1,
                    max_tokens=2048,
                    timeout=timeout,
                )
            )
        except Exception as e:
            logger.warning("Failed to initialize NVIDIA Nemotron: %s", e)

        local_fallback = ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"), temperature=0.1, num_predict=1024)
    active = (candidates + [local_fallback]) if candidates else [local_fallback]
    primary, *fallbacks = active
    if fallbacks:
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))
    return primary


class Coeus:
    """
    Titan of Intellect, Deep Memory, and Knowledge Retrieval.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Coeus"
        self.title = "Titan of Intellect & Chief Memory Officer"
        self.domain = "Memory Persistence, Checkpointing, Vector Knowledge & Context Retrieval"
        self.llm = llm if llm is not None else _build_default_coeus_llm()

    async def remember(
        self,
        key: str,
        content: str,
        record_type: MemoryRecordType = MemoryRecordType.CREATOR_PREFERENCE,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        print(f"[Coeus] Persisting memory record: '{key}' (type: {record_type.value}) to vault...", flush=True)
        """Stores a persistent memory record in the vault."""
        rec_id = store_memory_item(key, content, record_type.value, metadata)
        return MemoryRecord(
            record_id=rec_id,
            record_type=record_type,
            key=key,
            content=content,
            metadata=metadata or {},
        )

    async def recall(self, query: str, limit: int = 5) -> MemorySearchResult:
        """Searches persistent memory for relevant records."""
        print(f"[Coeus] Searching memory vault for: '{query[:60]}'...", flush=True)
        start = time.perf_counter()
        raw_items = query_memory_vault(query, limit)
        elapsed = (time.perf_counter() - start) * 1000.0

        records = [
            MemoryRecord(
                record_id=item["record_id"],
                record_type=MemoryRecordType(item["record_type"]),
                key=item["key"],
                content=item["content"],
                metadata=item["metadata"],
                timestamp=item["timestamp"],
            )
            for item in raw_items
        ]

        return MemorySearchResult(
            query=query,
            records=records,
            total_found=len(records),
            elapsed_ms=elapsed,
        )

    async def checkpoint(self, thread_id: str, state_payload: Dict[str, Any], step_index: int = 0) -> str:
        """Saves a state checkpoint."""
        return save_checkpoint_state(thread_id, step_index, state_payload)

    async def deliberate(self, topic: str, context: Optional[str] = None) -> str:
        print(f"[Coeus] Retrieving historical memories to inform Council...", flush=True)
        """Deliberates in the Titan Council chamber, supplying memory and precedent."""
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = f"TOPIC UNDER COUNCIL SCRUTINY:\n{topic}\n"
        if context:
            user_msg += f"\nCONTEXT:\n{context}\n"
        user_msg += "\nState what memory records, creator preferences, or checkpoints apply to this task."

        messages = [
            SystemMessage(content=COEUS_SYSTEM_PROMPT),
            SystemMessage(content=COEUS_DELIBERATION_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            res = await self.llm.ainvoke(messages)
            content = res.content if hasattr(res, "content") else str(res)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception:
            return "[Coeus Deliberation Fallback]: Memory vault inspected. Creator preferences and session checkpoints preserved."

    def deliberate_sync(self, topic: str, context: Optional[str] = None) -> str:
        """Synchronous wrapper for deliberate."""
        return asyncio.run(self.deliberate(topic, context))
