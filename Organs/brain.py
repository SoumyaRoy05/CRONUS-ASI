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

import asyncio
import json
import concurrent.futures
import re
import sys
import time
from collections import deque # used for maintaining a history of messages for context
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

# -----------------------------------------------------------------------------
# 1. Environment & Path Resolution (Root access for llm.py & Behaviour)
# -----------------------------------------------------------------------------
load_dotenv()

# Make root-level modules importable when this file is run directly.
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Model provider from project root
from llm import get_llm

# Vocal output organ
from Organs.mouth import speak

# Persona, canned receipts & cognitive router
from Behaviour import get_system_prompt, get_offline_receipt, get_router_prompt

# Titan Council Orchestrator
from Titan_Council.Chamber import CouncilChamber, CouncilConsensus


def _run_coro(coro):
    """Safely execute an asynchronous coroutine within sync LangGraph nodes."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


# -----------------------------------------------------------------------------
# 2. State Schema
# -----------------------------------------------------------------------------
class BrainState(TypedDict, total=False):
    # Graph 1 (Ingestion & Prompt Preparation)
    user_prompt: str
    chosen_title: str
    system_prompt: str
    messages: List[BaseMessage]
    selected_llm: Any

    # Graph 2 (Cognitive Routing & 4-Phase Deliberation)
    intent: str  # "REFLEX" or "COUNCIL"
    phase1_context: str
    phase1_memories: Any
    phase1_dossier: str
    phase2_deliberations: Dict[str, str]
    phase3_blueprint: Any
    phase3_audit_verdict: str
    phase_latencies: Dict[str, float]
    phase_start_time: float
    council_consensus: Any
    raw_response: str

    # Graph 3 (Output Sanitization & TTS Vocalization)
    final_response: str


# -----------------------------------------------------------------------------
# 3. Brain Multi-Graph Stateful Orchestration
# -----------------------------------------------------------------------------

class Brain:

    # Stores the Mouth function, Creates the conversation memory, Builds the Brain’s LangGraph workflow
    def __init__(self, mouth: Any | None = None):
        """Initializes vocal connections, Titan Council chamber, and compiles the multi-graph hierarchy."""
        self.mouth: Any = mouth if mouth is not None else speak
        self.history: deque[BaseMessage] = deque(maxlen=40) # keeps the latest 40 messages for context
        self.chamber = CouncilChamber()
        self.graph = self._build_master_graph()

    # ------------------------------- Sub Functions ------------------------------- #
    # Sub functions/methods used by node functions to perform specific tasks within the respective graph

    # sub function 1
    # used at Graph 3 in the output sanitization node to strip formatting symbols before TTS
    def _sanitize_for_tts(self, text: str) -> str:
        """Strips formatting symbols and leaked bracket tags to prevent speech synthesis glitches."""
        clean = re.sub(r"\[[a-zA-Z\s_-]+\]", "", text)
        clean = re.sub(r"[\*\_#\>\-`]", "", clean)
        return " ".join(clean.split()).strip()

    # sub function 2
    # remembers a response spoken outside the cognitive graph, such as the wake receipt or other assistant messages
    # takes a string message and appends it to the history deque for context in future interactions
    def remember_assistant_message(self, message: str) -> None:
        """Remember a response spoken outside the cognitive graph."""
        if message and message.strip():
            self.history.append(AIMessage(content=message.strip()))

    # =========================================================================
    # GRAPH 1 NODES: Prepares the Input with respect to Persona & Selects LLM from llm.py
    # =========================================================================

    # Node Function 1A
    # uses the get_system_prompt() from persona.py to construct the system prompt and dialogue messages
    # takes the user prompt from the BrainState and constructs a list of messages for the LLM to process
    def prepare_input_node(self, state: BrainState) -> dict:
        """Constructs persona directives and dialogue messages from raw speech."""
        chosen_title = state.get("chosen_title") or "Sir"
        sys_prompt = get_system_prompt(forced_title=chosen_title)
        dialogue: List[BaseMessage] = [
            SystemMessage(content=sys_prompt),
            *self.history, # include the history (last 40 messages) for context in API calls
            HumanMessage(content=state.get("user_prompt", "")),
        ]
        return {
            "chosen_title": chosen_title,
            "system_prompt": sys_prompt,
            "messages": dialogue,
        }

    # Node Function 1B
    # uses the get_llm() function from llm.py to select the active LLM instance for processing
    # takes the BrainState and returns the llm to be used
    def select_llm_node(self, state: BrainState) -> dict:
        """Resolves and selects the active LLM waterfall instance for processing."""
        active_llm = get_llm()
        return {"selected_llm": active_llm}

    # =========================================================================
    # GRAPH 2 NODES: Cognitive Router & 4-Phase Titan Council Deliberation
    # =========================================================================

    # Node Function 2A (Cognitive Router)
    # uses get_router_prompt() from Behaviour/router_prompt.py to classify intent as REFLEX vs COUNCIL
    # uses 0ms deterministic micro-bypass for pure greetings
    # takes the BrainState and returns the classified intent (and fast reply if reflex)
    def classify_intent_node(self, state: BrainState) -> dict:
        """Classifies user prompt into REFLEX (fast small talk) vs COUNCIL (deep task) using LLM."""
        raw_prompt = (state.get("user_prompt") or "").strip()
        title = state.get("chosen_title", "Sir")
        p_clean = re.sub(r"[^\w\s]", "", raw_prompt).strip().lower()

        # 1. 0ms Deterministic micro-bypass for pure greetings
        pure_greetings = {"hi", "hello", "hey", "greetings", "howdy", "sup", "yo", "good", "morning", "afternoon", "evening", "stand down", "thank you", "thanks", "bye", "goodbye", "good morning", "good afternoon", "good evening", "good night", "yes", "no", "status", "ready", "who are you", "who created you", "who made you", "how are you", "what is your name"}
        words = p_clean.split()
        if p_clean in pure_greetings or (words and len(words) <= 2 and all(w in pure_greetings or w in {"cronus", "buddy", "pal", "sir"} for w in words)):
            print(f"[Brain Cognitive Router] Micro-bypass: Fast REFLEX for '{raw_prompt}'", flush=True)
            return {"intent": "REFLEX"}

        # 2. LLM Intent Router (Single-Call Reflex Fusion)
        llm = state.get("selected_llm") or get_llm()
        router_prompt = get_router_prompt(raw_prompt, title=title)
        try:
            res = llm.invoke(router_prompt)
            content = res.content if hasattr(res, "content") else str(res)
            match = re.search(r"\{.*?\}", content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                intent = str(data.get("intent", "COUNCIL")).strip().upper()
                reply = str(data.get("reply", "")).strip()
                print(f"[Brain Cognitive Router] LLM Intent classified: {intent}", flush=True)
                if intent == "REFLEX" and reply:
                    return {"intent": "REFLEX", "raw_response": reply}
                return {"intent": intent}
        except Exception as e:
            print(f"[Brain Cognitive Router] LLM routing fallback error: {e}", flush=True)

        return {"intent": "COUNCIL"}

    # Conditional router edge function
    # routes the graph flow to fast_reflex_llm if intent is REFLEX or phase1_gather if intent is COUNCIL
    def route_cognitive_path(self, state: BrainState) -> str:
        """Conditional routing edge function for Subgraph 2."""
        return state.get("intent", "COUNCIL")

    # Node Function 2B (Reflex Processing Node)
    # uses the selected LLM from the BrainState to invoke the LLM and extract the raw output text
    # takes the BrainState and returns the raw output text from the LLM
    def processing_node(self, state: BrainState) -> dict:
        """Fast Reflex Node: Uses already generated reply or invokes LLM."""
        existing = state.get("raw_response")
        if existing and existing.strip():
            return {"raw_response": existing.strip()}

        llm = state.get("selected_llm") or get_llm()
        try:
            response = llm.invoke(state.get("messages", []))
            content = response.content if hasattr(response, "content") else str(response)
            if isinstance(content, str):
                content_text = content
            elif isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, str):
                        text_parts.append(block)
                    elif isinstance(block, dict) and isinstance(block.get("text"), str):
                        text_parts.append(block["text"])
                content_text = " ".join(text_parts)
            else:
                content_text = str(content)
            return {"raw_response": content_text.strip() if content_text else ""}
        except Exception as e:
            print(f"[Brain Graph 2 - LLM Reflex Execution Error]: {e}", flush=True)
            return {"raw_response": ""}

    # Node Function 2C (Phase 1 Context Gather)
    # uses the phase1_gather() from Titan_Council/Chamber.py to task Coeus (memory) and Hyperion (intel) in parallel
    # takes the BrainState and returns recalled memories and intelligence dossier
    def phase1_gather_node(self, state: BrainState) -> dict:
        """Phase 1: Task Coeus (Memory) & Hyperion (Intel) in parallel; speak milestone."""
        directive = state.get("user_prompt", "")
        t_start = time.perf_counter()

        title = state.get("chosen_title", "Sir")
        memory_res, hyperion_delib, context_summary, latencies = _run_coro(
            self.chamber.phase1_gather(directive, title=title)
        )
        return {
            "phase1_context": context_summary,
            "phase1_memories": memory_res,
            "phase1_dossier": hyperion_delib,
            "phase_latencies": latencies,
            "phase_start_time": t_start,
        }

    # Node Function 2D (Phase 2 Peer Deliberation)
    # uses the phase2_deliberate() from Titan_Council/Chamber.py to task Atlas, Themis, and Helios in parallel
    # takes the BrainState and returns peer deliberations from Atlas, Themis, and Helios
    def phase2_deliberate_node(self, state: BrainState) -> dict:
        """Phase 2: Atlas, Themis, and Helios peer deliberation; speak milestones."""
        directive = state.get("user_prompt", "")
        context_summary = state.get("phase1_context", "")

        title = state.get("chosen_title", "Sir")
        atlas_d, themis_d, helios_d, latencies = _run_coro(
            self.chamber.phase2_deliberate(directive, context_summary, title=title)
        )
        existing_latencies = dict(state.get("phase_latencies", {}))
        existing_latencies.update(latencies)

        deliberations = {
            "Hyperion": state.get("phase1_dossier", ""),
            "Atlas": atlas_d,
            "Themis": themis_d,
            "Helios": helios_d,
            "Coeus": f"Recalled {getattr(state.get('phase1_memories'), 'total_found', 0)} memories.",
        }
        return {
            "phase2_deliberations": deliberations,
            "phase_latencies": existing_latencies,
        }

    # Node Function 2E (Phase 3 Architectural Blueprint)
    # uses the phase3_architect() from Titan_Council/Chamber.py to formulate Prometheus blueprint and Themis AST audit
    # takes the BrainState and returns architectural blueprint and security audit verdict
    def phase3_architect_node(self, state: BrainState) -> dict:
        """Phase 3: Prometheus Blueprint & Themis AST audit; speak milestones."""
        directive = state.get("user_prompt", "")
        context_summary = state.get("phase1_context", "")

        title = state.get("chosen_title", "Sir")
        blueprint, verdict, latencies = _run_coro(
            self.chamber.phase3_architect(directive, context_summary, title=title)
        )
        existing_latencies = dict(state.get("phase_latencies", {}))
        existing_latencies.update(latencies)

        deliberations = dict(state.get("phase2_deliberations", {}))
        deliberations["Prometheus"] = blueprint.summary

        return {
            "phase3_blueprint": blueprint,
            "phase3_audit_verdict": verdict,
            "phase2_deliberations": deliberations,
            "phase_latencies": existing_latencies,
        }

    # Node Function 2F (Phase 4 Sovereign Decree & Archiving)
    # uses the phase4_synthesize() from Titan_Council/Chamber.py to synthesize consensus and save to PostgreSQL
    # takes the BrainState and returns the sovereign decree for CRONUS to speak aloud
    def phase4_decree_node(self, state: BrainState) -> dict:
        """Phase 4: Synthesize Sovereign Decree, persist to PostgreSQL, finalize raw response."""
        directive = state.get("user_prompt", "")
        blueprint = state.get("phase3_blueprint")
        deliberations = state.get("phase2_deliberations", {})
        verdict = state.get("phase3_audit_verdict", "APPROVED")
        latencies = state.get("phase_latencies", {})
        t_start = state.get("phase_start_time", time.perf_counter())

        title = state.get("chosen_title", "Sir")
        consensus = _run_coro(
            self.chamber.phase4_synthesize(
                directive=directive,
                blueprint=blueprint,
                deliberations=deliberations,
                audit_verdict=verdict,
                agent_latencies=latencies,
                start_time=t_start,
                title=title,
            )
        )
        return {
            "council_consensus": consensus,
            "raw_response": consensus.sovereign_decree,
        }

    # =========================================================================
    # GRAPH 3 NODES: Sanitize Output from LLM and Dispatch to Mouth for TTS
    # =========================================================================

    # Node Function 3A
    # uses the get_offline_receipt() from persona.py to provide a fallback response if the LLM output is empty
    # uses the _sanitize_for_tts() method to clean the raw output text for speech synthesis
    # takes the BrainState and returns the final sanitized output text for TTS
    def sanitize_output_node(self, state: BrainState) -> dict:
        """Cleans residual formatting and prepares output text for speech."""
        raw = state.get("raw_response", "")
        if not raw:
            clean_reply = get_offline_receipt()
        else:
            clean_reply = self._sanitize_for_tts(raw)

        return {"final_response": clean_reply}

    # Node Function 3B
    # uses the speak() from mouth.py module to vocalize the final sanitized text
    # takes the BrainState and returns an empty dict
    def mouth_speak_node(self, state: BrainState) -> dict:
        """Hands the final sanitized text directly to mouth for TTS vocalization."""
        reply = state.get("final_response", "")
        intent = state.get("intent", "COUNCIL")

        # In Council mode, wait until all queued Titan milestones have finished speaking
        if intent == "COUNCIL":
            try:
                from Organs.mouth import wait_for_speech
                wait_for_speech()
            except Exception as e:
                print(f"[Mouth Drain Error]: {e}", flush=True)

        if reply and self.mouth is not None:
            if callable(self.mouth):
                try:
                    self.mouth(reply, intent=intent)
                except TypeError:
                    self.mouth(reply)
        return {}

    # =========================================================================
    # SUBGRAPH BUILDERS
    # =========================================================================

    # Subgraph 1
    # builds the first subgraph that prepares the user input and selects the appropriate LLM for processing
    # returns a compiled StateGraph that can be invoked with the BrainState
    def ready_for_processing(self):
        """Graph 1: Ingests user input, formats persona directives, and picks the LLM."""
        workflow = StateGraph(BrainState)  # type: ignore

        # Nodes---
        workflow.add_node("prepare_input", self.prepare_input_node)
        workflow.add_node("select_llm", self.select_llm_node)

        # Edges---
        workflow.add_edge(START, "select_llm")
        workflow.add_edge("select_llm", "prepare_input")
        workflow.add_edge("prepare_input", END)

        return workflow.compile()

    # Subgraph 2
    # builds the second subgraph that routes between fast reflex and the 4-phase Titan Council
    # returns a compiled StateGraph that can be invoked with the BrainState
    def _build_processing_graph(self):
        """Graph 2: Cognitive Router with Fast Reflex vs 4-Phase Titan Council Subgraph."""
        workflow = StateGraph(BrainState)  # type: ignore

        # Nodes---
        workflow.add_node("classify_intent", self.classify_intent_node)
        workflow.add_node("fast_reflex_llm", self.processing_node)
        workflow.add_node("phase1_gather", self.phase1_gather_node)
        workflow.add_node("phase2_deliberate", self.phase2_deliberate_node)
        workflow.add_node("phase3_architect", self.phase3_architect_node)
        workflow.add_node("phase4_decree", self.phase4_decree_node)

        # Edges---
        workflow.add_edge(START, "classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_cognitive_path,
            {
                "REFLEX": "fast_reflex_llm",
                "COUNCIL": "phase1_gather",
            },
        )
        workflow.add_edge("fast_reflex_llm", END)
        workflow.add_edge("phase1_gather", "phase2_deliberate")
        workflow.add_edge("phase2_deliberate", "phase3_architect")
        workflow.add_edge("phase3_architect", "phase4_decree")
        workflow.add_edge("phase4_decree", END)

        return workflow.compile()

    # Subgraph 3
    # builds the third subgraph that sanitizes the raw output text and dispatches it to the mouth for TTS
    # returns a compiled StateGraph that can be invoked with the BrainState
    def ready_to_speak(self):
        """Graph 3: Sanitizes generated text and dispatches directly to mouth.speak."""
        workflow = StateGraph(BrainState)  # type: ignore

        # Nodes---
        workflow.add_node("sanitize_output", self.sanitize_output_node)
        workflow.add_node("mouth_speak", self.mouth_speak_node)

        # Edges---
        workflow.add_edge(START, "sanitize_output")
        workflow.add_edge("sanitize_output", "mouth_speak")
        workflow.add_edge("mouth_speak", END)

        return workflow.compile()

    # =========================================================================
    # MASTER GRAPH BUILDER
    # =========================================================================

    # builds the master graph that orchestrates the sequential flow of all three subgraphs: 
    # input preparation, LLM processing, and vocal output
    # returns a compiled StateGraph that can be invoked with the BrainState
    def _build_master_graph(self):
        """Graph 4: Master pipeline orchestrating the sequential flow of all 3 subgraphs."""
        graph_1 = self.ready_for_processing()
        graph_2 = self._build_processing_graph()
        graph_3 = self.ready_to_speak()

        master = StateGraph(BrainState)  # type: ignore

        # Nodes---
        master.add_node("input_preparation_graph", graph_1)
        master.add_node("processing_graph", graph_2)
        master.add_node("mouth_output_graph", graph_3)

        # Edges---
        master.add_edge(START, "input_preparation_graph")
        master.add_edge("input_preparation_graph", "processing_graph")
        master.add_edge("processing_graph", "mouth_output_graph")
        master.add_edge("mouth_output_graph", END)

        return master.compile()

    # =========================================================================
    # SENSORY ENTRYPOINT(Main calling function for the Brain)
    # =========================================================================

    # invoked by ears.take_input() to run the complete master cognitive graph
    # takes the user prompt as input and returns the final vocalized response text
    def think(self, user_prompt: str) -> str:
        """Invoked by ears.take_input() to run the complete master cognitive graph."""
        print("\n# ─────────────────── BRAIN is thinking ─────────────────── #")
        print(f"[Brain]---\nReceived user prompt: {user_prompt}", flush=True)

        if not user_prompt or not user_prompt.strip():
            return ""

        initial_state: BrainState = {
            "user_prompt": user_prompt.strip(),
            "system_prompt": "",
            "messages": [],
            "selected_llm": None,
            "raw_response": "",
            "final_response": "",
        }

        # Run the master graph with the initial state and a specific run configuration
        run_config: RunnableConfig = {"run_name": "Cronus-Master-Cognitive-Turn"}
        result = self.graph.invoke(initial_state, config=run_config)
        final_response = result.get("final_response", "")

        # Remember prompt and response in history for context in future interactions
        self.history.append(HumanMessage(content=user_prompt.strip())) # Remember the user prompt in history
        self.history.append(AIMessage(content=final_response)) # Remember the assistant's response in history

        # Background non-blocking logging to PostgreSQL (Zero-delay circuit breaker)
        try:
            from Database.client import log_dialogue_turn_background
            log_dialogue_turn_background(
                user_prompt=user_prompt.strip(),
                cleaned_speech_response=final_response,
                model_used="CRONUS_LLM_Waterfall",
            )
        except Exception:
            pass

        return final_response


if __name__ == "__main__":
    # Example usage
    brain = Brain()
    user_input = "Give me a brief summary of the latest advancements in AI research."
    brain.think(user_input)
