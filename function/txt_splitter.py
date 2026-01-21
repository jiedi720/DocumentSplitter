"""
TXT 分割逻辑

该模块实现了对纯文本文件（.txt）的各种分割方式，
包括按字符数分割和按行数分割。
"""
import os
from pathlib import Path
from .file_handler import FileHandler


class TxtSplitter:
    """TXT 分割器

    该类提供了对纯文本文件（.txt）进行分割的功能，
    支持按字符数分割和按行数分割两种方式。
    """

    def __init__(self):
        """初始化 TXT 分割器

        创建文件处理器实例，用于处理通用文件操作。
        """
        self.file_handler = FileHandler()

    def split_by_chars(self, input_path, chars_per_split, output_dir=None):
        """
        按字符数分割 TXT 文件

        该方法将文本文件的内容按照指定的字符数进行分割，
        每个分割后的文件包含指定数量的字符。

        Args:
            input_path (str): 输入 TXT 文件的完整路径
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

        # 验证文件是否为有效的 TXT 格式
        if not self.file_handler.get_file_type(input_path) == '.txt':
            raise ValueError(f"文件不是有效的 TXT 格式: {input_path}")

        # 验证字符数分割规则是否有效
        if not self.file_handler.validate_split_rule(chars_per_split, '.txt'):
            raise ValueError(f"无效的字符数分割规则: {chars_per_split}")

        # 以UTF-8编码读取 TXT 文件内容
        with open(input_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

        # 检查是否需要分割：如果总字符数小于等于分割字符数，则复制整个文件
        if len(text_content) <= chars_per_split:
            output_path = self.file_handler.generate_output_filename(
                input_path, 1, '.txt'
            )
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            return [output_path]

        # 按字符数分割文本内容
        text_parts = []  # 存储分割后的文本片段
        for i in range(0, len(text_content), chars_per_split):
            text_parts.append(text_content[i:i + chars_per_split])

        # 将每个文本部分写入新的 TXT 文件
        output_paths = []  # 存储输出文件路径的列表
        for idx, text_part in enumerate(text_parts, 1):
            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, idx, '.txt'
            )

            # 以UTF-8编码将文本内容写入新文件
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_part)

            output_paths.append(output_path)

        return output_paths

    def split_by_lines(self, input_path, lines_per_split, output_dir=None):
        """
        按行数分割 TXT 文件

        该方法将文本文件按指定的行数进行分割，
        每个分割后的文件包含指定数量的行。

        Args:
            input_path (str): 输入 TXT 文件的完整路径
            lines_per_split (int): 每个分割文件应包含的行数
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

        # 验证文件是否为有效的 TXT 格式
        if not self.file_handler.get_file_type(input_path) == '.txt':
            raise ValueError(f"文件不是有效的 TXT 格式: {input_path}")

        # 验证行数分割规则是否有效
        if not self.file_handler.validate_split_rule(lines_per_split, '.txt'):
            raise ValueError(f"无效的行数分割规则: {lines_per_split}")

        # 以UTF-8编码读取 TXT 文件的所有行
        with open(input_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 检查是否需要分割：如果总行数小于等于分割行数，则复制整个文件
        if len(lines) <= lines_per_split:
            output_path = self.file_handler.generate_output_filename(
                input_path, 1, '.txt'
            )
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            return [output_path]

        # 按行数分割文本内容
        output_paths = []  # 存储输出文件路径的列表
        part_num = 1       # 分割部分的编号

        # 循环处理每个分割部分
        for start_line in range(0, len(lines), lines_per_split):
            # 计算结束行索引（不超过总行数）
            end_line = min(start_line + lines_per_split, len(lines))

            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, part_num, '.txt'
            )

            # 将指定范围的行写入新文件
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[start_line:end_line])

            output_paths.append(output_path)
            part_num += 1

        return output_paths