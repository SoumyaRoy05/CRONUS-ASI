"""
Cronus Process Manager
Subprocess lifecycle and unbuffered real-time pipe reading for cronus.py
"""

from __future__ import annotations

import codecs
import os
import subprocess
import sys
import threading
from collections.abc import Callable
from pathlib import Path


def _project_root() -> Path:
    """Return the project root whether running from source or frozen EXE."""
    if getattr(sys, "frozen", False):
        # Frozen EXE: _MEIPASS is the temp extraction folder that contains cronus.py
        return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    # Running from source: process.py is in Application/frontend/, go up two levels
    return Path(__file__).resolve().parent.parent.parent


def _python_executable(root: Path) -> str:
    """Return the Python interpreter to execute cronus.py."""
    # Check in project root
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    # Check alongside the executable directory (when running as frozen EXE)
    exe_dir = Path(sys.executable).resolve().parent
    venv_beside_exe = exe_dir / ".venv" / "Scripts" / "python.exe"
    if venv_beside_exe.exists():
        return str(venv_beside_exe)
    if not getattr(sys, "frozen", False):
        return sys.executable
    return "python"


PROJECT_ROOT = _project_root()
CRONUS_SCRIPT = PROJECT_ROOT / "cronus.py"


class CronusProcess:
    """Manages the cronus.py subprocess lifecycle."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[bytes] | None = None
        self._reader_thread: threading.Thread | None = None

    @property
    def running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self, on_output: Callable[[str], None], on_exit: Callable[[int], None]) -> None:
        """Launch cronus.py and stream its stdout."""
        if self.running:
            return

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        python_bin = _python_executable(PROJECT_ROOT)

        self._process = subprocess.Popen(
            [python_bin, "-u", str(CRONUS_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )

        self._reader_thread = threading.Thread(
            target=self._read_output,
            args=(on_output, on_exit),
            daemon=True,
        )
        self._reader_thread.start()

    def stop(self) -> None:
        """Gracefully terminate the cronus subprocess."""
        if not self.running:
            return
        proc = self._process
        if proc is None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    def _read_output(self, on_output: Callable[[str], None], on_exit: Callable[[int], None]) -> None:
        """Background thread: reads raw chunks from stdout as they arrive."""
        proc = self._process
        if proc is None or proc.stdout is None:
            return
        fd = proc.stdout.fileno()
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        while True:
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            text = decoder.decode(data)
            if text:
                on_output(text)

        remaining = decoder.decode(b"", final=True)
        if remaining:
            on_output(remaining)

        proc.wait()
        on_exit(proc.returncode if proc.returncode is not None else 0)
