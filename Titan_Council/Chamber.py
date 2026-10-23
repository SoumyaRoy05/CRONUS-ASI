"""
Council Chamber - Titan Council Orchestrator
Asynchronous deliberation room where all 6 Titans convene to co-develop the sovereign decree.
Forged for creator Soumya Roy under the sovereign command of CRONUS ASI.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .Prometheus import Prometheus, ArchitecturalBlueprint
from .Atlas import Atlas
from .Themis import Themis
from .Hyperion import Hyperion
from .Helios import Helios
from .Coeus import Coeus

logger = logging.getLogger("CRONUS.TitanCouncil.Chamber")


class CouncilConsensus(BaseModel):
    """The unified, synthesized outcome of an asynchronous Titan Council session."""
    directive: str = Field(description="The primary directive from creator Soumya Roy")
    blueprint: Optional[ArchitecturalBlueprint] = Field(default=None, description="Prometheus Master Blueprint")
    deliberations: Dict[str, str] = Field(default_factory=dict, description="Transcripts of each Titan's stance")
    audit_verdict: str = Field(default="APPROVED", description="Themis quality & safety verdict")
    sovereign_decree: str = Field(description="The synthesized voice/action response for CRONUS")
    total_wall_clock_ms: float = Field(default=0.0, description="Total parallel execution duration")
    sequential_estimate_ms: float = Field(default=0.0, description="Estimated time if executed sequentially")
    concurrency_speedup: float = Field(default=1.0, description="Speedup multiplier achieved via asyncio")


class CouncilChamber:
    """
    The High Chamber of the Titan Council.
    Coordinates Prometheus, Atlas, Themis, Hyperion, Helios, and Coeus via asyncio.
    """

    def __init__(
        self,
        prometheus: Optional[Prometheus] = None,
        atlas: Optional[Atlas] = None,
        themis: Optional[Themis] = None,
        hyperion: Optional[Hyperion] = None,
        helios: Optional[Helios] = None,
        coeus: Optional[Coeus] = None,
    ) -> None:
        self.prometheus = prometheus or Prometheus()
        self.atlas = atlas or Atlas()
        self.themis = themis or Themis()
        self.hyperion = hyperion or Hyperion()
        self.helios = helios or Helios()
        self.coeus = coeus or Coeus()

    async def convene(
        self,
        directive: str,
        workspace_context: Optional[str] = None
    ) -> CouncilConsensus:
        """
        Convenes the full Titan Council using asyncio concurrent gathering.
        Returns the finalized CouncilConsensus with real-time console tracing.
        """
        start_time = time.perf_counter()
        agent_latencies: Dict[str, float] = {}

        print(f"\n[Council Chamber] ==================================================", flush=True)
        print(f"[Council Chamber] Convening Titan Council for directive: '{directive}'", flush=True)
        print(f"[Council Chamber] Phase 1: Tasking [Coeus] (Memory) & [Hyperion] (Intel) in parallel...", flush=True)

        # ---------------------------------------------------------------------
        # PHASE 1: Parallel Context Recall & Intelligence Gathering
        # ---------------------------------------------------------------------
        async def task_coeus():
            t0 = time.perf_counter()
            mem = await self.coeus.recall(directive, limit=3)
            agent_latencies["Coeus"] = (time.perf_counter() - t0) * 1000.0
            return mem

        async def task_hyperion():
            t0 = time.perf_counter()
            dossier = await self.hyperion.deliberate(directive, workspace_context)
            agent_latencies["Hyperion"] = (time.perf_counter() - t0) * 1000.0
            return dossier

        memory_res, hyperion_delib = await asyncio.gather(task_coeus(), task_hyperion())

        context_summary = f"Memory Matches: {memory_res.total_found}. Hyperion Advice: {hyperion_delib[:100]}..."

        print(f"[Council Chamber] [Coeus] provided memory context ({memory_res.total_found} records) to Council.", flush=True)
        print(f"[Council Chamber] [Hyperion] provided technical documentation dossier to Council.", flush=True)
        print(f"[Council Chamber] Phase 2: Dispatching context to [Atlas], [Themis], and [Helios] for peer review...", flush=True)

        # ---------------------------------------------------------------------
        # PHASE 2: Parallel Deliberation & Peer Critique
        # ---------------------------------------------------------------------
        async def task_atlas():
            t0 = time.perf_counter()
            res = await self.atlas.deliberate(directive, context_summary)
            agent_latencies["Atlas"] = (time.perf_counter() - t0) * 1000.0
            return res

        async def task_themis():
            t0 = time.perf_counter()
            res = await self.themis.deliberate(directive, context_summary)
            agent_latencies["Themis"] = (time.perf_counter() - t0) * 1000.0
            return res

        async def task_helios():
            t0 = time.perf_counter()
            res = await self.helios.deliberate(directive, context_summary)
            agent_latencies["Helios"] = (time.perf_counter() - t0) * 1000.0
            return res

        atlas_delib, themis_delib, helios_delib = await asyncio.gather(
            task_atlas(), task_themis(), task_helios()
        )

        print(f"[Council Chamber] Peer deliberations synchronized.", flush=True)
        print(f"[Council Chamber] Phase 3: Tasking [Prometheus] to formulate architectural blueprint...", flush=True)
        print(f"[Council Chamber] Relaying [Hyperion] docs & [Coeus] memories to [Prometheus]...", flush=True)

        # ---------------------------------------------------------------------
        # PHASE 3: Prometheus Blueprint & Sovereign Synthesis
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        blueprint = self.prometheus.plan(directive, workspace_context=context_summary)
        agent_latencies["Prometheus"] = (time.perf_counter() - t0) * 1000.0

        print(f"[Prometheus] Master blueprint formulated ({len(blueprint.steps)} execution steps).", flush=True)
        print(f"[Prometheus] Dispatched blueprint to [Themis] for AST safety verification...", flush=True)

        # Verify blueprint commands with Themis
        audit_verdict = "APPROVED"
        for step in blueprint.steps:
            if getattr(step, "command_or_input", None):
                audit = self.themis.audit_command(step.command_or_input)
                if audit.verdict.value == "REJECTED":
                    audit_verdict = "REJECTED"
                    print(f"[Themis] Step {step.step_id} REJECTED: {audit.summary}", flush=True)

        if audit_verdict == "APPROVED":
            print(f"[Themis] All blueprint steps verified: APPROVED. [Themis] cleared [Atlas] and [Helios] for execution.", flush=True)

        total_wall_clock_ms = (time.perf_counter() - start_time) * 1000.0
        sequential_sum_ms = sum(agent_latencies.values())
        speedup = sequential_sum_ms / total_wall_clock_ms if total_wall_clock_ms > 0 else 1.0

        sovereign_decree = (
            f"The Council of Titans has converged under CRONUS ASI. "
            f"Prometheus has forged a {len(blueprint.steps)}-step blueprint. "
            f"Atlas and Helios stand ready for system and GUI execution, "
            f"while Themis has audited all safety boundaries."
        )

        deliberations = {
            "Hyperion": hyperion_delib,
            "Atlas": atlas_delib,
            "Themis": themis_delib,
            "Helios": helios_delib,
            "Coeus": f"Recalled {memory_res.total_found} relevant memories.",
            "Prometheus": blueprint.summary,
        }

        # Archive blueprint and consensus to PostgreSQL
        try:
            from Database import save_blueprint_record
            bp_record_id = await save_blueprint_record(
                goal=directive,
                rationale=getattr(blueprint, "rationale", ""),
                planner_model="Prometheus/Nemotron-3-Ultra",
                total_steps=len(blueprint.steps),
                fallback_strategy=getattr(blueprint, "fallback_strategy", ""),
                raw_json=blueprint.model_dump() if hasattr(blueprint, "model_dump") else {},
            )
            if bp_record_id:
                print(f"[Council Chamber] Blueprint archived to PostgreSQL (ID: {bp_record_id}).", flush=True)
        except Exception as e:
            logger.debug("Database archiving fallback: %s", e)

        print(f"[Council Chamber] Consensus reached in {total_wall_clock_ms:.1f}ms (Parallel speedup: {speedup:.2f}x).", flush=True)
        print(f"[Council Chamber] Decree formulated: {sovereign_decree}", flush=True)
        print(f"[Council Chamber] ==================================================\n", flush=True)

        return CouncilConsensus(
            directive=directive,
            blueprint=blueprint,
            deliberations=deliberations,
            audit_verdict=audit_verdict,
            sovereign_decree=sovereign_decree,
            total_wall_clock_ms=total_wall_clock_ms,
            sequential_estimate_ms=sequential_sum_ms,
            concurrency_speedup=speedup,
        )

    def convene_sync(
        self,
        directive: str,
        workspace_context: Optional[str] = None
    ) -> CouncilConsensus:
        """Synchronous wrapper for convene."""
        return asyncio.run(self.convene(directive, workspace_context))
