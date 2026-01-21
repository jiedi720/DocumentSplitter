"""
设置面板组件

该组件提供了一个用户界面，允许用户配置文档分割的参数，
包括分割模式（按页数、按字符数、均分）、分割数值和输出路径。
采用卡片式布局，功能分组清晰，视觉层级分明。
"""
import tkinter as tk
from tkinter import ttk


class SettingsPanel(ttk.LabelFrame):
    """设置面板组件

    该组件继承自ttk.LabelFrame，提供了一个带有标题的框架，
    用于配置文档分割的各种参数，如分割模式、数值和输出路径。
    采用工程风格设计，布局清晰，功能分组明确。
    """

    def __init__(self, parent, **kwargs):
        """初始化设置面板组件

        Args:
            parent: 父级组件
            **kwargs: 传递给父类构造函数的其他参数
        """
        super().__init__(parent, text="分割设置", **kwargs)

        # 分割模式变量 (pages/chars/equal)
        self.mode_var = tk.StringVar(value="chars")

        # 分割值变量 - 按字数
        self.chars_var = tk.StringVar(value="1000")

        # 分割值变量 - 按页数
        self.pages_var = tk.StringVar(value="10")

        # 分割值变量 - 均分份数
        self.equal_var = tk.StringVar(value="5")

        # 输出路径变量
        self.output_path_var = tk.StringVar()

        # 保留章节完整性变量
        self.preserve_chapter_var = tk.BooleanVar(value=False)

        # 高级选项展开状态
        self.advanced_expanded = tk.BooleanVar(value=False)

        # 创建界面组件
        self.create_widgets()

        # 绑定模式变化事件
        self.mode_var.trace_add('write', self.on_mode_changed)

        # 初始化显示状态
        self.update_input_visibility()

    def create_widgets(self):
        """创建界面组件

        该方法创建分割模式选择、分割值输入和输出路径选择等界面组件，
        采用卡片式布局，功能分组清晰。
        """
        # 设置统一的内边距
        self.grid_columnconfigure(1, weight=1)

        # ========== 核心设置区域 ==========
        row = 0

        # 分割模式选择
        ttk.Label(self, text="分割模式", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=10, pady=(12, 8)
        )

        # 模式单选按钮容器
        mode_frame = ttk.Frame(self)
        mode_frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=(12, 8))

        # 按字数分割单选按钮
        self.chars_radio = ttk.Radiobutton(
            mode_frame,
            text="按字数",
            variable=self.mode_var,
            value="chars"
        )
        self.chars_radio.pack(side=tk.LEFT, padx=(0, 20))

        # 按页数分割单选按钮
        self.pages_radio = ttk.Radiobutton(
            mode_frame,
            text="按页数",
            variable=self.mode_var,
            value="pages"
        )
        self.pages_radio.pack(side=tk.LEFT, padx=(0, 20))

        # 均分单选按钮
        self.equal_radio = ttk.Radiobutton(
            mode_frame,
            text="均分",
            variable=self.mode_var,
            value="equal"
        )
        self.equal_radio.pack(side=tk.LEFT)
        row += 1

        # ========== 分割参数区域（与模式同行）==========
        ttk.Label(self, text="分割参数", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, padx=10, pady=(0, 8)
        )

        # 参数容器
        params_frame = ttk.Frame(self)
        params_frame.grid(row=row, column=1, columnspan=3, sticky=tk.W, padx=10, pady=(0, 8))

        # 按字数分割输入容器
        self.chars_frame = ttk.Frame(params_frame)

        ttk.Label(self.chars_frame, text="每份字数:").pack(side=tk.LEFT)
        self.chars_entry = ttk.Entry(self.chars_frame, textvariable=self.chars_var, width=15)
        self.chars_entry.pack(side=tk.LEFT, padx=(10, 5))
        self.chars_entry.bind('<FocusOut>', self.validate_chars_input)

        ttk.Label(self.chars_frame, text="字符", foreground='#888888').pack(side=tk.LEFT)

        # 按页数分割输入容器
        self.pages_frame = ttk.Frame(params_frame)

        ttk.Label(self.pages_frame, text="每份页数:").pack(side=tk.LEFT)
        self.pages_entry = ttk.Entry(self.pages_frame, textvariable=self.pages_var, width=15)
        self.pages_entry.pack(side=tk.LEFT, padx=(10, 5))
        self.pages_entry.bind('<FocusOut>', self.validate_pages_input)

        ttk.Label(self.pages_frame, text="页", foreground='#888888').pack(side=tk.LEFT)

        # 均分份数输入容器
        self.equal_frame = ttk.Frame(params_frame)

        ttk.Label(self.equal_frame, text="均分份数:").pack(side=tk.LEFT)
        self.equal_entry = ttk.Entry(self.equal_frame, textvariable=self.equal_var, width=15)
        self.equal_entry.pack(side=tk.LEFT, padx=(10, 5))
        self.equal_entry.bind('<FocusOut>', self.validate_equal_input)

        ttk.Label(self.equal_frame, text="份", foreground='#888888').pack(side=tk.LEFT)
        row += 1

        # ========== 高级选项区域（可折叠）==========
        # 高级选项标题栏
        advanced_header = ttk.Frame(self)
        advanced_header.grid(row=row, column=0, columnspan=4, sticky=tk.W, padx=10, pady=(8, 0))

        ttk.Label(advanced_header, text="高级选项", font=('TkDefaultFont', 9, 'bold')).pack(side=tk.LEFT)

        # 展开/折叠按钮
        self.advanced_button = ttk.Button(
            advanced_header,
            text="▼",
            width=3,
            command=self.toggle_advanced,
            style='Toolbutton'
        )
        self.advanced_button.pack(side=tk.LEFT, padx=(10, 0))
        row += 1

        # 高级选项内容容器
        self.advanced_frame = ttk.Frame(self)
        self.advanced_frame.grid(row=row, column=0, columnspan=4, sticky=tk.W, padx=10, pady=(0, 8))

        # 保留章节完整性选项
        self.preserve_chapter_check = ttk.Checkbutton(
            self.advanced_frame,
            text="保留章节完整性（尽量不在章节中间分割）",
            variable=self.preserve_chapter_var
        )
        self.preserve_chapter_check.pack(anchor=tk.W)
        row += 1

        # ========== 输出路径选择 ==========
        # 输出路径选择容器
        output_frame = ttk.Frame(self)
        output_frame.grid(row=row, column=0, columnspan=4, sticky=tk.EW, padx=10, pady=(0, 12))

        ttk.Label(output_frame, text="输出路径:").pack(side=tk.LEFT)

        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))

        # 浏览输出路径按钮
        self.output_button = ttk.Button(
            output_frame,
            text="浏览",
            command=self.browse_output_path,
            width=8
        )
        self.output_button.pack(side=tk.LEFT)

        # 初始状态：折叠高级选项
        self.toggle_advanced(force_collapse=True)

    def toggle_advanced(self, force_collapse=False):
        """切换高级选项的展开/折叠状态

        Args:
            force_collapse (bool): 是否强制折叠
        """
        if force_collapse:
            self.advanced_expanded.set(False)
        else:
            self.advanced_expanded.set(not self.advanced_expanded.get())

        if self.advanced_expanded.get():
            self.advanced_frame.grid()
            self.advanced_button.config(text="▲")
        else:
            self.advanced_frame.grid_remove()
            self.advanced_button.config(text="▼")

    def on_mode_changed(self, *args):
        """分割模式变化时的回调函数

        更新输入框的显示状态，只显示当前模式的输入框。

        Args:
            *args: 传递给回调函数的参数（未使用）
        """
        self.update_input_visibility()

    def update_input_visibility(self):
        """更新输入框的显示状态

        根据当前选择的分割模式，显示对应的输入框，隐藏其他输入框。
        """
        mode = self.mode_var.get()

        # 默认隐藏所有输入框
        self.chars_frame.grid_remove()
        self.pages_frame.grid_remove()
        self.equal_frame.grid_remove()

        # 显示当前模式的输入框
        if mode == "chars":
            self.chars_frame.grid()
        elif mode == "pages":
            self.pages_frame.grid()
        elif mode == "equal":
            self.equal_frame.grid()

    def validate_chars_input(self, event=None):
        """验证字数输入是否为正整数

        该方法检查用户在字数输入框中输入的值是否为正整数，
        如果不是，则恢复为默认值。

        Args:
            event: 事件对象（可选）

        Returns:
            bool: 如果输入有效则返回True，否则返回False
        """
        value = self.chars_var.get()
        if not self.is_positive_integer(value):
            self.chars_var.set("1000")
            return False
        return True

    def validate_pages_input(self, event=None):
        """验证页数输入是否为正整数

        该方法检查用户在页数输入框中输入的值是否为正整数，
        如果不是，则恢复为默认值。

        Args:
            event: 事件对象（可选）

        Returns:
            bool: 如果输入有效则返回True，否则返回False
        """
        value = self.pages_var.get()
        if not self.is_positive_integer(value):
            self.pages_var.set("10")
            return False
        return True

    def validate_equal_input(self, event=None):
        """验证均分份数输入是否为正整数

        该方法检查用户在均分份数输入框中输入的值是否为正整数，
        如果不是，则恢复为默认值。

        Args:
            event: 事件对象（可选）

        Returns:
            bool: 如果输入有效则返回True，否则返回False
        """
        value = self.equal_var.get()
        if not self.is_positive_integer(value):
            self.equal_var.set("5")
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
        # 验证输入是否有效
        if not self.validate_chars_input() or not self.validate_pages_input() or not self.validate_equal_input():
            return None

        # 组织设置参数
        mode = self.mode_var.get()
        if mode == "chars":
            value = int(self.chars_var.get())
        elif mode == "pages":
            value = int(self.pages_var.get())
        else:  # equal
            value = int(self.equal_var.get())

        settings = {
            'mode': mode,  # 分割模式
            'value': value,  # 分割数值
            'output_path': self.output_path_var.get(),  # 输出路径
            'preserve_chapter': self.preserve_chapter_var.get()  # 保留章节完整性
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
        path = filedialog.askdirectory(title='选择输出目录')
        if path:
            self.output_path_var.set(path)

    def set_mode_state(self, state, disable_pages=False):
        """设置模式选择的状态 (normal/disabled)

        该方法可以启用或禁用分割模式选择单选按钮，
        通常在不同文件类型时使用不同的可用模式。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
            disable_pages (bool, optional): 是否只禁用 "pages" 模式，默认为 False
        """
        if disable_pages:
            # 只禁用 "pages" 模式
            self.pages_radio.config(state=tk.DISABLED)
            self.chars_radio.config(state=state)
            self.equal_radio.config(state=state)
        else:
            # 禁用所有模式
            self.chars_radio.config(state=state)
            self.pages_radio.config(state=state)
            self.equal_radio.config(state=state)

    def set_value_state(self, state):
        """设置数值输入框的状态 (normal/disabled)

        该方法可以启用或禁用分割数值输入框。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
        """
        self.chars_entry.config(state=state)
        self.pages_entry.config(state=state)
        self.equal_entry.config(state=state)

    def set_output_controls_state(self, state):
        """设置输出路径控件的状态 (normal/disabled)

        该方法可以同时启用或禁用输出路径输入框和浏览按钮。

        Args:
            state (str): 控件状态，通常是 'normal' 或 'disabled'
        """
        self.output_entry.config(state=state)
        self.output_button.config(state=state)