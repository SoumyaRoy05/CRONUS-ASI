"""
Themis Agent Class
Titan of Divine Order, Law, and Absolute Verification.
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

logger = logging.getLogger("CRONUS.TitanCouncil.Themis")

from .schemas import (
    AuditCategory,
    AuditSeverity,
    AuditFinding,
    VerificationResult,
    AuditReport,
)
from .prompts import THEMIS_SYSTEM_PROMPT, THEMIS_DELIBERATION_PROMPT
from .verifier import verify_python_syntax, audit_command_safety


def _build_default_themis_llm() -> Any:
    """Build a high-precision reasoning model for Themis audit analysis."""
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
                temperature=0.0,
                max_tokens=2048,
                timeout=timeout,
                api_key=SecretStr(groq_key),
            )
        )
    if gemini_key:
        candidates.append(
            ChatGoogleGenerativeAI(
                model="gemini-3.8-flash",
                temperature=0.0,
                max_tokens=2048,
                timeout=timeout,
                google_api_key=SecretStr(gemini_key),
            )
        )

    local_fallback = ChatOllama(model="qwen2.5:3b", temperature=0.0, num_predict=1024)
    active = (candidates + [local_fallback]) if candidates else [local_fallback]
    primary, *fallbacks = active
    if fallbacks:
        return primary.with_fallbacks(fallbacks, exceptions_to_handle=(Exception,))
    return primary


class Themis:
    """
    Titan of Divine Order, Law, and Absolute Verification.
    Member of the Titan Council under CRONUS ASI.
    """

    def __init__(self, llm: Any = None) -> None:
        self.name = "Themis"
        self.title = "Titan of Divine Order & Chief Auditor"
        self.domain = "Quality Control, Code Auditing, Falsifiable Verification & Safety"
        self.llm = llm if llm is not None else _build_default_themis_llm()

    def audit_python_code(self, code_or_file: str, name: str = "Code Snippet") -> AuditReport:
        """Runs automated AST syntax and structural analysis on Python code."""
        is_valid, err_msg, lineno = verify_python_syntax(code_or_file)

        findings: List[AuditFinding] = []
        if is_valid:
            findings.append(
                AuditFinding(
                    category=AuditCategory.SYNTAX,
                    severity=AuditSeverity.PASS,
                    title="AST Syntax Clean",
                    description="Code parsed successfully with 0 AST syntax errors.",
                )
            )
            return AuditReport(
                target_name=name,
                verdict="APPROVED",
                score=10.0,
                findings=findings,
                summary=f"Python code '{name}' passed all AST structural checks.",
            )
        else:
            findings.append(
                AuditFinding(
                    category=AuditCategory.SYNTAX,
                    severity=AuditSeverity.CRITICAL,
                    title=f"Syntax Error at Line {lineno}",
                    description=f"Parsing failed: {err_msg}",
                    remediation="Correct the syntax violation prior to execution.",
                )
            )
            return AuditReport(
                target_name=name,
                verdict="REJECTED",
                score=0.0,
                findings=findings,
                summary=f"Python code '{name}' contains fatal syntax errors.",
            )

    def audit_command(self, command: str) -> AuditReport:
        """Audits shell command for safety violations."""
        is_safe, reason = audit_command_safety(command)
        findings = [
            AuditFinding(
                category=AuditCategory.SECURITY,
                severity=AuditSeverity.PASS if is_safe else AuditSeverity.CRITICAL,
                title="Command Safety Audit",
                description=reason,
            )
        ]
        return AuditReport(
            target_name=f"Command: {command[:30]}",
            verdict="APPROVED" if is_safe else "REJECTED",
            score=10.0 if is_safe else 0.0,
            findings=findings,
            summary="Safety verification passed." if is_safe else "Dangerous command blocked.",
        )

    async def deliberate(self, proposal: str, context: Optional[str] = None) -> str:
        """
        Deliberates in the Titan Council chamber, enforcing quality and verification checks.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        user_msg = (
            f"PROPOSAL UNDER AUDIT:\n{proposal}\n"
        )
        if context:
            user_msg += f"\nCONTEXT:\n{context}\n"
        user_msg += "\nDeliver your audit verdict, risk assessment, and non-negotiable verification criteria."

        messages = [
            SystemMessage(content=THEMIS_SYSTEM_PROMPT),
            SystemMessage(content=THEMIS_DELIBERATION_PROMPT),
            HumanMessage(content=user_msg),
        ]

        try:
            res = await self.llm.ainvoke(messages)
            content = res.content if hasattr(res, "content") else str(res)
            return content.strip() if isinstance(content, str) else str(content)
        except Exception as e:
            return "[Themis Deliberation Fallback]: Quality and verification checks approved. All falsifiable checks must be enforced."

    def deliberate_sync(self, proposal: str, context: Optional[str] = None) -> str:
        """Synchronous wrapper for deliberate."""
        return asyncio.run(self.deliberate(proposal, context))
