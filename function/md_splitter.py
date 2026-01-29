"""
Markdown 分割逻辑

该模块实现了对 Markdown 文件（.md）的各种分割方式，
包括按字符数分割和按行数分割。
"""
import os
from pathlib import Path
from .file_handler import FileHandler



class MdSplitter:
    """Markdown 分割器

    该类提供了对 Markdown 文件（.md）进行分割的功能，
    支持按字符数分割和按行数分割两种方式。
    """

    def __init__(self):
        """初始化 Markdown 分割器

        创建文件处理器实例，用于处理通用文件操作。
        """
        self.file_handler = FileHandler()

    def split_by_chars(self, input_path, chars_per_split, output_dir=None):
        """
        按字符数分割 Markdown 文件

        该方法将 Markdown 文件的内容按照指定的字符数进行分割，
        每个分割后的文件包含指定数量的字符。

        Args:
            input_path (str): 输入 Markdown 文件的完整路径
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

        # 验证文件是否为有效的 Markdown 格式
        if not self.file_handler.get_file_type(input_path) == '.md':
            raise ValueError(f"文件不是有效的 Markdown 格式: {input_path}")

        # 验证字符数分割规则是否有效
        if not self.file_handler.validate_split_rule(chars_per_split, '.md'):
            raise ValueError(f"无效的字符数分割规则: {chars_per_split}")

        # 以UTF-8编码读取 Markdown 文件内容
        with open(input_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

        # 检查是否需要分割：如果总字符数小于等于分割字符数，则复制整个文件
        if len(text_content) <= chars_per_split:
            output_path = self.file_handler.generate_output_filename(
                input_path, 1, '.md'
            )
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
            return [output_path]

        # 按字符数分割文本内容
        text_parts = []  # 存储分割后的文本片段

        # 直接按字符数分割
        for i in range(0, len(text_content), chars_per_split):
            text_parts.append(text_content[i:i + chars_per_split])

        # 将每个文本部分写入新的 Markdown 文件
        output_paths = []  # 存储输出文件路径的列表
        for idx, text_part in enumerate(text_parts, 1):
            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, idx, '.md'
            )

            # 以UTF-8编码将文本内容写入新文件
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_part)

            output_paths.append(output_path)

        return output_paths

    def split_by_lines(self, input_path, lines_per_split, output_dir=None):
        """
        按行数分割 Markdown 文件

        该方法将 Markdown 文件按指定的行数进行分割，
        每个分割后的文件包含指定数量的行。

        Args:
            input_path (str): 输入 Markdown 文件的完整路径
            lines_per_split (int): 每个分割文件应包含的行数
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

        # 验证文件是否为有效的 Markdown 格式
        if not self.file_handler.get_file_type(input_path) == '.md':
            raise ValueError(f"文件不是有效的 Markdown 格式: {input_path}")

        # 验证行数分割规则是否有效
        if not self.file_handler.validate_split_rule(lines_per_split, '.md'):
            raise ValueError(f"无效的行数分割规则: {lines_per_split}")

        # 以UTF-8编码读取 Markdown 文件的所有行
        with open(input_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 检查是否需要分割：如果总行数小于等于分割行数，则复制整个文件
        if len(lines) <= lines_per_split:
            output_path = self.file_handler.generate_output_filename(
                input_path, 1, '.md'
            )
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            return [output_path]

        # 按行数分割文本内容
        output_paths = []  # 存储输出文件路径的列表
        part_num = 1       # 分割部分的编号
        current_line = 0   # 当前处理到的行索引

        while current_line < len(lines):
            # 计算理论上的结束行索引
            target_end_line = min(current_line + lines_per_split, len(lines))
            end_line = target_end_line

            # 生成输出文件名
            output_path = self.file_handler.generate_output_filename(
                input_path, part_num, '.md'
            )

            # 将指定范围的行写入新文件
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(lines[current_line:end_line])

            output_paths.append(output_path)
            part_num += 1
            current_line = end_line

        return output_paths

    def split_by_equal_parts(self, input_path, parts_count, output_dir=None):
        """
        均分 Markdown 文件

        该方法将 Markdown 文件平均分割为指定的份数。

        Args:
            input_path (str): 输入 Markdown 文件的完整路径
            parts_count (int): 要分割的份数
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

        # 验证文件是否为有效的 Markdown 格式
        if not self.file_handler.get_file_type(input_path) == '.md':
            raise ValueError(f"文件不是有效的 Markdown 格式: {input_path}")

        # 验证分割份数是否有效
        if parts_count <= 0:
            raise ValueError("分割份数必须大于 0")

        # 以UTF-8编码读取 Markdown 文件内容
        with open(input_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

        # 计算每份的字符数
        total_chars = len(text_content)
        if parts_count >= total_chars:
            # 如果份数大于等于总字符数，每个文件至少一个字符
            chars_per_part = 1
        else:
            # 计算每份的字符数，向上取整
            chars_per_part = (total_chars + parts_count - 1) // parts_count

        # 调用 split_by_chars 方法进行分割
        return self.split_by_chars(input_path, chars_per_part, output_dir)

    def merge_mds(self, input_files, output_path=None):
        """
        合并多个 Markdown 文件

        该方法将多个 Markdown 文件合并为一个单一的 Markdown 文件。

        Args:
            input_files (list): 要合并的 Markdown 文件路径列表
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

        # 验证所有输入文件是否为 Markdown 格式
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"输入文件不存在: {file_path}")
            if not self.file_handler.get_file_type(file_path) == '.md':
                raise ValueError(f"文件不是有效的 Markdown 格式: {file_path}")

        # 如果未指定输出路径，则自动生成
        if output_path is None:
            output_path = self.file_handler.generate_merge_output_filename(input_files)

        # 合并所有 Markdown 文件
        merged_content = []
        for file_path in input_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content:
                    merged_content.append(content)

        # 将合并后的内容写入输出文件
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write('\n\n---\n\n'.join(merged_content))  # 在文件之间添加分隔线

        return output_path