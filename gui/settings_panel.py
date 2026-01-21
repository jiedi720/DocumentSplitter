"""
设置面板组件

该组件提供了一个用户界面，允许用户配置文档分割的参数，
包括分割模式（按页数或按字符数）、分割数值和输出路径。
"""
import tkinter as tk
from tkinter import ttk
import re


class SettingsPanel(ttk.LabelFrame):
    """设置面板组件

    该组件继承自ttk.LabelFrame，提供了一个带有标题的框架，
    用于配置文档分割的各种参数，如分割模式、数值和输出路径。
    """

    def __init__(self, parent, **kwargs):
        """初始化设置面板组件

        Args:
            parent: 父级组件
            **kwargs: 传递给父类构造函数的其他参数
        """
        super().__init__(parent, text="分割设置", **kwargs)

        # 分割模式变量 (pages/chars)
        self.mode_var = tk.StringVar(value="chars")

        # 分割值变量
        self.value_var = tk.StringVar(value="1000")

        # 输出路径变量
        self.output_path_var = tk.StringVar()

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件

        该方法创建分割模式选择、分割值输入和输出路径选择等界面组件，
        并将它们添加到面板中。
        """
        # 分割模式选择区域
        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill=tk.X, padx=10, pady=5)

        # 模式标签
        ttk.Label(mode_frame, text="分割模式:").pack(side=tk.LEFT)

        # 按字数分割单选按钮
        chars_radio = ttk.Radiobutton(
            mode_frame,
            text="按字数分割",
            variable=self.mode_var,  # 绑定到模式变量
            value="chars"  # 选择此选项时变量的值
        )
        chars_radio.pack(side=tk.LEFT, padx=(10, 0))

        # 按页数分割单选按钮 (仅对PDF有效)
        pages_radio = ttk.Radiobutton(
            mode_frame,
            text="按页数分割",
            variable=self.mode_var,  # 绑定到模式变量
            value="pages"  # 选择此选项时变量的值
        )
        pages_radio.pack(side=tk.LEFT, padx=(10, 0))

        # 分割值输入区域
        value_frame = ttk.Frame(self)
        value_frame.pack(fill=tk.X, padx=10, pady=5)

        # 数值标签
        ttk.Label(value_frame, text="分割数值:").pack(side=tk.LEFT)

        # 数值输入框
        self.value_entry = ttk.Entry(value_frame, textvariable=self.value_var, width=20)
        self.value_entry.pack(side=tk.LEFT, padx=(10, 0))

        # 绑定焦点离开事件，用于验证输入
        self.value_entry.bind('<FocusOut>', self.validate_input)

        # 输出路径选择区域
        output_frame = ttk.Frame(self)
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        # 输出路径标签
        ttk.Label(output_frame, text="输出路径:").pack(side=tk.LEFT)

        # 输出路径输入框
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        self.output_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # 浏览输出路径按钮
        self.output_button = ttk.Button(
            output_frame,
            text="浏览",
            command=self.browse_output_path  # 点击按钮时调用浏览路径方法
        )
        self.output_button.pack(side=tk.LEFT, padx=(5, 0))

    def validate_input(self, event=None):
        """验证输入是否为正整数

        该方法检查用户在数值输入框中输入的值是否为正整数，
        如果不是，则恢复为默认值。

        Args:
            event: 事件对象（可选）

        Returns:
            bool: 如果输入有效则返回True，否则返回False
        """
        value = self.value_var.get()
        if not self.is_positive_integer(value):
            # 如果输入无效，恢复为默认值
            self.value_var.set("1000")  # 设置默认值
            return False
        return True

    def is_positive_integer(self, value):
        """检查字符串是否为正整数

        该方法尝试将字符串转换为整数，并检查是否为正数。

        Args:
            value (str): 要检查的字符串

        Returns:
            bool: 如果字符串表示正整数则返回True，否则返回False
        """
        try:
            num = int(value)
            return num > 0
        except ValueError:
            return False

    def get_settings(self):
        """获取当前设置

        该方法收集用户在界面中设置的所有参数，
        并将其组织成字典格式返回。

        Returns:
            dict or None: 包含设置参数的字典，如果验证失败则返回None
        """
        # 首先验证输入是否有效
        if not self.validate_input():
            return None

        # 组织设置参数
        settings = {
            'mode': self.mode_var.get(),  # 分割模式
            'value': int(self.value_var.get()),  # 分割数值
            'output_path': self.output_path_var.get()  # 输出路径
        }

        return settings

    def set_default_output_path(self, path):
        """设置默认输出路径

        该方法将指定的路径设置为输出路径的默认值。

        Args:
            path (str): 要设置的默认输出路径
        """
        self.output_path_var.set(path)

    def browse_output_path(self):
        """浏览并选择输出路径

        该方法打开目录选择对话框，让用户选择输出目录，
        然后将选中的路径设置到输出路径变量中。
        """
        from tkinter import filedialog
        # 打开目录选择对话框
        path = filedialog.askdirectory(title='选择输出目录')
        if path:
            # 如果用户选择了路径，则更新变量
            self.output_path_var.set(path)

    def set_mode_state(self, state):
        """设置模式选择的状态 (normal/disabled)

        该方法可以启用或禁用分割模式选择单选按钮，
        通常在不同文件类型时使用不同的可用模式。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
        """
        # 获取第一个子组件（mode_frame）的所有子组件
        for child in self.winfo_children()[0].winfo_children():  # mode_frame的子组件
            if isinstance(child, ttk.Radiobutton):  # 如果是单选按钮
                child.config(state=state)  # 设置状态

    def set_value_state(self, state):
        """设置数值输入框的状态 (normal/disabled)

        该方法可以启用或禁用分割数值输入框。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
        """
        self.value_entry.config(state=state)

    def set_output_controls_state(self, state):
        """设置输出路径控件的状态 (normal/disabled)

        该方法可以同时启用或禁用输出路径输入框和浏览按钮。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
        """
        self.output_entry.config(state=state)
        self.output_button.config(state=state)