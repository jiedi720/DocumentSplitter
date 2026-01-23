"""
文档分割工具 - 主入口文件

该文件是整个应用程序的启动入口，负责初始化并运行主应用程序。
"""
from gui.main_window import MainApplication

if __name__ == "__main__":
    # 创建主应用程序实例
    app = MainApplication()
    # 运行应用程序主循环
    app.run()