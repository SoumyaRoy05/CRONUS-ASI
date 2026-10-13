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


def _find_project_root() -> Path:
    """Find the project root containing cronus.py, Organs, Behaviour, and .env."""
    # 1. Check current working directory
    cwd = Path.cwd()
    if (cwd / "cronus.py").exists():
        return cwd.resolve()

    # 2. Check executable directory hierarchy
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        for p in [exe_dir, exe_dir.parent, exe_dir.parent.parent]:
            if (p / "cronus.py").exists():
                return p.resolve()
        if hasattr(sys, "_MEIPASS"):
            mei_dir = Path(sys._MEIPASS).resolve()
            for p in [mei_dir, mei_dir.parent, mei_dir.parent.parent]:
                if (p / "cronus.py").exists():
                    return p.resolve()

    # 3. Check current file directory hierarchy
    this_file = Path(__file__).resolve()
    for p in [this_file.parent, this_file.parent.parent, this_file.parent.parent.parent]:
        if (p / "cronus.py").exists():
            return p.resolve()

    # 4. Fallback to known workspace root
    hard_root = Path(r"D:\Codes\CRONUS-ASI")
    if (hard_root / "cronus.py").exists():
        return hard_root.resolve()

    return cwd.resolve()


def _find_python_executable(root: Path) -> str:
    """Locate the project's dedicated .venv Python interpreter."""
    # 1. In project root
    root_venv = root / ".venv" / "Scripts" / "python.exe"
    if root_venv.exists():
        return str(root_venv.resolve())

    # 2. In current working directory
    cwd_venv = Path.cwd() / ".venv" / "Scripts" / "python.exe"
    if cwd_venv.exists():
        return str(cwd_venv.resolve())

    # 3. Hierarchy around executable
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        for p in [exe_dir, exe_dir.parent, exe_dir.parent.parent]:
            candidate = p / ".venv" / "Scripts" / "python.exe"
            if candidate.exists():
                return str(candidate.resolve())

    # 4. Hierarchy around this file
    this_dir = Path(__file__).resolve().parent
    for p in [this_dir, this_dir.parent, this_dir.parent.parent, this_dir.parent.parent.parent]:
        candidate = p / ".venv" / "Scripts" / "python.exe"
        if candidate.exists():
            return str(candidate.resolve())

    # 5. Dedicated known venv path
    default_venv = Path(r"D:\Codes\CRONUS-ASI\.venv\Scripts\python.exe")
    if default_venv.exists():
        return str(default_venv.resolve())

    if not getattr(sys, "frozen", False):
        return sys.executable
    return "python"


PROJECT_ROOT = _find_project_root()
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

        python_bin = _find_python_executable(PROJECT_ROOT)

        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

        self._process = subprocess.Popen(
            [python_bin, "-u", str(CRONUS_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            creationflags=creationflags,
            startupinfo=startupinfo,
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
