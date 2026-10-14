"""
Themis Schemas (Pydantic V2)
Quality audits, safety verifications, and compliance findings.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditCategory(str, Enum):
    SECURITY = "security"
    SYNTAX = "syntax"
    LOGIC = "logic"
    COMPLIANCE = "compliance"
    EFFICIENCY = "efficiency"


class AuditSeverity(str, Enum):
    PASS = "PASS"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditFinding(BaseModel):
    """An individual audit observation or compliance violation."""
    category: AuditCategory = Field(description="Category of the audit observation")
    severity: AuditSeverity = Field(description="Severity rating")
    title: str = Field(description="Brief title of the finding")
    description: str = Field(description="Detailed explanation of the issue or verification")
    remediation: Optional[str] = Field(default=None, description="Recommended fix or preventive action")


class VerificationResult(BaseModel):
    """Outcome of a falsifiable test or execution verification."""
    step_id: int = Field(description="Index of verified TaskStep")
    is_valid: bool = Field(description="Whether the verification passed")
    falsifiable_check_passed: bool = Field(description="True if verification condition was met")
    test_output: str = Field(default="", description="Captured test or command output")
    audit_notes: str = Field(default="", description="Themis review commentary")


class AuditReport(BaseModel):
    """Formal audit report produced by Themis."""
    target_name: str = Field(description="Name of artifact, blueprint, or code audited")
    verdict: str = Field(description="Audit verdict: APPROVED, REVISE, or REJECTED")
    score: float = Field(default=10.0, description="Quality score from 0.0 to 10.0")
    findings: List[AuditFinding] = Field(default_factory=list, description="List of findings")
    summary: str = Field(description="Executive summary of the audit")
