"""测试拖拽功能的简单脚本"""
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

def on_drop(event):
    """处理拖放事件"""
    print(f"原始数据: {event.data}")
    print(f"数据类型: {type(event.data)}")

    files = event.data
    if files.startswith('{') and files.endswith('}'):
        files = files[1:-1]

    file_list = files.split()
    print(f"文件列表: {file_list}")

    if file_list:
        file_path = file_list[0].strip()
        print(f"文件路径: {file_path}")

root = TkinterDnD.Tk()
root.title("拖拽测试")
root.geometry("400x200")

label = tk.Label(root, text="将文件拖拽到这里", relief=tk.SUNKEN, padx=20, pady=20)
label.pack(expand=True, fill=tk.BOTH)

label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', on_drop)

root.mainloop()