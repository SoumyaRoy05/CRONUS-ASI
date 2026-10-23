# Helios: Titan of the Sun & Screen Perception (`Titan_Council/Helios/`)

Helios is the watchful eye across the physical screen. Named after the Titan of the sun who sees everything beneath the heavens, Helios captures desktop frames, identifies visual GUI elements, computes normalized coordinates, and automates mouse and keyboard interactions.

---

## 1. Core Responsibilities

* **High-Speed Screen Capture**: Takes full-screen or window-specific captures using `PIL.ImageGrab` or direct Windows desktop APIs.
* **Coordinate Mapping & Normalization**: Translates raw pixel coordinates across high-DPI displays into standardized click targets.
* **GUI Automation**: Drives desktop interactions (clicks, keyboard input, drag-and-drop, scroll actions) using `pyautogui` and `pywin32`.
* **Visual Validation**: Confirms whether application windows opened successfully or dialog buttons rendered properly.

---

## 2. Data Schemas (`schemas.py`)

```python
class ScreenCoordinates(BaseModel):
    x: int
    y: int

class UIElement(BaseModel):
    label: str
    element_type: str  # 'button', 'input_field', 'window', 'icon'
    coordinates: ScreenCoordinates
    confidence: float

class VisionPerception(BaseModel):
    active_window_title: str
    elements_detected: List[UIElement]
    screen_resolution: str
```

---

## 3. Public API

```python
from Titan_Council.Helios import Helios

eye = Helios()

# Capture visual state
perception = eye.perceive_screen()
print(f"Active Window: {perception.active_window_title}")
print(f"Detected {len(perception.elements_detected)} UI elements.")

# Click a target element
eye.interact_ui(action="click", coords={"x": 500, "y": 300})
```
