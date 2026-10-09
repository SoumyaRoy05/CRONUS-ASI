# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['Application/launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Application/frontend', 'Application/frontend'),
        ('Organs', 'Organs'),
        ('Behaviour', 'Behaviour'),
        ('Info-organs', 'Info-organs'),
        ('src/atlas_voice_assistant', 'src/atlas_voice_assistant'),
        ('atlas.py', '.'),
        ('llm.py', '.'),
        ('Mic_Check.py', '.'),
    ],
    hiddenimports=[
        'fastapi', 'uvicorn', 'starlette', 'faster_whisper', 'torch', 'numpy',
        'sounddevice', 'kokoro', 'langchain', 'langchain_core', 'langchain_google_genai',
        'langchain_groq', 'langchain_ollama', 'google.generativeai', 'openai', 'ollama',
        'openwakeword', 'phonemizer', 'pyttsx3', 'python_dotenv', 'reportlab', 'pydantic',
        'typing_extensions', 'anyio', 'h11', 'httptools', 'watchfiles', 'websockets',
        'cffi', 'cryptography', 'certifi', 'charset_normalizer', 'idna', 'requests',
        'urllib3', 'clr', 'sys', 'subprocess', 'threading',
    ],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'IPython', 'jupyter', 'notebook', 'pytest', 
        'setuptools', 'pip', 'wheel', 'build', 'tomli_w', 'virtualenv', 
        'distlib', 'filelock', 'jaraco', 'more_itertools',  
        
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
    name='ATLAS',
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