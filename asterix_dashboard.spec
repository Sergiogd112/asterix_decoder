# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['dashboard.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('mapdata.py', '.'),
        ('Test_Data', 'Test_Data'),
    ],
    hiddenimports=[
        'dearpygui',
        'numpy',
        'pandas',
        'tqdm',
        'decoder.decoder',
        'decoder.geoutils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'contextily',
        'imageio',
        'ffmpeg-python',
        'ipykernel',
        'ipython',
        'ipywidgets',
        'nbformat',
        'black',
    ],
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
    name='asterix_dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
