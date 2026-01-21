"""
配置管理模块

该模块负责处理应用程序的配置保存和读取功能，
包括分割参数、输入输出目录等设置的持久化存储。
"""
import configparser
import os
from pathlib import Path


class ConfigManager:
    """配置管理器类

    该类负责管理应用程序的配置文件，提供配置的读取和保存功能。
    """

    def __init__(self):
        """初始化配置管理器

        该方法初始化配置管理器，设置配置文件路径并确保目录存在。
        """
        # 配置文件路径 - 优先使用可执行文件所在目录
        import sys
        if hasattr(sys, '_MEIPASS'):
            # 打包后环境：使用可执行文件所在目录
            exe_dir = Path(sys.executable).parent
            self.config_path = exe_dir / "DocumentSplitter.ini"
        else:
            # 开发环境：使用项目根目录
            self.config_path = Path(__file__).resolve().parents[1] / "DocumentSplitter.ini"

        # 初始化配置解析器
        self.config = configparser.ConfigParser()

        # 确保配置文件存在
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """确保配置文件存在

        该方法检查配置文件是否存在，如果不存在则创建默认配置。
        """
        if not self.config_path.exists():
            # 创建默认配置
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置

        该方法创建默认的配置文件，包含所有必要的设置项。
        """
        # 添加默认配置 - 按照指定顺序
        self.config["SplitSettings"] = {
            "mode": "chars",
            "preserve_chapter": "False",
            "chars_value": "1000",
            "pages_value": "10",
            "equal_value": "5"
        }

        self.config["Paths"] = {
            "input_dir": "",
            "output_dir": ""
        }

        # 写入配置文件
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

    def read_config(self):
        """读取配置

        该方法从配置文件中读取所有配置项，并返回一个包含所有配置的字典。

        Returns:
            dict: 包含所有配置项的字典
        """
        # 读取配置文件
        self.config.read(self.config_path, encoding="utf-8")

        # 构建配置字典
        config = {
            "SplitSettings": {
                "chars_value": self.config.get("SplitSettings", "chars_value", fallback="1000"),
                "pages_value": self.config.get("SplitSettings", "pages_value", fallback="10"),
                "equal_value": self.config.get("SplitSettings", "equal_value", fallback="5"),
                "mode": self.config.get("SplitSettings", "mode", fallback="chars"),
                "preserve_chapter": self.config.getboolean("SplitSettings", "preserve_chapter", fallback=False)
            },
            "Paths": {
                "input_dir": self.config.get("Paths", "input_dir", fallback=""),
                "output_dir": self.config.get("Paths", "output_dir", fallback="")
            }
        }

        return config

    def save_config(self, config):
        """保存配置

        该方法将配置字典保存到配置文件中。

        Args:
            config (dict): 包含所有配置项的字典
        """
        # 更新配置 - 按照指定顺序
        if "SplitSettings" in config:
            # 按照指定顺序更新配置
            split_settings = config["SplitSettings"]
            # 确保按照指定顺序更新
            ordered_keys = ["mode", "preserve_chapter", "chars_value", "pages_value", "equal_value"]
            for key in ordered_keys:
                if key in split_settings:
                    self.config["SplitSettings"][key] = str(split_settings[key])

        if "Paths" in config:
            for key, value in config["Paths"].items():
                if key not in self.config["Paths"]:
                    self.config["Paths"][key] = value
                else:
                    self.config["Paths"][key] = str(value)

        # 写入配置文件
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)