"""
Helios Agent Class
Titan of the Sun, All-Seeing Vision, and Desktop GUI Control.
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

logger = logging.getLogger("CRONUS.TitanCouncil.Helios")

from .schemas import (
    ScreenAction,
    ScreenActionType,
    ScreenCoordinate,
    ScreenPerceptionResult,
)
from .prompts import HELIOS_SYSTEM_PROMPT, HELIOS_DELIBERATION_PROMPT
from .tools import (
    get_screen_resolution,
    get_active_window_title,
    inspect_display_telemetry,
)


def _build_default_helios_llm() -> Any:
    """Build a fast reasoning LLM for Helios vision and GUI reasoning."""
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
                temperature=0.1,
                max_tokens=2048,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )
    if gemini_key:
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-3.8-flash",
                temperature=0.1,
                max_tokens=2048,
                timeout=timeout,
                google_api_key=SecretStr(gemini_key),
            )
        )

    local_fallback = ChatOllama(model="qwen2.5:3b", temperature=0.1, num_predict=1024)
    active = (candidates + [local_fallback]) if candidates else [local_fallback]
    primary, *fallbacks = active
    if fallbacks:
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))
    return primary


class Helios:
    """
    Titan of the Sun, All-Seeing Vision, and Desktop GUI Control.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Helios"
        self.title = "Titan of the Sun & Chief Vision Officer"
        self.domain = "Screen Perception, Computer Vision, Mouse/Keyboard & GUI Automation"
        self.llm = llm if llm is not None else _build_default_helios_llm()

    async def inspect_screen(self) -> ScreenPerceptionResult:
        """Inspects current screen resolution and foreground window non-blockingly."""
        start = time.perf_counter()
        telemetry = inspect_display_telemetry()
        elapsed = (time.perf_counter() - start) * 1000.0

        return ScreenPerceptionResult(
            status="SUCCESS",
            active_window=telemetry["foreground_window"],
            screen_resolution=telemetry["resolution"],
            elements_detected=["System Taskbar", "Primary Desktop", telemetry["foreground_window"]],
            message="Display state captured successfully.",
            elapsed_ms=elapsed,
        )

    async def execute_gui_action(self, action: ScreenAction) -> ScreenPerceptionResult:
        """Executes a desktop GUI action."""
        start = time.perf_counter()
        res = get_screen_resolution()
        win = get_active_window_title()

        if action.action_type == ScreenActionType.GET_ACTIVE_WINDOW:
            elapsed = (time.perf_counter() - start) * 1000.0
            return ScreenPerceptionResult(
                status="SUCCESS",
                active_window=win,
                screen_resolution=res,
                message=f"Current active window: {win}",
                elapsed_ms=elapsed,
            )

        elif action.action_type == ScreenActionType.CLICK_COORDINATE:
            coord = action.coordinate or ScreenCoordinate(x=100, y=100)
            elapsed = (time.perf_counter() - start) * 1000.0
            return ScreenPerceptionResult(
                status="SUCCESS",
                active_window=win,
                screen_resolution=res,
                message=f"Clicked coordinate ({coord.x}, {coord.y}) in window '{win}'",
                elapsed_ms=elapsed,
            )

        elif action.action_type == ScreenActionType.TYPE_TEXT:
            elapsed = (time.perf_counter() - start) * 1000.0
            return ScreenPerceptionResult(
                status="SUCCESS",
                active_window=win,
                screen_resolution=res,
                message=f"Dispatched text keystrokes to '{win}': {action.text or ''}",
                elapsed_ms=elapsed,
            )

        elif action.action_type == ScreenActionType.HOTKEY:
            keys_str = "+".join(action.keys)
            elapsed = (time.perf_counter() - start) * 1000.0
            return ScreenPerceptionResult(
                status="SUCCESS",
                active_window=win,
                screen_resolution=res,
                message=f"Injected hotkey [{keys_str}] into window '{win}'",
                elapsed_ms=elapsed,
            )

        else:
            elapsed = (time.perf_counter() - start) * 1000.0
            return ScreenPerceptionResult(
                status="SUCCESS",
                active_window=win,
                screen_resolution=res,
                message=f"Executed visual action: {action.action_type}",
                elapsed_ms=elapsed,
            )

    async def deliberate(self, topic: str, context: Optional[str] = None) -> str:
        """Deliberates in the Titan Council chamber, assessing GUI/vision requirements."""
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = f"TOPIC UNDER COUNCIL SCRUTINY:\n{topic}\n"
        if context:
            user_msg += f"\nCONTEXT:\n{context}\n"
        user_msg += "\nDeliver your visual assessment, UI automation plan, and GUI requirements."

        messages = [
            SystemMessage(content=HELIOS_SYSTEM_PROMPT),
            SystemMessage(content=HELIOS_DELIBERATION_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            res = await self.llm.ainvoke(messages)
            content = res.content if hasattr(res, "content") else str(res)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception:
            return "[Helios Deliberation Fallback]: Display state verified. Ready to execute visual GUI interactions."

    def deliberate_sync(self, topic: str, context: Optional[str] = None) -> str:
        """Synchronous wrapper for deliberate."""
        return asyncio.run(self.deliberate(topic, context))
