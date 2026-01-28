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

        # 使用 PdfMerger 自动处理书签合并
        merger = PyPDF2.PdfMerger()

        # 合并所有 PDF 文件
        for i, file_path in enumerate(input_files):
            print(f"DEBUG: 正在处理第 {i+1} 个文件: {file_path}")
            try:
                # import_outline=True 是关键，它会自动保留并调整原有的书签页码
                merger.append(file_path, import_outline=True)
                print(f"DEBUG: 成功添加文件: {file_path}")
            except Exception as e:
                print(f"DEBUG: 添加文件时出错: {file_path}")
                print(f"DEBUG: 错误详情: {str(e)}")
                raise

        # 将内容写入输出文件
        print(f"DEBUG: 所有文件添加完成，准备写入输出文件: {output_path}")
        try:
            with open(output_path, 'wb') as fileobj:
                merger.write(fileobj)
            print(f"DEBUG: 成功写入输出文件")
        except Exception as e:
            print(f"DEBUG: 写入文件时出错")
            print(f"DEBUG: 错误详情: {str(e)}")
            raise
        
        # 关闭合并器，释放资源
        merger.close()
        print(f"DEBUG: 合并完成，输出文件: {output_path}")

        return output_path


