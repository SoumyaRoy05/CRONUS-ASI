"""
Atlas Tool Suite
Async and sync tool execution primitives (Shell, File I/O, Environment).
"""

from __future__ import annotations
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


async def async_run_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: float = 30.0
) -> Tuple[int, str, str, float]:
    """
    Executes a shell command asynchronously and returns (exit_code, stdout, stderr, elapsed_ms).
    """
    start_time = time.perf_counter()
    working_dir = cwd if cwd and os.path.exists(cwd) else os.getcwd()

    try:
        proc = await asyncio.wait_for(
            asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            ),
            timeout=timeout
        )
        stdout_bytes, stderr_bytes = await proc.communicate()
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        stdout_str = stdout_bytes.decode("utf-8", errors="replace")
        stderr_str = stderr_bytes.decode("utf-8", errors="replace")
        return proc.returncode or 0, stdout_str, stderr_str, elapsed_ms

    except asyncio.TimeoutError:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return -1, "", f"Command timed out after {timeout} seconds", elapsed_ms
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return 1, "", str(e), elapsed_ms


def read_file(file_path: str) -> Tuple[bool, str]:
    """Reads file content safely. Returns (success, content_or_error)."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File does not exist: {file_path}"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return True, f.read()
    except Exception as e:
        return False, str(e)


def write_file(file_path: str, content: str, overwrite: bool = True) -> Tuple[bool, str]:
    """Writes content to file, creating parent directories if needed."""
    try:
        path = Path(file_path)
        if path.exists() and not overwrite:
            return False, f"File already exists and overwrite=False: {file_path}"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"Successfully written {len(content)} characters to {file_path}"
    except Exception as e:
        return False, str(e)


def patch_file(file_path: str, target_snippet: str, replacement_snippet: str) -> Tuple[bool, str]:
    """Replaces target_snippet with replacement_snippet in the specified file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if target_snippet not in content:
            return False, "Target snippet not found in file."
        updated = content.replace(target_snippet, replacement_snippet, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
        return True, f"Successfully patched {file_path}"
    except Exception as e:
        return False, str(e)


def inspect_environment() -> Dict[str, Any]:
    """Returns runtime telemetry for Atlas execution."""
    import platform
    telemetry = {
        "os": platform.system(),
        "release": platform.release(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "cwd": os.getcwd(),
        "cuda_available": False,
        "device_count": 0,
    }
    try:
        import torch
        telemetry["cuda_available"] = torch.cuda.is_available()
        telemetry["device_count"] = torch.cuda.device_count() if torch.cuda.is_available() else 0
        if torch.cuda.is_available():
            telemetry["device_name"] = torch.cuda.get_device_name(0)
    except Exception:
        pass
    return telemetry
