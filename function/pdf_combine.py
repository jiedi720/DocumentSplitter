"""
PDF 合并逻辑

该模块实现了对多个 PDF 文件的合并功能，
包括保留原始书签结构。
"""
import os
import PyPDF2
from pathlib import Path
from .file_handler import FileHandler


class PDFCombiner:
    """PDF 合并器

    该类提供了对多个 PDF 文件进行合并的功能，
    支持保留原始书签结构。
    """

    def __init__(self):
        """初始化 PDF 合并器

        创建文件处理器实例，用于处理通用文件操作。
        """
        self.file_handler = FileHandler()

    def merge_pdfs(self, input_files, output_path=None):
        """
        合并多个 PDF 文件

        该方法将多个 PDF 文件合并为一个单一的 PDF 文件，并保留原始书签。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str, optional): 输出文件路径，默认为自动生成

        Returns:
            str: 合并后文件的路径

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出
            ValueError: 当文件格式不正确或输入列表为空时抛出
        """
        # 验证输入文件列表
        if not input_files:
            raise ValueError("输入文件列表不能为空")

        # 验证所有输入文件是否为 PDF 格式
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"输入文件不存在: {file_path}")
            if not self.file_handler.get_file_type(file_path) == '.pdf':
                raise ValueError(f"文件不是有效的 PDF 格式: {file_path}")

        # 如果未指定输出路径，则自动生成
        if output_path is None:
            output_path = self.file_handler.generate_merge_output_filename(input_files)

        # 创建一个空的 PDF 写入器作为基础
        writer = PyPDF2.PdfWriter()

        # 页面偏移量
        page_offset = 0

        # 处理每个 PDF 文件
        for file_path in input_files:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # 添加所有页面
                for page in reader.pages:
                    writer.add_page(page)
                
                # 处理书签
                if hasattr(reader, 'outline') and reader.outline:
                    self._process_outline(reader.outline, writer, reader, page_offset)
                
                # 更新页面偏移量
                page_offset += len(reader.pages)

        # 写入输出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return output_path
    
    def _process_outline(self, outline, writer, reader, page_offset, parent=None):
        """
        处理 PDF 大纲（书签）

        Args:
            outline: 大纲对象
            writer: PDF 写入器对象
            reader: PDF 读取器对象
            page_offset: 页面偏移量
            parent: 父书签对象
        """
        last_added = None
        
        if isinstance(outline, list):
            for item in outline:
                if isinstance(item, list):
                    # 处理子大纲
                    if last_added:
                        self._process_outline(item, writer, reader, page_offset, last_added)
                else:
                    # 处理单个大纲项
                    try:
                        title = item.title
                        # 使用 get_destination_page_number 获取页码
                        page_num = reader.get_destination_page_number(item)
                        target_page = page_num + page_offset
                        # 添加书签并记录引用
                        last_added = writer.add_outline_item(title, target_page, parent=parent)
                    except Exception as e:
                        print(f"处理书签项时出错: {e}")
        else:
            # 处理单个大纲项
            try:
                title = outline.title
                page_num = reader.get_destination_page_number(outline)
                target_page = page_num + page_offset
                last_added = writer.add_outline_item(title, target_page, parent=parent)
            except Exception as e:
                print(f"处理书签项时出错: {e}")


