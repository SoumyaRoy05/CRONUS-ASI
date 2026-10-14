"""
Hyperion Module - Titan Council
Titan of Heavenly Light, Observation, and Live Intelligence.
"""

from .schemas import (
    ResearchSource,
    IntelligenceItem,
    IntelligenceDossier,
)
from .prompts import HYPERION_SYSTEM_PROMPT, HYPERION_DELIBERATION_PROMPT
from .tools import inspect_workspace_symbols, read_reference_doc
from .agent import Hyperion

__all__ = [
    "Hyperion",
    "ResearchSource",
    "IntelligenceItem",
    "IntelligenceDossier",
    "HYPERION_SYSTEM_PROMPT",
    "HYPERION_DELIBERATION_PROMPT",
    "inspect_workspace_symbols",
    "read_reference_doc",
]
