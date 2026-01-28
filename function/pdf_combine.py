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

        # 创建 PDF 写入器对象
        writer = PyPDF2.PdfWriter()

        # 页面偏移量，用于调整书签页码
        page_offset = 0

        # 合并所有 PDF 文件
        for file_index, file_path in enumerate(input_files):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # 将所有页面添加到写入器
                for page in reader.pages:
                    writer.add_page(page)
                
                # 尝试使用最基本的方法处理书签
                try:
                    # 直接使用 writer.add_outline_item 添加书签
                    # 这里我们使用一种更简单的方法：为每个文件添加一个目录项
                    # 这样至少可以确保每个文件的内容都能被访问
                    
                    # 添加一个文件标题书签
                    file_title = f"文件 {file_index + 1}: {os.path.basename(file_path)}"
                    file_bookmark = writer.add_outline_item(file_title, page_offset)
                    
                    # 为每个页面添加一个简单的书签，确保用户能访问所有内容
                    num_pages = len(reader.pages)
                    if num_pages > 1:
                        # 如果文件有多个页面，为每个页面添加书签
                        for i in range(num_pages):
                            page_title = f"页面 {i + 1}"
                            target_page = page_offset + i
                            writer.add_outline_item(page_title, target_page, parent=file_bookmark)
                    
                    # 尝试获取并处理原始书签，作为文件标题的子书签
                    self._add_original_bookmarks(reader, writer, page_offset, file_bookmark)
                    
                except Exception as e:
                    print(f"处理书签时出错: {e}")
                
                # 更新页面偏移量
                page_offset += len(reader.pages)

        # 将内容写入输出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return output_path

    def _add_original_bookmarks(self, reader, writer, page_offset, parent=None):
        """
        添加原始书签

        尝试获取并添加原始 PDF 文件中的书签

        Args:
            reader: PDF 读取器对象
            writer: PDF 写入器对象
            page_offset: 页面偏移量
            parent: 父书签对象
        """
        try:
            # 尝试获取大纲
            if hasattr(reader, 'outline'):
                outline = reader.outline
                if outline:
                    self._process_outline(outline, writer, page_offset, parent)
            elif hasattr(reader, 'outlines'):
                outlines = reader.outlines
                if outlines:
                    self._process_outline(outlines, writer, page_offset, parent)
        except Exception as e:
            print(f"获取大纲时出错: {e}")

    def _process_outline(self, outline, writer, page_offset, parent=None):
        """
        处理大纲（书签）

        Args:
            outline: 大纲对象
            writer: PDF 写入器对象
            page_offset: 页面偏移量
            parent: 父书签对象
        """
        # 处理列表类型的大纲
        if isinstance(outline, list):
            for item in outline:
                self._process_outline_item(item, writer, page_offset, parent)
        # 处理单个大纲项
        else:
            self._process_outline_item(outline, writer, page_offset, parent)

    def _process_outline_item(self, item, writer, page_offset, parent=None):
        """
        处理单个大纲项

        Args:
            item: 大纲项
            writer: PDF 写入器对象
            page_offset: 页面偏移量
            parent: 父书签对象
        """
        try:
            # 处理元组类型的大纲项
            if isinstance(item, tuple):
                if len(item) >= 2:
                    title = item[0]
                    page_ref = item[1]
                    
                    # 尝试获取页码
                    page_num = 0
                    try:
                        if hasattr(page_ref, 'page_number'):
                            page_num = page_ref.page_number
                        elif isinstance(page_ref, int):
                            page_num = page_ref
                    except Exception:
                        pass
                    
                    # 调整页码
                    if page_num > 0:
                        page_num -= 1
                    
                    # 计算目标页码
                    target_page = page_num + page_offset
                    
                    # 添加书签
                    new_parent = writer.add_outline_item(title, target_page, parent=parent)
                    
                    # 处理子书签
                    if len(item) > 2:
                        for subitem in item[2:]:
                            if isinstance(subitem, (list, tuple)):
                                self._process_outline(subitem, writer, page_offset, new_parent)
            
            # 处理字典类型的大纲项（某些 PDF 格式）
            elif isinstance(item, dict):
                if 'Title' in item and 'Page' in item:
                    title = item['Title']
                    page_ref = item['Page']
                    
                    # 尝试获取页码
                    page_num = 0
                    try:
                        if hasattr(page_ref, 'page_number'):
                            page_num = page_ref.page_number
                        elif isinstance(page_ref, int):
                            page_num = page_ref
                    except Exception:
                        pass
                    
                    # 调整页码
                    if page_num > 0:
                        page_num -= 1
                    
                    # 计算目标页码
                    target_page = page_num + page_offset
                    
                    # 添加书签
                    new_parent = writer.add_outline_item(title, target_page, parent=parent)
                    
                    # 处理子书签
                    if 'Kids' in item:
                        self._process_outline(item['Kids'], writer, page_offset, new_parent)
            
            # 处理对象类型的大纲项
            elif hasattr(item, 'title') and hasattr(item, 'page'):
                title = item.title
                page_ref = item.page
                
                # 尝试获取页码
                page_num = 0
                try:
                    if hasattr(page_ref, 'page_number'):
                        page_num = page_ref.page_number
                except Exception:
                    pass
                
                # 调整页码
                if page_num > 0:
                    page_num -= 1
                
                # 计算目标页码
                target_page = page_num + page_offset
                
                # 添加书签
                new_parent = writer.add_outline_item(title, target_page, parent=parent)
                
                # 处理子书签
                if hasattr(item, 'children'):
                    self._process_outline(item.children, writer, page_offset, new_parent)
        except Exception as e:
            print(f"处理大纲项时出错: {e}")
