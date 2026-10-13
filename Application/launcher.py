"""
Cronus Desktop Launcher
Entry point for the Cronus Voice Assistant graphical command interface.
"""

from __future__ import annotations

import sys

# 0. Windows Process Explicit AppUserModelID (MUST be registered before any UI/Tk initialization)
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cronus.asi.titan.v1")
    except Exception:
        pass

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pathlib import Path

# Ensure project root and Application directory are in sys.path
_app_dir = Path(__file__).resolve().parent
_root_dir = _app_dir.parent
for p in (_root_dir, _app_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from Application.frontend import CronusApp
except ImportError:
    from frontend import CronusApp


def main() -> None:
    print("[CRONUS] Initializing Graphical Command Interface...", flush=True)
    try:
        app = CronusApp()
        print("[CRONUS] Desktop Command Interface online.", flush=True)
        app.mainloop()
    except Exception as e:
        print(f"[CRONUS - Critical Error]: Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
