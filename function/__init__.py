"""
功能模块 - 文档分割与分析工具

该模块包含了文档分割与分析工具的核心功能实现，
包括文件处理、PDF分割、Word分割、文本分割和文档分析等功能。
"""

# 导入所有功能模块
from .file_handler import FileHandler
from .pdf_splitter import PDFSplitter
from .word_splitter import WordSplitter
from .txt_splitter import TxtSplitter
from .document_analyzer import DocumentAnalyzer

__all__ = [
    'FileHandler',
    'PDFSplitter',
    'WordSplitter',
    'TxtSplitter',
    'DocumentAnalyzer'
]