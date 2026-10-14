# 🏛️ Prometheus — Titan of Forethought & Grand Architect

> *"Before a single line of code is forged, the blueprint must already foresee the end."*  
> **Council Role:** Master Systems Architect, Strategic Planner & Task Decomposition Specialist  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Prometheus** represents the foundational intelligence of the **Titan Council**. He ensures that no task, tool call, or shell execution is ever undertaken impulsively or blindly.

Prometheus takes raw user intent or directives originating from **Subgraph 1 (Input Preparation)** in `brain.py`, analyzes latent prerequisites, maps out architectural contracts, and produces a complete, deterministic, and dependency-ordered **`ArchitecturalBlueprint`**.

### Core Responsibilities
1. **Strategic Deconstruction:** Ingests high-level or ambiguous goals and extracts explicit deliverables, dependencies, and constraints.
2. **Deterministic Task Decomposition:** Breaks down engineering directives into atomic, sequenced, and numbered `TaskStep` objects.
3. **Pre-Mortem Risk Analysis:** Identifies potential points of failure (environment barriers, permissions, API rate limits, breaking versions) before code execution starts.
4. **Falsifiable Verification Specifications:** Equips every step with a falsifiable test condition proving whether the step succeeded.
5. **Adaptive Replanning:** Ingests execution failure logs from Atlas and produces an updated blueprint that routes around errors while preserving completed work.

---

## 2. Cognitive Protocol: Hierarchical Forethought

Prometheus operates strictly under the **Hierarchical Forethought Protocol**, executing five deterministic phases:

```
                      [ DIRECTIVE / USER INTENT ]
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  1. Deconstruct the Directive │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │     2. System Architecture    │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  3. Atomic Task Decomposition │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │   4. Pre-Mortem Risk Matrix   │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  5. Falsifiable Verification  │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                    [ ArchitecturalBlueprint JSON ]
```

1. **Directive Deconstruction:** Extracts the underlying technical goal, scope, and target files.
2. **System Architecture Design:** Defines module contracts, data flows, and schemas before implementation.
3. **Atomic Task Decomposition:** Breaks work into sequenced tasks delegated to the appropriate Titan (`Atlas`, `Themis`, `Hyperion`, or `Prometheus`).
4. **Pre-Mortem Risk Analysis:** Maps each potential risk to a pre-computed architectural mitigation.
5. **Falsifiable Verification:** Guarantees that every task step has an unambiguous test command or check.

---

## 3. Data Contracts & Schemas (`schemas.py`)

Prometheus enforces strict **Pydantic V2** validation contracts:

### `TaskStep`
Represents an individual atomic task inside the execution graph:
* `step_id` (*int*): 1-based sequential index.
* `title` (*str*): Concise, action-oriented title.
* `assigned_agent` (*str*): Target Titan agent (`Atlas`, `Themis`, `Hyperion`, `Prometheus`).
* `action_type` (*str*): Category (`write_file`, `shell_command`, `web_research`, `design`, `verification`).
* `details` (*str*): Technical instructions for the executing agent.
* `dependencies` (*List[int]*): Step IDs that must complete before this step can begin.
* `verification_check` (*str*): Falsifiable command or test condition proving success.
* `fallback_plan` (*str*): Pre-computed recovery plan if the step fails.

### `RiskItem`
Pre-emptive risk identification:
* `risk` (*str*): Description of failure mode.
* `severity` (*str*): `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
* `mitigation` (*str*): Architectural mitigation or countermeasure.

### `ArchitecturalBlueprint`
The master output object returned by Prometheus:
* `goal` (*str*): The directive established by Soumya Roy.
* `summary` (*str*): Executive technical overview.
* `architecture_overview` (*str*): Component layout and contracts.
* `files_to_touch` (*List[str]*): Explicit list of files modified or created.
* `steps` (*List[TaskStep]*): Dependency-ordered list of atomic steps.
* `risk_matrix` (*List[RiskItem]*): Anticipated risks and mitigations.
* `estimated_effort` (*str*): Complexity and resource assessment.

---

## 4. Internal Architecture & File Layout

Prometheus is modularized into four specialized files:

```text
Titan_Council/Prometheus/
├── __init__.py      # Clean public API exposing Prometheus and all schemas
├── schemas.py       # Pydantic V2 data contracts (Blueprint, TaskStep, RiskItem)
├── prompts.py       # Forethought system prompt and dynamic replanning prompt
├── agent.py         # Prometheus class, high-token LLM waterfall, and parsing engine
└── README.md        # This technical documentation file
```

### Module Responsibilities:
* **[`schemas.py`](schemas.py):** Contains the Pydantic models. Separating schemas ensures fast imports without initializing LLM libraries.
* **[`prompts.py`](prompts.py):** Contains `PROMETHEUS_SYSTEM_PROMPT` and `REPLAN_SYSTEM_PROMPT`.
* **[`agent.py`](agent.py):**
  * Houses `_build_default_planner_llm()`: Builds a dedicated high-token LLM waterfall (`max_tokens=3072`, `temperature=0.2`) across Groq (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`), Google Gemini (`gemini-3.8-flash`, `gemini-3.7-flash`), and local Ollama (`qwen2.5:3b`).
  * Houses the `Prometheus` agent class with `plan()`, `replan()`, `format_markdown()`, `to_dict()`, and `to_json()`.

---

## 5. Dual Parsing Pipeline

To prevent JSON parsing failures on complex multi-step blueprints:
1. **Primary Method:** Uses LangChain's native `with_structured_output(ArchitecturalBlueprint)` bound to the active model.
2. **Deterministic Fallback:** If the provider drops the schema or returns raw text, Prometheus routes the output through an internal regex extraction engine:
   ```python
   # Regex isolating the outermost JSON block
   json_match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
   ```
   The extracted JSON is parsed and re-validated through `ArchitecturalBlueprint.model_validate()`.

---

## 6. How to Use Prometheus

### Instantiation
```python
from Titan_Council.Prometheus import Prometheus

# Initializes Prometheus with the default high-token model waterfall
prometheus = Prometheus()
```

### Generating an Architectural Blueprint (`plan`)
```python
directive = "Build an asynchronous council deliberation engine connecting Subgraph 1 to Subgraph 3 in brain.py"
context = "CRONUS-ASI codebase running on Python 3.13"

blueprint = prometheus.plan(directive=directive, workspace_context=context)

# Accessing structured blueprint properties
print(f"Goal: {blueprint.goal}")
print(f"Total Steps: {len(blueprint.steps)}")
for step in blueprint.steps:
    print(f"[{step.step_id}] ({step.assigned_agent}) {step.title} -> Check: {step.verification_check}")
```

### Dynamic Replanning on Failure (`replan`)
```python
# If Atlas reports that Step 2 failed during execution:
failed_step = blueprint.steps[1]
error_log = "PermissionError: [WinError 5] Access is denied: 'C:\\Program Files\\...'"

revised_blueprint = prometheus.replan(
    original_blueprint=blueprint,
    failed_step=failed_step,
    error_log=error_log
)
print(f"Revised Summary: {revised_blueprint.summary}")
```

### Pretty-Printing Markdown
```python
markdown_doc = prometheus.format_markdown(blueprint)
print(markdown_doc)
```
