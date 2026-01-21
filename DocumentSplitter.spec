# -*- mode: python ; coding: utf-8 -*-
import os

# 获取当前目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(SPEC))

# 图标文件的完整路径（使用 PNG 格式）
ICON_PATH = os.path.join(current_dir, 'icons', 'DocumentSplitter.png')

a = Analysis(
    ['DocumentSplitter.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含项目目录
        ('function', 'function'),  # 包含整个 function 目录
        ('gui', 'gui'),            # 包含整个 gui 目录
        ('icons', 'icons'),        # 包含整个 icons 目录
        # 如果有配置文件，在此处添加
        # ('config.ini', '.'),
    ],
    hiddenimports=[
        # tkinter 相关的隐式导入
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        # tkinterdnd2 拖拽功能
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        # 项目模块
        'function.file_handler',
        'function.pdf_splitter',
        'function.word_splitter',
        'function.txt_splitter',
        'gui.file_selector',
        'gui.main_window',
        'gui.settings_panel',
        # 第三方库依赖
        'PyPDF2',
        'docx',
        'pdfplumber',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'pytest',
        'unittest',
        # PySide6 相关（本项目使用 tkinter，不需要）
        'PySide6',
        'PyQt5',
        'PyQt6',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DocumentSplitter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为 False 以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,  # 设置程序图标和标题栏图标（支持 PNG 格式）
)

coll = COLLECT(
    exe,                # 包含之前定义的 EXE 对象（主程序）
    a.binaries,         # 收集所有依赖的 DLL/动态库
    a.datas,            # 收集所有的资源文件（图片、配置等）
    strip=False,        # 是否移除符号表（通常选 False 以防报错）
    upx=True,           # 是否使用 UPX 压缩混淆
    upx_exclude=[],     # 排除不压缩的文件
    name='DocumentSplitter',  # 最终生成的文件夹名称
)