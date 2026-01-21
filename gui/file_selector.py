"""
文件选择组件

该组件提供了一个用户界面，允许用户浏览并选择要分割的文档文件。
它包含一个选择按钮和一个显示所选文件路径的标签。
支持点击选择和拖拽文件两种方式。
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pathlib import Path


class FileSelector(ttk.Frame):
    """文件选择组件

    该组件继承自ttk.Frame，提供了一个标准的文件选择界面，
    包括一个按钮用于打开文件对话框和一个标签用于显示选中的文件路径。
    支持点击选择和拖拽文件两种方式。
    """

    def __init__(self, parent, **kwargs):
        """初始化文件选择组件

        Args:
            parent: 父级组件
            **kwargs: 传递给父类构造函数的其他参数
        """
        super().__init__(parent, **kwargs)

        # 创建一个StringVar变量来存储选中的文件路径
        self.selected_file_path = tk.StringVar()

        # 创建界面组件
        self.create_widgets()

        # 尝试注册拖放功能
        self.setup_drag_and_drop()

    def create_widgets(self):
        """创建界面组件

        该方法创建文件选择按钮和文件路径显示标签，
        并将它们添加到组件中。
        """
        # 创建文件选择按钮
        self.select_button = ttk.Button(
            self,
            text="选择文件",
            command=self.browse_file  # 点击按钮时调用browse_file方法
        )
        # 将按钮放置在左侧，并设置右边距
        self.select_button.pack(side=tk.LEFT, padx=(0, 10))

        # 创建拖放区域容器
        self.drop_frame = ttk.Frame(self)
        self.drop_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 创建文件路径显示标签（也作为拖放区域）
        self.file_label = ttk.Label(
            self.drop_frame,
            textvariable=self.selected_file_path,  # 绑定到文件路径变量
            relief=tk.SUNKEN,  # 设置下沉边框效果
            anchor=tk.W,  # 文本左对齐
            padding=5
        )
        # 将标签放置在左侧，并使其填充剩余空间
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 设置默认提示文本
        if not self.selected_file_path.get():
            self.selected_file_path.set("点击按钮选择文件，或拖拽文件到此处")

    def browse_file(self):
        """浏览并选择文件

        该方法打开文件对话框，让用户选择要分割的文档文件，
        然后将选中的文件路径存储到selected_file_path变量中。
        """
        # 定义支持的文件类型
        filetypes = (
            ('Supported Files', '*.pdf *.docx *.txt'),
            ('PDF files', '*.pdf'),
            ('Word files', '*.docx'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )

        # 打开文件对话框
        filename = filedialog.askopenfilename(
            title='选择要分割的文件',
            initialdir='/',  # 初始目录
            filetypes=filetypes  # 文件类型过滤器
        )

        # 如果用户选择了文件，则更新路径变量
        if filename:
            self.selected_file_path.set(filename)

    def get_selected_file(self):
        """获取选中的文件路径

        Returns:
            str: 选中的文件路径，如果没有选择文件则返回空字符串
        """
        return self.selected_file_path.get()

    def set_selected_file(self, file_path):
        """设置选中的文件路径

        该方法可以直接设置组件中显示的文件路径，
        而不需要用户手动选择。

        Args:
            file_path (str): 要设置的文件路径
        """
        self.selected_file_path.set(file_path)

    def setup_drag_and_drop(self):
        """设置拖放功能

        该方法尝试使用 tkinterdnd2 库注册拖放事件。
        如果库不可用，则跳过拖放功能，程序仍可正常使用点击选择。
        """
        try:
            from tkinterdnd2 import DND_FILES

            # 获取根窗口
            root = self.winfo_toplevel()

            # 检查根窗口是否支持拖放
            if not hasattr(root, 'tkinterdnd2'):
                print("主窗口不支持拖放功能")
                return

            print("正在注册拖放事件...")

            # 为拖放区域注册拖放事件
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)

            print("拖放事件注册成功")

        except ImportError:
            # tkinterdnd2 未安装，拖放功能不可用
            print("提示：安装 tkinterdnd2 库可启用拖拽文件功能")
            print("安装命令：pip install tkinterdnd2")
        except Exception as e:
            # 其他错误，不影响主功能
            print(f"拖放功能初始化失败：{e}")
            import traceback
            traceback.print_exc()

    def on_drag_enter(self, event):
        """拖拽进入时的视觉反馈

        Args:
            event: 拖拽事件对象
        """
        self.file_label.config(relief=tk.RAISED, background="#e8f4f8")

    def on_drag_leave(self, event):
        """拖拽离开时的视觉反馈

        Args:
            event: 拖拽事件对象
        """
        self.file_label.config(relief=tk.SUNKEN, background="")

    def on_drop(self, event):
        """处理文件拖放事件

        Args:
            event: 拖拽事件对象，包含拖放的文件路径
        """
        # 获取拖放的文件路径
        files = event.data

        # 处理 Windows 路径格式（可能包含花括号）
        if files.startswith('{') and files.endswith('}'):
            files = files[1:-1]

        # 分割多个文件（如果用户拖放了多个）
        file_list = files.split()

        # 只处理第一个文件
        if file_list:
            file_path = file_list[0].strip()

            # 验证文件是否存在
            if Path(file_path).exists():
                # 验证文件类型
                file_ext = Path(file_path).suffix.lower()
                supported_extensions = ['.pdf', '.docx', '.txt']

                if file_ext in supported_extensions:
                    self.selected_file_path.set(file_path)
                    # 触发变量变化事件，通知主窗口
                    self.selected_file_path.trace_vwrite('w', lambda *args: None)
                else:
                    # 不支持的文件类型
                    self.selected_file_path.set(f"不支持的文件类型：{file_ext}")
            else:
                # 文件不存在
                self.selected_file_path.set("文件不存在")

        # 恢复默认样式
        self.file_label.config(relief=tk.SUNKEN, background="")