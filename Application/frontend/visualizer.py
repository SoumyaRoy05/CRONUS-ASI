"""
Kinetic Audio Visualizer
Celestial Singularity Horizon: Symmetrical Gravitational Waves & Chrono-Singularity Core.
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from collections.abc import Callable

from .theme import Theme


class KineticVisualizer(tk.Frame):
    """Encapsulates the celestial singularity audio horizon."""

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 46,
        on_speaking_change: Callable[[bool], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.GOLD_EDGE,
            highlightthickness=1,
            **kwargs,
        )

        self._on_speaking_change = on_speaking_change
        self._canvas = tk.Canvas(
            self,
            bg=Theme.CARD_BG,
            height=height,
            bd=0,
            highlightthickness=0,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._anim_phase = 0.0
        self._anim_running = False
        self._speaking_until = 0.0
        self._current_amp = 3.5
        self._was_speaking = False

    def start(self) -> None:
        """Start the animation loop."""
        self._animate()

    def set_running(self, running: bool) -> None:
        """Toggle between dormant celestial breathing and ignited reality distortion."""
        self._anim_running = running
        if not running:
            self._speaking_until = 0.0
            self._current_amp = 3.5
            if self._was_speaking and self._on_speaking_change:
                self._on_speaking_change(False)
            self._was_speaking = False
            self.config(highlightbackground=Theme.GOLD_EDGE)
        else:
            self.config(highlightbackground=Theme.ACCENT_CYAN)

    def trigger_speech(self, duration: float) -> None:
        """Trigger dynamic voice waveform surge for estimated speech duration."""
        self._speaking_until = max(self._speaking_until, time.time() + duration)

    def _animate(self) -> None:
        canvas = self._canvas
        canvas.delete("all")

        w = canvas.winfo_width()
        h = canvas.winfo_height()

        if w > 20 and h > 10:
            mid_y = h / 2.0
            mid_x = w / 2.0

            if self._anim_running:
                # ── State 2 & 3: IGNITED (Resting Singularity vs Voice Warp) ──
                now = time.time()
                is_speaking = now < self._speaking_until

                if is_speaking != self._was_speaking:
                    self._was_speaking = is_speaking
                    if self._on_speaking_change:
                        self._on_speaking_change(is_speaking)

                target_amp = 16.5 if is_speaking else 4.0
                self._current_amp += (target_amp - self._current_amp) * (0.16 if is_speaking else 0.08)

                speed = 0.14 if is_speaking else 0.05
                self._anim_phase += speed

                # Symmetrical Horizon Baseline (fading towards edges)
                canvas.create_line(0, mid_y, w, mid_y, fill="#1E0A34", width=1)

                # Multidimensional Gravitational Waves
                waves = [
                    (Theme.ACCENT_CYAN, 0.85, 0.032, 0.0, 1),
                    (Theme.ACCENT_VIOLET, 1.0, 0.046, 1.2, 2),
                    (Theme.ACCENT_AMBER if is_speaking else Theme.GOLD_IMPERIAL, 1.25 if is_speaking else 0.9, 0.060, 2.4, 2),
                ]

                step = 4
                for color, scale_amp, freq, phase_offset, line_w in waves:
                    points_top = []
                    points_bot = []
                    amp = self._current_amp * scale_amp
                    for x in range(0, w + step, step):
                        norm_dist = (x - mid_x) / (w * 0.46)
                        env = math.exp(-(norm_dist ** 2) * 2.1)
                        if is_speaking:
                            wave = (
                                math.sin(x * freq - self._anim_phase + phase_offset) * 0.65
                                + math.sin(x * freq * 2.2 - self._anim_phase * 1.7 + phase_offset) * 0.25
                                + math.sin(x * freq * 3.8 - self._anim_phase * 2.4) * 0.10
                            )
                        else:
                            wave = math.sin(x * freq - self._anim_phase + phase_offset)

                        y_offset = wave * amp * env
                        points_top.extend([x, mid_y - y_offset])
                        if is_speaking:
                            points_bot.extend([x, mid_y + (y_offset * 0.85)])

                    if len(points_top) >= 4:
                        canvas.create_line(points_top, fill=color, width=line_w, smooth=True)
                    if is_speaking and len(points_bot) >= 4:
                        canvas.create_line(points_bot, fill=color, width=1, smooth=True)

                # Central Chrono-Singularity Node
                node_r = 4.5 if is_speaking else 3.0
                node_col = "#FFFFFF" if is_speaking else Theme.GOLD_IMPERIAL
                canvas.create_polygon(
                    mid_x, mid_y - node_r,
                    mid_x + node_r, mid_y,
                    mid_x, mid_y + node_r,
                    mid_x - node_r, mid_y,
                    fill=node_col, outline="",
                )

            else:
                # ── State 1: DORMANT CELESTIAL BREATHING (Titan at Rest) ──
                now = time.time()
                breath_phase = now * 1.6
                breath_amp = 2.8 + math.sin(breath_phase) * 1.2

                # 1. Gold Horizon Axis
                canvas.create_line(0, mid_y, w, mid_y, fill="#2A1042", width=1)
                horizon_len = min(w * 0.40, 240)
                canvas.create_line(
                    mid_x - horizon_len, mid_y,
                    mid_x + horizon_len, mid_y,
                    fill="#4D1D75", width=1,
                )

                # 2. Dual Mirrored Breathing Waves (Gold & Violet)
                points_top = []
                points_bot = []
                step = 4
                for x in range(0, w + step, step):
                    norm_dist = (x - mid_x) / (w * 0.40)
                    env = math.exp(-(norm_dist ** 2) * 2.4)
                    w_val = math.sin(x * 0.038 - breath_phase) * breath_amp * env
                    points_top.extend([x, mid_y - abs(w_val)])
                    points_bot.extend([x, mid_y + abs(w_val)])

                if len(points_top) >= 4:
                    canvas.create_line(points_top, fill=Theme.GOLD_DARK, width=1, smooth=True)
                if len(points_bot) >= 4:
                    canvas.create_line(points_bot, fill="#3A125E", width=1, smooth=True)

                # 3. Astrolabe Singularity Reticle at Center
                # Golden Diamond Core
                canvas.create_polygon(
                    mid_x, mid_y - 3.5,
                    mid_x + 3.5, mid_y,
                    mid_x, mid_y + 3.5,
                    mid_x - 3.5, mid_y,
                    fill=Theme.GOLD_IMPERIAL, outline="",
                )
                # Delicate Astrolabe Reticle Ticks
                canvas.create_line(mid_x - 14, mid_y - 2, mid_x - 14, mid_y + 2, fill=Theme.GOLD_DARK, width=1)
                canvas.create_line(mid_x + 14, mid_y - 2, mid_x + 14, mid_y + 2, fill=Theme.GOLD_DARK, width=1)
                canvas.create_line(mid_x - 28, mid_y, mid_x - 18, mid_y, fill=Theme.GOLD_DARK, width=1)
                canvas.create_line(mid_x + 18, mid_y, mid_x + 28, mid_y, fill=Theme.GOLD_DARK, width=1)

        self.after(35, self._animate)
