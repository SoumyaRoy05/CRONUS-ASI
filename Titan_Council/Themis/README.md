# ⚖️ Themis — Titan of Divine Order & Chief Auditor

> *"Action without law is ruin; truth requires neither trust nor assumption, only falsifiable proof."*  
> **Council Role:** Chief Quality Auditor, AST Syntax Verifier, Security Guardian & Compliance Officer  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Themis** holds the Scales of Justice and Truth. While Prometheus envisions plans and Atlas builds them, Themis guarantees that no defective code, catastrophic shell command, or unverified claim passes through the system.

She performs deep static analysis, AST syntax verification, security pattern matching, and falsifiable proof auditing before any output reaches creator Soumya Roy or production runtime.

### Core Responsibilities
1. **Automated AST Syntax Auditing:** Parses Python code using Python's native `ast` engine to guarantee 0 syntax errors before execution.
2. **Security & Destructive Command Interception:** Intercepts and blocks dangerous shell commands (system formatting, unrestricted deletion, fork bombs, database destruction).
3. **Falsifiable Verification Enforcement:** Verifies that every completed step has a concrete, falsifiable test proving it succeeded.
4. **Council Quality Gating:** Deliberates during Council sessions with an authoritative verdict (`APPROVED`, `REVISE`, or `REJECTED`) and non-negotiable audit requirements.

---

## 2. Operational Protocol: The Audit Pipeline

Themis audits code and plans through a deterministic four-tier inspection:

```
                 [ Code / Command / Blueprint ]
                               │
                               ▼
               ┌───────────────────────────────┐
               │    1. Security Pattern Scan   │
               │ (Block hazardous commands)    │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │    2. Static AST Validation   │
               │ (Parse syntax with ast.parse) │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │ 3. Falsifiable Test Checking  │
               │ (Verify empirical proof)      │
               └───────────────┬───────────────┘
                               │
                               ▼
               ┌───────────────────────────────┐
               │     4. Emit AuditReport       │
               │ (Verdict: APPROVED / REVISE)  │
               └───────────────────────────────┘
```

1. **Security Interception:** Scans command strings against regex patterns matching irreversible or destructive operations.
2. **AST Parsing:** Parses Python files or strings into Abstract Syntax Trees, isolating exact line numbers and error strings on failure.
3. **Proof Verification:** Ensures that Atlas's tool executions produced the expected return codes, artifacts, or assertions.
4. **Formal Verdict:** Emits a structured `AuditReport` with a quality score from `0.0` to `10.0`.

---

## 3. Data Contracts & Schemas (`schemas.py`)

Themis enforces strict **Pydantic V2** audit models:

### `AuditCategory` (Enum)
* `SECURITY`: Permission, execution, or destructive pattern hazard.
* `SYNTAX`: Language grammar and AST integrity.
* `LOGIC`: Algorithmic soundness and edge-case handling.
* `COMPLIANCE`: Conformance to creator Soumya Roy's directives.
* `EFFICIENCY`: Computational overhead and resource efficiency.

### `AuditSeverity` (Enum)
* `PASS`: Fully verified.
* `LOW`: Minor cosmetic or style observation.
* `MEDIUM`: Non-breaking improvement suggested.
* `HIGH`: Potential failure mode under specific conditions.
* `CRITICAL`: Immediate blocker (syntax error or destructive command).

### `AuditFinding`
An individual audit observation:
* `category` (*AuditCategory*): Observation category.
* `severity` (*AuditSeverity*): Severity rating.
* `title` (*str*): Concise title of the finding.
* `description` (*str*): Detailed technical diagnosis.
* `remediation` (*Optional[str]*): Recommended corrective action.

### `AuditReport`
The formal audit verdict returned by Themis:
* `target_name` (*str*): Name of audited artifact.
* `verdict` (*str*): `APPROVED`, `REVISE`, or `REJECTED`.
* `score` (*float*): Rating from `0.0` to `10.0`.
* `findings` (*List[AuditFinding]*): List of all findings.
* `summary` (*str*): Executive audit summary.

---

## 4. Internal Architecture & File Layout

```text
Titan_Council/Themis/
├── __init__.py      # Clean public API exposing Themis, schemas, and verifiers
├── schemas.py       # Pydantic V2 audit and verification models
├── prompts.py       # Themis persona and council auditing prompts
├── verifier.py      # AST syntax verifier and command safety interceptor
├── agent.py         # Themis agent class with automated audits and council debate
└── README.md        # This technical documentation file
```

---

## 5. Verifier Tools (`verifier.py`)

* **`verify_python_syntax(code_string_or_file)`:** Uses `ast.parse` to confirm that code is 100% syntactically valid. Catches unclosed brackets, indentation errors, or malformed constructs with line-level accuracy.
* **`audit_command_safety(command)`:** Scans shell commands against high-risk regex signatures (e.g. `rm -rf /`, `del /s /q C:\Windows`, `format`, fork bombs), immediately blocking hazardous operations.

---

## 6. How to Use Themis

### Instantiation
```python
from Titan_Council.Themis import Themis

themis = Themis()
```

### Auditing Python Code for Syntax Errors
```python
clean_code = "def calculate(x: int) -> int:\n    return x * 2\n"
report = themis.audit_python_code(clean_code, name="Calculation Function")
print(f"Verdict: {report.verdict} | Score: {report.score}/10")
# Output: Verdict: APPROVED | Score: 10.0/10
```

### Auditing Shell Commands for Security
```python
dangerous_command = "rm -rf /"
report = themis.audit_command(dangerous_command)
print(f"Verdict: {report.verdict} | Score: {report.score}/10")
print(f"Summary: {report.summary}")
# Output: Verdict: REJECTED | Score: 0.0/10 | Summary: Dangerous command blocked.
```

### Participating in Council Deliberation
```python
proposal = "Atlas plans to rewrite brain.py and install new packages."
deliberation = themis.deliberate_sync(proposal)
print(deliberation)
```
