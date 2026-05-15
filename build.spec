# PyInstaller spec — produces single .exe bundling Python + all deps
# Run: python -m PyInstaller build.spec

import os
from pathlib import Path

block_cipher = None
ROOT = str(Path('.').resolve())
TEMPLATE = os.path.join(ROOT, 'assets', 'HM WCM CV (sample Assistant Professor).docx')

a = Analysis(
    [os.path.join('src', 'launcher.py')],
    pathex=[ROOT, os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[
        (TEMPLATE, '.'),
        (os.path.join('src', 'config.py'), '.'),
        (os.path.join('src', 'schema.py'), '.'),
        (os.path.join('src', 'extract.py'), '.'),
        (os.path.join('src', 'populate.py'), '.'),
        (os.path.join('src', 'app.py'), '.'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'pystray._win32',
        'PIL._tkinter_finder',
        'pdfminer.high_level',
        'pdfminer.layout',
        'pdfminer.utils',
        'docx',
    ],
    hookspath=[],
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
    name='HMCVReformatter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    windowed=True,
    icon=None,
)
