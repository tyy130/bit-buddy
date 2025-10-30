# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Bit Buddy Desktop Application
Builds standalone executable for Windows, macOS, and Linux
"""

import sys
from pathlib import Path

block_cipher = None

# Determine platform-specific settings
if sys.platform == 'win32':
    icon_file = 'assets/buddy_icon.ico'
    name = 'BitBuddy'
elif sys.platform == 'darwin':
    icon_file = 'assets/buddy_icon.icns'
    name = 'BitBuddy'
else:
    icon_file = None
    name = 'bit-buddy'

a = Analysis(
    ['buddy_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include app modules
        ('app/*.py', 'app'),
        ('app/config.yaml', 'app'),
        
        # Include custodian templates
        ('custodian/manifest.yaml', 'custodian'),
        ('custodian/policy.yaml', 'custodian'),
        
        # Include enhanced_buddy and dependencies
        ('enhanced_buddy.py', '.'),
        ('installer.py', '.'),
        
        # Include README and docs
        ('README.md', '.'),
        ('docs/user/END_USER_GUIDE.md', 'docs/user'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'fastapi',
        'uvicorn',
        'pydantic',
        'starlette',
        
        # AI/ML dependencies
        'fastembed',
        'fastembed.text',
        'fastembed.text.text_embedding',
        'sentence_transformers',
        'chromadb',
        'numpy',
        'torch',
        
        # Document processing
        'pypdf',
        'docx2txt',
        'markdown_it',
        'chardet',
        
        # Utilities
        'yaml',
        'psutil',
        'requests',
        
        # Tkinter (should be included but being explicit)
        'tkinter',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'pandas',
        'scipy',
        'pytest',
        'IPython',
        'jupyter',
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
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if (icon_file and Path(icon_file).exists()) else None,
)

# macOS-specific app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='BitBuddy.app',
        icon=icon_file if Path(icon_file).exists() else None,
        bundle_identifier='com.bitbuddy.app',
        info_plist={
            'CFBundleName': 'Bit Buddy',
            'CFBundleDisplayName': 'Bit Buddy',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
