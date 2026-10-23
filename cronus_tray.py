"""
CRONUS System Tray Daemon (JARVIS Always-On Mode)
Runs CRONUS silently in the Windows System Tray with zero terminal windows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Reconfigure stdout/stderr for clean utf-8 log file output
root_dir = Path(__file__).resolve().parent
log_path = root_dir / "cronus.log"


class _LogWriter:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.terminal = sys.__stdout__

    def write(self, message):
        if not message:
            return
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass
        if self.terminal:
            try:
                self.terminal.write(message)
            except Exception:
                pass

    def flush(self):
        if self.terminal:
            try:
                self.terminal.flush()
            except Exception:
                pass


sys.stdout = _LogWriter(log_path)
sys.stderr = sys.stdout

import atexit
import subprocess
import threading
import time
from typing import Optional

from PIL import Image
import pystray
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 1. Environment & Hardware Setup
# -----------------------------------------------------------------------------
load_dotenv(root_dir / ".env")

nvidia_dir = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
if nvidia_dir.exists():
    for bin_folder in nvidia_dir.rglob("bin"):
        if bin_folder.is_dir():
            try:
                os.add_dll_directory(str(bin_folder))
                os.environ["PATH"] = str(bin_folder) + os.pathsep + os.environ.get("PATH", "")
            except Exception:
                pass

# Single instance lock file
lock_path = root_dir / "cronus_tray.lock"
try:
    if lock_path.exists():
        # Check if lock is stale
        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                old_pid = int(f.read().strip())
            # Check if process exists
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1000, False, old_pid)
            if handle:
                kernel32.CloseHandle(handle)
                # Process is already running!
                print(f"[CRONUS Tray] Instance already running (PID {old_pid}). Exiting duplicate.")
                sys.exit(0)
        except Exception:
            pass

    with open(lock_path, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
except Exception:
    pass


def _cleanup_lock():
    try:
        if lock_path.exists():
            lock_path.unlink()
    except Exception:
        pass


atexit.register(_cleanup_lock)

# -----------------------------------------------------------------------------
# 2. Global State Flags
# -----------------------------------------------------------------------------
_running = threading.Event()
_running.set()

_muted = threading.Event()  # Cleared = listening, Set = muted

_tray_icon: Optional[pystray.Icon] = None
_worker_thread: Optional[threading.Thread] = None

# -----------------------------------------------------------------------------
# 3. Audio / AI Assistant Worker Loop
# -----------------------------------------------------------------------------
def _assistant_worker():
    """Background thread running the continuous listening & thinking loop."""
    print(f"\n{'=' * 60}")
    print("          CRONUS JARVIS SYSTEM TRAY DAEMON ONLINE          ")
    print(f"{'=' * 60}\n")

    try:
        from faster_whisper import WhisperModel
        from Organs.ears import hear
        from Organs.mouth import speak
        from Organs.brain import Brain
        from Behaviour.persona import get_wake_receipt

        print("[CNS] Initializing acoustic and cognitive subsystems in background...")
        brain = Brain(mouth=speak)

        # Greet on startup
        receipt = get_wake_receipt()
        brain.remember_assistant_message(receipt)
        speak(receipt)

        print("[CNS] Loading Faster-Whisper on CUDA (float16)...")
        whisper_model = WhisperModel(
            "base.en",
            device="cuda",
            compute_type="float16",
            local_files_only=True,
        )

        print("[CNS] JARVIS listening loop active.")

        while _running.is_set():
            if _muted.is_set():
                time.sleep(0.5)
                continue

            transcript = hear(whisper_model)
            if transcript and _running.is_set() and not _muted.is_set():
                brain.think(transcript)

    except Exception as e:
        print(f"[CNS - Error in Tray Worker]: {e}")
    finally:
        print("[CNS] Tray worker loop terminated.")


# -----------------------------------------------------------------------------
# 4. Tray Menu Actions
# -----------------------------------------------------------------------------
def _toggle_mute(icon, item):
    if _muted.is_set():
        _muted.clear()
        print("[CRONUS Tray] Voice listening UNMUTED.")
    else:
        _muted.set()
        print("[CRONUS Tray] Voice listening MUTED.")


def _open_log(icon, item):
    try:
        os.startfile(str(log_path))
    except Exception:
        subprocess.Popen(["notepad.exe", str(log_path)])


def _open_folder(icon, item):
    try:
        os.startfile(str(root_dir))
    except Exception:
        pass


def _on_exit(icon, item):
    print("[CRONUS Tray] Exit requested by user. Shutting down gracefully...")
    _running.clear()
    _muted.set()
    _cleanup_lock()
    icon.stop()


def _get_status_label(item):
    if _muted.is_set():
        return "Status: Muted"
    return "Status: Listening (Active)"


def _is_mute_checked(item):
    return _muted.is_set()


# -----------------------------------------------------------------------------
# 5. Tray Main Entrypoint
# -----------------------------------------------------------------------------
def main():
    global _tray_icon, _worker_thread

    ico_path = root_dir / "pictures" / "cronus.ico"
    png_path = root_dir / "pictures" / "CRONUS.png"

    if ico_path.exists():
        img = Image.open(ico_path)
    elif png_path.exists():
        img = Image.open(png_path)
    else:
        img = Image.new("RGB", (64, 64), color=(218, 165, 32))

    menu = pystray.Menu(
        pystray.MenuItem("CRONUS ASI", lambda: None, enabled=False),
        pystray.MenuItem(_get_status_label, lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Mute Microphone", _toggle_mute, checked=_is_mute_checked),
        pystray.MenuItem("View Live Log", _open_log),
        pystray.MenuItem("Open Project Folder", _open_folder),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit CRONUS", _on_exit),
    )

    _tray_icon = pystray.Icon("CRONUS", img, "CRONUS Digital Steward", menu)

    # Launch background AI worker
    _worker_thread = threading.Thread(target=_assistant_worker, daemon=True)
    _worker_thread.start()

    # Run tray message loop (blocks main thread until Exit is clicked)
    _tray_icon.run()


if __name__ == "__main__":
    main()
