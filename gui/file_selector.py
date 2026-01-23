"""
文件选择组件

该组件提供了一个用户界面，允许用户浏览并选择要分割的文档文件。
采用上下分行布局：上为文件拖拽区域（主交互区），下为操作按钮区域（次级交互区）。
支持点击选择和拖拽文件两种方式。
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path
import os


class FileSelector(ttk.Frame):
    """文件选择组件

    该组件继承自ttk.Frame，提供了一个标准的文件选择界面，
    采用上下分行布局，视觉层级清晰，符合工程类软件设计习惯。
    """

    def __init__(self, parent, config_manager=None, **kwargs):
        """初始化文件选择组件

        Args:
            parent: 父级组件
            config_manager: 配置管理器实例（可选）
            **kwargs: 传递给父类构造函数的其他参数
        """
        super().__init__(parent, **kwargs)

        # 配置管理器
        self.config_manager = config_manager

        # 创建一个StringVar变量来存储选中的文件路径（支持多文件）
        self.selected_file_path = tk.StringVar()
        self.selected_files = []  # 存储选中的文件列表

        # 加载保存的目录
        self.load_saved_directories()

        # 创建界面组件
        self.create_widgets()

        # 尝试注册拖放功能
        self.setup_drag_and_drop()

    def create_widgets(self):
        """创建界面组件

        该方法创建文件拖拽区域和操作按钮区域，采用上下分行布局。
        """
        # 配置网格布局权重
        self.columnconfigure(0, weight=1)

        # ========== 第一行：文件拖拽区域（主交互区）==========
        # 创建拖放区域容器（使用 tk.Frame 而不是 ttk.Frame 以支持拖放）
        self.drop_frame = tk.Frame(
            self,
            relief=tk.SUNKEN,
            borderwidth=2,
            height=60  # 设置固定高度，增强视觉存在感
        )
        self.drop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=0, pady=(0, 10))
        self.drop_frame.grid_propagate(False)  # 防止子组件改变容器大小

        # 创建文件路径显示标签（也作为拖放区域）
        self.file_label = ttk.Label(
            self.drop_frame,
            textvariable=self.selected_file_path,
            anchor=tk.W,
            padding=12,
            font=('TkDefaultFont', 9)  # 使用稍大的字体
        )
        self.file_label.pack(fill=tk.BOTH, expand=True)

        # 设置默认提示文本
        if not self.selected_file_path.get():
            self.selected_file_path.set("拖拽文件到此处，或使用下方按钮选择")

        # ========== 第二行：操作按钮区域（次级交互区）==========
        # 创建按钮容器
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky=tk.W)

        # 定义按钮样式参数（保持一致性）
        button_width = 12
        button_padx = 5

        # 创建文件选择按钮（选择新文件时会清除已选文件）
        self.select_button = ttk.Button(
            button_frame,
            text="选择文件",
            width=button_width,
            command=self.browse_file
        )
        self.select_button.pack(side=tk.LEFT, padx=(0, button_padx))

        # 创建增加文件按钮（在已选文件基础上增加新文件）
        self.add_file_button = ttk.Button(
            button_frame,
            text="增加文件",
            width=button_width,
            command=self.browse_file_add
        )
        self.add_file_button.pack(side=tk.LEFT, padx=(0, button_padx))

        # 创建选择目录按钮
        self.select_dir_button = ttk.Button(
            button_frame,
            text="选择目录",
            width=button_width,
            command=self.browse_directory
        )
        self.select_dir_button.pack(side=tk.LEFT, padx=(0, button_padx))

        # 创建清除文件按钮（清除当前已选文件）
        self.clear_file_button = ttk.Button(
            button_frame,
            text="清除文件",
            width=button_width,
            command=self.clear_files
        )
        self.clear_file_button.pack(side=tk.LEFT)

    def browse_file(self):
        """浏览并选择文件（清除已选文件）

        该方法打开文件对话框，让用户选择要分割的文档文件，
        清除之前已选的文件，然后将新选中的文件路径存储到selected_file_path变量中。
        """
        from tkinter import filedialog

        # 获取主窗口
        parent = self.winfo_toplevel()

        # 定义支持的文件类型
        filetypes = (
            ('Supported Files', '*.pdf *.docx *.txt *.md'),
            ('PDF files', '*.pdf'),
            ('Word files', '*.docx'),
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('All files', '*.*')
        )

        # 打开文件对话框（支持多文件选择）
        filenames = filedialog.askopenfilenames(
            parent=parent,
            title='选择要分割的文件（可多选）',
            filetypes=filetypes  # 文件类型过滤器
        )

        # 如果用户选择了文件，则更新路径变量（清除之前的文件）
        if filenames:
            self.selected_files = list(filenames)
            # 显示第一个文件路径，但保留所有文件在列表中
            if len(filenames) == 1:
                self.selected_file_path.set(filenames[0])
            else:
                self.selected_file_path.set(f"已选择 {len(filenames)} 个文件")
        else:
            # 用户取消了选择，保持当前状态不变
            pass

    def browse_file_add(self):
        """浏览并增加文件（不清除已选文件）

        该方法打开文件对话框，让用户选择要添加的文档文件，
        将新选中的文件添加到已选文件列表中。
        """
        from tkinter import filedialog

        # 获取主窗口
        parent = self.winfo_toplevel()

        # 定义支持的文件类型
        filetypes = (
            ('Supported Files', '*.pdf *.docx *.txt *.md'),
            ('PDF files', '*.pdf'),
            ('Word files', '*.docx'),
            ('Text files', '*.txt'),
            ('Markdown files', '*.md'),
            ('All files', '*.*')
        )

        # 打开文件对话框（支持多文件选择）
        filenames = filedialog.askopenfilenames(
            parent=parent,
            title='选择要添加的文件（可多选）',
            filetypes=filetypes  # 文件类型过滤器
        )

        # 如果用户选择了文件，则添加到已选文件列表
        if filenames:
            # 添加新文件到列表中（避免重复）
            for filename in filenames:
                if filename not in self.selected_files:
                    self.selected_files.append(filename)

            # 更新显示
            if len(self.selected_files) == 1:
                self.selected_file_path.set(self.selected_files[0])
            else:
                self.selected_file_path.set(f"已选择 {len(self.selected_files)} 个文件")

    def clear_files(self):
        """清除所有已选文件

        该方法清除当前已选的所有文件，重置为初始状态。
        """
        self.selected_files = []
        self.selected_file_path.set("拖拽文件到此处，或使用下方按钮选择")

    def browse_directory(self):
        """浏览并选择目录，读取目录中所有支持的文件

        该方法打开目录选择对话框，让用户选择一个目录，
        然后读取该目录中所有支持的文件（.pdf, .docx, .txt）。
        """
        from tkinter import filedialog

        # 获取主窗口
        parent = self.winfo_toplevel()

        # 使用上次选择的目录作为初始目录
        initial_dir = self.last_input_dir if self.last_input_dir else None

        # 打开目录选择对话框
        directory = filedialog.askdirectory(
            parent=parent,
            title='选择包含文件的目录',
            initialdir=initial_dir
        )

        if not directory:
            return

        # 保存选择的目录
        self.save_input_directory(directory)

        # 支持的文件扩展名
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']

        # 扫描目录中的所有文件
        valid_files = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # 只处理文件，不处理子目录
                if os.path.isfile(file_path):
                    # 检查文件扩展名
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_extensions:
                        valid_files.append(file_path)
        except Exception as e:
            return

        # 更新文件列表（清除之前的文件）
        if valid_files:
            self.selected_files = valid_files
            # 按文件名排序
            self.selected_files.sort()

            # 更新显示
            if len(self.selected_files) == 1:
                self.selected_file_path.set(self.selected_files[0])
            else:
                self.selected_file_path.set(f"已选择 {len(self.selected_files)} 个文件")
        else:
            self.selected_file_path.set("目录中没有支持的文件")

    def get_selected_file(self):
        """获取选中的文件路径

        Returns:
            str: 选中的文件路径，如果没有选择文件则返回空字符串
        """
        return self.selected_file_path.get()

    def get_selected_files(self):
        """获取选中的所有文件路径

        Returns:
            list: 选中的文件路径列表
        """
        return self.selected_files

    def set_selected_file(self, file_path):
        """设置选中的文件路径

        该方法可以直接设置组件中显示的文件路径，
        而不需要用户手动选择。

        Args:
            file_path (str): 要设置的文件路径
        """
        self.selected_files = [file_path]
        self.selected_file_path.set(file_path)

    def load_saved_directories(self):
        """加载保存的目录配置"""
        if self.config_manager:
            try:
                config = self.config_manager.read_config()
                self.last_input_dir = config.get("Paths", {}).get("input_dir", "")
                self.last_output_dir = config.get("Paths", {}).get("output_dir", "")
            except Exception:
                self.last_input_dir = ""
                self.last_output_dir = ""
        else:
            self.last_input_dir = ""
            self.last_output_dir = ""

    def save_input_directory(self, directory):
        """保存输入目录到配置文件"""
        if self.config_manager:
            try:
                config = self.config_manager.read_config()
                config["Paths"]["input_dir"] = directory
                self.config_manager.save_config(config)
                self.last_input_dir = directory
            except Exception:
                pass

    def setup_drag_and_drop(self):
        """设置拖放功能

        该方法尝试使用 tkinterdnd2 库注册拖放事件。
        如果库不可用，则跳过拖放功能，程序仍可正常使用点击选择。
        """
        try:
            from tkinterdnd2 import DND_FILES

            # 获取根窗口
            root = self.winfo_toplevel()

            # 为拖放区域注册拖放事件
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)

        except ImportError:
            # tkinterdnd2 未安装，拖放功能不可用
            pass
        except Exception as e:
            # 其他错误，不影响主功能
            pass

    def on_drag_enter(self, event):
        """拖拽进入时的视觉反馈

        Args:
            event: 拖拽事件对象
        """
        self.drop_frame.config(background="#e8f4f8")

    def on_drag_leave(self, event):
        """拖拽离开时的视觉反馈

        Args:
            event: 拖拽事件对象
        """
        self.drop_frame.config(background="")

    def on_drop(self, event):
        """处理文件拖放事件

        Args:
            event: 拖拽事件对象，包含拖放的文件路径
        """
        # 获取拖放的文件路径
        files = event.data

        # 处理 Windows 路径格式（可能包含花括号或引号）
        if isinstance(files, str):
            # 移除可能的引号
            files = files.strip('"\'')
        # 分割多个文件（如果用户拖放了多个）
        # 对于Windows，多个文件路径通常被花括号包围，格式为 {路径1} {路径2}
        import re
        # 匹配花括号包围的路径
        bracket_paths = re.findall(r'\{([^}]*)\}', files)

        if bracket_paths:
            # 如果找到花括号包围的路径，使用这些路径
            path_list = bracket_paths
        else:
            # 尝试匹配用引号包围的路径
            quoted_paths = re.findall(r'"([^"]*)"|\'([^\']*)\'', files)
            if quoted_paths:
                # 如果找到引号包围的路径，使用这些路径
                path_list = [match[0] or match[1] for match in quoted_paths if match[0] or match[1]]
            else:
                # 如果没有引号包围的路径，对于Windows拖拽，通常整个路径被花括号包围作为一个整体
                # 或者路径中包含空格但没有引号，我们需要特殊处理这种情况
                files_stripped = files.strip('{}')  # 移除最外层的花括号

                # 如果路径包含常见的文件扩展名且有空格，很可能这是一个带空格的完整路径
                if any(ext in files_stripped.lower() for ext in ['.pdf', '.docx', '.txt']):
                    # 假设整个（去除花括号后）的字符串是一个路径
                    path_list = [files_stripped]
                else:
                    # 否则按空格分割
                    path_list = files_stripped.split()

        # 处理所有路径（可能是文件或文件夹）
        valid_files = []
        unsupported_items = []

        for path in path_list:
            path = path.strip()

            if not path:
                continue

            # 尝试规范化路径
            try:
                normalized_path = Path(path).resolve()
                path = str(normalized_path)
            except Exception as e:
                continue

            # 检查路径是否存在
            if Path(path).exists():
                if Path(path).is_file():
                    # 如果是文件，验证文件类型
                    file_ext = Path(path).suffix.lower()
                    supported_extensions = ['.pdf', '.docx', '.txt', '.md']

                    if file_ext in supported_extensions:
                        valid_files.append(path)
                    else:
                        unsupported_items.append(path)
                elif Path(path).is_dir():
                    # 如果是目录，扫描目录中的所有支持的文件
                    dir_valid_files = self.scan_directory_for_supported_files(path)
                    valid_files.extend(dir_valid_files)
                else:
                    # 其他类型（不太可能）
                    unsupported_items.append(path)
            else:
                # 路径不存在 - 尝试多种路径格式
                import urllib.parse
                decoded_path = urllib.parse.unquote(path)
                if Path(decoded_path).exists():
                    if Path(decoded_path).is_file():
                        file_ext = Path(decoded_path).suffix.lower()
                        supported_extensions = ['.pdf', '.docx', '.txt', '.md']
                        if file_ext in supported_extensions:
                            valid_files.append(decoded_path)
                        else:
                            unsupported_items.append(decoded_path)
                    elif Path(decoded_path).is_dir():
                        # 如果是目录，扫描目录中的所有支持的文件
                        dir_valid_files = self.scan_directory_for_supported_files(decoded_path)
                        valid_files.extend(dir_valid_files)

        # 更新文件列表（清除之前的文件）
        self.selected_files = valid_files

        # 更新显示
        if len(valid_files) == 0:
            if len(unsupported_items) > 0:
                self.selected_file_path.set("拖拽的文件/文件夹无效或不支持")
            else:
                self.selected_file_path.set("拖拽的文件/文件夹不存在")
        elif len(valid_files) == 1:
            self.selected_file_path.set(valid_files[0])
        else:
            self.selected_file_path.set(f"已选择 {len(valid_files)} 个文件")

        # 恢复默认样式
        self.drop_frame.config(background="")

    def scan_directory_for_supported_files(self, directory):
        """扫描目录中所有支持的文件

        Args:
            directory (str): 目录路径

        Returns:
            list: 支持的文件路径列表
        """
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']
        valid_files = []

        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # 只处理文件，不处理子目录
                if os.path.isfile(file_path):
                    # 检查文件扩展名
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_extensions:
                        valid_files.append(file_path)
        except Exception as e:
            # 如果目录无法访问，返回空列表
            pass

        return valid_files