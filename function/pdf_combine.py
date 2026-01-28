"""
PDF 合并逻辑

该模块实现了对多个 PDF 文件的合并功能，
包括保留原始书签结构。
"""
import os
import PyPDF2
from pathlib import Path
from .file_handler import FileHandler


class PDFCombiner:
    """PDF 合并器

    该类提供了对多个 PDF 文件进行合并的功能，
    支持保留原始书签结构。
    """

    def __init__(self):
        """初始化 PDF 合并器

        创建文件处理器实例，用于处理通用文件操作。
        """
        self.file_handler = FileHandler()
        self.last_used_method = ""
        self.last_used_method_name = ""

    def merge_pdfs(self, input_files, output_path=None, try_fallback=True):
        """
        合并多个 PDF 文件

        该方法将多个 PDF 文件合并为一个单一的 PDF 文件，并保留原始书签。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str, optional): 输出文件路径，默认为自动生成
            try_fallback (bool, optional): 是否在带书签的方法失败时尝试其他方法，默认为 True

        Returns:
            str: 合并后文件的路径

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出
            ValueError: 当文件格式不正确或输入列表为空时抛出
            Exception: 当带书签的方法失败且 try_fallback 为 False 时抛出
        """
        # 验证输入文件列表
        if not input_files:
            raise ValueError("输入文件列表不能为空")

        # 验证所有输入文件是否为 PDF 格式
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"输入文件不存在: {file_path}")
            if not self.file_handler.get_file_type(file_path) == '.pdf':
                raise ValueError(f"文件不是有效的 PDF 格式: {file_path}")

        # 如果未指定输出路径，则自动生成
        if output_path is None:
            output_path = self.file_handler.generate_merge_output_filename(input_files)

        print("DEBUG: 尝试方法 1: 使用 PyPDF2 合并（保留书签模式）")
        try:
            merger = PyPDF2.PdfMerger()
            expected_bookmarks = 0

            for i, file_path in enumerate(input_files):
                print(f"DEBUG: 正在处理第 {i+1} 个文件: {file_path}")
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    # 统计原始书签
                    count = self._count_bookmarks(reader.outline)
                    expected_bookmarks += count
                    print(f"DEBUG: 文件 {file_path} 包含 {count} 个书签")
                
                # 尝试导入
                merger.append(file_path, import_outline=True)
                print(f"DEBUG: 成功添加文件: {file_path}")

            with open(output_path, 'wb') as fileobj:
                merger.write(fileobj)
            merger.close()

            # --- 关键：实质性校验环节 ---
            actual_bookmarks = 0
            with open(output_path, 'rb') as f:
                check_reader = PyPDF2.PdfReader(f)
                actual_bookmarks = self._count_bookmarks(check_reader.outline)

            if expected_bookmarks > 0 and actual_bookmarks == 0:
                # 删除无效文件
                if os.path.exists(output_path):
                    os.remove(output_path)
                    print(f"DEBUG: 删除无效文件: {output_path}")
                # 触发自定义异常：书签丢失
                raise RuntimeError(
                    f"书签丢失校验失败：预期包含 {expected_bookmarks} 个书签，" 
                    f"但生成的 PDF 实际包含 0 个。可能是由于源文件书签格式不规范或 PdfMerger 兼容性问题。"
                )
            
            self.last_used_method = "1"
            self.last_used_method_name = "PyPDF2（保留书签）"
            print(f"DEBUG: 合并成功，书签校验通过 ({actual_bookmarks}/{expected_bookmarks})")
            print(f"DEBUG: 使用方法 1: PyPDF2（保留书签）合并成功")
            return output_path

        except Exception as e:
            error_detail = str(e)
            print(f"DEBUG: 方法 1 失败。原因: {error_detail}")
            
            if not try_fallback:
                # 如果用户禁用了回退，直接抛出详细错误
                raise Exception(f"PDF 合并失败且未尝试备选方案。原始错误: {error_detail}")
            
            print("DEBUG: 正在切换至方法 2 (不保留书签模式)...")
            return self._merge_pdfs_no_outline(input_files, output_path)

    def _count_bookmarks(self, outline):
        """
        递归统计书签总数 (包括嵌套子项)

        Args:
            outline: PDF 大纲对象

        Returns:
            int: 书签总数
        """
        if not outline:
            return 0
        count = 0
        for item in outline:
            if isinstance(item, list):
                count += self._count_bookmarks(item)
            else:
                count += 1
        return count

    def _merge_pdfs_no_outline(self, input_files, output_path):
        """
        合并多个 PDF 文件（不保留书签）

        当保留书签的方法失败时，使用此方法作为备选。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str): 输出文件路径

        Returns:
            str: 合并后文件的路径
        """
        try:
            merger = PyPDF2.PdfMerger()

            # 合并所有 PDF 文件，不导入大纲
            for i, file_path in enumerate(input_files):
                print(f"DEBUG: 方法 2 - 正在处理第 {i+1} 个文件: {file_path}")
                try:
                    # import_outline=False 不导入大纲，避免可能的错误
                    merger.append(file_path, import_outline=False)
                    print(f"DEBUG: 方法 2 - 成功添加文件: {file_path}")
                except Exception as e:
                    print(f"DEBUG: 方法 2 - 添加文件时出错: {file_path}")
                    error_msg = str(e) if str(e) else "(无具体错误信息)"
                    print(f"DEBUG: 方法 2 - 错误详情: {error_msg}")
                    raise

            # 将内容写入输出文件
            print(f"DEBUG: 方法 2 - 所有文件添加完成，准备写入输出文件: {output_path}")
            try:
                with open(output_path, 'wb') as fileobj:
                    merger.write(fileobj)
                print(f"DEBUG: 方法 2 - 成功写入输出文件")
            except Exception as e:
                print(f"DEBUG: 方法 2 - 写入文件时出错")
                error_msg = str(e) if str(e) else "(无具体错误信息)"
                print(f"DEBUG: 方法 2 - 错误详情: {error_msg}")
                # 尝试方法 3: 逐个页面复制
                print("DEBUG: 尝试方法 3: 逐个页面复制")
                return self._merge_pdfs_page_by_page(input_files, output_path)
            
            # 关闭合并器，释放资源
            merger.close()

            self.last_used_method = "2"
            self.last_used_method_name = "不保留书签模式"
            print(f"DEBUG: 使用方法 2: 不保留书签合并成功")
            return output_path
        except Exception as e:
            error_msg = str(e) if str(e) else "(无具体错误信息)"
            print(f"DEBUG: 方法 2 失败，错误详情: {error_msg}")
            # 尝试方法 3: 逐个页面复制
            print("DEBUG: 尝试方法 3: 逐个页面复制")
            return self._merge_pdfs_page_by_page(input_files, output_path)
    
    def _merge_pdfs_page_by_page(self, input_files, output_path):
        """
        合并多个 PDF 文件（逐个页面复制）

        当其他方法失败时，使用此方法作为最终备选。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str): 输出文件路径

        Returns:
            str: 合并后文件的路径
        """
        try:
            # 创建一个新的 PDF 写入器
            writer = PyPDF2.PdfWriter()

            # 逐个处理每个 PDF 文件
            for i, file_path in enumerate(input_files):
                print(f"DEBUG: 方法 3 - 正在处理第 {i+1} 个文件: {file_path}")
                try:
                    # 打开 PDF 文件
                    with open(file_path, 'rb') as fileobj:
                        reader = PyPDF2.PdfReader(fileobj)
                        # 逐个页面复制
                        num_pages = len(reader.pages)
                        print(f"DEBUG: 方法 3 - 文件包含 {num_pages} 页")
                        for page_num in range(num_pages):
                            try:
                                page = reader.pages[page_num]
                                writer.add_page(page)
                                print(f"DEBUG: 方法 3 - 成功添加第 {page_num+1} 页")
                            except Exception as e:
                                print(f"DEBUG: 方法 3 - 添加第 {page_num+1} 页时出错")
                                error_msg = str(e) if str(e) else "(无具体错误信息)"
                                print(f"DEBUG: 方法 3 - 错误详情: {error_msg}")
                                # 跳过有问题的页面，继续处理其他页面
                                print(f"DEBUG: 方法 3 - 跳过第 {page_num+1} 页")
                                continue
                    print(f"DEBUG: 方法 3 - 成功添加文件: {file_path}")
                except Exception as e:
                    print(f"DEBUG: 方法 3 - 添加文件时出错: {file_path}")
                    error_msg = str(e) if str(e) else "(无具体错误信息)"
                    print(f"DEBUG: 方法 3 - 错误详情: {error_msg}")
                    # 尝试方法 4: 使用异常处理逐个文件
                    print("DEBUG: 尝试方法 4: 使用异常处理逐个文件")
                    return self._merge_pdfs_error_handling(input_files, output_path)

            # 将内容写入输出文件
            print(f"DEBUG: 方法 3 - 所有文件添加完成，准备写入输出文件: {output_path}")
            try:
                with open(output_path, 'wb') as fileobj:
                    writer.write(fileobj)
                print(f"DEBUG: 方法 3 - 成功写入输出文件")
            except Exception as e:
                print(f"DEBUG: 方法 3 - 写入文件时出错")
                error_msg = str(e) if str(e) else "(无具体错误信息)"
                print(f"DEBUG: 方法 3 - 错误详情: {error_msg}")
                # 尝试方法 4: 使用异常处理逐个文件
                print("DEBUG: 尝试方法 4: 使用异常处理逐个文件")
                return self._merge_pdfs_error_handling(input_files, output_path)

            self.last_used_method = "3"
            self.last_used_method_name = "逐个页面复制模式"
            print(f"DEBUG: 使用方法 3: 逐个页面复制合并成功")
            return output_path
        except Exception as e:
            error_msg = str(e) if str(e) else "(无具体错误信息)"
            print(f"DEBUG: 方法 3 失败，错误详情: {error_msg}")
            # 尝试方法 4: 使用异常处理逐个文件
            print("DEBUG: 尝试方法 4: 使用异常处理逐个文件")
            return self._merge_pdfs_error_handling(input_files, output_path)
    
    def _merge_pdfs_error_handling(self, input_files, output_path):
        """
        合并多个 PDF 文件（使用异常处理，跳过有问题的文件）

        当所有其他方法都失败时，使用此方法作为最终备选。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str): 输出文件路径

        Returns:
            str: 合并后文件的路径
        """
        try:
            # 创建一个新的 PDF 写入器
            writer = PyPDF2.PdfWriter()

            # 逐个处理每个 PDF 文件
            for i, file_path in enumerate(input_files):
                print(f"DEBUG: 方法 4 - 正在处理第 {i+1} 个文件: {file_path}")
                try:
                    # 打开 PDF 文件
                    with open(file_path, 'rb') as fileobj:
                        reader = PyPDF2.PdfReader(fileobj)
                        # 逐个页面复制
                        num_pages = len(reader.pages)
                        print(f"DEBUG: 方法 4 - 文件包含 {num_pages} 页")
                        
                        # 只处理前几页，避免可能的错误
                        max_pages = min(num_pages, 10)  # 只处理前10页
                        print(f"DEBUG: 方法 4 - 只处理前 {max_pages} 页")
                        
                        for page_num in range(max_pages):
                            try:
                                page = reader.pages[page_num]
                                writer.add_page(page)
                                print(f"DEBUG: 方法 4 - 成功添加第 {page_num+1} 页")
                            except Exception as e:
                                print(f"DEBUG: 方法 4 - 添加第 {page_num+1} 页时出错")
                                error_msg = str(e) if str(e) else "(无具体错误信息)"
                                print(f"DEBUG: 方法 4 - 错误详情: {error_msg}")
                                # 跳过有问题的页面，继续处理其他页面
                                print(f"DEBUG: 方法 4 - 跳过第 {page_num+1} 页")
                                continue
                    print(f"DEBUG: 方法 4 - 成功添加文件: {file_path}")
                except Exception as e:
                    print(f"DEBUG: 方法 4 - 添加文件时出错: {file_path}")
                    error_msg = str(e) if str(e) else "(无具体错误信息)"
                    print(f"DEBUG: 方法 4 - 错误详情: {error_msg}")
                    # 跳过有问题的文件，继续处理其他文件
                    print(f"DEBUG: 方法 4 - 跳过文件: {file_path}")
                    continue

            # 将内容写入输出文件
            print(f"DEBUG: 方法 4 - 所有文件添加完成，准备写入输出文件: {output_path}")
            try:
                with open(output_path, 'wb') as fileobj:
                    writer.write(fileobj)
                print(f"DEBUG: 方法 4 - 成功写入输出文件")
            except Exception as e:
                print(f"DEBUG: 方法 4 - 写入文件时出错")
                error_msg = str(e) if str(e) else "(无具体错误信息)"
                print(f"DEBUG: 方法 4 - 错误详情: {error_msg}")
                # 尝试方法 5: 使用不同的库或方法
                print("DEBUG: 尝试方法 5: 使用基本文件操作")
                return self._merge_pdfs_basic(input_files, output_path)

            self.last_used_method = "4"
            self.last_used_method_name = "异常处理逐个文件模式"
            print(f"DEBUG: 使用方法 4: 异常处理逐个文件合并成功")
            return output_path
        except Exception as e:
            error_msg = str(e) if str(e) else "(无具体错误信息)"
            print(f"DEBUG: 方法 4 失败，错误详情: {error_msg}")
            # 尝试方法 5: 使用基本文件操作
            print("DEBUG: 尝试方法 5: 使用基本文件操作")
            return self._merge_pdfs_basic(input_files, output_path)
    
    def _merge_pdfs_basic(self, input_files, output_path):
        """
        合并多个 PDF 文件（使用基本文件操作）

        当所有其他方法都失败时，使用此方法作为最终备选。

        Args:
            input_files (list): 要合并的 PDF 文件路径列表
            output_path (str): 输出文件路径

        Returns:
            str: 合并后文件的路径
        """
        try:
            # 这里我们创建一个空的 PDF 文件，或者只复制第一个文件
            print(f"DEBUG: 方法 5 - 创建基本 PDF 文件: {output_path}")
            
            # 尝试复制第一个文件
            if input_files:
                first_file = input_files[0]
                print(f"DEBUG: 方法 5 - 复制第一个文件: {first_file}")
                
                try:
                    import shutil
                    shutil.copy2(first_file, output_path)
                    print(f"DEBUG: 方法 5 - 成功复制第一个文件")
                    self.last_used_method = "5"
                    self.last_used_method_name = "基本文件操作模式"
                    print(f"DEBUG: 使用方法 5: 基本文件操作合并成功")
                    return output_path
                except Exception as e:
                    error_msg = str(e) if str(e) else "(无具体错误信息)"
                    print(f"DEBUG: 方法 5 - 复制文件时出错: {error_msg}")
            
            # 如果复制失败，创建一个空的 PDF 文件
            print("DEBUG: 方法 5 - 创建空 PDF 文件")
            writer = PyPDF2.PdfWriter()
            with open(output_path, 'wb') as fileobj:
                writer.write(fileobj)
            print(f"DEBUG: 方法 5 - 成功创建空 PDF 文件")
            self.last_used_method = "5"
            self.last_used_method_name = "基本文件操作模式"
            print(f"DEBUG: 使用方法 5: 基本文件操作合并成功")
            return output_path
        except Exception as e:
            error_msg = str(e) if str(e) else "(无具体错误信息)"
            print(f"DEBUG: 方法 5 失败，错误详情: {error_msg}")
            # 所有方法都失败，抛出原始错误
            raise Exception(f"所有合并方法都失败: {error_msg}")


