# -*- mode: python ; coding: utf-8 -*-

import os

project_path = os.path.abspath('.')

a = Analysis(
    [os.path.join(project_path, 'release', 'run.py')],
    pathex=[project_path],
    binaries=[],
    datas=[
        (os.path.join(project_path, 'echolure'), 'echolure'),
        (os.path.join(project_path, 'asset'), 'asset'),
    ],
    hiddenimports=[
        'numpy',
        'pygame',
        'pygame.mixer',
        'pygame.font',
        'pygame.draw',
        'pygame.display',
        'pygame.event',
        'pygame.time',
        'pygame.key',
        'pygame.mouse',
        'pygame.surface',
        'pygame.rect',
        'pygame.constants',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EchoLure',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('asset', 'icon.png'),
)

# macOS App Bundle
app = BUNDLE(
    exe,
    name='EchoLure.app',
    icon=None,
    bundle_identifier='com.echolure.game',
)
