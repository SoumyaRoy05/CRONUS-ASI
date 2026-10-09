from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

def root_dir() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
        return Path(meipass)
    return Path(__file__).resolve().parent.parent

PROJECT_ROOT = root_dir()
HOST = "127.0.0.1"
PORT = 8765
BASE_URL = f"http://{HOST}:{PORT}"

def backend_is_ready() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=1):
            return True
    except Exception:
        return False

def start_backend() -> subprocess.Popen[bytes] | None:
    if backend_is_ready():
        return None
    cmd = [sys.executable, "-m", "uvicorn", "Application.backend.server:app", "--host", HOST, "--port", str(PORT)]
    return subprocess.Popen(cmd, cwd=PROJECT_ROOT)

def main() -> None:
    server = start_backend()
    try:
        if server:
            server.wait()
    except KeyboardInterrupt:
        if server:
            server.terminate()
            server.wait(timeout=5)

if __name__ == "__main__":
    main()