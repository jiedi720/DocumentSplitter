"""
测试拖拽文件修复功能的脚本
"""
import os
from pathlib import Path

def test_path_processing():
    """测试路径处理逻辑"""
    print("测试路径处理逻辑...")
    
    # 测试不同类型的路径格式
    test_paths = [
        r"C:\Users\test\Documents\file.pdf",  # 正常路径
        r"{C:\Users\test\Documents\file with spaces.pdf}",  # 带花括号的路径
        r'"C:\Users\test\Documents\file with spaces.pdf"',  # 带双引号的路径
        r"'C:\Users\test\Documents\file with spaces.pdf'",  # 带单引号的路径
    ]
    
    for path_str in test_paths:
        print(f"\n测试路径: {path_str}")
        
        # 模拟处理逻辑
        processed_path = path_str
        
        # 移除花括号
        if processed_path.startswith('{') and processed_path.endswith('}'):
            processed_path = processed_path[1:-1]
            
        # 移除引号
        processed_path = processed_path.strip('"\'')

        print(f"处理后路径: {processed_path}")
        
        # 尝试解析为Path对象
        try:
            normalized_path = Path(processed_path).resolve()
            final_path = str(normalized_path)
            print(f"规范化路径: {final_path}")
        except Exception as e:
            print(f"路径规范化失败: {e}")

if __name__ == "__main__":
    test_path_processing()