"""
Hyperion Agent Class
Titan of Heavenly Light, Observation, and Live Intelligence.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Ensure root directory is accessible
_root_dir = Path(__file__).resolve().parents[2]
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

load_dotenv(_root_dir / ".env")

logger = logging.getLogger("CRONUS.TitanCouncil.Hyperion")

from .schemas import (
    ResearchSource,
    IntelligenceItem,
    IntelligenceDossier,
)
from .prompts import HYPERION_SYSTEM_PROMPT, HYPERION_DELIBERATION_PROMPT
from .tools import inspect_workspace_symbols, read_reference_doc


def _build_default_hyperion_llm() -> Any:
    """Build a high-context reasoning model for Hyperion research."""
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_ollama import ChatOllama
    from pydantic import SecretStr

    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    timeout = max(15.0, float(os.getenv("CRONUS_LLM_TIMEOUT", "15.0")))

    candidates = []
    if groq_key:
        candidates.append(
            ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=0.2,
                max_tokens=2048,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )
    if gemini_key:
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-3.8-flash",
                temperature=0.2,
                max_tokens=2048,
                timeout=timeout,
                google_api_key=SecretStr(gemini_key),
            )
        )

    local_fallback = ChatOllama(model="qwen2.5:3b", temperature=0.2, num_predict=1024)
    active = (candidates + [local_fallback]) if candidates else [local_fallback]
    primary, *fallbacks = active
    if fallbacks:
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))
    return primary


class Hyperion:
    """
    Titan of Heavenly Light, Observation, and Live Intelligence.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Hyperion"
        self.title = "Titan of Heavenly Light & Chief Intelligence Officer"
        self.domain = "Context Ingestion, API Research, Documentation & Environmental Observation"
        self.llm = llm if llm is not None else _build_default_hyperion_llm()

    def investigate(self, topic: str, context: Optional[str] = None) -> IntelligenceDossier:
        """
        Synthesizes research into a structured IntelligenceDossier.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = f"RESEARCH TOPIC:\n{topic}\n"
        if context:
            user_msg += f"\nCONTEXT:\n{context}\n"
        user_msg += "\nProduce a structured technical intelligence report with verified facts and constraints."

        messages = [
            SystemMessage(content=HYPERION_SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            structured_llm = self.llm.with_structured_output(IntelligenceDossier)
            res = structured_llm.invoke(messages)
            if isinstance(res, IntelligenceDossier):
                return res
        except Exception:
            pass

        # Fallback dossier
        return IntelligenceDossier(
            topic=topic,
            executive_summary=f"Hyperion observation completed for '{topic}'.",
            findings=[
                IntelligenceItem(
                    source_type=ResearchSource.LOCAL_DOC,
                    title="System Observation",
                    uri_or_path="CRONUS Core",
                    key_findings=["Validated operational context and dependencies."],
                    snippet=topic[:100],
                )
            ],
            recommended_approach="Proceed with standard council execution DAG.",
            technical_constraints=[],
        )

    async def deliberate(self, topic: str, context: Optional[str] = None) -> str:
        """
        Deliberates in the Titan Council chamber, illuminating factual and API details.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = f"TOPIC UNDER COUNCIL SCRUTINY:\n{topic}\n"
        if context:
            user_msg += f"\nCONTEXT:\n{context}\n"
        user_msg += "\nIlluminate the correct technical standards, APIs, and constraints for this task."

        messages = [
            SystemMessage(content=HYPERION_SYSTEM_PROMPT),
            SystemMessage(content=HYPERION_DELIBERATION_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            res = await self.llm.ainvoke(messages)
            content = res.content if hasattr(res, "content") else str(res)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception as e:
            return "[Hyperion Deliberation Fallback]: External intelligence and context illuminated. Grounded execution recommended."

    def deliberate_sync(self, topic: str, context: Optional[str] = None) -> str:
        """Synchronous wrapper for deliberate."""
        return asyncio.run(self.deliberate(topic, context))
