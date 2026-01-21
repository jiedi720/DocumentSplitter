"""
主窗口界面

该模块实现了文档分割工具的主界面，包括文件选择、
分割设置、进度显示、操作日志和控制按钮等功能。
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from pathlib import Path

# 导入GUI组件
from .file_selector import FileSelector
from .settings_panel import SettingsPanel
from .analysis_result_window import AnalysisResultWindow

# 导入功能模块
import sys
from pathlib import Path
import os

# 添加项目根目录到系统路径
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from function.file_handler import FileHandler
from function.pdf_splitter import PDFSplitter
from function.word_splitter import WordSplitter
from function.txt_splitter import TxtSplitter
from function.document_analyzer import DocumentAnalyzer


class MainApplication:
    """主应用程序类

    该类实现了文档分割工具的主界面和核心功能，
    包括文件选择、分割参数设置、进度显示和日志记录等。
    """

    def __init__(self):
        """初始化主应用程序

        创建主窗口、初始化功能模块、构建界面组件，
        并设置窗口居中显示。
        """
        # 尝试使用 TkinterDnD 创建支持拖放的窗口
        try:
            from tkinterdnd2 import TkinterDnD
            self.root = TkinterDnD.Tk()
            print("使用 TkinterDnD.Tk() 创建窗口，支持拖放功能")
        except ImportError:
            # 如果 tkinterdnd2 不可用，使用普通 Tk
            self.root = tk.Tk()
            print("使用普通 tk.Tk() 创建窗口，不支持拖放功能")
        except Exception as e:
            # 其他错误，使用普通 Tk
            self.root = tk.Tk()
            print(f"创建 TkinterDnD 窗口失败：{e}，使用普通窗口")

        # 先隐藏窗口，避免显示时的闪烁
        self.root.withdraw()  # 暂时隐藏窗口

        # 设置窗口图标
        self.setup_window_icon()

        # 设置窗口标题和尺寸
        self.root.title("DocumentSplitter")  # 设置窗口标题
        self.root.geometry("800x600")

        # 初始化功能模块
        self.file_handler = FileHandler()
        self.pdf_splitter = PDFSplitter()
        self.word_splitter = WordSplitter()
        self.txt_splitter = TxtSplitter()
        self.document_analyzer = DocumentAnalyzer()

        # 当前选中的文件路径
        self.current_file_path = ""

        # 创建所有界面组件
        self.create_widgets()

        # 计算并设置窗口居中位置
        self.center_window()

        # 显示窗口
        self.root.deiconify()

    def create_widgets(self):
        """创建主界面组件

        该方法构建主窗口的所有界面元素，包括：
        - 文件选择区域
        - 设置面板
        - 进度显示区域
        - 控制按钮
        - 日志显示区域
        """
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重，使界面能随窗口大小调整
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)

        # 创建文件选择组件
        self.file_selector = FileSelector(file_frame)
        self.file_selector.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # 绑定文件选择变化事件，当文件路径改变时触发回调
        self.file_selector.selected_file_path.trace('w', self.on_file_selected)

        # 设置面板
        self.settings_panel = SettingsPanel(main_frame)
        self.settings_panel.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # 进度信息变量和标签
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=tk.W)

        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',  # 确定模式，显示具体进度
            length=300
        )
        self.progress_bar.pack(pady=(5, 0), fill=tk.X)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # 开始分割按钮
        self.split_button = ttk.Button(
            button_frame,
            text="开始分割",
            command=self.start_splitting,
            state=tk.DISABLED  # 初始禁用，直到选择文件
        )
        self.split_button.pack(side=tk.LEFT, padx=(0, 10))

        # 文档分析按钮
        self.analyze_button = ttk.Button(
            button_frame,
            text="分析文档",
            command=self.analyze_document,
            state=tk.DISABLED  # 初始禁用，直到选择文件
        )
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))

        # 取消按钮
        self.cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.cancel_operation,
            state=tk.DISABLED  # 初始禁用
        )
        self.cancel_button.pack(side=tk.LEFT)

        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # 创建文本框和滚动条
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 操作状态标志
        self.operation_cancelled = False

    def on_file_selected(self, *args):
        """当文件被选择时的回调函数

        该方法在用户选择文件后被调用，根据文件类型
        调整界面设置并启用相应的功能。

        Args:
            *args: 传递给回调函数的参数（未使用）
        """
        # 获取选中的所有文件
        selected_files = self.file_selector.get_selected_files()
        selected_file = self.file_selector.get_selected_file()

        # 检查是否有选中的文件
        if selected_files:
            # 启用分析按钮（支持多文件分析）
            self.analyze_button.config(state=tk.NORMAL)

            # 如果只有一个文件，启用分割按钮并调整设置
            if len(selected_files) == 1:
                file_path = selected_files[0]
                if os.path.exists(file_path):
                    self.current_file_path = file_path
                    self.split_button.config(state=tk.NORMAL)

                    # 根据文件类型调整设置面板
                    file_type = self.file_handler.get_file_type(file_path)
                    if file_type == '.pdf':
                        self.settings_panel.set_mode_state(tk.NORMAL)
                    else:
                        self.settings_panel.mode_var.set("chars")
                        self.settings_panel.set_mode_state(tk.DISABLED)

                    # 设置默认输出路径为文件所在目录
                    default_output = str(Path(file_path).parent)
                    self.settings_panel.set_default_output_path(default_output)

                    # 记录日志
                    self.log_message(f"已选择文件: {file_path}")
            else:
                # 多个文件，禁用分割按钮（分割功能只支持单个文件）
                self.split_button.config(state=tk.DISABLED)
                self.log_message(f"已选择 {len(selected_files)} 个文件，可用于分析")
        elif selected_file and ("文件不存在" in selected_file or "不支持的文件类型" in selected_file or "拖拽的文件无效" in selected_file):
            # 文件选择错误
            self.split_button.config(state=tk.DISABLED)
            self.analyze_button.config(state=tk.DISABLED)
            self.log_message(f"文件选择错误: {selected_file}")
        else:
            # 未选择文件
            self.split_button.config(state=tk.DISABLED)
            self.analyze_button.config(state=tk.DISABLED)

    def analyze_document(self):
        """分析文档

        该方法在用户点击"分析文档"按钮后被调用，
        分析当前选中的文档（支持多个）并显示元数据信息。
        """
        # 获取选中的所有文件
        selected_files = self.file_selector.get_selected_files()

        if not selected_files:
            messagebox.showerror("错误", "请选择一个或多个有效的文件")
            return

        try:
            # 分析所有文档
            self.log_message(f"正在分析 {len(selected_files)} 个文档...")
            results = self.document_analyzer.analyze_files(selected_files)

            # 显示分析结果
            AnalysisResultWindow(self.root, results)
            self.log_message(f"文档分析完成，共分析 {len(results)} 个文件")

        except Exception as e:
            error_msg = f"文档分析失败: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("错误", error_msg)

    def start_splitting(self):
        """开始分割文档

        该方法在用户点击"开始分割"按钮后被调用，
        验证输入参数并启动分割操作线程。
        """
        # 获取选中的文件
        file_path = self.file_selector.get_selected_file()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择一个有效的文件")
            return

        # 获取用户设置的参数
        settings = self.settings_panel.get_settings()
        if not settings:
            messagebox.showerror("错误", "请输入有效的分割参数")
            return

        # 禁用相关UI元素，防止重复操作
        self.split_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.file_selector.select_button.config(state=tk.DISABLED)

        # 重置取消标志
        self.operation_cancelled = False

        # 在新线程中执行分割操作，避免界面冻结
        self.split_thread = threading.Thread(
            target=self.perform_splitting,
            args=(file_path, settings)
        )
        self.split_thread.start()

    def perform_splitting(self, file_path, settings):
        """执行分割操作

        该方法在后台线程中执行实际的文档分割操作，
        根据文件类型和用户设置调用相应的分割方法。

        Args:
            file_path (str): 要分割的文件路径
            settings (dict): 用户设置的分割参数
        """
        try:
            # 更新进度信息
            self.update_progress("正在分析文件...", 0)

            # 获取文件类型
            file_type = self.file_handler.get_file_type(file_path)
            if not file_type:
                raise ValueError(f"不支持的文件格式: {file_path}")

            # 根据文件类型和设置执行相应的分割方法
            output_files = []

            if file_type == '.pdf':
                if settings['mode'] == 'pages':
                    self.log_message(f"开始按页数分割 PDF 文件，每份 {settings['value']} 页")
                    output_files = self.pdf_splitter.split_by_pages(
                        file_path,
                        settings['value'],
                        settings['output_path']
                    )
                elif settings['mode'] == 'chars':
                    self.log_message(f"开始按字符数分割 PDF 文件，每份 {settings['value']} 字符")
                    output_files = self.pdf_splitter.split_by_chars(
                        file_path,
                        settings['value'],
                        settings['output_path']
                    )
            elif file_type == '.docx':
                self.log_message(f"开始按字符数分割 Word 文件，每份 {settings['value']} 字符")
                output_files = self.word_splitter.split_by_chars(
                    file_path,
                    settings['value'],
                    settings['output_path']
                )
            elif file_type == '.txt':
                self.log_message(f"开始按字符数分割 TXT 文件，每份 {settings['value']} 字符")
                output_files = self.txt_splitter.split_by_chars(
                    file_path,
                    settings['value'],
                    settings['output_path']
                )

            # 检查操作是否被用户取消
            if self.operation_cancelled:
                self.log_message("操作已取消")
                return

            # 更新进度为完成状态
            self.update_progress(f"分割完成！生成了 {len(output_files)} 个文件", 100)

            # 记录生成的文件
            for output_file in output_files:
                self.log_message(f"已生成: {output_file}")

            # 显示完成消息
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"文档分割完成！\n共生成 {len(output_files)} 个文件。"
            ))

        except Exception as e:
            # 错误处理
            error_msg = f"分割过程中发生错误: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            # 操作完成后恢复UI元素状态
            self.root.after(0, self.reset_ui_after_operation)

    def cancel_operation(self):
        """取消当前操作

        该方法在用户点击"取消"按钮后被调用，
        设置取消标志并更新进度信息。
        """
        self.operation_cancelled = True
        self.update_progress("正在取消操作...", 0)
        self.log_message("正在取消操作...")

    def reset_ui_after_operation(self):
        """操作完成后重置UI状态

        该方法在分割操作完成后被调用，
        恢复按钮和其他UI元素的正常状态。
        """
        self.split_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.file_selector.select_button.config(state=tk.NORMAL)

    def update_progress(self, message, value):
        """更新进度信息

        该方法更新进度标签和进度条的显示内容。

        Args:
            message (str): 要显示的进度信息
            value (int): 进度条的值（0-100）
        """
        self.progress_var.set(message)
        self.progress_bar['value'] = value
        self.root.update_idletasks()

    def log_message(self, message):
        """记录日志消息

        该方法将消息添加到日志显示区域，自动添加时间戳。

        Args:
            message (str): 要记录的消息
        """
        import datetime
        # 获取当前时间并格式化
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        # 格式化日志条目
        log_entry = f"[{timestamp}] {message}\n"

        # 在主线程中更新UI（因为这是在后台线程中调用的）
        self.root.after(0, lambda entry=log_entry: self._add_log_entry(entry))

    def _add_log_entry(self, entry):
        """添加日志条目（在主线程中执行）

        该方法在主线程中向日志文本框添加条目，
        并自动滚动到底部。

        Args:
            entry (str): 要添加的日志条目
        """
        # 插入日志条目到文本框末尾
        self.log_text.insert(tk.END, entry)
        # 自动滚动到最新条目
        self.log_text.see(tk.END)
        # 更新界面
        self.root.update_idletasks()

    def setup_window_icon(self):
        """设置窗口图标

        该方法加载并设置应用程序的图标，支持开发环境和打包后的环境。
        """
        try:
            # 获取图标文件路径
            icon_path = Path(__file__).resolve().parents[1] / 'icons' / 'DocumentSplitter.png'

            # 检查图标文件是否存在
            if icon_path.exists():
                # 加载图标
                self.icon_image = tk.PhotoImage(file=str(icon_path))

                # 设置窗口图标
                self.root.iconphoto(True, self.icon_image)
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"加载图标失败: {e}")

    def center_window(self):
        """将窗口居中显示在屏幕上

        该方法计算屏幕中心位置并将窗口移动到该位置。
        """
        # 更新窗口以确保几何信息正确
        self.root.update_idletasks()

        # 获取窗口的宽度和高度
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 获取屏幕的宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算居中坐标
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def run(self):
        """运行应用程序

        启动Tkinter主事件循环，显示界面并响应用户操作。
        """
        self.root.mainloop()