"""
Prometheus Agent
Titan of Forethought, Systems Architecture, and Strategic Planning.
"""

from __future__ import annotations

import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, List, Optional

from dotenv import load_dotenv

# Ensure root directory is accessible for imports
_root_dir = Path(__file__).resolve().parents[2]
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

load_dotenv(_root_dir / ".env")

logger = logging.getLogger("CRONUS.TitanCouncil.Prometheus")

from .schemas import ArchitecturalBlueprint, TaskStep, RiskItem
from .prompts import PROMETHEUS_SYSTEM_PROMPT, REPLAN_SYSTEM_PROMPT

def _build_default_planner_llm() -> Any:
    """Build a high-token reasoning LLM waterfall tuned specifically for Prometheus planning."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_ollama import ChatOllama
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr

    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    timeout = max(20.0, float(os.getenv("CRONUS_LLM_TIMEOUT", "20.0")))

    candidates = []

    if groq_key:
        candidates.append(
            ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=0.2,
                max_tokens=3072,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )
        candidates.append(
            ChatGroq(
                model="openai/gpt-oss-20b",
                temperature=0.2,
                max_tokens=3072,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )

    if gemini_key:
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                temperature=0.2,
                max_tokens=3072,
                google_api_key=SecretStr(gemini_key),
            )
        )
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-pro-latest",
                temperature=0.2,
                max_tokens=3072,
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
                    temperature=0.2,
                    max_tokens=3072,
                    timeout=timeout,
                )
            )
        except Exception as e:
            logger.warning("Failed to initialize NVIDIA Nemotron: %s", e)

    # Local Ollama fallback
    local_fallback = ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"), temperature=0.2, num_predict=1024)

    active_candidates = (candidates + [local_fallback]) if candidates else [local_fallback]
    primary, *fallbacks = active_candidates
    if fallbacks:
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))
    return primary


# =============================================================================
# 4. PROMETHEUS AGENT CLASS
# =============================================================================

class Prometheus:
    """
    Titan of Forethought, Systems Architecture, and Strategic Planning.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Prometheus"
        self.title = "Titan of Forethought & Grand Architect"
        self.domain = "Systems Architecture, Strategic Planning & Task Decomposition"

        if llm is not None:
            self.llm = llm
        else:
            self.llm = _build_default_planner_llm()

    def plan(
        self,
        directive: str,
        workspace_context: Optional[str] = None
    ) -> ArchitecturalBlueprint:
        print(f"[Prometheus] Formulating architectural blueprint for directive: '{directive}'", flush=True)
        """
        Formulate a comprehensive Master Blueprint and execution graph for a directive.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_content = f"DIRECTIVE FROM CREATOR SOUMYA ROY:\n{directive}\n"
        if workspace_context:
            user_content += f"\nWORKSPACE CONTEXT & ENVIRONMENT:\n{workspace_context}\n"

        user_content += (
            "\nProduce the complete ArchitecturalBlueprint JSON object. "
            "Ensure all steps are atomic, dependency-ordered, and contain falsifiable verification checks."
        )

        messages = [
            SystemMessage(content=PROMETHEUS_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        # 1. Attempt structured output first
        try:
            structured_llm = self.llm.with_structured_output(ArchitecturalBlueprint)
            result = structured_llm.invoke(messages)
            if isinstance(result, ArchitecturalBlueprint):
                return result
            elif isinstance(result, dict):
                return ArchitecturalBlueprint(**result)
        except Exception as e:
            logger.debug(f"Direct structured output fallback triggered: {e}")

        # 2. Fallback: Direct invocation with robust JSON extraction
        response = self.llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        return self._parse_json_blueprint(raw_text, directive)

    def replan(
        self,
        current_blueprint: ArchitecturalBlueprint,
        failed_step_id: int,
        error_log: str
    ) -> ArchitecturalBlueprint:
        print(f"[Prometheus] Step {failed_step_id} failed with error: '{error_log[:80]}'. Formulating adaptive recovery blueprint...", flush=True)
        """
        Re-evaluate the blueprint in response to an execution failure, producing a revised plan.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_content = (
            f"ORIGINAL BLUEPRINT:\n{current_blueprint.model_dump_json(indent=2)}\n\n"
            f"FAILED STEP ID: {failed_step_id}\n"
            f"ERROR LOG / REASON:\n{error_log}\n\n"
            "Formulate a revised ArchitecturalBlueprint overcoming this failure."
        )

        messages = [
            SystemMessage(content=REPLAN_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        try:
            structured_llm = self.llm.with_structured_output(ArchitecturalBlueprint)
            result = structured_llm.invoke(messages)
            if isinstance(result, ArchitecturalBlueprint):
                return result
            elif isinstance(result, dict):
                return ArchitecturalBlueprint(**result)
        except Exception as e:
            logger.debug(f"Replan structured output fallback triggered: {e}")

        response = self.llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        return self._parse_json_blueprint(raw_text, current_blueprint.goal)

    def _parse_json_blueprint(self, raw_text: str, fallback_goal: str) -> ArchitecturalBlueprint:
        """Safely extract and parse JSON from LLM text output."""
        clean_text = raw_text.strip()
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        else:
            first_brace = clean_text.find("{")
            last_brace = clean_text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                clean_text = clean_text[first_brace : last_brace + 1]

        try:
            data = json.loads(clean_text)
            return ArchitecturalBlueprint(**data)
        except Exception as e:
            logger.warning(f"Prometheus JSON parse failed ({e}), constructing synthesized blueprint.")
            return ArchitecturalBlueprint(
                goal=fallback_goal,
                summary="Synthesized fallback execution plan.",
                architecture_overview="Direct execution required.",
                files_to_touch=[],
                steps=[
                    TaskStep(
                        step_id=1,
                        title="Execute Primary Objective",
                        assigned_agent="Atlas",
                        action_type="design",
                        details=fallback_goal,
                        dependencies=[],
                        verification_check="Task completed successfully.",
                        fallback_plan="Request manual review."
                    )
                ],
                risk_matrix=[
                    RiskItem(
                        risk="Output required fallback synthesis",
                        severity="LOW",
                        mitigation="Proceed with foundational execution step."
                    )
                ],
                estimated_effort="Standard"
            )

    @staticmethod
    def to_dict(blueprint: ArchitecturalBlueprint) -> dict[str, Any]:
        """Convert blueprint to a clean dictionary."""
        return blueprint.model_dump()

    @staticmethod
    def to_json(blueprint: ArchitecturalBlueprint, indent: int = 2) -> str:
        """Serialize blueprint to a formatted JSON string."""
        return blueprint.model_dump_json(indent=indent)

    @staticmethod
    def format_markdown(blueprint: ArchitecturalBlueprint) -> str:
        """Render an ArchitecturalBlueprint into a formatted Markdown report."""
        lines = [
            f"# [PROMETHEUS MASTER BLUEPRINT]: {blueprint.goal}",
            f"**Effort Rating**: `{blueprint.estimated_effort}`\n",
            "## Executive Summary",
            f"{blueprint.summary}\n",
            "## Architectural Design & Contracts",
            f"{blueprint.architecture_overview}\n",
        ]

        if blueprint.files_to_touch:
            lines.append("## Impacted Files")
            for f in blueprint.files_to_touch:
                lines.append(f"- `{f}`")
            lines.append("")

        lines.append("## Sequenced Execution Graph")
        lines.append("| Step | Title | Agent | Action Type | Dependencies | Verification |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for s in blueprint.steps:
            deps = ", ".join(str(d) for d in s.dependencies) if s.dependencies else "None"
            lines.append(
                f"| `{s.step_id}` | **{s.title}** | `{s.assigned_agent}` | `{s.action_type}` | {deps} | {s.verification_check} |"
            )
        lines.append("")

        lines.append("### Detailed Step Directives")
        for s in blueprint.steps:
            lines.append(f"#### Step {s.step_id}: {s.title}")
            lines.append(f"- **Assigned Agent**: `{s.assigned_agent}` (`{s.action_type}`)")
            lines.append(f"- **Directive**: {s.details}")
            lines.append(f"- **Verification**: {s.verification_check}")
            lines.append(f"- **Fallback Contingency**: {s.fallback_plan}")
            lines.append("")

        if blueprint.risk_matrix:
            lines.append("## Pre-Mortem Risk Matrix")
            lines.append("| Risk / Failure Mode | Severity | Pre-emptive Mitigation |")
            lines.append("| :--- | :--- | :--- |")
            for r in blueprint.risk_matrix:
                lines.append(f"| {r.risk} | **`{r.severity}`** | {r.mitigation} |")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# 5. STANDALONE VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TITAN COUNCIL: PROMETHEUS INITIALIZATION")
    print("=" * 70)

    agent = Prometheus()
    print(f"[+] Titan Online: {agent.name} - {agent.title}")
    print(f"[+] Domain: {agent.domain}")

    test_directive = "Design a low-latency audio ring buffer for Cronus ears"
    print(f"\n[>] Formulating Blueprint for: '{test_directive}'...\n")

    try:
        plan = agent.plan(
            directive=test_directive,
            workspace_context="CRONUS Voice Assistant / Python 3.13 / Windows / Sounddevice"
        )
        print(agent.format_markdown(plan))
        print("\n[+] SUCCESS: Prometheus generated a verified Master Blueprint!")
    except Exception as e:
        print(f"[-] Execution error: {e}")
        import traceback
        traceback.print_exc()
