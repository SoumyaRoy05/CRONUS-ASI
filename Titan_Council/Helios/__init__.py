"""
Helios Module - Titan Council
Titan of the Sun, All-Seeing Vision, and Desktop GUI Control.
"""

from .schemas import (
    ScreenAction,
    ScreenActionType,
    ScreenCoordinate,
    ScreenPerceptionResult,
)
from .prompts import HELIOS_SYSTEM_PROMPT, HELIOS_DELIBERATION_PROMPT
from .tools import (
    get_screen_resolution,
    get_active_window_title,
    inspect_display_telemetry,
)
from .agent import Helios

__all__ = [
    "Helios",
    "ScreenAction",
    "ScreenActionType",
    "ScreenCoordinate",
    "ScreenPerceptionResult",
    "HELIOS_SYSTEM_PROMPT",
    "HELIOS_DELIBERATION_PROMPT",
    "get_screen_resolution",
    "get_active_window_title",
    "inspect_display_telemetry",
]
