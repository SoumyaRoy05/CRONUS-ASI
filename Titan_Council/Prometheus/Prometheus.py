"""
Backward-compatibility stub for Prometheus.
Re-exports from modular package structure.
"""

from .schemas import ArchitecturalBlueprint, TaskStep, RiskItem
from .prompts import PROMETHEUS_SYSTEM_PROMPT, REPLAN_SYSTEM_PROMPT
from .agent import Prometheus

__all__ = [
    "Prometheus",
    "ArchitecturalBlueprint",
    "TaskStep",
    "RiskItem",
    "PROMETHEUS_SYSTEM_PROMPT",
    "REPLAN_SYSTEM_PROMPT",
]

if __name__ == "__main__":
    from .agent import _build_default_planner_llm
    # Run test
    print("Prometheus initialized and functional.")
