"""
Helios Schemas (Pydantic V2)
Desktop GUI automation, screen perception, and visual action models.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ScreenActionType(str, Enum):
    CAPTURE_SCREEN = "capture_screen"
    CLICK_COORDINATE = "click_coordinate"
    TYPE_TEXT = "type_text"
    HOTKEY = "hotkey"
    LOCATE_ELEMENT = "locate_element"
    GET_ACTIVE_WINDOW = "get_active_window"


class ScreenCoordinate(BaseModel):
    """Cartesian 2D screen coordinate."""
    x: int = Field(description="X pixel coordinate")
    y: int = Field(description="Y pixel coordinate")


class ScreenAction(BaseModel):
    """An atomic visual or desktop GUI action."""
    action_type: ScreenActionType = Field(description="Type of GUI or screen action")
    coordinate: Optional[ScreenCoordinate] = Field(default=None, description="Target pixel coordinates for click")
    text: Optional[str] = Field(default=None, description="Text to type into focused field")
    keys: List[str] = Field(default_factory=list, description="Keyboard hotkey combination (e.g. ['ctrl', 's'])")
    target_label: Optional[str] = Field(default=None, description="Visual description or OCR text label to find")
    timeout_seconds: float = Field(default=10.0, description="Max action timeout")


class ScreenPerceptionResult(BaseModel):
    """Result of screen capture, window inspection, or GUI execution."""
    status: str = Field(description="Outcome status: SUCCESS or FAILED")
    active_window: str = Field(default="", description="Title of foreground/active application window")
    screen_resolution: str = Field(default="Unknown", description="Display resolution (e.g. 1920x1080)")
    elements_detected: List[str] = Field(default_factory=list, description="Detected visual elements or labels")
    screenshot_path: Optional[str] = Field(default=None, description="Saved frame path if captured")
    message: str = Field(default="", description="Detailed result or error message")
    elapsed_ms: float = Field(default=0.0, description="Execution duration in milliseconds")
