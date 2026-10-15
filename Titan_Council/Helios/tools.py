"""
Helios Tools
Desktop screen inspection, foreground window detection, and GUI automation primitives.
"""

from __future__ import annotations
import ctypes
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_screen_resolution() -> str:
    """Returns the primary screen resolution on Windows."""
    try:
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        return f"{w}x{h}"
    except Exception:
        return "1920x1080"


def get_active_window_title() -> str:
    """Returns the title of the active foreground window on Windows."""
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "No Active Window"
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return "Desktop / Background"
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    except Exception as e:
        return f"Error detecting window: {e}"


def inspect_display_telemetry() -> Dict[str, Any]:
    """Inspects display metrics and current UI foreground state."""
    res = get_screen_resolution()
    win = get_active_window_title()
    return {
        "resolution": res,
        "foreground_window": win,
        "platform": sys.platform,
        "gui_automation_ready": True,
    }
