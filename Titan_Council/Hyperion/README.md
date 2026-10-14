# ☀️ Hyperion — Titan of Heavenly Light & Chief Intelligence Officer

> *"Darkness is merely the absence of observation; where light reaches, uncertainty dissolves into fact."*  
> **Council Role:** Chief Intelligence Officer, Context Ingestion, API & Documentation Researcher  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Hyperion** embodies radiant perception and intellectual clarity. While Prometheus architectures, Atlas executes, and Themis audits, Hyperion ensures that the Council never operates in ignorance or with stale assumptions.

Hyperion scans local codebases, maps workspace symbols, inspects library versions, and synthesizes technical documentation into structured **`IntelligenceDossier`** reports, ensuring that every Council decision is grounded in empirical facts.

### Core Responsibilities
1. **Context & Symbol Ingestion:** Rapidly scans workspace directories to map active source files, packages, and AST symbols without polluting memory with virtualenvs.
2. **API & SDK Grounding:** Researches method signatures, parameter names, and version compatibilities for third-party libraries (LangGraph, FastAPI, PyTorch, CTranslate2).
3. **Technical Dossier Synthesis:** Compiles structured intelligence dossiers summarizing facts, code references, and technical constraints.
4. **Council Knowledge Illumination:** Enriches Titan Council deliberations with exact import paths, deprecation warnings, and architectural best practices.

---

## 2. Operational Protocol: The Intelligence Cycle

Hyperion operates through an empirical observation cycle:

```
                    [ Research Topic / Directive ]
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │   1. Workspace Symbol Scan    │
                  │ (Map existing source files)   │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │ 2. Reference & Doc Ingestion  │
                  │ (Extract SDK signatures & API)│
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │    3. Constraint Synthesis    │
                  │ (Isolate version bottlenecks) │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │ 4. IntelligenceDossier Return │
                  │ (Facts delivered to Council)  │
                  └───────────────────────────────┘
```

1. **Symbol Scanning:** Maps the workspace layout, ensuring the Council references actual project files.
2. **Doc Ingestion:** Reads relevant reference guides, markdown documentation, or library contracts.
3. **Constraint Synthesis:** Isolates breaking changes, platform limitations (e.g. Windows UTF-8 console caveats), or required environment variables.
4. **Dossier Emission:** Delivers structured evidence to Prometheus for blueprint formulation.

---

## 3. Data Contracts & Schemas (`schemas.py`)

Hyperion enforces strict **Pydantic V2** intelligence schemas:

### `ResearchSource` (Enum)
* `LOCAL_DOC`: Local markdown or text documentation.
* `WEB_SEARCH`: External web retrieval.
* `CODEBASE_AST`: Local workspace AST scan.
* `SYSTEM_INSPECTION`: Runtime environment inspection.

### `IntelligenceItem`
An individual verified factual finding:
* `source_type` (*ResearchSource*): Origin of the intelligence item.
* `title` (*str*): Title of document or discovery.
* `uri_or_path` (*str*): File path or URI reference.
* `key_findings` (*List[str]*): Bullet points of verified facts.
* `relevance_score` (*float*): Score from `0.0` to `1.0`.
* `snippet` (*str*): Code snippet or quote.

### `IntelligenceDossier`
The comprehensive research report returned by Hyperion:
* `topic` (*str*): Target research query.
* `executive_summary` (*str*): Synthesis of findings.
* `findings` (*List[IntelligenceItem]*): Curated evidence items.
* `recommended_approach` (*str*): Authoritative implementation path.
* `technical_constraints` (*List[str]*): Identified technical barriers.

---

## 4. Internal Architecture & File Layout

```text
Titan_Council/Hyperion/
├── __init__.py      # Clean public API exposing Hyperion, schemas, and tools
├── schemas.py       # Pydantic V2 intelligence schemas
├── prompts.py       # Hyperion persona and deliberation directives
├── tools.py         # Workspace symbol scanner and reference reader
├── agent.py         # Hyperion agent class with structured investigation
└── README.md        # This technical documentation file
```

---

## 5. Tool Primitives (`tools.py`)

* **`inspect_workspace_symbols(root_dir, extension)`:** Recursively scans the workspace directory, filtering out `.venv`, `.git`, and `__pycache__`, returning clean relative file paths.
* **`read_reference_doc(file_path, max_chars)`:** Safely reads reference documentation up to a specified character limit to prevent token overflows.

---

## 6. How to Use Hyperion

### Instantiation
```python
from Titan_Council.Hyperion import Hyperion, inspect_workspace_symbols

hyperion = Hyperion()
```

### Inspecting Workspace Files
```python
files = inspect_workspace_symbols(r"D:\Codes\CRONUS-ASI")
print(f"Total source files mapped: {len(files)}")
print(f"Sample files: {files[:3]}")
```

### Generating an Intelligence Dossier
```python
dossier = hyperion.investigate(
    topic="LangGraph AsyncPostgresSaver setup and dependencies on Python 3.13"
)
print(f"Topic: {dossier.topic}")
print(f"Summary: {dossier.executive_summary}")
print(f"Recommended Approach: {dossier.recommended_approach}")
```

### Participating in Council Deliberation
```python
topic = "Integration of LangGraph AsyncPostgresSaver for durable memory persistence"
deliberation = hyperion.deliberate_sync(topic)
print(deliberation)
```
