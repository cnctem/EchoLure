# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 基础路径
base_path = os.path.abspath(SPECDIR if 'SPECDIR' in dir() else os.path.dirname(__file__))
project_path = os.path.dirname(base_path)

# 分析依赖
a = Analysis(
    [os.path.join(project_path, 'release', 'run.py')],
    pathex=[project_path],
    binaries=[],
    datas=[
        (os.path.join(project_path, 'echolure'), 'echolure'),
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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    icon=None,
)

# macOS App Bundle
app = BUNDLE(
    exe,
    name='EchoLure.app',
    icon=None,
    bundle_identifier='com.echolure.game',
)
