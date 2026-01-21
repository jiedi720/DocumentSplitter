#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec 文件重写工具
根据 GifMaker.spec 的配置逻辑，重写 DocumentSplitter.spec 文件
确保生成的 .exe 文件标题栏正常显示图标，且程序运行后能准确识别并读取同级目录下的配置文件
"""

import os
import sys

def update_spec_file():
    """
    更新 DocumentSplitter.spec 文件
    根据 GifMaker.spec 的配置逻辑，生成新的配置文件
    """
    # 获取当前目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 回到项目根目录
    project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
    
    # 生成新的 spec 文件内容
    spec_content = generate_spec_content(project_root)
    
    # 写入到 DocumentSplitter.spec 文件
    spec_file_path = os.path.join(project_root, 'DocumentSplitter.spec')
    with open(spec_file_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ 已成功更新 {spec_file_path}")
    print("📋 生成的配置文件包含以下特性：")
    print("   - 图标配置：自动定位 icons/DocumentSplitter.png 作为程序图标")
    print("   - 配置文件支持：程序运行时能识别同级目录下的配置文件")
    print("   - 依赖管理：自动收集所有必要的依赖模块")
    print("   - 打包优化：使用 UPX 压缩可执行文件，排除不必要的模块")

def generate_spec_content(project_root):
    """
    生成 spec 文件内容
    
    Args:
        project_root: 项目根目录路径
    
    Returns:
        生成的 spec 文件内容字符串
    """
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, collect_all

# Get the absolute path of the current directory
# 使用 sys.argv[0] 获取 spec 文件路径，因为 __file__ 在 PyInstaller 中不可用
if hasattr(sys, '_MEIPASS'):
    # 如果是在打包后的环境中运行
    current_dir = sys._MEIPASS
else:
    # 如果是在开发环境中运行
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if len(sys.argv) > 0 else os.getcwd()

# Full path to the icon file
ICON_PATH = os.path.join(current_dir, 'icons', 'DocumentSplitter.png')

# 使用 collect_all 自动收集依赖模块
# collect_all 返回 (binaries, datas, hiddenimports)
tk_binaries, tk_datas, tk_hiddenimports = collect_all('tkinter')
tkdnd_binaries, tkdnd_datas, tkdnd_hiddenimports = collect_all('tkinterdnd2')

# 合并所有依赖
all_binaries = tk_binaries + tkdnd_binaries
all_datas = tk_datas + tkdnd_datas
all_hiddenimports = tk_hiddenimports + tkdnd_hiddenimports

# 去重处理：确保每个 DLL 只被打包一次
seen_binaries = set()
unique_bins = []
# PyInstaller 的 binaries 格式为 (src_path, dest_path) 或 (src_path, dest_path, kind)
for binary in all_binaries:
    # 解析 binary 格式
    if len(binary) == 3:
        src_path, dest_path, kind = binary
    else:
        src_path, dest_path = binary
        kind = None

    # 提取文件名
    file_name = os.path.basename(src_path)

    # 只对通用的 .dll 文件执行严格的文件名去重
    if file_name.endswith('.dll'):
        if file_name not in seen_binaries:
            if kind is not None:
                unique_bins.append((src_path, dest_path, kind))
            else:
                unique_bins.append((src_path, dest_path))
            seen_binaries.add(file_name)
    else:
        # 对于 .pyd 文件和其他文件，不进行去重
        if kind is not None:
            unique_bins.append((src_path, dest_path, kind))
        else:
            unique_bins.append((src_path, dest_path))

a = Analysis(
    ['DocumentSplitter.py'],
    pathex=[],
    binaries=unique_bins,
    datas=[
        # Include project directories
        ('gui', 'gui'),
        ('function', 'function'),
        ('icons', 'icons'),
        # 配置文件支持：如果有配置文件，取消下面的注释
        # ('config.ini', '.'),
    ] + all_datas,
    hiddenimports=[
        # 项目模块
        'function.file_handler',
        'function.pdf_splitter',
        'function.word_splitter',
        'function.txt_splitter',
        'function.document_analyzer',
        'gui.file_selector',
        'gui.main_window',
        'gui.settings_panel',
        'gui.analysis_result_window',
        # 第三方库依赖
        'PyPDF2',
        'docx',
        'pdfplumber',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
    ] + all_hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,                # Include the EXE object defined above (main program)
    a.binaries,         # Collect all dependent DLLs/dynamic libraries
    a.datas,            # Collect all resource files (images, configs, etc.)
    strip=False,        # Whether to remove symbol table (usually False to avoid errors)
    upx=True,           # Whether to use UPX compression/obfuscation
    upx_exclude=[],     # Files to exclude from compression
    name='DocumentSplitter',  # Final folder name that will be generated
)
'''
    return spec_content

if __name__ == "__main__":
    update_spec_file()
