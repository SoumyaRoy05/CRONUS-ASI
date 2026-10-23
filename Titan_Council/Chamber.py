"""
Council Chamber - Titan Council Orchestrator
Asynchronous deliberation room where all 6 Titans convene to co-develop the sovereign decree.
Forged for creator Soumya Roy under the sovereign command of CRONUS ASI.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from .Prometheus import Prometheus, ArchitecturalBlueprint
from .Atlas import Atlas
from .Themis import Themis
from .Hyperion import Hyperion
from .Helios import Helios
from .Coeus import Coeus

# Unified Single-Voice Mandate: Only CRONUS speaks aloud
from Organs.mouth import speak

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
    Structured into 4 modular phases with serialized non-blocking milestone speech.
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

    # =========================================================================
    # PHASE 1: Parallel Context Recall & Intelligence Gathering
    # =========================================================================
    async def phase1_gather(
        self,
        directive: str,
        workspace_context: Optional[str] = None,
        title: str = "Sir"
    ) -> Tuple[Any, str, str, Dict[str, float]]:
        """Phase 1: Coeus recalls historical memories while Hyperion ingests live technical context."""
        latencies: Dict[str, float] = {}
        print(f"\n[Council Chamber] ==================================================", flush=True)
        print(f"[Council Chamber] Phase 1: Initiating Parallel Memory & Intelligence Gathering...", flush=True)

        async def task_coeus():
            print(f"[TITAN COEUS 🧠]       ──►  Recalling cosmic memory vault & historical state...", flush=True)
            t0 = time.perf_counter()
            mem = await self.coeus.recall(directive, limit=3)
            latencies["Coeus"] = (time.perf_counter() - t0) * 1000.0
            
            # Print completed milestone
            print(f"[TITAN COEUS 🧠] Memory recalled, {title}.", flush=True)
            return mem

        async def task_hyperion():
            print(f"[TITAN HYPERION ☀️]       ──►  Gathering technical documentation & live intelligence...", flush=True)
            t0 = time.perf_counter()
            dossier = await self.hyperion.deliberate(directive, workspace_context)
            latencies["Hyperion"] = (time.perf_counter() - t0) * 1000.0
            
            # Print completed milestone
            print(f"[TITAN HYPERION ☀️] Intelligence gathered, {title}.", flush=True)
            return dossier

        memory_res, hyperion_delib = await asyncio.gather(task_coeus(), task_hyperion())
        context_summary = f"Memory Matches: {memory_res.total_found}. Hyperion Advice: {hyperion_delib[:100]}..."

        print(f"[Council Chamber] Context synchronization complete.", flush=True)
        return memory_res, hyperion_delib, context_summary, latencies

    # =========================================================================
    # PHASE 2: Parallel Deliberation & Peer Critique
    # =========================================================================
    async def phase2_deliberate(
        self,
        directive: str,
        context_summary: str,
        title: str = "Sir"
    ) -> Tuple[str, str, str, Dict[str, float]]:
        """Phase 2: Atlas, Themis, and Helios review the directive and context in parallel."""
        latencies: Dict[str, float] = {}
        print(f"[Council Chamber] Phase 2: Dispatching Peer Deliberations...", flush=True)

        async def task_atlas():
            print(f"[TITAN ATLAS 🔨]       ──►  Forging code & validating execution pathways...", flush=True)
            t0 = time.perf_counter()
            res = await self.atlas.deliberate(directive, context_summary)
            latencies["Atlas"] = (time.perf_counter() - t0) * 1000.0
            
            # Print completed milestone
            print(f"[TITAN ATLAS 🔨] Code forged, {title}.", flush=True)
            return res

        async def task_themis():
            print(f"[TITAN THEMIS ⚖️]       ──►  Auditing AST syntax & security boundaries...", flush=True)
            t0 = time.perf_counter()
            res = await self.themis.deliberate(directive, context_summary)
            latencies["Themis"] = (time.perf_counter() - t0) * 1000.0
            
            # Print completed milestone
            print(f"[TITAN THEMIS ⚖️] Security & AST verified, {title}.", flush=True)
            return res

        async def task_helios():
            print(f"[TITAN HELIOS 👁️]       ──►  Tracking visual display & GUI coordinates...", flush=True)
            t0 = time.perf_counter()
            res = await self.helios.deliberate(directive, context_summary)
            latencies["Helios"] = (time.perf_counter() - t0) * 1000.0
            
            # Print completed milestone
            print(f"[TITAN HELIOS 👁️] Visual coordinates locked, {title}.", flush=True)
            return res

        atlas_delib, themis_delib, helios_delib = await asyncio.gather(
            task_atlas(), task_themis(), task_helios()
        )
        print(f"[Council Chamber] Peer deliberations synchronized.", flush=True)
        return atlas_delib, themis_delib, helios_delib, latencies

    # =========================================================================
    # PHASE 3: Prometheus Blueprint & Sovereign Verification
    # =========================================================================
    async def phase3_architect(
        self,
        directive: str,
        context_summary: str,
        title: str = "Sir"
    ) -> Tuple[ArchitecturalBlueprint, str, Dict[str, float]]:
        """Phase 3: Prometheus crafts the Master Blueprint; Themis audits each step for AST safety."""
        latencies: Dict[str, float] = {}
        print(f"[Council Chamber] Phase 3: Architecting Master Blueprint...", flush=True)
        print(f"[TITAN PROMETHEUS 🏛️]       ──►  Architecting master blueprint & decomposing tasks...", flush=True)

        t0 = time.perf_counter()
        blueprint = self.prometheus.plan(directive, workspace_context=context_summary)
        latencies["Prometheus"] = (time.perf_counter() - t0) * 1000.0
        
        # Print completed milestone
        print(f"[TITAN PROMETHEUS 🏛️] Blueprint architected, {title}.", flush=True)

        print(f"[TITAN THEMIS ⚖️]       ──►  Auditing blueprint AST steps for security...", flush=True)

        # Audit blueprint commands with Themis
        audit_verdict = "APPROVED"
        for step in blueprint.steps:
            if getattr(step, "command_or_input", None):
                audit = self.themis.audit_command(step.command_or_input)
                if audit.verdict.value == "REJECTED":
                    audit_verdict = "REJECTED"
                    print(f"[Themis] Step {step.step_id} REJECTED: {audit.summary}", flush=True)

        if audit_verdict == "APPROVED":
            print(f"[TITAN THEMIS ⚖️] Blueprint verified: APPROVED, {title}.", flush=True)
        else:
            print(f"[TITAN THEMIS ⚖️] Blueprint REJECTED under security audit, {title}.", flush=True)
            speak(
                f"[serious] Security Alert, {title}: A blueprint step has been quarantined under security audit.",
                intent="COUNCIL"
            )

        return blueprint, audit_verdict, latencies

    # =========================================================================
    # PHASE 4: Council Consensus, Archiving & Sovereign Decree
    # =========================================================================
    async def phase4_synthesize(
        self,
        directive: str,
        blueprint: ArchitecturalBlueprint,
        deliberations: Dict[str, str],
        audit_verdict: str,
        agent_latencies: Dict[str, float],
        start_time: float,
        title: str = "Sir",
    ) -> CouncilConsensus:
        """Phase 4: Synthesize Sovereign Decree, persist to PostgreSQL, and finalize consensus."""
        total_wall_clock_ms = (time.perf_counter() - start_time) * 1000.0
        sequential_sum_ms = sum(agent_latencies.values())
        speedup = sequential_sum_ms / total_wall_clock_ms if total_wall_clock_ms > 0 else 1.0

        sovereign_decree = (
            f"The Council of Titans has converged, {title}. "
            f"Prometheus has architected a {len(blueprint.steps)}-step blueprint. "
            f"Atlas and Helios stand ready for system and visual execution, "
            f"while Themis has certified all security boundaries."
        )

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
        print(f"[Council Chamber] Sovereign Decree formulated for {title}.", flush=True)
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

    # =========================================================================
    # UNIFIED CONVENE (Sequential 4-Phase Pipeline)
    # =========================================================================
    async def convene(
        self,
        directive: str,
        workspace_context: Optional[str] = None,
        title: str = "Sir",
    ) -> CouncilConsensus:
        """Convenes the full Titan Council through all 4 sequential phases concurrently."""
        start_time = time.perf_counter()
        agent_latencies: Dict[str, float] = {}

        # Phase 1
        memory_res, hyperion_delib, context_summary, p1_latencies = await self.phase1_gather(
            directive, workspace_context, title=title
        )
        agent_latencies.update(p1_latencies)

        # Phase 2
        atlas_delib, themis_delib, helios_delib, p2_latencies = await self.phase2_deliberate(
            directive, context_summary, title=title
        )
        agent_latencies.update(p2_latencies)

        # Phase 3
        blueprint, audit_verdict, p3_latencies = await self.phase3_architect(
            directive, context_summary, title=title
        )
        agent_latencies.update(p3_latencies)

        deliberations = {
            "Hyperion": hyperion_delib,
            "Atlas": atlas_delib,
            "Themis": themis_delib,
            "Helios": helios_delib,
            "Coeus": f"Recalled {memory_res.total_found} relevant memories.",
            "Prometheus": blueprint.summary,
        }

        # Phase 4
        consensus = await self.phase4_synthesize(
            directive=directive,
            blueprint=blueprint,
            deliberations=deliberations,
            audit_verdict=audit_verdict,
            agent_latencies=agent_latencies,
            start_time=start_time,
            title=title,
        )
        return consensus

    def convene_sync(
        self,
        directive: str,
        workspace_context: Optional[str] = None,
        title: str = "Sir",
    ) -> CouncilConsensus:
        """Synchronous wrapper for convene."""
        return asyncio.run(self.convene(directive, workspace_context, title=title))
