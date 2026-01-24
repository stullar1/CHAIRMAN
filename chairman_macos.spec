# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CHAIRMAN - macOS App Bundle
Creates a .app bundle for macOS
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project directory
project_dir = Path(SPECPATH)

# Collect all data files
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
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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

# Create macOS app bundle
app = BUNDLE(
    coll,
    name='CHAIRMAN.app',
    icon=str(project_dir / 'assets' / 'icons' / 'app_icon.icns') if (project_dir / 'assets' / 'icons' / 'app_icon.icns').exists() else None,
    bundle_identifier='com.chairman.app',
    info_plist={
        'CFBundleName': 'CHAIRMAN',
        'CFBundleDisplayName': 'CHAIRMAN',
        'CFBundleGetInfoString': 'Barber Shop Management System',
        'CFBundleIdentifier': 'com.chairman.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Supports dark mode
        'LSMinimumSystemVersion': '10.15.0',
    },
)
