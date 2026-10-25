# CRONUS Titan Council Cognitive Framework

The **Titan Council** is the high-concurrency, autonomous multi-agent cognitive architecture of CRONUS ASI. When a user request exceeds conversational small talk or requires complex, multi-step problem solving—such as installing software, auditing scripts, inspecting the desktop GUI, searching online documentation, or persisting memories across sessions—the **Council Chamber** mobilizes the 6 specialized Titans.

---

## 1. The Titan Roster & Domains of Authority

| Titan | Domain & Identity | Core Implementation | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Prometheus** | **Forethought & Architecture** | [Titan_Council/Prometheus/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Prometheus) | High-level goal decomposition, multi-stage blueprint design, dependency resolution, dynamic replanning on step failure. |
| **Atlas** | **Endurance & System Execution** | [Titan_Council/Atlas/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Atlas) | Sandboxed PowerShell/cmd command execution, secure file read/write/list operations, process lifecycle supervision. |
| **Themis** | **Law & AST Safety Audit** | [Titan_Council/Themis/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Themis) | Static Abstract Syntax Tree (AST) code auditing, forbidden module detection, destructive command interception, execution verification. |
| **Hyperion** | **Light & Context Retrieval** | [Titan_Council/Hyperion/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Hyperion) | Web and DuckDuckGo search, URL documentation scraping, API reference extraction, context window optimization. |
| **Helios** | **Vision & Screen Perception** | [Titan_Council/Helios/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Helios) | Desktop screen capture, coordinate mapping, UI element localization, PyAutoGUI and pywin32 mouse/keyboard automation. |
| **Coeus** | **Intellect & Memory Persistence** | [Titan_Council/Coeus/](file:///D:/Codes/CRONUS-ASI/Titan_Council/Coeus) | SQLite key-value store, tag/category indexing, session journal logging, long-term memory retrieval across system restarts. |
| **Chamber** | **Consensus & Orchestration** | [Titan_Council/Chamber.py](file:///D:/Codes/CRONUS-ASI/Titan_Council/Chamber.py) | High-concurrency async orchestrator (`asyncio.gather`), plan-audit-execute pipeline, error recovery protocol. |

---

## 2. Multi-Agent Deliberation Flow

```text
=============================================================================
                      TITAN COUNCIL EXECUTION WORKFLOW
=============================================================================

                   User Request / Complex Autonomous Goal
                                     |
                                     v
                       +---------------------------+
                       |   CouncilChamber Engine   |
                       +-------------+-------------+
                                     |
        Stage 1: Context & Intelligence Retrieval
                                     v
        +---------------------------------------------------------+
        |  Hyperion (Web/Docs) <---> Coeus (Long-Term Memories)   |
        +----------------------------+----------------------------+
                                     |
        Stage 2: Strategic Architectural Decomposition
                                     v
        +---------------------------------------------------------+
        |  Prometheus: Generates Multi-Stage Task Blueprint       |
        |  - Steps, Dependencies, Risk Levels, Expected Outputs    |
        +----------------------------+----------------------------+
                                     |
        Stage 3: Safety, Security & AST Audit Gate
                                     v
        +---------------------------------------------------------+
        |  Themis: Evaluates Blueprint, Commands & Code Snippets  |
        |  - PASS: Proceed to Stage 4                             |
        |  - FAIL: Halt or trigger Prometheus Replanning          |
        +----------------------------+----------------------------+
                                     |
        Stage 4: Physical System & Visual Execution
                                     v
        +---------------------------------------------------------+
        |  Atlas (Shell & File I/O) <---> Helios (Screen & GUI)   |
        +----------------------------+----------------------------+
                                     |
        Stage 5: State Persistence & Knowledge Archiving
                                     v
        +---------------------------------------------------------+
        |  Coeus: Commits results to SQLite Vault (.cronus_memory)|
        +---------------------------------------------------------+
=============================================================================
```

---

## 3. Titan Council Document Navigation

* **[Chamber.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Chamber.md)**: The central asynchronous council chamber and consensus orchestrator.
* **[Prometheus.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Prometheus.md)**: Systems architecture, task graph decomposition, and dynamic replanning.
* **[Atlas.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Atlas.md)**: Operating system execution, sandboxed shell execution, and contained file I/O.
* **[Themis.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Themis.md)**: Static AST syntax safety, forbidden module detection, and execution whitelists.
* **[Hyperion.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Hyperion.md)**: Live web search, documentation scraping, and contextual intelligence.
* **[Helios.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Helios.md)**: Desktop screen perception, coordinate mapping, and GUI interaction.
* **[Coeus.md](file:///D:/Codes/CRONUS-ASI/Cronus_Dismantled/Titans/Coeus.md)**: SQLite memory vault, session journal, and cross-restart continuity.

---

## 4. Real-Time Console Telemetry Format

Just like the physical Organs print operational status during execution (`[Ears] Listening...`, `[Brain] Processing...`, `[Mouth] Spoken Response`), the **Titan Council** prints real-time trace receipts with exact `[Titan Name]` tags:

```text
[Council Chamber] Convening Titan Council for directive: '...'
[Council Chamber] Phase 1: Tasking [Coeus] (Memory) & [Hyperion] (Intel) in parallel...
[Coeus] Searching memory vault for context related to directive...
[Hyperion] Deliberating technical context & web intelligence for Council...
[Council Chamber] [Coeus] and [Hyperion] delivered intelligence context to Council.
[Council Chamber] Phase 2: Dispatching context to [Atlas], [Themis], and [Helios] for peer review...
[Atlas] Deliberating system feasibility & resource containment...
[Themis] Deliberating safety boundaries & security constraints for Council...
[Helios] Assessing visual state & GUI automation pathways...
[Council Chamber] Phase 3: Tasking [Prometheus] to formulate architectural blueprint...
[Prometheus] Formulating architectural blueprint for directive...
[Prometheus] Master blueprint formulated with 6 execution steps.
[Prometheus] Dispatched blueprint to [Themis] for AST safety verification...
[Themis] All blueprint steps verified: APPROVED. [Themis] cleared [Atlas] and [Helios] for execution.
[Atlas] Received Step 1 from [Prometheus]: '...'
[Atlas] Executing shell command: '...'
[Council Chamber] Consensus reached in 35.8s (Parallel speedup: 1.20x).
[Council Chamber] Response formulated: ...
```
