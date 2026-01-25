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

    def __init__(self, parent, results: List[Dict[str, Optional[str]]], on_close=None):
        """初始化分析结果窗口

        Args:
            parent: 父窗口
            results (List[Dict[str, Optional[str]]]): 分析结果列表
            on_close: 窗口关闭时的回调函数
        """
        self.parent = parent
        self.results = results
        self.on_close = on_close

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("文档信息汇总")
        self.window.geometry("550x400")

        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # 使窗口居中
        self.center_window()

        # 创建界面组件
        self.create_widgets()

        # 显示结果
        self.display_results()

    def on_window_close(self):
        """窗口关闭时的处理"""
        # 调用回调函数
        if self.on_close:
            self.on_close()
        # 销毁窗口
        self.window.destroy()

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

        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建统计信息框架（固定在表格上方）
        stats_frame = ttk.Frame(table_frame)
        stats_frame.pack(fill=tk.X, side=tk.TOP)
        
        # 创建总计行
        total_frame = ttk.Frame(stats_frame)
        total_frame.pack(fill=tk.X)
        
        # 创建总计行标签
        self.total_labels = {
            'filename': ttk.Label(total_frame, text="总计", anchor=tk.CENTER, relief=tk.SOLID, borderwidth=1),
            'file_type': ttk.Label(total_frame, text="-", anchor=tk.CENTER, relief=tk.SOLID, borderwidth=1),
            'char_count': ttk.Label(total_frame, text="0", anchor=tk.E, relief=tk.SOLID, borderwidth=1),
            'page_count': ttk.Label(total_frame, text="0", anchor=tk.CENTER, relief=tk.SOLID, borderwidth=1),
            'file_size': ttk.Label(total_frame, text="0.00 MB", anchor=tk.E, relief=tk.SOLID, borderwidth=1)
        }
        
        # 使用grid布局，精确控制列宽与表格对齐
        # 参考表格列宽：filename=200, file_type=70, char_count=70, page_count=70, file_size=70
        total_frame.columnconfigure(0, minsize=200, weight=0)
        total_frame.columnconfigure(1, minsize=70, weight=0)
        total_frame.columnconfigure(2, minsize=70, weight=0)
        total_frame.columnconfigure(3, minsize=70, weight=0)
        total_frame.columnconfigure(4, minsize=70, weight=0)
        
        # 布局总计行标签
        self.total_labels['filename'].grid(row=0, column=0, sticky=tk.W+tk.E)
        self.total_labels['file_type'].grid(row=0, column=1, sticky=tk.W+tk.E)
        self.total_labels['char_count'].grid(row=0, column=2, sticky=tk.W+tk.E)
        self.total_labels['page_count'].grid(row=0, column=3, sticky=tk.W+tk.E)
        self.total_labels['file_size'].grid(row=0, column=4, sticky=tk.W+tk.E)

        # 创建表格
        columns = ('filename', 'file_type', 'char_count', 'page_count', 'file_size')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        # 排序状态
        self.sort_column = None
        self.sort_order = 'ascending'  # ascending 或 descending

        # 设置列标题和排序功能
        self.tree.heading('filename', text='文件名', command=lambda: self.sort_by_column('filename'))
        self.tree.heading('file_type', text='文件类型', command=lambda: self.sort_by_column('file_type'))
        self.tree.heading('char_count', text='字符数', command=lambda: self.sort_by_column('char_count'))
        self.tree.heading('page_count', text='页数', command=lambda: self.sort_by_column('page_count'))
        self.tree.heading('file_size', text='文件大小', command=lambda: self.sort_by_column('file_size'))

        # 设置列宽和对齐方式
        self.tree.column('filename', width=200, minwidth=200, stretch=False, anchor=tk.W)
        self.tree.column('file_type', width=70, minwidth=60, stretch=False, anchor=tk.CENTER)
        self.tree.column('char_count', width=70, minwidth=60, stretch=False, anchor=tk.E)
        self.tree.column('page_count', width=70, minwidth=60, stretch=False, anchor=tk.CENTER)
        self.tree.column('file_size', width=70, minwidth=60, stretch=False, anchor=tk.E)

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
            command=self.on_window_close
        )
        close_button.pack(pady=(10, 0))

    def display_results(self):
        """显示分析结果，包括统计信息"""
        # 计算统计信息
        total_chars = 0
        total_pages = 0
        total_size_mb = 0.0
        
        for result in self.results:
            # 计算总字符数
            char_count_str = result.get('char_count', '')
            if char_count_str.isdigit() or (char_count_str and char_count_str.replace(',', '').isdigit()):
                # 移除千位分隔符
                clean_chars = char_count_str.replace(',', '')
                total_chars += int(clean_chars)
            
            # 计算总页数
            page_count_str = result.get('page_count', '')
            if page_count_str.isdigit():
                total_pages += int(page_count_str)
            
            # 计算总大小
            file_size_str = result.get('file_size', '')
            if file_size_str and 'MB' in file_size_str:
                try:
                    # 提取数字部分
                    size_mb = float(''.join(c for c in file_size_str if c.isdigit() or c == '.'))
                    total_size_mb += size_mb
                except ValueError:
                    pass
        
        # 格式化统计结果
        total_char_str = f"{total_chars:,}" if total_chars > 0 else "0"
        total_page_str = f"{total_pages:,}" if total_pages > 0 else "0"
        total_size_str = f"{total_size_mb:.2f} MB" if total_size_mb > 0 else "0.00 MB"
        
        # 更新固定统计行的标签文本
        self.total_labels['char_count'].config(text=total_char_str)
        self.total_labels['page_count'].config(text=total_page_str)
        self.total_labels['file_size'].config(text=total_size_str)
        
        # 插入实际数据
        for result in self.results:
            # 确保所有必需的键都存在
            filename = result.get('filename', '')
            file_type = result.get('file_type', '')
            char_count = result.get('char_count', '')
            page_count = result.get('page_count', '')
            file_size = result.get('file_size', '')
            
            self.tree.insert(
                '',
                tk.END,
                values=(
                    filename,
                    file_type,
                    char_count,
                    page_count,
                    file_size
                )
            )

    def sort_by_column(self, col):
        """按列排序
        
        Args:
            col: 要排序的列名
        """
        # 获取所有项目
        items = self.tree.get_children('')
        
        # 准备排序数据
        data = []
        for item in items:
            values = self.tree.item(item, 'values')
            # 根据列名获取对应的值
            if col == 'filename':
                value = values[0]
            elif col == 'file_type':
                value = values[1]
            elif col == 'char_count':
                # 尝试将字符数转换为整数进行排序
                try:
                    # 移除千位分隔符和非数字字符
                    clean_value = ''.join(c for c in values[2] if c.isdigit())
                    value = int(clean_value) if clean_value else 0
                except:
                    value = values[2]
            elif col == 'page_count':
                # 尝试将页数转换为整数进行排序
                try:
                    value = int(values[3]) if values[3].isdigit() else 0
                except:
                    value = values[3]
            elif col == 'file_size':
                # 尝试将文件大小转换为浮点数进行排序
                try:
                    # 提取数字部分
                    clean_value = ''.join(c for c in values[4] if c.isdigit() or c == '.')
                    value = float(clean_value) if clean_value else 0.0
                except:
                    value = values[4]
            else:
                value = ''
            
            data.append((value, item))
        
        # 切换排序顺序
        if self.sort_column == col:
            self.sort_order = 'descending' if self.sort_order == 'ascending' else 'ascending'
        else:
            self.sort_order = 'ascending'
            self.sort_column = col
        
        # 排序
        if self.sort_order == 'ascending':
            data.sort(key=lambda x: x[0])
        else:
            data.sort(key=lambda x: x[0], reverse=True)
        
        # 重新排列项目
        for i, (_, item) in enumerate(data):
            self.tree.move(item, '', i)

    def show(self):
        """显示窗口"""
        self.window.mainloop()