"""
Atlas Schemas (Pydantic V2)
Execution actions, atomic step outcomes, and execution summaries.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolActionType(str, Enum):
    SHELL_COMMAND = "shell_command"
    WRITE_FILE = "write_file"
    READ_FILE = "read_file"
    PATCH_FILE = "patch_file"
    INSPECT_ENV = "inspect_env"
    LIST_DIR = "list_dir"


class ToolAction(BaseModel):
    """An atomic low-level tool action executed by Atlas."""
    action_type: ToolActionType = Field(description="The category of tool action to perform")
    command: Optional[str] = Field(default=None, description="Shell command string if action is shell_command")
    file_path: Optional[str] = Field(default=None, description="Target filesystem path")
    content: Optional[str] = Field(default=None, description="Content to write or prepend")
    target_snippet: Optional[str] = Field(default=None, description="Exact snippet to replace for patch_file")
    replacement_snippet: Optional[str] = Field(default=None, description="Replacement snippet for patch_file")
    timeout_seconds: float = Field(default=30.0, description="Max execution time in seconds")


class StepExecutionResult(BaseModel):
    """Deterministic result of executing an atomic task step."""
    step_id: int = Field(description="Index of the executed TaskStep")
    title: str = Field(description="Title of the executed step")
    action_type: str = Field(description="Type of action performed")
    status: str = Field(description="Outcome status: SUCCESS, FAILED, BLOCKED, or SKIPPED")
    stdout: str = Field(default="", description="Captured standard output")
    stderr: str = Field(default="", description="Captured standard error")
    exit_code: int = Field(default=0, description="Process exit code (0 for success)")
    error_message: Optional[str] = Field(default=None, description="Explicit failure explanation if any")
    execution_time_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
    artifacts_created: List[str] = Field(default_factory=list, description="Files created or modified")


class ExecutionSummary(BaseModel):
    """Consolidated summary of a multi-step blueprint execution."""
    goal: str = Field(description="The primary directive that was executed")
    total_steps: int = Field(description="Total number of steps in blueprint")
    successful_steps: int = Field(description="Count of successfully executed steps")
    failed_steps: int = Field(description="Count of failed steps")
    overall_status: str = Field(description="Overall execution verdict: SUCCESS, PARTIAL, or FAILED")
    elapsed_time_ms: float = Field(default=0.0, description="Total wall-clock execution time")
    results: List[StepExecutionResult] = Field(default_factory=list, description="Ordered step results")
