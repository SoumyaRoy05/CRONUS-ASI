"""
UI Components for CRONUS Desktop Launcher
OrganCard telemetry, StatusPill header badge, and CosmicPurpleBanner (Titan of Supreme Command & Time)
"""

from __future__ import annotations

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

from .theme import Theme


class OrganCard(tk.Frame):
    """An individual organ telemetry card with prominent icon, 2px gold borders, and dynamic tinting."""

    def __init__(
        self,
        parent: tk.Widget,
        icon: str,
        name: str,
        subtext: str,
        status_text: str = "OFFLINE",
        name_color: str | None = None,
        icon_color: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.GOLD_EDGE,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs,
        )

        self._default_icon_color = icon_color or Theme.GOLD_IMPERIAL

        self._content_row = tk.Frame(self, bg=Theme.CARD_BG)
        self._content_row.pack(fill=tk.X, expand=True)

        # High-visibility colored icon glyph
        self.icon_lbl = tk.Label(
            self._content_row,
            text=icon,
            font=("Segoe UI Emoji", 20),
            bg=Theme.CARD_BG,
            fg=self._default_icon_color,
        )
        self.icon_lbl.pack(side=tk.LEFT, padx=(0, 12))

        self._info_col = tk.Frame(self._content_row, bg=Theme.CARD_BG)
        self._info_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._top_line = tk.Frame(self._info_col, bg=Theme.CARD_BG)
        self._top_line.pack(fill=tk.X)

        self.name_lbl = tk.Label(
            self._top_line,
            text=name,
            font=Theme.FONT_CARD_TITLE,
            bg=Theme.CARD_BG,
            fg=name_color or Theme.TEXT_MAIN,
        )
        self.name_lbl.pack(side=tk.LEFT)

        self.status_lbl = tk.Label(
            self._top_line,
            text=status_text,
            font=Theme.FONT_CARD_STATUS if hasattr(Theme, "FONT_CARD_STATUS") else Theme.FONT_CARD_SUB,
            bg=Theme.CARD_BG,
            fg=Theme.GOLD_IMPERIAL,
        )
        self.status_lbl.pack(side=tk.RIGHT)

        self.sub_lbl = tk.Label(
            self._info_col,
            text=subtext,
            font=Theme.FONT_CARD_SUB,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
        )
        self.sub_lbl.pack(anchor="w", pady=(2, 0))

    def set_active(self, accent_color: str, status_text: str) -> None:
        """Light up card with subsystem accent color and status."""
        self.config(highlightbackground=accent_color)
        self.name_lbl.config(fg=accent_color)
        self.status_lbl.config(text=status_text, fg=accent_color)
        self.icon_lbl.config(fg=accent_color)

    def set_standby(self, status_text: str = "OFFLINE") -> None:
        """Reset card to muted uniform standby appearance with gold edge."""
        self.config(highlightbackground=Theme.GOLD_EDGE)
        self.name_lbl.config(fg=Theme.TEXT_MAIN)
        self.status_lbl.config(text=status_text, fg=Theme.GOLD_IMPERIAL)
        self.icon_lbl.config(fg=self._default_icon_color)

    def set_card_bg(self, color: str) -> None:
        """Seamlessly update background across all internal elements."""
        self.config(bg=color)
        self._content_row.config(bg=color)
        self.icon_lbl.config(bg=color)
        self._info_col.config(bg=color)
        self._top_line.config(bg=color)
        self.name_lbl.config(bg=color)
        self.status_lbl.config(bg=color)
        self.sub_lbl.config(bg=color)


class StatusPill(tk.Frame):
    """Header status badge indicating overall Central Nervous System activation."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(
            parent,
            bg="#000000",
            highlightbackground=Theme.GOLD_EDGE,
            highlightthickness=1,
            padx=12,
            pady=5,
            **kwargs,
        )

        self.dot = tk.Label(
            self,
            text="●",
            font=("Segoe UI", 8, "bold"),
            bg="#000000",
            fg=Theme.GOLD_IMPERIAL,
        )
        self.dot.pack(side=tk.LEFT, padx=(0, 6))

        self.text_lbl = tk.Label(
            self,
            text="TITAN STANDBY",
            font=("Consolas", 8, "bold"),
            bg="#000000",
            fg=Theme.GOLD_IMPERIAL,
        )
        self.text_lbl.pack(side=tk.LEFT)

    def set_active(self, accent_color: str = "#E0AAFF", text: str = "TITAN CORE ACTIVE", bg_color: str = "#120524") -> None:
        self.config(highlightbackground="#D4AF37", bg=bg_color)
        self.dot.config(fg=accent_color, bg=bg_color)
        self.text_lbl.config(text=text, fg="#FFFFFF", bg=bg_color)

    def set_standby(self, text: str = "TITAN STANDBY") -> None:
        self.config(highlightbackground=Theme.GOLD_EDGE, bg="#000000")
        self.dot.config(fg=Theme.GOLD_IMPERIAL, bg="#000000")
        self.text_lbl.config(text=text, fg=Theme.GOLD_IMPERIAL, bg="#000000")


class CosmicPurpleBanner(tk.Canvas):
    """Modern Cosmic Purple, Imperial Gold & Void Black Header Banner for CRONUS."""

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "C R O N U S",
        subtitle: str = "ARTIFICIAL SUPER-INTELLIGENT (ASI) AGENTIC SYSTEM",
        height: int = 84,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            height=height,
            bd=0,
            highlightthickness=0,
            bg="#020104",
            **kwargs,
        )
        self._height = height
        self._title_text = title
        self._subtitle_text = subtitle
        self._current_w = 940
        self._photo_img: ImageTk.PhotoImage | None = None
        self._right_widget: tk.Widget | None = None
        self._right_window_id: int | None = None

        self._draw_banner(self._current_w)
        self.bind("<Configure>", self._on_resize)

    def attach_right_widget(self, widget: tk.Widget) -> None:
        self._right_widget = widget
        self._update_right_widget()

    def _update_right_widget(self) -> None:
        if self._right_widget and self._current_w > 10:
            target_x = self._current_w - 24
            target_y = self._height / 2
            if self._right_window_id is None:
                self._right_window_id = self.create_window(
                    target_x,
                    target_y,
                    window=self._right_widget,
                    anchor="e",
                )
            else:
                self.coords(self._right_window_id, target_x, target_y)

    def _render_cosmic_nebula(self, width: int, height: int) -> Image.Image:
        # Base pure obsidian void: [2, 1, 4] -> profound deep black darkness
        img_arr = np.full((height, width, 3), [2, 1, 4], dtype=np.float32)
        y, x = np.mgrid[0:height, 0:width]

        # Cosmic Singularity Violet Glow (left side atmospheric bloom)
        dist_singularity = ((x - 130) / 260.0) ** 2 + ((y - 41) / 38.0) ** 2
        singularity_glow = np.exp(-dist_singularity * 1.8) * 0.45
        violet_singularity = np.array([68, 18, 110], dtype=np.float32)
        for c in range(3):
            img_arr[:, :, c] += (violet_singularity[c] - img_arr[:, :, c]) * singularity_glow

        # Right anchor: very subtle deep cosmic mist
        dist_right = ((x - (width - 160)) / 280.0) ** 2 + ((y - 41) / 45.0) ** 2
        right_glow = np.exp(-dist_right * 2.2) * 0.22
        violet_deep = np.array([38, 10, 64], dtype=np.float32)
        for c in range(3):
            img_arr[:, :, c] += (violet_deep[c] - img_arr[:, :, c]) * right_glow

        # Horizontal Event Horizon Line (y ~ 54)
        horizon_dist = ((y - 54) / 6.0) ** 2
        horizon_glow = np.exp(-horizon_dist * 1.5) * 0.18
        horizon_fade = np.sin(np.linspace(0, np.pi, width)) ** 2.0
        horizon_intensity = horizon_glow * horizon_fade[None, :]
        horizon_color = np.array([125, 42, 185], dtype=np.float32)
        for c in range(3):
            img_arr[:, :, c] += (horizon_color[c] - img_arr[:, :, c]) * horizon_intensity

        # Top subtle obsidian violet line
        top_fade = np.sin(np.linspace(0, np.pi, width)) ** 1.8
        top_col = np.array([45, 14, 72], dtype=np.float32) * top_fade[:, None]
        img_arr[0, :] = top_col

        # Bottom Dual-Trim: Razor Imperial Gold Hairline with Cosmic Purple Underglow
        bot_glow_col = np.array([55, 16, 90], dtype=np.float32) * (np.sin(np.linspace(0, np.pi, width)) ** 1.6)[:, None]
        img_arr[-3, :] = bot_glow_col

        x_norm = np.linspace(0, np.pi, width)
        gold_curve = np.sin(x_norm) ** 1.2
        gold_base = np.array([197, 160, 89], dtype=np.float32)    # #C5A059
        gold_bright = np.array([235, 198, 115], dtype=np.float32) # #EBC673
        gold_dark = np.array([90, 68, 28], dtype=np.float32)

        gold_hairline = gold_dark + (gold_base - gold_dark) * gold_curve[:, None] + (gold_bright - gold_base) * (gold_curve[:, None] ** 4) * 0.4
        img_arr[-2, :] = gold_hairline

        # Pure obsidian drop shadow
        img_arr[-1, :] = [0, 0, 0]

        return Image.fromarray(np.uint8(np.clip(img_arr, 0, 255)))

    def _draw_banner(self, w: int) -> None:
        h = self._height
        img = self._render_cosmic_nebula(w, h)
        self._photo_img = ImageTk.PhotoImage(img)

        self.delete("all")
        self._right_window_id = None
        self.create_image(0, 0, image=self._photo_img, anchor="nw", tags="bg_img")

        # ── 1. Master Title: C R O N U S ──
        title_y = 34
        # Deep cosmic shadow
        self.create_text(
            29, title_y + 1,
            text=self._title_text,
            font=("Segoe UI", 21, "bold"),
            fill="#140526",
            anchor="w",
            tags="banner_text",
        )
        # Platinum core title
        self.create_text(
            28, title_y,
            text=self._title_text,
            font=("Segoe UI", 21, "bold"),
            fill="#FFFFFF",
            anchor="w",
            tags="banner_text",
        )

        # ── 2. Subtitle: ARTIFICIAL SUPER-INTELLIGENT (ASI) AGENTIC SYSTEM ──
        sub_y = 62
        self.create_text(
            28, sub_y,
            text="ARTIFICIAL SUPER-INTELLIGENT (ASI) AGENTIC SYSTEM",
            font=("Consolas", 9, "bold"),
            fill="#D4AF37",
            anchor="w",
            tags="banner_text",
        )

        self.tag_lower("bg_img")
        self._update_right_widget()

    def _on_resize(self, event: tk.Event) -> None:
        w = event.width
        if w < 50 or w == self._current_w:
            return
        self._current_w = w
        self._draw_banner(w)


# Backward-compatible alias
ShinyGoldBanner = CosmicPurpleBanner
