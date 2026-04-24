# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[
        # matplotlib – both backend names needed (code uses qt5agg explicitly)
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_qtagg',
        # reportlab – platypus and its submodules are not auto-detected
        'reportlab',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.enums',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.lib.utils',
        'reportlab.platypus',
        'reportlab.platypus.tables',
        'reportlab.platypus.flowables',
        'reportlab.rl_settings',
    ],
    excludes=[
        # legacy tkinter UI – dead code, not reachable from main.py
        # (pyparsing.__init__ imports pyparsing.testing which imports unittest,
        # so stdlib test modules must NOT be excluded)
        'tkinter',
        '_tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
)
