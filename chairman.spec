# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CHAIRMAN - Barber Shop Management App
Creates a one-folder distribution with all assets
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project directory
project_dir = Path(SPECPATH)

# Collect all data files - these will be extracted alongside the exe
datas = [
    (str(project_dir / 'assets'), 'assets'),
    (str(project_dir / 'style.qss'), '.'),
]

# Hidden imports for PySide6 and other modules
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtMultimedia',
    'PySide6.QtCharts',
    'sqlite3',
    'hashlib',
    'secrets',
    'pathlib',
    'datetime',
    'json',
    'logging',
    'typing',
]

a = Analysis(
    ['app.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create a one-folder bundle (easier to distribute)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CHAIRMAN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / 'assets' / 'icons' / 'app_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CHAIRMAN',
)
