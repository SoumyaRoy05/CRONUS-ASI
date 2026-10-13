# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Resolve project root dynamically (Application/backend/ is 2 levels below root)
_spec_dir = Path(SPECPATH).resolve() if "SPECPATH" in locals() else Path(__file__).resolve().parent
if _spec_dir.name == "backend" and _spec_dir.parent.name == "Application":
    PROJECT_ROOT = _spec_dir.parent.parent
elif _spec_dir.name == "backend":
    PROJECT_ROOT = _spec_dir.parent
else:
    PROJECT_ROOT = _spec_dir

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "Application" / "launcher.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "Application" / "frontend"), "Application/frontend"),
        (str(PROJECT_ROOT / "Organs"), "Organs"),
        (str(PROJECT_ROOT / "Behaviour"), "Behaviour"),
        (str(PROJECT_ROOT / "Info-organs"), "Info-organs"),
        (str(PROJECT_ROOT / "User_info"), "User_info"),
        (str(PROJECT_ROOT / "src" / "cronus_asi"), "src/cronus_asi"),
        (str(PROJECT_ROOT / "cronus.py"), "."),
        (str(PROJECT_ROOT / "llm.py"), "."),
        (str(PROJECT_ROOT / "Mic_Check.py"), "."),
        (str(PROJECT_ROOT / ".env"), "."),
    ],
    hiddenimports=[
        "faster_whisper", "torch", "numpy",
        "sounddevice", "kokoro", "langchain", "langchain_core", "langchain_google_genai",
        "langchain_groq", "langchain_ollama", "google.generativeai", "openai", "ollama",
        "openwakeword", "phonemizer", "pyttsx3", "python_dotenv", "reportlab", "pydantic",
        "typing_extensions", "anyio",
        "cffi", "cryptography", "certifi", "charset_normalizer", "idna", "requests",
        "urllib3", "sys", "subprocess", "threading", "tkinter", "tkinter.scrolledtext",
        "PIL", "PIL.Image", "PIL.ImageTk", "PIL.ImageDraw", "PIL.ImageFont",
        "Application.frontend", "Application.frontend.theme",
        "Application.frontend.process", "Application.frontend.components",
        "Application.frontend.visualizer", "Application.frontend.main_window",
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[
        "matplotlib", "IPython", "jupyter", "notebook", "pytest",
        "virtualenv",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CRONUS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="CRONUS",
)
