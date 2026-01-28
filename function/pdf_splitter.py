"""
PDF 分割逻辑

该模块实现了对 PDF 文件的各种分割方式，
包括按页数分割和按字符数分割。
"""
import os
import PyPDF2
from pathlib import Path
from .file_handler import FileHandler
from .chapter_detector import ChapterDetector


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
        self.chapter_detector = ChapterDetector()

    def split_by_pages(self, input_path, pages_per_split, output_dir=None, preserve_chapter=False, split_mode='fixed'):
        """
        按页数分割 PDF 文件

        该方法将输入的 PDF 文件按照指定的页数进行分割，
        每个分割后的文件包含指定数量的页面。

        Args:
            input_path (str): 输入 PDF 文件的完整路径
            pages_per_split (int): 每个分割文件应包含的页数，或要分割的份数（当 split_mode='equal' 时）
            output_dir (str, optional): 输出目录路径，默认为输入文件所在目录
            preserve_chapter (bool, optional): 是否保留章节完整性，默认为 False
            split_mode (str, optional): 分割模式，'fixed' 表示固定每页数量，'equal' 表示平均分割为指定份数，默认为 'fixed'

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

        # 读取 PDF 文件并获取总页数
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            # 计算实际的每页数量
            if split_mode == 'equal':
                # 均分模式：计算每页数量
                if pages_per_split <= 0:
                    raise ValueError("分割份数必须大于 0")
                if pages_per_split >= total_pages:
                    # 如果份数大于等于总页数，每个文件一页
                    pages_per_split = 1
                else:
                    # 计算每页数量，向上取整
                    pages_per_split = (total_pages + pages_per_split - 1) // pages_per_split
            else:
                # 固定模式：验证页数分割规则是否有效
                if not self.file_handler.validate_split_rule(pages_per_split, '.pdf'):
                    raise ValueError(f"无效的页数分割规则: {pages_per_split}")

            # 特殊情况：如果每份的页数大于等于总页数，则只生成一份文件
            if pages_per_split >= total_pages:
                output_path = self.file_handler.generate_output_filename(
                    input_path, 1, '.pdf'
                )
                self._write_pdf(reader, 0, total_pages, output_path)
                return [output_path]

        # 如果需要保留章节完整性，先查找所有章节位置
        chapter_pages = []
        if preserve_chapter:
            chapter_pages = self.chapter_detector.find_page_chapter_positions(reader.pages)
            chapter_page_nums = [ch['page_num'] for ch in chapter_pages]

        # 开始按指定页数分割 PDF
        output_paths = []  # 存储输出文件路径的列表
        part_num = 1       # 分割部分的编号
        current_page = 0   # 当前处理到的页码

        while current_page < total_pages:
            # 计算理论上的结束页码
            target_end_page = min(current_page + pages_per_split, total_pages)

            # 如果需要保留章节完整性，调整结束页码
            if preserve_chapter and chapter_page_nums:
                # 查找目标结束页码之后的第一个章节页
                next_chapter_page = None
                for chapter_page in chapter_page_nums:
                    if chapter_page > current_page and chapter_page < target_end_page:
                        next_chapter_page = chapter_page
                        break

                # 如果在目标范围内找到了章节页，则在章节页处分割
                if next_chapter_page is not None:
                    end_page = next_chapter_page
                else:
                    # 没有找到章节页，使用原始的结束页码
                    end_page = target_end_page
            else:
                end_page = target_end_page

            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, part_num, '.pdf'
            )

            # 读取原文件并写入当前分割部分
            with open(input_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                self._write_pdf(reader, current_page, end_page, output_path)

            # 将输出路径添加到结果列表
            output_paths.append(output_path)
            part_num += 1
            current_page = end_page

        return output_paths

    def split_by_equal_parts(self, input_path, parts_count, output_dir=None, preserve_chapter=False):
        """
        均分 PDF 文件

        该方法将输入的 PDF 文件平均分割为指定的份数。

        Args:
            input_path (str): 输入 PDF 文件的完整路径
            parts_count (int): 要分割的份数
            output_dir (str, optional): 输出目录路径，默认为输入文件所在目录
            preserve_chapter (bool, optional): 是否保留章节完整性，默认为 False

        Returns:
            list: 包含所有成功分割的文件路径的列表

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出
            ValueError: 当文件格式不正确或分割规则无效时抛出
        """
        return self.split_by_pages(input_path, parts_count, output_dir, preserve_chapter, split_mode='equal')

    def split_by_chars(self, input_path, chars_per_split, output_dir=None, preserve_chapter=False):
        """
        按字符数分割 PDF 文件

        该方法先提取 PDF 文件的文本内容以确定分割点，
        然后按照计算出的页面范围分割原始 PDF 文件，
        保留原始 PDF 的格式和内容。

        Args:
            input_path (str): 输入 PDF 文件的完整路径
            chars_per_split (int): 每个分割文件应包含的字符数
            output_dir (str, optional): 输出目录路径，默认为输入文件所在目录
            preserve_chapter (bool, optional): 是否保留章节完整性，默认为 False

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

        # 打开 PDF 文件
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            # 提取每页的文本内容和字符数
            page_texts = []  # 存储每页的文本内容
            page_char_counts = []  # 存储每页的字符数
            cumulative_chars = []  # 存储累积字符数

            current_total = 0
            for page in reader.pages:
                text = page.extract_text() or ""
                page_texts.append(text)
                char_count = len(text)
                page_char_counts.append(char_count)
                current_total += char_count
                cumulative_chars.append(current_total)

            # 计算分割点（页面范围）
            split_ranges = []  # 存储分割的页面范围 (start_page, end_page)
            current_char = 0
            start_page = 0

            while current_char < cumulative_chars[-1]:
                target_char = current_char + chars_per_split

                # 查找目标字符数所在的页面
                end_page = total_pages
                for i, char_sum in enumerate(cumulative_chars):
                    if char_sum >= target_char:
                        end_page = i + 1  # 因为页面是从0开始计数的
                        break

                # 如果需要保留章节完整性，调整分割点
                if preserve_chapter and start_page < end_page - 1:
                    # 这里可以添加章节完整性检查逻辑
                    pass

                # 添加分割范围
                split_ranges.append((start_page, end_page))

                # 更新当前字符位置和起始页面
                if end_page < total_pages:
                    current_char = cumulative_chars[end_page - 1]
                else:
                    current_char = cumulative_chars[-1]
                start_page = end_page

        # 执行分割
        output_paths = []  # 存储输出文件路径的列表

        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            for idx, (start_page, end_page) in enumerate(split_ranges, 1):
                # 生成输出文件名
                output_path = self.file_handler.generate_output_filename(
                    input_path, idx, '.pdf'
                )

                # 写入指定页面范围到新文件
                self._write_pdf(reader, start_page, end_page, output_path)
                output_paths.append(output_path)

        return output_paths

    def _write_pdf(self, reader, start_page, end_page, output_path):
        """
        将 PDF 的指定页面范围写入新文件

        这是一个内部辅助方法，用于将 PDF 文档的特定页面范围
        复制到新的 PDF 文件中，并保留相应的书签。

        Args:
            reader (PyPDF2.PdfReader): 已打开的 PDF 读取器对象
            start_page (int): 起始页码（从0开始计数）
            end_page (int): 结束页码（不包括此页）
            output_path (str): 输出文件的完整路径
        """
        # 创建 PDF 写入器对象
        writer = PyPDF2.PdfWriter()

        # 页面映射：原始页码 -> 新页码
        page_map = {}
        new_page_num = 0

        # 将指定范围内的页面添加到写入器
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
            page_map[page_num] = new_page_num
            new_page_num += 1

        # 复制书签（如果有）
        self._copy_bookmarks(reader, writer, page_map, start_page, end_page)

        # 将内容写入输出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

    def _copy_bookmarks(self, reader, writer, page_map, start_page, end_page):
        """
        复制 PDF 书签

        这是一个内部辅助方法，用于将 PDF 文档的书签复制到新文件中，
        并调整页码以匹配新文件中的页面位置。

        Args:
            reader (PyPDF2.PdfReader): 已打开的 PDF 读取器对象
            writer (PyPDF2.PdfWriter): 已创建的 PDF 写入器对象
            page_map (dict): 原始页码到新页码的映射
            start_page (int): 起始页码（从0开始计数）
            end_page (int): 结束页码（不包括此页）
        """
        try:
            # 检查是否有大纲（书签）
            if hasattr(reader, 'outlines') and reader.outlines:
                # 递归处理书签
                self._process_bookmark_item(reader.outlines, writer, page_map, start_page, end_page)
        except Exception as e:
            # 如果处理书签时出错，忽略错误继续执行
            print(f"处理书签时出错: {e}")

    def _process_bookmark_item(self, bookmark_item, writer, page_map, start_page, end_page, parent=None):
        """
        处理单个书签项

        Args:
            bookmark_item: 书签项
            writer (PyPDF2.PdfWriter): 已创建的 PDF 写入器对象
            page_map (dict): 原始页码到新页码的映射
            start_page (int): 起始页码（从0开始计数）
            end_page (int): 结束页码（不包括此页）
            parent: 父书签（可选）
        """
        # 检查是否是列表（多个书签项）
        if isinstance(bookmark_item, list):
            for item in bookmark_item:
                self._process_bookmark_item(item, writer, page_map, start_page, end_page, parent)
            return

        # 检查是否是元组（单个书签项）
        if isinstance(bookmark_item, tuple):
            # 解包书签项
            title, page_obj, *rest = bookmark_item

            # 获取书签指向的页码
            page_num = -1
            try:
                # 尝试获取页码
                if hasattr(page_obj, 'page_number'):
                    page_num = page_obj.page_number
                else:
                    # 对于 PyPDF2 的大纲项，尝试使用其他方法获取页码
                    # 注意：这里我们假设 page_obj 是一个页码引用
                    # 在 PyPDF2 中，书签通常直接引用页码
                    if isinstance(page_obj, int):
                        page_num = page_obj
                    else:
                        # 尝试获取页码信息
                        try:
                            # 对于某些 PyPDF2 版本，page_obj 可能是一个字典
                            if isinstance(page_obj, dict) and '/Page' in page_obj:
                                # 这里我们无法直接获取页码，所以使用一个默认值
                                # 实际应用中，可能需要更复杂的逻辑来处理这种情况
                                pass
                        except:
                            pass
            except Exception as e:
                print(f"获取书签页码时出错: {e}")
            
            # 对于无法获取页码的情况，我们需要使用其他方法
            # 这里我们遍历所有可能的页码，检查是否在分割范围内
            if page_num == -1:
                # 尝试所有可能的页码
                for num in page_map:
                    if start_page <= num < end_page:
                        try:
                            # 尝试添加书签到这个页码
                            new_page_num = page_map.get(num, None)
                            if new_page_num is not None:
                                new_parent = writer.add_outline_item(
                                    title,
                                    new_page_num,
                                    parent=parent
                                )
                                # 处理子书签
                                if rest and len(rest) > 0 and isinstance(rest[0], (list, tuple)):
                                    self._process_bookmark_item(rest[0], writer, page_map, start_page, end_page, new_parent)
                                break
                        except Exception as e:
                            print(f"添加书签到新文件时出错: {e}")
                return
            
            # 检查页码是否在当前分割范围内
            if start_page <= page_num < end_page:
                # 获取新页码
                new_page_num = page_map.get(page_num, None)
                if new_page_num is not None:
                    # 添加书签到新文件
                    try:
                        new_parent = writer.add_outline_item(
                            title,
                            new_page_num,
                            parent=parent
                        )

                        # 处理子书签
                        if rest and len(rest) > 0 and isinstance(rest[0], (list, tuple)):
                            self._process_bookmark_item(rest[0], writer, page_map, start_page, end_page, new_parent)
                    except Exception as e:
                        print(f"添加书签到新文件时出错: {e}")
        elif hasattr(bookmark_item, 'title') and hasattr(bookmark_item, 'page'):
            # 对于某些 PyPDF2 版本的书签对象
            title = bookmark_item.title
            try:
                page_num = bookmark_item.page.page_number if hasattr(bookmark_item.page, 'page_number') else 0
            except:
                page_num = 0

            # 检查页码是否在当前分割范围内
            if start_page <= page_num < end_page:
                # 获取新页码
                new_page_num = page_map.get(page_num, None)
                if new_page_num is not None:
                    # 添加书签到新文件
                    try:
                        new_parent = writer.add_outline_item(
                            title,
                            new_page_num,
                            parent=parent
                        )

                        # 处理子书签
                        if hasattr(bookmark_item, 'children') and bookmark_item.children:
                            self._process_bookmark_item(bookmark_item.children, writer, page_map, start_page, end_page, new_parent)
                    except Exception as e:
                        print(f"添加书签到新文件时出错: {e}")

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