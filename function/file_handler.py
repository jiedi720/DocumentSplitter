"""
通用文件处理逻辑

该模块提供了文档分割工具中通用的文件处理功能，
包括文件类型识别、分割规则验证、输出文件名生成等。
"""
import os
from pathlib import Path


class FileHandler:
    """文件处理器，用于识别文件类型和验证分割规则"""

    # 支持的文件格式列表
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.md']

    def __init__(self):
        """初始化文件处理器"""
        pass

    @staticmethod
    def get_file_type(file_path):
        """
        获取文件类型

        该方法通过检查文件扩展名来确定文件类型，
        并验证该类型是否在支持的格式列表中。

        Args:
            file_path (str): 文件路径

        Returns:
            str: 文件扩展名（小写），如 '.pdf', '.docx', '.txt'；
                 如果文件类型不受支持则返回 None
        """
        # 获取文件扩展名并转换为小写
        ext = Path(file_path).suffix.lower()
        # 检查扩展名是否在支持的格式列表中
        return ext if ext in FileHandler.SUPPORTED_FORMATS else None

    @staticmethod
    def validate_split_rule(value, file_type):
        """
        验证分割规则是否合法

        该方法检查给定的分割值是否符合特定文件类型的规则要求。

        Args:
            value (int): 分割值（页数或字符数）
            file_type (str): 文件类型

        Returns:
            bool: 如果分割规则合法则返回 True，否则返回 False
        """
        # 检查值是否为正整数
        if not isinstance(value, int) or value <= 0:
            return False

        # 根据不同文件类型验证最小分割单位
        if file_type in ['.pdf']:
            # PDF 文件的最小分割单位是1页
            return value >= 1
        elif file_type in ['.docx', '.txt', '.md']:
            # 文本文件的最小分割单位是1个字符
            return value >= 1

        return False

    @staticmethod
    def generate_output_filename(original_path, part_number, extension=None):
        """
        生成输出文件名

        该方法根据原始文件路径和部分编号生成新的输出文件名，
        格式为：原文件名_part{序号}.{扩展名}

        Args:
            original_path (str): 原始文件路径
            part_number (int): 部分编号（从1开始）
            extension (str, optional): 输出文件扩展名，默认使用原始文件扩展名

        Returns:
            str: 输出文件的完整路径
        """
        # 将原始路径转换为 Path 对象以便处理
        path_obj = Path(original_path)

        # 如果未指定扩展名，则使用原始文件的扩展名
        if extension is None:
            extension = path_obj.suffix
        else:
            # 确保扩展名以点开头
            if not extension.startswith('.'):
                extension = '.' + extension

        # 生成新文件名：原文件名_part{序号}.扩展名
        new_name = f"{path_obj.stem}_part{part_number}{extension}"
        # 返回完整的输出路径
        return str(path_obj.parent / new_name)

    @staticmethod
    def get_file_size_mb(file_path):
        """
        获取文件大小（MB）

        该方法计算并返回指定文件的大小，单位为兆字节（MB）。

        Args:
            file_path (str): 文件路径

        Returns:
            float: 文件大小（MB），保留两位小数
        """
        # 获取文件大小（字节）
        size_bytes = os.path.getsize(file_path)
        # 转换为 MB 并保留两位小数
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)