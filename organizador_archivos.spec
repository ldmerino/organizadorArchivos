# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# Configuración para macOS
block_cipher = None

# Datos adicionales que podrían ser necesarios
added_files = []

# Librerías ocultas que PyInstaller podría no detectar
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'send2trash',
    'watchdog',
    'watchdog.observers',
    'watchdog.events',
    'PyPDF2',
    'fitz',  # PyMuPDF
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.pdfgen.canvas',
    'dateutil',
    'regex',
    'organizer.main_window',
    'organizer.processors.pdf_processor',
    'organizer.processors.pdf_thread',
    'organizer.ui.pdf_dialog',
    'organizer.ui.pdf_tabs',
    'organizer.ui.styles',
    'organizer.utils.patterns'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrganizadorArchivos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Configuración del ícono
    icon='app-icon.ico'
)

# Para macOS, crear también el bundle .app
app = BUNDLE(
    exe,
    name='OrganizadorArchivos.app',
    icon='app-icon.ico',
    bundle_identifier='com.organizador.archivos',
    version='1.0.0'
)
