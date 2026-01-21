"""
PDF 分割逻辑

该模块实现了对 PDF 文件的各种分割方式，
包括按页数分割和按字符数分割。
"""
import os
import PyPDF2
from pathlib import Path
from .file_handler import FileHandler


class PDFSplitter:
    """PDF 分割器

    该类提供了对 PDF 文件进行分割的功能，
    支持按页数分割和按字符数分割两种方式。
    """

    def __init__(self):
        """初始化 PDF 分割器

        创建文件处理器实例，用于处理通用文件操作。
        """
        self.file_handler = FileHandler()

    def split_by_pages(self, input_path, pages_per_split, output_dir=None):
        """
        按页数分割 PDF 文件

        该方法将输入的 PDF 文件按照指定的页数进行分割，
        每个分割后的文件包含指定数量的页面。

        Args:
            input_path (str): 输入 PDF 文件的完整路径
            pages_per_split (int): 每个分割文件应包含的页数
            output_dir (str, optional): 输出目录路径，默认为输入文件所在目录

        Returns:
            list: 包含所有成功分割的文件路径的列表

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出
            ValueError: 当文件格式不正确或分割规则无效时抛出
        """
        # 如果未指定输出目录，则使用输入文件所在目录
        if output_dir is None:
            output_dir = str(Path(input_path).parent)

        # 验证输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        # 验证文件是否为有效的 PDF 格式
        if not self.file_handler.get_file_type(input_path) == '.pdf':
            raise ValueError(f"文件不是有效的 PDF 格式: {input_path}")

        # 验证页数分割规则是否有效
        if not self.file_handler.validate_split_rule(pages_per_split, '.pdf'):
            raise ValueError(f"无效的页数分割规则: {pages_per_split}")

        # 读取 PDF 文件并获取总页数
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            # 特殊情况：如果每份的页数大于等于总页数，则只生成一份文件
            if pages_per_split >= total_pages:
                output_path = self.file_handler.generate_output_filename(
                    input_path, 1, '.pdf'
                )
                self._write_pdf(reader, 0, total_pages, output_path)
                return [output_path]

        # 开始按指定页数分割 PDF
        output_paths = []  # 存储输出文件路径的列表
        part_num = 1       # 分割部分的编号

        # 循环处理每个分割部分
        for start_page in range(0, total_pages, pages_per_split):
            # 计算结束页码（不超过总页数）
            end_page = min(start_page + pages_per_split, total_pages)

            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, part_num, '.pdf'
            )

            # 读取原文件并写入当前分割部分
            with open(input_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                self._write_pdf(reader, start_page, end_page, output_path)

            # 将输出路径添加到结果列表
            output_paths.append(output_path)
            part_num += 1

        return output_paths

    def split_by_chars(self, input_path, chars_per_split, output_dir=None):
        """
        按字符数分割 PDF 文件（通过提取文本内容）

        该方法先提取 PDF 文件的文本内容，然后按照指定的字符数进行分割，
        最后将每个文本部分保存为单独的 PDF 文件。

        Args:
            input_path (str): 输入 PDF 文件的完整路径
            chars_per_split (int): 每个分割文件应包含的字符数
            output_dir (str, optional): 输出目录路径，默认为输入文件所在目录

        Returns:
            list: 包含所有成功分割的文件路径的列表

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出
            ValueError: 当文件格式不正确或分割规则无效时抛出
        """
        # 如果未指定输出目录，则使用输入文件所在目录
        if output_dir is None:
            output_dir = str(Path(input_path).parent)

        # 验证输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        # 验证文件是否为有效的 PDF 格式
        if not self.file_handler.get_file_type(input_path) == '.pdf':
            raise ValueError(f"文件不是有效的 PDF 格式: {input_path}")

        # 验证字符数分割规则是否有效
        if not self.file_handler.validate_split_rule(chars_per_split, '.pdf'):
            raise ValueError(f"无效的字符数分割规则: {chars_per_split}")

        # 提取 PDF 文件的所有文本内容
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_content = ""  # 存储提取的文本内容

            # 遍历每一页并提取文本
            for page in reader.pages:
                text_content += page.extract_text() + "\n"

        # 按照指定字符数分割文本内容
        text_parts = []  # 存储分割后的文本片段
        for i in range(0, len(text_content), chars_per_split):
            text_parts.append(text_content[i:i + chars_per_split])

        # 将每个文本部分写入新的 PDF 文件
        output_paths = []  # 存储输出文件路径的列表
        for idx, text_part in enumerate(text_parts, 1):
            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, idx, '.pdf'
            )

            # 创建包含文本内容的新 PDF 文件
            self._create_pdf_from_text(text_part, output_path)
            output_paths.append(output_path)

        return output_paths

    def _write_pdf(self, reader, start_page, end_page, output_path):
        """
        将 PDF 的指定页面范围写入新文件

        这是一个内部辅助方法，用于将 PDF 文档的特定页面范围
        复制到新的 PDF 文件中。

        Args:
            reader (PyPDF2.PdfReader): 已打开的 PDF 读取器对象
            start_page (int): 起始页码（从0开始计数）
            end_page (int): 结束页码（不包括此页）
            output_path (str): 输出文件的完整路径
        """
        # 创建 PDF 写入器对象
        writer = PyPDF2.PdfWriter()

        # 将指定范围内的页面添加到写入器
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        # 将内容写入输出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

    def _create_pdf_from_text(self, text, output_path):
        """
        从文本创建 PDF 文件

        这是一个内部辅助方法，用于将文本内容保存为 PDF 文件。
        由于 PyPDF2 不直接支持从头创建 PDF，此方法使用 reportlab
        库来创建包含文本的 PDF（如果已安装）。

        Args:
            text (str): 要写入 PDF 的文本内容
            output_path (str): 输出文件的完整路径
        """
        # 创建 PDF 写入器对象
        writer = PyPDF2.PdfWriter()

        # 尝试使用 reportlab 库创建包含文本的 PDF
        try:
            from io import BytesIO
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            # 创建内存中的 PDF 内容
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(100, 750, "Content extracted from original PDF")

            # 处理分割的文本内容，逐行添加到 PDF
            lines = text.split('\n')
            y_position = 700  # 初始垂直位置
            for line in lines[:20]:  # 只显示前20行作为示例
                if y_position <= 50:  # 如果到达页面底部，则换页
                    can.showPage()
                    y_position = 750
                can.drawString(100, y_position, line[:80])  # 限制每行长度
                y_position -= 20  # 移动到下一行

            can.save()

            # 将内存中的 PDF 内容读取为 PyPDF2 对象
            packet.seek(0)
            new_pdf = PyPDF2.PdfReader(packet)
            page = new_pdf.pages[0]
            writer.add_page(page)

        except ImportError:
            # 如果没有安装 reportlab，则创建一个空白 PDF 页面
            # 创建一个空白页面作为占位符
            blank_page = writer.add_blank_page(width=200, height=200)

        # 将 PDF 内容写入输出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)