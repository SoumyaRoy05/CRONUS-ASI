"""
Hyperion Tool Suite
Context gathering, file content inspection, and doc search primitives.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def inspect_workspace_symbols(root_dir: str, extension: str = ".py") -> List[str]:
    """Scans workspace directory to map out existing modules and source files."""
    found_files = []
    root_path = Path(root_dir)
    if not root_path.exists():
        return found_files

    for path in root_path.rglob(f"*{extension}"):
        if any(ignored in path.parts for ignored in [".venv", "__pycache__", ".git", "scratch"]):
            continue
        found_files.append(str(path.relative_to(root_path)))
    return found_files


def read_reference_doc(file_path: str, max_chars: int = 5000) -> Tuple[bool, str]:
    """Reads a reference documentation file safely."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"Reference path does not exist: {file_path}"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
        return True, content
    except Exception as e:
        return False, str(e)
