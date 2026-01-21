"""
文档分析器模块

该模块提供文档元数据提取功能，支持 PDF、Word (.docx) 和 TXT 格式。
可以提取文件名、字符数和页数等信息。
"""
from pathlib import Path
from typing import Dict, List, Optional
import PyPDF2
from docx import Document


class DocumentAnalyzer:
    """文档分析器类

    用于提取文档的元数据信息，包括文件名、字符数和页数。
    """

    def __init__(self):
        """初始化文档分析器"""
        pass

    def analyze_file(self, file_path: str) -> Dict[str, Optional[str]]:
        """分析单个文档文件

        Args:
            file_path (str): 文档文件路径

        Returns:
            Dict[str, Optional[str]]: 包含文件名、字符数和页数的字典
                {
                    'filename': str,      # 文件名（含扩展名）
                    'char_count': str,    # 字符数（格式化后的字符串）
                    'page_count': str     # 页数（格式化后的字符串，TXT 文件为 '-'）
                }
        """
        path = Path(file_path)

        if not path.exists():
            return {
                'filename': path.name,
                'char_count': '错误',
                'page_count': '错误'
            }

        file_ext = path.suffix.lower()

        try:
            if file_ext == '.pdf':
                return self._analyze_pdf(path)
            elif file_ext == '.docx':
                return self._analyze_docx(path)
            elif file_ext == '.txt':
                return self._analyze_txt(path)
            else:
                return {
                    'filename': path.name,
                    'char_count': '不支持的格式',
                    'page_count': '-'
                }
        except Exception as e:
            return {
                'filename': path.name,
                'char_count': f'错误: {str(e)}',
                'page_count': '-'
            }

    def _analyze_pdf(self, path: Path) -> Dict[str, Optional[str]]:
        """分析 PDF 文件

        Args:
            path (Path): PDF 文件路径

        Returns:
            Dict[str, Optional[str]]: PDF 文件的元数据
        """
        char_count = 0
        page_count = 0

        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)

            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    char_count += len(text)

        return {
            'filename': path.name,
            'char_count': self._format_number(char_count),
            'page_count': str(page_count)
        }

    def _analyze_docx(self, path: Path) -> Dict[str, Optional[str]]:
        """分析 Word (.docx) 文件

        Args:
            path (Path): Word 文件路径

        Returns:
            Dict[str, Optional[str]]: Word 文件的元数据
        """
        doc = Document(path)
        char_count = 0

        # 统计所有段落的字符数
        for paragraph in doc.paragraphs:
            char_count += len(paragraph.text)

        # 统计表格中的字符数
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    char_count += len(cell.text)

        page_count = len(doc.sections)

        return {
            'filename': path.name,
            'char_count': self._format_number(char_count),
            'page_count': str(page_count)
        }

    def _analyze_txt(self, path: Path) -> Dict[str, Optional[str]]:
        """分析 TXT 文件

        Args:
            path (Path): TXT 文件路径

        Returns:
            Dict[str, Optional[str]]: TXT 文件的元数据
        """
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            char_count = len(content)

        return {
            'filename': path.name,
            'char_count': self._format_number(char_count),
            'page_count': '-'
        }

    def analyze_files(self, file_paths: List[str]) -> List[Dict[str, Optional[str]]]:
        """分析多个文档文件

        Args:
            file_paths (List[str]): 文档文件路径列表

        Returns:
            List[Dict[str, Optional[str]]]: 所有文档的元数据列表
        """
        results = []

        for file_path in file_paths:
            result = self.analyze_file(file_path)
            results.append(result)

        return results

    def _format_number(self, number: int) -> str:
        """格式化数字，添加千位分隔符

        Args:
            number (int): 要格式化的数字

        Returns:
            str: 格式化后的字符串
        """
        return f"{number:,}"