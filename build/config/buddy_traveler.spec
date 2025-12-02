# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Bit Buddy Portable (Traveler) build
- Onedir outputs for easy copy to USB/flash drive
- Excludes heavy ML stacks (torch/transformers/sentence_transformers/chromadb)
- Keeps core functionality with graceful degradation
"""

import sys
from pathlib import Path

# SPECPATH points to build/config
ROOT = Path(SPECPATH).resolve().parents[1]

block_cipher = None

# Platform-specific icon/name
if sys.platform == 'win32':
    icon_file = str(ROOT / 'assets' / 'buddy_icon.ico')
    name = 'BitBuddy-Portable'
elif sys.platform == 'darwin':
    icon_file = str(ROOT / 'assets' / 'buddy_icon.icns')
    name = 'BitBuddy-Portable'
else:
    icon_file = None
    name = 'bit-buddy-portable'

# Analysis
a = Analysis(
    [str(ROOT / 'buddy_gui.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Core app modules and config
        (f"{ROOT}/app/*.py", 'app'),
        (f"{ROOT}/app/config.yaml", 'app'),

        # Minimal custodian templates
        (f"{ROOT}/custodian/manifest.yaml", 'custodian'),
        (f"{ROOT}/custodian/policy.yaml", 'custodian'),

        # Core scripts
        (f"{ROOT}/enhanced_buddy.py", '.'),
        (f"{ROOT}/installer.py", '.'),
        (f"{ROOT}/deploy.py", '.'),

        # Docs (optional)
        (f"{ROOT}/README.md", '.'),
    ],
    hiddenimports=[
        # Core runtime dependencies
        'fastapi', 'uvicorn', 'pydantic', 'starlette',
        'fastembed', 'fastembed.text', 'fastembed.text.text_embedding',
        'numpy', 'pypdf', 'docx2txt', 'markdown_it', 'chardet',
        'yaml', 'psutil', 'requests',
        'tkinter', 'tkinter.scrolledtext', 'tkinter.filedialog', 'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy ML stacks (defer to runtime install if desired)
        'torch', 'transformers', 'sentence_transformers', 'chromadb',
        # Size reducers
        'matplotlib', 'pandas', 'scipy', 'pytest', 'IPython', 'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# For onedir builds (portable), exclude binaries/datas from EXE and include them in COLLECT
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if (icon_file and Path(icon_file).exists()) else None,
)

# Always produce onedir for portability
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=name,
)
