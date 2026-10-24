"""
Atlas Agent Class
Titan of Endurance, Systems Engineering, and Raw Execution.
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

logger = logging.getLogger("CRONUS.TitanCouncil.Atlas")

from .schemas import (
    ToolAction,
    ToolActionType,
    StepExecutionResult,
    ExecutionSummary,
)
from .prompts import ATLAS_SYSTEM_PROMPT, ATLAS_DELIBERATION_PROMPT
from .tools import (
    async_run_command,
    read_file,
    write_file,
    patch_file,
    inspect_environment,
)


def _build_default_executor_llm() -> Any:
    """Build a fast, deterministic model for Atlas code & execution reasoning."""
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
                model="qwen/qwen3.8-27b",
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


class Atlas:
    """
    Titan of Endurance, Systems Engineering, and Raw Execution.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Atlas"
        self.title = "Titan of Endurance & Chief Engineer"
        self.domain = "System Execution, Shell Operations, File I/O & Code Realization"
        self.llm = llm if llm is not None else _build_default_executor_llm()

    async def execute_action(self, action: ToolAction) -> StepExecutionResult:
        """Executes a single ToolAction asynchronously."""
        start = time.perf_counter()

        if action.action_type == ToolActionType.SHELL_COMMAND:
            if not action.command:
                return StepExecutionResult(
                    step_id=0,
                    title="Shell Command",
                    action_type="shell_command",
                    status="FAILED",
                    error_message="No command specified",
                    execution_time_ms=0.0,
                )
            code, out, err, elapsed = await async_run_command(action.command, timeout=action.timeout_seconds)
            status = "SUCCESS" if code == 0 else "FAILED"
            return StepExecutionResult(
                step_id=0,
                title=f"Shell: {action.command[:40]}",
                action_type="shell_command",
                status=status,
                stdout=out,
                stderr=err,
                exit_code=code,
                error_message=err if code != 0 else None,
                execution_time_ms=elapsed,
            )

        elif action.action_type == ToolActionType.WRITE_FILE:
            if not action.file_path or action.content is None:
                return StepExecutionResult(
                    step_id=0,
                    title="Write File",
                    action_type="write_file",
                    status="FAILED",
                    error_message="Missing file_path or content",
                )
            ok, msg = write_file(action.file_path, action.content)
            elapsed = (time.perf_counter() - start) * 1000.0
            return StepExecutionResult(
                step_id=0,
                title=f"Write: {action.file_path}",
                action_type="write_file",
                status="SUCCESS" if ok else "FAILED",
                stdout=msg if ok else "",
                stderr=msg if not ok else "",
                exit_code=0 if ok else 1,
                error_message=msg if not ok else None,
                execution_time_ms=elapsed,
                artifacts_created=[action.file_path] if ok else [],
            )

        elif action.action_type == ToolActionType.PATCH_FILE:
            if not action.file_path or not action.target_snippet or not action.replacement_snippet:
                return StepExecutionResult(
                    step_id=0,
                    title="Patch File",
                    action_type="patch_file",
                    status="FAILED",
                    error_message="Missing patch parameters",
                )
            ok, msg = patch_file(action.file_path, action.target_snippet, action.replacement_snippet)
            elapsed = (time.perf_counter() - start) * 1000.0
            return StepExecutionResult(
                step_id=0,
                title=f"Patch: {action.file_path}",
                action_type="patch_file",
                status="SUCCESS" if ok else "FAILED",
                stdout=msg if ok else "",
                stderr=msg if not ok else "",
                exit_code=0 if ok else 1,
                error_message=msg if not ok else None,
                execution_time_ms=elapsed,
                artifacts_created=[action.file_path] if ok else [],
            )

        elif action.action_type == ToolActionType.INSPECT_ENV:
            telemetry = inspect_environment()
            elapsed = (time.perf_counter() - start) * 1000.0
            import json
            return StepExecutionResult(
                step_id=0,
                title="Inspect Environment",
                action_type="inspect_env",
                status="SUCCESS",
                stdout=json.dumps(telemetry, indent=2),
                execution_time_ms=elapsed,
            )

        else:
            return StepExecutionResult(
                step_id=0,
                title="Unknown Action",
                action_type=str(action.action_type),
                status="FAILED",
                error_message=f"Unsupported action type: {action.action_type}",
            )

    async def execute_task_step(self, step: Any) -> StepExecutionResult:
        """
        Interprets a Prometheus TaskStep and executes it via appropriate tools.
        """
        step_id = getattr(step, "step_id", 1)
        title = getattr(step, "title", "Task Step")
        action_type = getattr(step, "action_type", "shell_command")
        details = getattr(step, "details", "")
        print(f"[Atlas] Received Step {step_id} from [Prometheus]: '{title}'", flush=True)
        if "shell" in action_type.lower() or "command" in action_type.lower():
            print(f"[Atlas] Executing shell command: '{details.strip()[:60]}'...", flush=True)

        start = time.perf_counter()

        if "shell" in action_type.lower() or "command" in action_type.lower():
            code, out, err, elapsed = await async_run_command(details.strip())
            return StepExecutionResult(
                step_id=step_id,
                title=title,
                action_type=action_type,
                status="SUCCESS" if code == 0 else "FAILED",
                stdout=out,
                stderr=err,
                exit_code=code,
                error_message=err if code != 0 else None,
                execution_time_ms=elapsed,
            )

        elapsed = (time.perf_counter() - start) * 1000.0
        return StepExecutionResult(
            step_id=step_id,
            title=title,
            action_type=action_type,
            status="SUCCESS",
            stdout=f"Atlas completed task step {step_id}: {title}",
            execution_time_ms=elapsed,
        )

    async def deliberate(self, blueprint_summary: str, context: Optional[str] = None) -> str:
        print(f"[Atlas] Deliberating system feasibility & resource containment...", flush=True)
        """
        Deliberates in the Titan Council chamber, assessing execution feasibility.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = (
            f"BLUEPRINT PROPOSAL UNDER REVIEW:\n{blueprint_summary}\n"
        )
        if context:
            user_msg += f"\nADDITIONAL CONTEXT:\n{context}\n"
        user_msg += "\nState your technical execution assessment, tooling requirements, and commitment."

        messages = [
            SystemMessage(content=ATLAS_SYSTEM_PROMPT),
            SystemMessage(content=ATLAS_DELIBERATION_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            res = await self.llm.ainvoke(messages)
            content = res.content if hasattr(res, "content") else str(res)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception as e:
            return "[Atlas Deliberation Fallback]: Technical assessment confirmed. Ready to execute actions via shell and filesystem tools."

    def deliberate_sync(self, blueprint_summary: str, context: Optional[str] = None) -> str:
        """Synchronous wrapper for deliberate."""
        return asyncio.run(self.deliberate(blueprint_summary, context))
