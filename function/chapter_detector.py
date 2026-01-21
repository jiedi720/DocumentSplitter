"""
章节识别模块

该模块提供了识别文档中章节标题的功能，支持多种常见的章节标记格式。
"""
import re


class ChapterDetector:
    """章节识别器

    该类用于识别文档中的章节标题，支持多种常见的章节标记格式，
    包括中文和英文的章节编号格式。
    """

    def __init__(self):
        """初始化章节识别器

        定义各种章节标题的正则表达式模式。
        """
        # 中文章节标题模式（如：第一章、第1章、一、1.、1.1 等）
        self.cn_chapter_patterns = [
            # 第X章/第X节（X为中文数字或阿拉伯数字）
            r'^第[一二三四五六七八九十百千0-9]+[章节篇]',
            # 中文数字序号（一、二、三...）
            r'^[一二三四五六七八九十百千]+[、\.]',
            # 阿拉伯数字序号（1.、2.、3. ...）
            r'^\d+\.',
            # 多级序号（1.1、1.1.1、2.3.4 等）
            r'^\d+\.\d+(\.\d+)*\.?',
        ]

        # 英文章节标题模式（如：Chapter 1、Section 1.1、1. Introduction 等）
        self.en_chapter_patterns = [
            # Chapter X / Section X
            r'^(Chapter|Section|Part)\s+\d+',
            # 阿拉伯数字序号（1.、2.、3. ...）
            r'^\d+\.',
            # 多级序号（1.1、1.1.1、2.3.4 等）
            r'^\d+\.\d+(\.\d+)*\.?',
        ]

    def is_chapter_title(self, text, language='cn'):
        """
        判断文本是否为章节标题

        该方法检查文本是否符合章节标题的格式。

        Args:
            text (str): 要检查的文本
            language (str): 语言类型，'cn' 表示中文，'en' 表示英文

        Returns:
            bool: 如果文本是章节标题则返回 True，否则返回 False
        """
        if not text or not text.strip():
            return False

        text = text.strip()

        # 根据语言类型选择匹配模式
        patterns = self.cn_chapter_patterns if language == 'cn' else self.en_chapter_patterns

        # 检查是否匹配任一模式
        for pattern in patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        return False

    def find_chapter_positions(self, text, language='cn'):
        """
        在文本中查找所有章节标题的位置

        该方法扫描文本，返回所有章节标题的位置信息。

        Args:
            text (str): 要扫描的文本
            language (str): 语言类型，'cn' 表示中文，'en' 表示英文

        Returns:
            list: 章节位置列表，每个元素是一个字典，包含 'position'（字符位置）和 'title'（标题文本）
        """
        chapters = []
        lines = text.split('\n')

        current_pos = 0
        for line in lines:
            line = line.strip()
            if self.is_chapter_title(line, language):
                chapters.append({
                    'position': current_pos,
                    'title': line
                })
            current_pos += len(line) + 1  # +1 是换行符

        return chapters

    def find_page_chapter_positions(self, pages):
        """
        在 PDF 页面中查找章节标题的位置

        该方法扫描 PDF 页面的文本内容，返回所有章节标题所在的页码。

        Args:
            pages (list): PDF 页面对象列表

        Returns:
            list: 章节页码列表，每个元素是一个字典，包含 'page_num'（页码）和 'title'（标题文本）
        """
        chapters = []

        for page_num, page in enumerate(pages):
            try:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if self.is_chapter_title(line, 'cn') or self.is_chapter_title(line, 'en'):
                            chapters.append({
                                'page_num': page_num,
                                'title': line
                            })
                            break  # 每页只记录第一个章节标题
            except Exception:
                continue

        return chapters

    def find_paragraph_chapter_positions(self, paragraphs):
        """
        在 Word 段落中查找章节标题的位置

        该方法扫描 Word 文档的段落，返回所有章节标题所在的段落索引。

        Args:
            paragraphs (list): Word 段落对象列表

        Returns:
            list: 章节段落索引列表，每个元素是一个字典，包含 'para_index'（段落索引）和 'title'（标题文本）
        """
        chapters = []

        for para_index, paragraph in enumerate(paragraphs):
            text = paragraph.text.strip()
            if text and (self.is_chapter_title(text, 'cn') or self.is_chapter_title(text, 'en')):
                chapters.append({
                    'para_index': para_index,
                    'title': text
                })

        return chapters

    def find_line_chapter_positions(self, lines):
        """
        在文本行中查找章节标题的位置

        该方法扫描文本文件的行，返回所有章节标题所在的行索引。

        Args:
            lines (list): 文本行列表

        Returns:
            list: 章节行索引列表，每个元素是一个字典，包含 'line_index'（行索引）和 'title'（标题文本）
        """
        chapters = []

        for line_index, line in enumerate(lines):
            text = line.strip()
            if text and (self.is_chapter_title(text, 'cn') or self.is_chapter_title(text, 'en')):
                chapters.append({
                    'line_index': line_index,
                    'title': text
                })

        return chapters

    def get_chapter_breaks(self, text, language='cn'):
        """
        获取文本中所有章节的分割点

        该方法返回所有章节标题的位置，用于在分割文档时避免在章节中间分割。

        Args:
            text (str): 要分析的文本
            language (str): 语言类型，'cn' 表示中文，'en' 表示英文

        Returns:
            list: 章节分割点位置列表（字符位置）
        """
        chapters = self.find_chapter_positions(text, language)
        return [chapter['position'] for chapter in chapters]

    def adjust_split_point(self, target_position, text, language='cn', max_adjustment=1000):
        """
        调整分割点以避免在章节中间分割

        该方法在目标分割点附近查找最近的章节标题位置，
        并返回更合适的分割点，确保不会在章节中间分割。

        Args:
            target_position (int): 目标分割位置
            text (str): 完整文本
            language (str): 语言类型，'cn' 表示中文，'en' 表示英文
            max_adjustment (int): 最大调整距离（字符数）

        Returns:
            int: 调整后的分割位置
        """
        # 获取所有章节分割点
        chapter_breaks = self.get_chapter_breaks(text, language)

        if not chapter_breaks:
            return target_position

        # 查找目标位置附近的章节分割点
        # 优先查找最近的章节标题（向前或向后）
        best_position = target_position
        min_distance = float('inf')

        for chapter_pos in chapter_breaks:
            # 只考虑在目标位置附近的章节标题
            distance = abs(chapter_pos - target_position)
            if distance <= max_adjustment and distance < min_distance:
                min_distance = distance
                # 如果章节标题在目标位置之前，则在章节标题处分割
                # 如果章节标题在目标位置之后，则在章节标题之前分割
                if chapter_pos <= target_position:
                    best_position = chapter_pos
                else:
                    # 章节标题在目标位置之后，尝试在章节标题之前分割
                    # 查找前一个换行符
                    newline_pos = text.rfind('\n', 0, chapter_pos)
                    if newline_pos != -1 and newline_pos >= target_position - max_adjustment:
                        best_position = newline_pos
                    else:
                        best_position = chapter_pos

        return best_position
