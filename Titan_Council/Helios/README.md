# 👁️ Helios — Titan of the Sun & Chief Vision Officer

> *"No window remains unseen; what exists upon the glass is illuminated and mastered."*  
> **Council Role:** Chief Vision Officer, Screen Perception, Mouse/Keyboard & GUI Automation  
> **Allegiance:** Operating under the sovereign command of **CRONUS ASI** in dedicated service to creator **Soumya Roy**.

---

## 1. Overview & Purpose

In the **CRONUS ASI** cognitive ecosystem, **Helios** gives the Council eyes and physical hands upon the desktop. While Atlas executes shell commands and manages the backend, Helios operates visual software that lacks command-line interfaces: browser applications, media players, graphic editors, and OS dialog windows.

Helios captures screen telemetry, tracks the foreground application window, and injects mouse clicks and keystrokes with surgical precision.

### Core Responsibilities
1. **Screen & Window Perception:** Detects display resolutions and tracks active foreground window titles in real time.
2. **GUI Interaction:** Dispatches mouse clicks to Cartesian coordinates, types into text fields, and injects system hotkeys (`Ctrl+S`, `Alt+Tab`, `Win+D`).
3. **Multimodal Task Routing:** Determines during Council deliberation whether a directive can be executed headlessly by Atlas or requires GUI interaction.

---

## 2. Operational Protocol

```
                  [ Directive Requiring Desktop Action ]
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    1. Inspect Display State   │
                    │ (Resolution & Active Window)  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   2. Coordinate/Field Target  │
                    │  (Determine Click/Type Target)│
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     3. GUI Action Injection   │
                    │  (Mouse Click / Text / Hotkey)│
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ 4. ScreenPerceptionResult Out │
                    │ (Telemetry delivered to Brain)│
                    └───────────────────────────────┘
```

---

## 3. Data Contracts & Schemas (`schemas.py`)

* **`ScreenActionType`**: Action category (`capture_screen`, `click_coordinate`, `type_text`, `hotkey`, `get_active_window`).
* **`ScreenCoordinate`**: 2D Cartesian `(x, y)` pixel location.
* **`ScreenAction`**: Pydantic instruction containing target coordinates, text, or key combinations.
* **`ScreenPerceptionResult`**: Output containing foreground window title, screen resolution, detected UI items, and latency.

---

## 4. How to Use Helios

```python
import asyncio
from Titan_Council.Helios import Helios, ScreenAction, ScreenActionType

async def main():
    helios = Helios()
    
    # 1. Inspect display telemetry
    state = await helios.inspect_screen()
    print(f"Active Window: {state.active_window} | Resolution: {state.screen_resolution}")
    
    # 2. Inject hotkey
    hotkey_action = ScreenAction(
        action_type=ScreenActionType.HOTKEY,
        keys=["ctrl", "shift", "esc"]
    )
    res = await helios.execute_gui_action(hotkey_action)
    print(f"Status: {res.status} | {res.message}")

asyncio.run(main())
```
