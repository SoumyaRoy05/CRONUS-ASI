# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Resolve project root dynamically whether spec is in Application/backend/ or root
_current_dir = Path(SPECPATH).resolve() if "SPECPATH" in locals() else Path(__file__).resolve().parent
if _current_dir.name == "backend" and _current_dir.parent.name == "Application":
    PROJECT_ROOT = _current_dir.parent.parent
elif _current_dir.name == "backend":
    PROJECT_ROOT = _current_dir.parent
else:
    PROJECT_ROOT = _current_dir

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "Application" / "launcher.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / "Organs"), "Organs"),
        (str(PROJECT_ROOT / "Behaviour"), "Behaviour"),
        (str(PROJECT_ROOT / "Info-organs"), "Info-organs"),
        (str(PROJECT_ROOT / "User_info"), "User_info"),
        (str(PROJECT_ROOT / "cronus.py"), "."),
        (str(PROJECT_ROOT / "llm.py"), "."),
        (str(PROJECT_ROOT / ".env"), "."),
    ],
    hiddenimports=[
        "faster_whisper", "torch", "numpy",
        "sounddevice", "kokoro", "langchain", "langchain_core", "langchain_google_genai",
        "langchain_groq", "langchain_ollama", "google.generativeai", "openai", "ollama",
        "phonemizer", "python_dotenv", "pydantic",
        "typing_extensions",
        "cffi", "cryptography", "certifi", "charset_normalizer", "idna", "requests",
        "urllib3", "sys", "subprocess", "threading", "tkinter",
        "Application.frontend", "Application.frontend.theme",
        "Application.frontend.process", "Application.frontend.components",
        "Application.frontend.visualizer", "Application.frontend.main_window",
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[
        "matplotlib", "IPython", "jupyter", "notebook", "pytest",
        "setuptools", "pip", "wheel", "build", "tomli_w", "virtualenv",
        "distlib", "filelock", "jaraco", "more_itertools",
        "fastapi", "uvicorn", "starlette",
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="CRONUS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
