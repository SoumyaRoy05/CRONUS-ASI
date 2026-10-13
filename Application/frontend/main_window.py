"""
CRONUS Desktop Command Interface
Main Window application class coordinating GUI subsystems and background process
"""

from __future__ import annotations

import sys

# Register Windows Application User Model ID before any Tkinter / UI initialization
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cronus.asi.titan.v1")
    except Exception:
        pass

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

        # Register Windows Application User Model ID for dedicated taskbar grouping & icon
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cronus.asi.titan.v1")
        except Exception:
            pass

        self.title("CRONUS")
        self.configure(bg=Theme.BG)
        self.geometry("940x660")
        self.minsize(760, 540)

        # Setup Window Titlebar Icon, Taskbar Icon & System Tray
        self._setup_icons_and_tray()

        self._cronus = CronusProcess()
        self._build_ui()
        self._apply_titlebar_theme()
        self._set_state("stopped")
        self._visualizer.start()
        self._msg_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._poll_output_queue()



        # Clean up on window close
        self.protocol("WM_DELETE_WINDOW", self._on_window_close_clicked)

        # Ensure window is surfaced to front on launch
        try:
            self.lift()
            self.attributes("-topmost", True)
            self.after_idle(self.attributes, "-topmost", False)
            self.focus_force()
        except Exception:
            pass

    def _setup_icons_and_tray(self) -> None:
        """Configure high-DPI window icon, taskbar identity, and system tray icon."""
        from pathlib import Path
        pics_dir = Path(r"D:\Codes\CRONUS-ASI\pictures")
        assets_dir = Path(__file__).resolve().parent / "assets"
        ico_candidates = [
            pics_dir / "cronus.ico",
            pics_dir / "CRONUS.ico",
            Path(r"D:\Codes\CRONUS-ASI\cronus.ico"),
            assets_dir / "cronus.ico",
        ]
        ico_path = next((p for p in ico_candidates if p.exists()), ico_candidates[0])

        png_candidates = [
            pics_dir / "CRONUS.png",
            pics_dir / "cronus.png",
            Path(r"D:\Codes\CRONUS-ASI\cronus.png"),
            assets_dir / "cronus.png",
        ]
        png_path = next((p for p in png_candidates if p.exists()), png_candidates[0])

        # 1. High-DPI Windows Top-Level Icon & Taskbar Attachment
        if ico_path.exists():
            try:
                self.iconbitmap(default=str(ico_path.resolve()))
            except Exception:
                pass
            self._apply_native_taskbar_icon(ico_path.resolve())

        # 2. Start System Tray in background thread
        self._tray_icon = None
        if png_path.exists():
            self._init_system_tray(png_path)

    def _apply_native_taskbar_icon(self, ico_path) -> None:
        """Inject native Win32 48x48, 32x32, and 16x16 icon handles and AppUserModelID directly into the OS window frame."""
        import sys
        if sys.platform != "win32":
            return
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            shell32 = ctypes.windll.shell32
            self.update_idletasks()

            child_hwnd = self.winfo_id()
            parent_hwnd = user32.GetAncestor(child_hwnd, 2) or user32.GetParent(child_hwnd) or child_hwnd

            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x0010
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            # 1. Load 48x48 (Taskbar / Alt-Tab), 32x32 (Standard), 16x16 (Titlebar / Taskbar Small)
            hicon_big = user32.LoadImageW(None, str(ico_path), IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
            if not hicon_big:
                hicon_big = user32.LoadImageW(None, str(ico_path), IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
            hicon_sm = user32.LoadImageW(None, str(ico_path), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

            for hwnd in (parent_hwnd, child_hwnd):
                if hicon_big:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
                if hicon_sm:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_sm)
                try:
                    set_class = getattr(user32, "SetClassLongPtrW", getattr(user32, "SetClassLongW"))
                    if hicon_big:
                        set_class(hwnd, -14, hicon_big)   # GCLP_HICON
                    if hicon_sm:
                        set_class(hwnd, -34, hicon_sm)    # GCLP_HICONSM
                except Exception:
                    pass

            # 2. Assign PKEY_AppUserModel_ID directly to window's IPropertyStore for Windows 10/11 taskbar binding
            try:
                import comtypes
                from comtypes import GUID, IUnknown, COMMETHOD, HRESULT

                class PROPERTYKEY(ctypes.Structure):
                    _fields_ = [('fmtid', GUID), ('pid', wintypes.DWORD)]

                class PROPVARIANT(ctypes.Structure):
                    _fields_ = [
                        ('vt', wintypes.WORD),
                        ('wReserved1', wintypes.WORD),
                        ('wReserved2', wintypes.WORD),
                        ('wReserved3', wintypes.WORD),
                        ('pwszVal', wintypes.LPWSTR),
                        ('dummy', ctypes.c_byte * 8)
                    ]

                class IPropertyStore(IUnknown):
                    _iid_ = GUID('{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}')
                    _methods_ = [
                        COMMETHOD([], HRESULT, 'GetCount', (['out'], ctypes.POINTER(wintypes.DWORD), 'cProps')),
                        COMMETHOD([], HRESULT, 'GetAt', (['in'], wintypes.DWORD, 'iProp'), (['out'], ctypes.POINTER(PROPERTYKEY), 'pkey')),
                        COMMETHOD([], HRESULT, 'GetValue', (['in'], ctypes.POINTER(PROPERTYKEY), 'key'), (['out'], ctypes.POINTER(PROPVARIANT), 'pv')),
                        COMMETHOD([], HRESULT, 'SetValue', (['in'], ctypes.POINTER(PROPERTYKEY), 'key'), (['in'], ctypes.POINTER(PROPVARIANT), 'pv')),
                        COMMETHOD([], HRESULT, 'Commit')
                    ]

                pStore = ctypes.POINTER(IPropertyStore)()
                iid = IPropertyStore._iid_
                if shell32.SHGetPropertyStoreForWindow(parent_hwnd, ctypes.byref(iid), ctypes.byref(pStore)) == 0 and pStore:
                    pkey = PROPERTYKEY()
                    pkey.fmtid = GUID('{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}')
                    pkey.pid = 5
                    pv = PROPVARIANT()
                    pv.vt = 31  # VT_LPWSTR
                    pv.pwszVal = "cronus.asi.titan.v1"
                    pStore.SetValue(ctypes.byref(pkey), ctypes.byref(pv))
                    pStore.Commit()
            except Exception:
                pass
        except Exception:
            pass

    def _init_system_tray(self, png_path) -> None:
        """Initialize background system tray icon near clock."""
        try:
            import threading
            from PIL import Image
            import pystray

            tray_img = Image.open(png_path).resize((64, 64))

            def on_restore(icon, item):
                self.after(0, self._restore_window)

            def on_toggle(icon, item):
                self.after(0, self._on_stop if self._cronus.running else self._on_start)

            def on_exit(icon, item):
                self.after(0, self._quit_application)

            menu = pystray.Menu(
                pystray.MenuItem("CRONUS ASI - Sovereign Agent", lambda i, it: None, enabled=False),
                pystray.MenuItem("Open CRONUS", on_restore, default=True),
                pystray.MenuItem(lambda it: ("■ Stand Down Titan" if self._cronus.running else "▶ Awaken Titan"), on_toggle),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit CRONUS", on_exit)
            )

            self._tray_icon = pystray.Icon("CRONUS", tray_img, "CRONUS Super-Intelligence", menu)
            self._tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
            self._tray_thread.start()
        except Exception as e:
            print(f"[CRONUS] System tray notice: {e}")

    def _on_window_close_clicked(self) -> None:
        """When the window 'X' is clicked, seamlessly minimize to the system tray while keeping Titan online."""
        self.withdraw()
        if hasattr(self, "_tray_icon") and self._tray_icon:
            if not getattr(self, "_notified_tray", False):
                self._notified_tray = True
                try:
                    self._tray_icon.notify(
                        "CRONUS is active in the background. The Titan remains listening.",
                        "CRONUS - ASI Online"
                    )
                except Exception:
                    pass

    def _restore_window(self) -> None:
        """Restore window from system tray and surface to the foreground."""
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.focus_force()

    def _quit_application(self) -> None:
        """Completely terminate CRONUS, halt background audio/LLM engines, and remove tray icon."""
        if hasattr(self, "_tray_icon") and self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        if self._cronus.running:
            self._cronus.stop()
        self.destroy()

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
        self._quit_application()

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

