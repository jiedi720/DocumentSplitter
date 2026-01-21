"""测试文档分析器功能"""
from function.document_analyzer import DocumentAnalyzer

def test_analyzer():
    """测试文档分析器"""
    analyzer = DocumentAnalyzer()

    print("文档分析器测试")
    print("=" * 50)

    # 测试文件列表（请根据实际情况修改路径）
    test_files = [
        "test.pdf",
        "test.docx",
        "test.txt"
    ]

    for file_path in test_files:
        print(f"\n分析文件: {file_path}")
        result = analyzer.analyze_file(file_path)
        print(f"  文件名: {result['filename']}")
        print(f"  字符数: {result['char_count']}")
        print(f"  页数: {result['page_count']}")

if __name__ == "__main__":
    test_analyzer()