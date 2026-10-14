"""
Atlas Module - Titan Council
Titan of Endurance, Systems Engineering, and Raw Execution.
"""

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
from .agent import Atlas

__all__ = [
    "Atlas",
    "ToolAction",
    "ToolActionType",
    "StepExecutionResult",
    "ExecutionSummary",
    "ATLAS_SYSTEM_PROMPT",
    "ATLAS_DELIBERATION_PROMPT",
    "async_run_command",
    "read_file",
    "write_file",
    "patch_file",
    "inspect_environment",
]
