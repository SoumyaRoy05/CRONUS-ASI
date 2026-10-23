"""
Themis Verifier Tools
Static analysis, AST syntax verification, and command safety audits.
"""

from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Destructive command patterns to block or flag
DANGEROUS_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+)?(\/|~)",  # rm -rf / or rm -rf ~
    r"del(\s+/[a-zA-Z]+)*\s+([c-zC-Z]:\\|/)?(windows|system32)",  # del with multiple flags targeting system dirs
    r"format\s+[c-zC-Z]:",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Fork bomb
    r"drop\s+database",
    r"shred\s+",
    r"diskpart",
]


def verify_python_syntax(code_string_or_file: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Parses Python code using AST to guarantee zero syntax errors.
    Returns (is_valid, error_message, line_number).
    """
    code_text = code_string_or_file
    path = Path(code_string_or_file)
    if path.exists() and path.is_file():
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                code_text = f.read()
        except Exception as e:
            return False, f"File read error: {e}", None

    try:
        ast.parse(code_text)
        return True, None, None
    except SyntaxError as se:
        return False, se.msg, se.lineno
    except Exception as e:
        return False, str(e), None


def audit_command_safety(command: str) -> Tuple[bool, str]:
    """
    Inspects shell command against critical destructive patterns.
    Returns (is_safe, reason).
    """
    cmd_lower = command.lower().strip()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd_lower):
            return False, f"Critical security alert: Command matches hazardous pattern: {pattern}"
    return True, "Command safety check passed."
