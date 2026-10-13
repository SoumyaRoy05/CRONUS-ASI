"""
CRONUS UI Theme & Design Tokens
Cosmic Purple Void & Luxury Gold Architecture
"""

from __future__ import annotations


class Theme:
    # ── Interface & Box Hierarchy ──
    # Interface backdrop retains the slight cosmic purple formerly on boxes
    BG            = "#0D0718"  # Slight Cosmic Purple Backdrop
    CARD_BG       = "#000000"  # All 5 Boxes always pure obsidian black
    CARD_BORDER   = "#D4AF37"  # Metallic Gold borders in standby
    GOLD_EDGE     = "#D4AF37"  # Imperial Gold edge before ignition

    # ── Titan Sovereign Luxury Gold ──
    GOLD_IMPERIAL = "#D4AF37"  # Imperial Gold
    GOLD_PALE     = "#E5C158"  # Pale / Champagne Gold
    GOLD_HAIRLINE = "#C5A059"  # Hairline Metallic Gold
    GOLD_DARK     = "#6E531C"  # Dark Burnished Gold Accent

    # ── Typography Colors ──
    TEXT_MAIN     = "#F5EFFF"  # Stellar White
    TEXT_MUTED    = "#9E8EB8"  # Nebula Gray
    TEXT_DIM      = "#55446C"  # Dark Starlight Gray

    # ── Telemetry Accent Colors ──
    ACCENT_CYAN   = "#38BDF8"  # Electric Cyan (Ears / Acoustic Sensor)
    ACCENT_VIOLET = "#A855F7"  # Titan Neon Violet (Brain / Cognitive Core)
    ACCENT_AMBER  = "#F59E0B"  # Solar Amber (Mouth / Vocal Organ)
    ACCENT_GREEN  = "#10B981"  # Emerald Green (Ignite Cronus)
    ACCENT_RED    = "#EF4444"  # High-Tech Crimson Red (Stand Down)

    # ── Button Colors (Ignite Green / Stand Down Red) ──
    BTN_START_BG        = "#10B981"  # Vibrant Emerald Green
    BTN_START_ACTIVE    = "#059669"  # Dark Emerald Green on press
    BTN_START_DIS_BG    = "#064E3B"  # Muted Dark Emerald when running
    BTN_START_DIS_FG    = "#34D399"  # Subtle glowing green text

    BTN_STOP_BG         = "#1E080B"  # Dark Red in Standby
    BTN_STOP_FG         = "#EF4444"  # Red text in Standby
    BTN_STOP_RUN_BG     = "#EF4444"  # Vibrant Crimson Red when Cronus is running
    BTN_STOP_RUN_FG     = "#FFFFFF"  # White text when active
    BTN_STOP_ACTIVE_BG  = "#DC2626"  # Active press Red
    BTN_STOP_ACTIVE_FG  = "#FFFFFF"

    # ── Fonts ──
    FONT_TITLE      = ("Segoe UI", 21, "bold")
    FONT_SUBTITLE   = ("Consolas", 9, "bold")
    FONT_CARD_TITLE = ("Segoe UI", 9, "bold")
    FONT_CARD_SUB   = ("Consolas", 8)
    FONT_BADGE      = ("Consolas", 8, "bold")
    FONT_BUTTON     = ("Segoe UI", 10, "bold")
    FONT_BUTTON_SM  = ("Consolas", 9, "bold")
    FONT_LOG        = ("Consolas", 10)
    FONT_EMOJI      = ("Segoe UI Emoji", 20)
