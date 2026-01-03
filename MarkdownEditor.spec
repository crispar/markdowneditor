# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Exclude unnecessary Qt modules to reduce size
qt_excludes = [
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DExtras',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DRender',
    'PySide6.QtAxContainer',
    'PySide6.QtBluetooth',
    'PySide6.QtCharts',
    'PySide6.QtConcurrent',
    'PySide6.QtDataVisualization',
    'PySide6.QtDesigner',
    'PySide6.QtHelp',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtNfc',
    'PySide6.QtNetworkAuth',
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtQuick',
    'PySide6.QtQuick3D',
    'PySide6.QtQuickControls2',
    'PySide6.QtQuickWidgets',
    'PySide6.QtQml',
    'PySide6.QtRemoteObjects',
    'PySide6.QtScxml',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtSql',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
    'PySide6.QtTest',
    'PySide6.QtUiTools',
    'PySide6.QtVirtualKeyboard',
    'PySide6.QtWebSockets',
    'PySide6.QtXml',
]

# Exclude unnecessary Python modules
python_excludes = [
    'tkinter',
    'unittest',
    'pydoc',
    'doctest',
    'test',
    'PIL.ImageTk',
    'numpy',
    'scipy',
    'pandas',
    'matplotlib',
    'multiprocessing',
    'concurrent',
    'curses',
    'lib2to3',
    'xmlrpc',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/styles/preview.css', 'src/styles'),
        ('resources/js/mermaid.min.js', 'resources/js'),
    ],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'pygments.lexers',
        'pygments.formatters',
        'pygments.styles.monokai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=qt_excludes + python_excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary binaries to reduce size
# We filter out specific DLLs and all translation files (.qm)
a.binaries = [x for x in a.binaries if not any(
    exclude in x[0].lower() for exclude in [
        'qt6designer',
        'qt63d',
        'qt6charts',
        'qt6datavisualization',
        'qt6multimedia',
        'qt6bluetooth',
        'qt6sensors',
        'qt6serialport',
        'qt6sql',
        'qt6pdf',
        'qt6virtualkeyboard',
        'qt6networkauth',
        # Note: qt6quick, qt6qml, opengl32sw are required by QtWebEngine
    ]
)]

# Remove translation files to save space (can be 20MB+)
a.datas = [x for x in a.datas if not x[0].endswith('.qm')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarkdownEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
