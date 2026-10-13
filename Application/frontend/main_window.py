"""
CRONUS Desktop Command Interface
Main Window application class coordinating GUI subsystems and background process
"""

from __future__ import annotations

import queue
import tkinter as tk
from tkinter import scrolledtext

from .components import CosmicPurpleBanner, OrganCard, ShinyGoldBanner, StatusPill
from .process import CronusProcess
from .theme import Theme
from .visualizer import KineticVisualizer


class CronusApp(tk.Tk):
    """Futuristic high-tech command interface for Cronus Voice Assistant."""

    def __init__(self) -> None:
        super().__init__()

        self.title("CRONUS")
        self.configure(bg=Theme.BG)
        self.geometry("940x660")
        self.minsize(760, 540)

        self._cronus = CronusProcess()
        self._build_ui()
        self._apply_titlebar_theme()
        self._set_state("stopped")
        self._visualizer.start()
        self._msg_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._poll_output_queue()

        # Clean up on window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Ensure window is surfaced to front on launch
        try:
            self.lift()
            self.attributes("-topmost", True)
            self.after_idle(self.attributes, "-topmost", False)
            self.focus_force()
        except Exception:
            pass

    def _apply_titlebar_theme(self) -> None:
        """Apply shiny metallic gold caption with black text to the Windows title bar."""
        import sys
        if sys.platform != "win32":
            return
        try:
            import ctypes
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()

            # Void Black (#06020E) & Hairline Imperial Gold (#C5A059) & Platinum Text (#FFFFFF)
            void_color = 0x0018070D     # 0x00BBGGRR (R=0x06, G=0x02, B=0x0E)
            gold_border = 0x0059A0C5    # 0x00BBGGRR (R=0xC5, G=0xA0, B=0x59)
            text_white = 0x00FFFFFF

            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(ctypes.c_int(gold_border)), ctypes.sizeof(ctypes.c_int))
            dwm.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(ctypes.c_int(void_color)), ctypes.sizeof(ctypes.c_int))
            dwm.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(ctypes.c_int(text_white)), ctypes.sizeof(ctypes.c_int))
        except Exception:
            pass

    # ── UI Construction ──────────────────────────────────────────────────
    def _build_ui(self) -> None:
        # ── 1. Shiny Metallic Gold Header Banner (Full Edge-to-Edge) ──
        self._banner = CosmicPurpleBanner(
            self,
            title="C R O N U S",
            subtitle="ARTIFICIAL SUPER-INTELLIGENT (ASI) AGENTIC SYSTEM",
            height=84,
        )
        self._banner.pack(fill=tk.X, side=tk.TOP)

        # Status Pill Badge docked cleanly inside the right of the Gold Banner
        self._status_pill = StatusPill(self._banner)
        self._banner.attach_right_widget(self._status_pill)

        # Outer Margin Container for Subsystems, Visualizer, Logs, and Controls
        outer = tk.Frame(self, bg=Theme.BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(12, 16))

        # ── 2. Organ Subsystems Telemetry Cards ──
        telemetry_row = tk.Frame(outer, bg=Theme.BG)
        telemetry_row.pack(fill=tk.X, pady=(0, 12))

        self._card_ears = OrganCard(
            telemetry_row,
            icon="🎧",
            name="OMNIPRESENT AUDITORY HORIZON",
            subtext="Quantum Acoustic Perception · Omniscient Stream",
            status_text="[ PASSIVE ]",
            icon_color=Theme.ACCENT_CYAN,
        )
        self._card_ears.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self._card_brain = OrganCard(
            telemetry_row,
            icon="🧠",
            name="CHRONO-COGNITIVE NEXUS",
            subtext="Superintelligent Neural Matrix · StateGraph Core",
            status_text="[ DORMANT ]",
            icon_color=Theme.ACCENT_VIOLET,
        )
        self._card_brain.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        self._card_mouth = OrganCard(
            telemetry_row,
            icon="🔊",
            name="THE LOGOS (VOICE OF DECREE)",
            subtext="Resonant Harmonic Synthesis · 24kHz Decree",
            status_text="[ SILENT ]",
            icon_color=Theme.ACCENT_AMBER,
        )
        self._card_mouth.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # ── 3. Kinetic Audio Visualizer Canvas ──
        self._visualizer = KineticVisualizer(
            outer,
            height=46,
            on_speaking_change=self._on_speaking_change,
        )
        self._visualizer.pack(fill=tk.X, pady=(0, 12))

        # ── 4. Control Bar ──
        controls = tk.Frame(outer, bg=Theme.BG)
        controls.pack(fill=tk.X, pady=(0, 12))

        self._start_btn = tk.Button(
            controls,
            text="▶   AWAKEN THE TITAN",
            font=Theme.FONT_BUTTON,
            bg=Theme.BTN_START_BG,
            fg="#FFFFFF",
            activebackground=Theme.BTN_START_ACTIVE,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=22,
            pady=7,
            cursor="hand2",
            command=self._on_start,
        )
        self._start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self._stop_btn = tk.Button(
            controls,
            text="■   STAND DOWN",
            font=Theme.FONT_BUTTON,
            bg=Theme.BTN_STOP_BG,
            fg=Theme.BTN_STOP_FG,
            activebackground=Theme.BTN_STOP_ACTIVE_BG,
            activeforeground=Theme.BTN_STOP_ACTIVE_FG,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=7,
            cursor="hand2",
            command=self._on_stop,
        )
        self._stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        self._clear_btn = tk.Button(
            controls,
            text="PURGE CHRONO-STREAM",
            font=Theme.FONT_BUTTON_SM,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
            activebackground=Theme.CARD_BORDER,
            activeforeground=Theme.TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self._clear_logs,
        )
        self._clear_btn.pack(side=tk.RIGHT)

        # ── 5. Neural Telemetry Stream (Log Panel) ──
        self._log_container = tk.Frame(
            outer,
            bg=Theme.CARD_BG,
            highlightbackground=Theme.GOLD_EDGE,
            highlightthickness=1,
        )
        log_container = self._log_container
        log_container.pack(fill=tk.BOTH, expand=True)

        # Stream Subheader
        stream_header = tk.Frame(log_container, bg=Theme.CARD_BG)
        stream_header.pack(fill=tk.X, padx=12, pady=(8, 4))

        tk.Label(
            stream_header,
            text="◆  CHRONO-ARCHIVE // SOVEREIGN STREAM",
            font=Theme.FONT_BADGE,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MUTED,
        ).pack(side=tk.LEFT)

        tk.Label(
            stream_header,
            text="● ZERO-LATENCY EVENT HORIZON",
            font=Theme.FONT_BADGE,
            bg=Theme.CARD_BG,
            fg=Theme.ACCENT_CYAN,
        ).pack(side=tk.RIGHT)

        self._log = scrolledtext.ScrolledText(
            log_container,
            bg=Theme.CARD_BG,
            fg=Theme.TEXT_MAIN,
            font=Theme.FONT_LOG,
            insertbackground=Theme.TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        self._log.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # Setup Tag Styling for colorful terminal output
        self._log.tag_configure("ears", foreground=Theme.ACCENT_CYAN, font=("Consolas", 10, "bold"))
        self._log.tag_configure("brain", foreground=Theme.ACCENT_VIOLET, font=("Consolas", 10, "bold"))
        self._log.tag_configure("mouth", foreground=Theme.ACCENT_AMBER, font=("Consolas", 10, "bold"))
        self._log.tag_configure("cns", foreground=Theme.ACCENT_CYAN, font=("Consolas", 10, "bold"))
        self._log.tag_configure("dim", foreground=Theme.TEXT_DIM)
        self._log.tag_configure("plain", foreground=Theme.TEXT_MAIN)

    def _on_speaking_change(self, is_speaking: bool) -> None:
        """Called by visualizer when Cronus transitions speaking state."""
        if hasattr(self, "_card_mouth") and self._cronus.running:
            if is_speaking:
                self._card_mouth.status_lbl.config(text="● DECREEING", fg=Theme.ACCENT_AMBER)
            else:
                self._card_mouth.status_lbl.config(text="● RESONATING", fg=Theme.ACCENT_AMBER)

    # ── State & Process Actions ──────────────────────────────────────────
    def _on_start(self) -> None:
        if self._cronus.running:
            return
        self._set_state("running")
        self._cronus.start(
            on_output=self._on_cronus_output,
            on_exit=self._on_cronus_exit,
        )

    def _on_stop(self) -> None:
        self._cronus.stop()
        self._set_state("stopped")

    def _on_close(self) -> None:
        if self._cronus.running:
            self._cronus.stop()
        self.destroy()

    def _clear_logs(self) -> None:
        self._log.configure(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.configure(state=tk.DISABLED)

    # ── Background Callbacks & Thread-Safe Queue ─────────────────────────
    def _poll_output_queue(self) -> None:
        """Poll the thread-safe message queue on the main GUI thread."""
        try:
            while True:
                msg_type, payload = self._msg_queue.get_nowait()
                if msg_type == "output":
                    self._append_log(str(payload))
                elif msg_type == "exit":
                    self._append_log(f"\n[SYSTEM] Cronus core deactivated (exit code {payload}).\n")
                    self._set_state("stopped")
        except queue.Empty:
            pass
        except Exception:
            pass
        self.after(30, self._poll_output_queue)

    def _on_cronus_output(self, text: str) -> None:
        self._msg_queue.put(("output", text))

    def _on_cronus_exit(self, code: int) -> None:
        self._msg_queue.put(("exit", code))

    # ── Helpers ──────────────────────────────────────────────────────────
    def _append_log(self, text: str) -> None:
        self._log.configure(state=tk.NORMAL)

        # Smart syntax highlighting for neural stream
        lower = text.lower()
        if "brain" in lower or "cognitive" in lower:
            tag = "brain"
        elif "ears" in lower or "acoustic" in lower or "start speaking" in lower:
            tag = "ears"
        elif "mouth" in lower or "final response:" in lower:
            tag = "mouth"
        elif "cns" in lower or "central nervous system" in lower:
            tag = "cns"
        elif text.startswith("=") or (text.startswith("-") and not any(k in lower for k in ["brain", "ears", "mouth", "cns"])):
            tag = "dim"
        else:
            tag = "plain"

        # Dynamically trigger visualizer voice reaction when Cronus speaks
        if "mouth is speaking" in lower or "final response:" in lower:
            words = len(text.split())
            duration = max(2.5, words * 0.35)
            self._visualizer.trigger_speech(duration)

        self._log.insert(tk.END, text, tag)
        self._log.see(tk.END)
        self._log.configure(state=tk.DISABLED)
        self._log.update_idletasks()

    def _set_state(self, state: str) -> None:
        if state == "running":
            self._visualizer.set_running(True)
            self._status_pill.set_active(
                accent_color="#E0AAFF",
                text="TITAN CORE ONLINE",
                bg_color="#120524",
            )
            self._start_btn.config(
                state=tk.DISABLED,
                bg=Theme.BTN_START_DIS_BG,
                fg=Theme.BTN_START_DIS_FG,
                text="●   TITAN AWAKENED",
            )
            self._stop_btn.config(
                state=tk.NORMAL,
                bg=Theme.BTN_STOP_RUN_BG,
                fg=Theme.BTN_STOP_RUN_FG,
                text="■   SEAL TITAN CORE",
            )

            if hasattr(self, "_card_ears"):
                self._card_ears.set_active(Theme.ACCENT_CYAN, "● PERCEIVING")
                self._card_brain.set_active(Theme.ACCENT_VIOLET, "● DECREEING")
                self._card_mouth.set_active(Theme.ACCENT_AMBER, "● RESONATING")
            if hasattr(self, "_visualizer"):
                self._visualizer.config(highlightbackground=Theme.ACCENT_CYAN)
            if hasattr(self, "_log_container"):
                self._log_container.config(highlightbackground=Theme.ACCENT_VIOLET)
        else:
            self._visualizer.set_running(False)
            self._status_pill.set_standby("TITAN STANDBY")
            self._start_btn.config(
                state=tk.NORMAL,
                bg=Theme.BTN_START_BG,
                fg="#FFFFFF",
                text="▶   AWAKEN THE TITAN",
            )
            self._stop_btn.config(
                state=tk.DISABLED,
                bg=Theme.BTN_STOP_BG,
                fg=Theme.BTN_STOP_FG,
                text="■   STAND DOWN",
            )

            if hasattr(self, "_card_ears"):
                self._card_ears.set_standby("[ PASSIVE ]")
                self._card_brain.set_standby("[ DORMANT ]")
                self._card_mouth.set_standby("[ SILENT ]")
            if hasattr(self, "_visualizer"):
                self._visualizer.config(highlightbackground=Theme.GOLD_EDGE)
            if hasattr(self, "_log_container"):
                self._log_container.config(highlightbackground=Theme.GOLD_EDGE)

