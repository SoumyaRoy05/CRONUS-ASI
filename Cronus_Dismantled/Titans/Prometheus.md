# Prometheus: Titan of Forethought & Architecture (`Titan_Council/Prometheus/`)

Prometheus serves as the chief strategist and architectural planner of the Titan Council. Named after the Titan of forethought, Prometheus translates high-level user goals into structured, dependency-ordered execution blueprints.

---

## 1. Core Responsibilities

* **Goal Decomposition**: Breaks complex, ambiguous user objectives into discrete, actionable steps (`TaskStep`).
* **Dependency Mapping**: Resolves prerequisites to ensure prerequisites execute in topological order.
* **Risk Assessment**: Categorizes each step by operational risk (LOW, MEDIUM, HIGH, CRITICAL) to inform Themis's audit thresholds.
* **Dynamic Replanning**: When a step encounters an unexpected runtime error, `replan(...)` generates an adaptive contingency blueprint.

---

## 2. Data Schemas (`schemas.py`)

```python
class TaskStep(BaseModel):
    step_id: int
    title: str
    action_type: str        # 'shell', 'file_io', 'web_search', 'gui', 'memory'
    command_or_input: str
    target_path: Optional[str]
    dependencies: List[int]
    risk_level: str         # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    expected_output: str

class ArchitecturalBlueprint(BaseModel):
    goal: str
    rationale: str
    steps: List[TaskStep]
    risks: List[RiskItem]
    fallback_strategy: str
```

---

## 3. Multi-Tier LLM Planner Waterfall

Prometheus utilizes a high-token reasoning LLM waterfall:
1. **Tier 1**: Groq (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`)
2. **Tier 2**: Google Gemini (`gemini-flash-latest`, `gemini-pro-latest`)
3. **Tier 3**: NVIDIA NIM (`nvidia/nemotron-3-ultra-550b-a55b` — 550B MoE flagship)
4. **Tier 4**: Local Ollama (`qwen2.5:3b`)

---

## 4. Public API

```python
from Titan_Council.Prometheus import Prometheus

planner = Prometheus()
blueprint = planner.plan(
    goal="Install project dependencies and run pytest validation suite."
)
for step in blueprint.steps:
    print(f"[{step.step_id}] {step.title} (Risk: {step.risk_level})")
```
