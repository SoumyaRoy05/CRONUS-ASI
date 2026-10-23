# Themis: Titan of Law & AST Safety Audit (`Titan_Council/Themis/`)

Themis embodies divine law, justice, and order. Acting as the chief security and verification authority of the Titan Council, Themis audits all code snippets, shell commands, and execution blueprints before they touch the operating system.

---

## 1. Core Responsibilities

* **Static AST Code Auditing**: Parses Python scripts via the `ast` module to identify dangerous constructs (e.g., unauthorized `eval()`, `exec()`, `ctypes` memory tampering, monkey-patching).
* **Command Screening**: Evaluates shell commands against dangerous heuristics (e.g., destructive disk formatting, recursive root deletion, external credential transmission).
* **Security Verdicts**: Emits an `AuditResult` featuring a concrete verdict: `APPROVED`, `WARNING`, or `REJECTED`.
* **Execution Gatekeeper**: Integrates with the Council Chamber to veto unsafe operations before Atlas executes them.

---

## 2. Data Schemas (`schemas.py`)

```python
class SecurityVerdict(str, Enum):
    APPROVED = "APPROVED"
    WARNING = "WARNING"
    REJECTED = "REJECTED"

class AuditResult(BaseModel):
    verdict: SecurityVerdict
    is_safe: bool
    violations_detected: List[str]
    severity_level: str  # 'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    remediation_advice: Optional[str]
```

---

## 3. Public API

```python
from Titan_Council.Themis import Themis

themis = Themis()

# Audit a proposed shell command
audit = themis.audit_command("Remove-Item -Recurse -Force C:\Windows")
print(f"Verdict: {audit.verdict}")
print(f"Is Safe: {audit.is_safe}")
print(f"Violations: {audit.violations_detected}")
```
