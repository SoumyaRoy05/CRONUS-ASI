"""
Prometheus Schemas (Pydantic V2)
Structured Blueprint, atomic task steps, and risk matrix.
"""

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class TaskStep(BaseModel):
    """An atomic, sequenced step in the Master Blueprint."""
    step_id: int = Field(description="Sequential 1-based index of the step")
    title: str = Field(description="Concise, action-oriented title of the step")
    assigned_agent: str = Field(
        default="Atlas",
        description="Target Titan agent (Atlas, Hyperion, Themis, Prometheus)"
    )
    action_type: str = Field(
        description="Type of action: write_file, shell_command, web_research, design, or verification"
    )
    details: str = Field(description="Exhaustive technical instructions for the executing agent")
    dependencies: List[int] = Field(
        default_factory=list,
        description="List of step_ids that must complete before this step starts"
    )
    verification_check: str = Field(
        description="A falsifiable condition or test command proving step success"
    )
    fallback_plan: str = Field(
        description="Pre-computed contingency if this step encounters an error"
    )


class RiskItem(BaseModel):
    """An anticipated failure mode and its pre-emptive mitigation."""
    risk: str = Field(description="Potential failure point or obstacle")
    severity: str = Field(description="Severity rating: LOW, MEDIUM, HIGH, or CRITICAL")
    mitigation: str = Field(description="Pre-emptive architectural countermeasure")


class ArchitecturalBlueprint(BaseModel):
    """The complete, deterministic Master Blueprint produced by Prometheus."""
    goal: str = Field(description="The primary directive established by creator Soumya Roy")
    summary: str = Field(description="Executive technical summary of the proposed solution")
    architecture_overview: str = Field(description="Component design, data flow, and contracts")
    files_to_touch: List[str] = Field(
        default_factory=list,
        description="List of file paths that will be created or modified"
    )
    steps: List[TaskStep] = Field(
        default_factory=list,
        description="Ordered sequence of atomic execution tasks"
    )
    risk_matrix: List[RiskItem] = Field(
        default_factory=list,
        description="Anticipated failure modes and their mitigations"
    )
    estimated_effort: str = Field(
        default="Direct Execution",
        description="Estimated complexity or computational weight"
    )
