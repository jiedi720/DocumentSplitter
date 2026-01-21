"""
文档分析结果展示窗口

该模块用于展示文档分析的结果，以表格形式呈现文档的元数据信息。
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional


class AnalysisResultWindow:
    """文档分析结果展示窗口类

    以表格形式展示文档的元数据信息，包括文件名、字符数和页数。
    """

    def __init__(self, parent, results: List[Dict[str, Optional[str]]]):
        """初始化分析结果窗口

        Args:
            parent: 父窗口
            results (List[Dict[str, Optional[str]]]): 分析结果列表
        """
        self.parent = parent
        self.results = results

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("文档信息汇总")
        self.window.geometry("600x400")

        # 使窗口居中
        self.center_window()

        # 创建界面组件
        self.create_widgets()

        # 显示结果
        self.display_results()

    def center_window(self):
        """将窗口居中显示在屏幕上"""
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标题标签
        title_label = ttk.Label(
            main_frame,
            text="文档信息汇总",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格
        columns = ('filename', 'char_count', 'page_count')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        # 设置列标题
        self.tree.heading('filename', text='文件名')
        self.tree.heading('char_count', text='字符数')
        self.tree.heading('page_count', text='页数')

        # 设置列宽和对齐方式
        self.tree.column('filename', width=250, anchor=tk.W)
        self.tree.column('char_count', width=100, anchor=tk.E)
        self.tree.column('page_count', width=80, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 布局表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建关闭按钮
        close_button = ttk.Button(
            main_frame,
            text="关闭",
            command=self.window.destroy
        )
        close_button.pack(pady=(10, 0))

    def display_results(self):
        """显示分析结果"""
        for result in self.results:
            self.tree.insert(
                '',
                tk.END,
                values=(
                    result['filename'],
                    result['char_count'],
                    result['page_count']
                )
            )

    def show(self):
        """显示窗口"""
        self.window.mainloop()