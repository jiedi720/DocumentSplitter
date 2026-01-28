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
        
        # 加载排除的文件格式
        self.load_excluded_formats()

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
        
        # ========== 第三行：排除文件格式设置 ==========
        # 创建排除格式设置区域
        exclude_frame = ttk.Frame(self)
        exclude_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0), padx=10)
        
        ttk.Label(exclude_frame, text="排除文件格式:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # 创建支持的文件格式列表
        self.supported_formats = ['.pdf', '.docx', '.txt', '.md']
        
        # 创建排除格式选择框
        self.exclude_formats_combobox = ttk.Combobox(
            exclude_frame, 
            values=self.supported_formats,
            width=7,
            state='readonly'
        )
        self.exclude_formats_combobox.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 添加选择按钮
        self.add_exclude_button = ttk.Button(
            exclude_frame, 
            text="添加", 
            width=6,
            command=self.add_excluded_format
        )
        self.add_exclude_button.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        # 添加移除所有按钮
        self.remove_exclude_button = ttk.Button(
            exclude_frame, 
            text="移除所有", 
            width=8,
            command=self.remove_all_excluded_formats
        )
        self.remove_exclude_button.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # 显示当前已排除的格式
        self.excluded_formats_display = ttk.Label(
            exclude_frame, 
            text="无", 
            foreground='#666666'
        )
        self.excluded_formats_display.grid(row=0, column=4, sticky=tk.W)
        
        # 存储当前已排除的格式列表
        self.current_excluded_formats = []
        
        # 初始化显示
        self.update_excluded_formats_display()

    def browse_file(self):
        """浏览并选择文件（清除已选文件）

        该方法打开文件对话框，让用户选择要分割的文档文件，
        清除之前已选的文件，然后将新选中的文件路径存储到selected_file_path变量中。
        """
        from tkinter import filedialog

        # 获取主窗口
        parent = self.winfo_toplevel()

        # 定义支持的文件类型
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']
        
        # 获取排除的文件格式
        excluded_formats = self.get_excluded_formats()
        
        # 过滤支持的扩展名，排除不需要的格式
        filtered_extensions = [ext for ext in supported_extensions if ext not in excluded_formats]
        
        # 构建文件类型过滤器
        if filtered_extensions:
            # 构建第一个过滤器：所有支持且未被排除的文件
            first_filter_pattern = ' '.join([f'*{ext}' for ext in filtered_extensions])
            filetypes = [
                ('Supported Files', first_filter_pattern),
            ]
            
            # 为每个剩余的扩展名添加单独的过滤器
            for ext in filtered_extensions:
                if ext == '.pdf':
                    filetypes.append(('PDF files', '*.pdf'))
                elif ext == '.docx':
                    filetypes.append(('Word files', '*.docx'))
                elif ext == '.txt':
                    filetypes.append(('Text files', '*.txt'))
                elif ext == '.md':
                    filetypes.append(('Markdown files', '*.md'))
            
            filetypes.append(('All files', '*.*'))
        else:
            # 如果所有格式都被排除，只显示所有文件选项
            filetypes = [('All files', '*.*')]

        # 打开文件对话框（支持多文件选择）
        filenames = filedialog.askopenfilenames(
            parent=parent,
            title='选择要分割的文件（可多选）',
            filetypes=filetypes  # 文件类型过滤器
        )

        # 如果用户选择了文件，则更新路径变量（清除之前的文件）
        if filenames:
            # 应用排除格式过滤
            filtered_files = []
            for filename in filenames:
                file_ext = Path(filename).suffix.lower()
                if file_ext in filtered_extensions:
                    filtered_files.append(filename)
            
            self.selected_files = filtered_files
            # 显示第一个文件路径，但保留所有文件在列表中
            if len(filtered_files) == 1:
                self.selected_file_path.set(filtered_files[0])
            elif filtered_files:
                self.selected_file_path.set(f"已选择 {len(filtered_files)} 个文件")
            else:
                self.selected_file_path.set("拖拽文件到此处，或使用下方按钮选择")
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
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']
        
        # 获取排除的文件格式
        excluded_formats = self.get_excluded_formats()
        
        # 过滤支持的扩展名，排除不需要的格式
        filtered_extensions = [ext for ext in supported_extensions if ext not in excluded_formats]
        
        # 构建文件类型过滤器
        if filtered_extensions:
            # 构建第一个过滤器：所有支持且未被排除的文件
            first_filter_pattern = ' '.join([f'*{ext}' for ext in filtered_extensions])
            filetypes = [
                ('Supported Files', first_filter_pattern),
            ]
            
            # 为每个剩余的扩展名添加单独的过滤器
            for ext in filtered_extensions:
                if ext == '.pdf':
                    filetypes.append(('PDF files', '*.pdf'))
                elif ext == '.docx':
                    filetypes.append(('Word files', '*.docx'))
                elif ext == '.txt':
                    filetypes.append(('Text files', '*.txt'))
                elif ext == '.md':
                    filetypes.append(('Markdown files', '*.md'))
            
            filetypes.append(('All files', '*.*'))
        else:
            # 如果所有格式都被排除，只显示所有文件选项
            filetypes = [('All files', '*.*')]

        # 打开文件对话框（支持多文件选择）
        filenames = filedialog.askopenfilenames(
            parent=parent,
            title='选择要添加的文件（可多选）',
            filetypes=filetypes  # 文件类型过滤器
        )

        # 如果用户选择了文件，则添加到已选文件列表
        if filenames:
            # 添加新文件到列表中（避免重复，且只添加未被排除的格式）
            for filename in filenames:
                if filename not in self.selected_files:
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in filtered_extensions:
                        self.selected_files.append(filename)

            # 更新显示
            if len(self.selected_files) == 1:
                self.selected_file_path.set(self.selected_files[0])
            elif self.selected_files:
                self.selected_file_path.set(f"已选择 {len(self.selected_files)} 个文件")
            else:
                self.selected_file_path.set("拖拽文件到此处，或使用下方按钮选择")

    def clear_files(self):
        """清除所有已选文件

        该方法清除当前已选的所有文件，重置为初始状态。
        """
        self.selected_files = []
        self.selected_file_path.set("拖拽文件到此处，或使用下方按钮选择")

    def browse_directory(self):
        """浏览并选择目录，读取目录中所有支持的文件，包括子文件夹

        该方法打开目录选择对话框，让用户选择一个目录，
        然后读取该目录及其所有子目录中所有支持的文件（.pdf, .docx, .txt, .md）。
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

        # 扫描目录及其子目录中的所有支持文件
        valid_files = self.scan_directory_for_supported_files(directory)

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
    
    def add_excluded_format(self):
        """添加选中的格式到排除列表"""
        selected_format = self.exclude_formats_combobox.get()
        if selected_format and selected_format not in self.current_excluded_formats:
            self.current_excluded_formats.append(selected_format)
            self.update_excluded_formats_display()
            self.save_excluded_formats()
    
    def remove_all_excluded_formats(self):
        """移除所有排除的格式"""
        self.current_excluded_formats = []
        self.update_excluded_formats_display()
        self.save_excluded_formats()
    
    def update_excluded_formats_display(self):
        """更新显示当前已排除的格式"""
        if self.current_excluded_formats:
            display_text = ", ".join(self.current_excluded_formats)
        else:
            display_text = "无"
        self.excluded_formats_display.config(text=display_text)
    
    def save_excluded_formats(self):
        """保存排除格式到配置文件"""
        if self.config_manager:
            try:
                config = self.config_manager.read_config()
                config["SplitSettings"]["exclude_formats"] = ",".join(self.current_excluded_formats)
                self.config_manager.save_config(config)
            except Exception as e:
                pass
    
    def load_excluded_formats(self):
        """从配置文件加载排除的文件格式"""
        self.current_excluded_formats = []
        if self.config_manager:
            try:
                config = self.config_manager.read_config()
                exclude_formats_str = config.get("SplitSettings", {}).get("exclude_formats", "")
                if exclude_formats_str:
                    self.current_excluded_formats = [f.strip() for f in exclude_formats_str.split(",") if f.strip()]
            except Exception as e:
                pass
    
    def get_excluded_formats(self):
        """获取排除的文件格式列表
        
        Returns:
            list: 排除的文件格式列表
        """
        return self.current_excluded_formats

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
        else:
            files = str(files)

        # 分割多个文件（如果用户拖放了多个）
        # 对于Windows，多个文件路径通常被花括号包围，格式为 {路径1} {路径2}
        import re
        path_list = []

        # 优先处理花括号包围的路径格式（Windows标准格式）
        if files.startswith('{') and files.endswith('}'):
            # 移除最外层的花括号
            files_content = files[1:-1]
            
            # 尝试多种方式分割路径
            # 1. 尝试按 '} {' 分割（常见的多文件格式）
            if '} {' in files_content:
                split_paths = files_content.split('} {')
                # 清理每个路径
                cleaned_paths = []
                for p in split_paths:
                    cleaned = p.strip()
                    if cleaned:
                        cleaned_paths.append(cleaned)
                if cleaned_paths:
                    path_list = cleaned_paths
            else:
                # 2. 尝试匹配内部的花括号包围的路径
                bracket_paths = re.findall(r'\{([^}]*)\}', files_content)
                
                if bracket_paths:
                    path_list = bracket_paths
                else:
                    # 3. 尝试按空格分割，但要注意路径中的空格
                    # 这种情况可能是单文件路径，包含空格但没有被正确包围
                    path_list = [files_content]
        else:
            # 检查是否包含花括号（可能是不完整的花括号包围格式）
            if '{' in files or '}' in files:
                # 尝试清理并分割路径
                # 移除所有花括号
                cleaned_files = files.replace('{', '').replace('}', '')
                
                # 检查是否包含多个文件扩展名
                extensions = ['.pdf', '.docx', '.txt', '.md']
                extension_count = 0
                for ext in extensions:
                    extension_count += cleaned_files.lower().count(ext)
                
                if extension_count > 1:
                    # 多个文件，尝试按扩展名分割
                    # 改进正则表达式，支持包含中文和空格的完整路径
                    extension_pattern = '|'.join([re.escape(ext) for ext in extensions])
                    # 匹配完整路径：从非空白字符开始，包含任意字符（包括空格和中文），直到遇到扩展名
                    # 注意：这个正则表达式假设路径之间用空格分隔
                    path_pattern = rf'([^\s].*?{extension_pattern})'
                    multi_paths = re.findall(path_pattern, cleaned_files)
                    
                    if multi_paths:
                        # 清理分割后的路径
                        cleaned_multi_paths = []
                        for p in multi_paths:
                            # 移除路径末尾的空格
                            cleaned = p.strip()
                            if cleaned:
                                cleaned_multi_paths.append(cleaned)
                        
                        if cleaned_multi_paths:
                            path_list = cleaned_multi_paths
                        else:
                            # 尝试简单的空格分割
                            path_list = cleaned_files.split()
                    else:
                        # 尝试简单的空格分割
                        path_list = cleaned_files.split()
                else:
                    # 单个文件
                    path_list = [cleaned_files]
            else:
                # 尝试匹配用引号包围的路径
                quoted_paths = re.findall(r'"([^"]*)"|\'([^\']*)\'', files)
                if quoted_paths:
                    # 如果找到引号包围的路径，使用这些路径
                    path_list = [match[0] or match[1] for match in quoted_paths if match[0] or match[1]]
                else:
                    # 尝试处理没有引号包围但包含空格的路径
                    # 检查是否包含常见文件扩展名
                    has_extension = any(ext in files.lower() for ext in ['.pdf', '.docx', '.txt', '.md'])
                    
                    if has_extension:
                        # 检查是否包含多个文件扩展名（多个文件）
                        extensions = ['.pdf', '.docx', '.txt', '.md']
                        extension_count = 0
                        for ext in extensions:
                            extension_count += files.lower().count(ext)
                        
                        if extension_count > 1:
                            # 多个文件，尝试按扩展名分割
                            # 改进正则表达式，支持包含中文和空格的完整路径
                            extension_pattern = '|'.join([re.escape(ext) for ext in extensions])
                            # 匹配完整路径：从非空白字符开始，包含任意字符（包括空格和中文），直到遇到扩展名
                            # 注意：这个正则表达式假设路径之间用空格分隔
                            path_pattern = rf'([^\s].*?{extension_pattern})'
                            multi_paths = re.findall(path_pattern, files)
                            
                            if multi_paths:
                                # 清理分割后的路径
                                cleaned_multi_paths = []
                                for p in multi_paths:
                                    # 移除路径末尾的空格
                                    cleaned = p.strip()
                                    if cleaned:
                                        cleaned_multi_paths.append(cleaned)
                                
                                if cleaned_multi_paths:
                                    path_list = cleaned_multi_paths
                                else:
                                    # 如果正则表达式分割失败，尝试简单的空格分割
                                    path_list = files.split()
                            else:
                                # 如果正则表达式分割失败，尝试简单的空格分割
                                path_list = files.split()
                        else:
                            # 单个文件，假设整个字符串是一个路径（可能包含空格）
                            path_list = [files]
                    else:
                        # 否则按空格分割（适用于多个简单路径）
                        path_list = files.split()

        # 处理所有路径（可能是文件或文件夹）
        valid_files = []
        unsupported_items = []

        for path in path_list:
            path = path.strip()

            if not path:
                continue

            # 尝试多种路径处理方法
            processed_paths = [path]
            
            # 添加可能的解码路径
            try:
                import urllib.parse
                decoded_path = urllib.parse.unquote(path)
                if decoded_path != path:
                    processed_paths.append(decoded_path)
            except Exception:
                pass

            # 尝试处理所有可能的路径
            path_valid = False
            for processed_path in processed_paths:
                try:
                    # 尝试规范化路径
                    normalized_path = Path(processed_path).resolve()
                    path_str = str(normalized_path)

                    # 检查路径是否存在
                    if Path(path_str).exists():
                        
                        if Path(path_str).is_file():
                            # 如果是文件，验证文件类型
                            file_ext = Path(path_str).suffix.lower()
                            supported_extensions = ['.pdf', '.docx', '.txt', '.md']
                            
                            # 获取排除的文件格式
                            excluded_formats = self.get_excluded_formats()

                            if file_ext in supported_extensions and file_ext not in excluded_formats:
                                valid_files.append(path_str)
                                path_valid = True
                                break
                            else:
                                unsupported_items.append(path_str)
                                path_valid = True  # 路径存在但不支持
                                break
                        elif Path(path_str).is_dir():
                            # 如果是目录，扫描目录中的所有支持的文件
                            dir_valid_files = self.scan_directory_for_supported_files(path_str)
                            if dir_valid_files:
                                valid_files.extend(dir_valid_files)
                                path_valid = True
                                break
                            else:
                                unsupported_items.append(path_str)
                                path_valid = True  # 路径存在但目录中没有支持的文件
                                break
                    else:
                        # 路径不存在，继续尝试其他处理方法
                        continue
                except Exception:
                    # 路径处理出错，继续尝试其他方法
                    continue

            # 如果所有处理方法都失败，将路径添加到不支持列表
            if not path_valid:
                unsupported_items.append(path)

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
        """扫描目录中所有支持的文件，包括子文件夹

        Args:
            directory (str): 目录路径

        Returns:
            list: 支持的文件路径列表
        """
        supported_extensions = ['.pdf', '.docx', '.txt', '.md']
        valid_files = []
        
        # 获取排除的文件格式
        excluded_formats = self.get_excluded_formats()

        try:
            # 递归遍历目录及其子目录
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    # 检查文件扩展名
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_extensions and file_ext not in excluded_formats:
                        valid_files.append(file_path)
        except Exception as e:
            # 如果目录无法访问，返回空列表
            pass

        return valid_files