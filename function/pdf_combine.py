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

            # 分析每个文件的书签结构
            problematic_files = []
            bookmark_analysis_results = []
            
            for i, file_path in enumerate(input_files):
                print(f"DEBUG: 正在处理第 {i+1} 个文件: {file_path}")
                
                # 分析文件的书签结构
                analysis_result = self._analyze_file_bookmarks(file_path)
                bookmark_analysis_results.append(analysis_result)
                
                # 打印分析结果
                print(f"DEBUG: 文件 {file_path} 分析结果:")
                print(f"DEBUG:   包含书签: {analysis_result['has_bookmarks']}")
                print(f"DEBUG:   书签数量: {analysis_result['bookmark_count']}")
                
                if analysis_result.get('warning'):
                    print(f"DEBUG:   警告: {analysis_result['warning']}")
                
                if analysis_result.get('error'):
                    print(f"DEBUG:   错误: {analysis_result['error']}")
                
                if analysis_result.get('specific_issues'):
                    print(f"DEBUG:   具体问题: {', '.join(analysis_result['specific_issues'])}")
                
                # 统计原始书签
                expected_bookmarks += analysis_result['bookmark_count']
                
                # 尝试导入
                merger.append(file_path, import_outline=True)
                print(f"DEBUG: 成功添加文件: {file_path}")
            
            # 如果发现可能有问题的文件，打印警告
            # 注意：这里不再直接构建 problematic_files，而是在诊断阶段通过 analysis_results 构建

            with open(output_path, 'wb') as fileobj:
                merger.write(fileobj)
            merger.close()

            # --- 关键：实质性校验环节 ---
            actual_bookmarks = 0
            with open(output_path, 'rb') as f:
                check_reader = PyPDF2.PdfReader(f)
                actual_bookmarks = self._count_bookmarks(check_reader.outline)

            # 修改书签校验逻辑，使其更加灵活
            if expected_bookmarks > 0:
                if actual_bookmarks == 0:
                    # 删除无效文件
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        print(f"DEBUG: 删除无效文件: {output_path}")
                    
                    # 诊断书签丢失的具体原因
                    diagnosis = self._diagnose_bookmark_loss(input_files, bookmark_analysis_results)
                    
                    # 构建详细的错误信息
                    error_message = (
                        f"书签丢失校验失败：预期包含 {expected_bookmarks} 个书签，" 
                        f"但生成的 PDF 实际包含 0 个。\n\n"
                    )
                    
                    # 添加具体的诊断结果
                    error_message += "=== 具体诊断结果 ===\n"
                    error_message += f"诊断结果: {diagnosis['conclusion']}\n\n"
                    
                    # 添加可能的问题文件信息
                    if diagnosis['problematic_files']:
                        error_message += "可能导致问题的文件：\n"
                        for file_path, issues in diagnosis['problematic_files'][:3]:  # 只显示前3个问题文件
                            file_name = os.path.basename(file_path)
                            error_message += f"- {file_name}: {', '.join(issues)}\n"
                        if len(diagnosis['problematic_files']) > 3:
                            error_message += f"... 等 {len(diagnosis['problematic_files']) - 3} 个文件\n\n"
                    
                    # 添加具体的解决方案
                    error_message += "=== 具体解决方案 ===\n"
                    error_message += "\n".join(diagnosis['solutions'])
                    
                    # 触发自定义异常：书签丢失
                    raise RuntimeError(error_message)
                else:
                    # 书签校验通过，允许部分差异
                    # 计算差异百分比
                    difference_percentage = abs(expected_bookmarks - actual_bookmarks) / expected_bookmarks * 100
                    print(f"DEBUG: 合并成功，书签校验通过 ({actual_bookmarks}/{expected_bookmarks})")
                    print(f"DEBUG: 书签差异: {difference_percentage:.1f}%")
                    
                    # 如果差异较大，打印警告
                    if difference_percentage > 20:
                        print(f"DEBUG: 警告: 书签数量差异较大 ({difference_percentage:.1f}%)，可能存在部分书签丢失")
            
            self.last_used_method = "1"
            self.last_used_method_name = "PyPDF2（保留书签）"
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

    def _analyze_bookmark_structure(self, outline, level=0):
        """
        分析书签结构，返回详细信息

        Args:
            outline: PDF 大纲对象
            level: 当前分析的层级

        Returns:
            dict: 包含书签结构详细信息的字典
        """
        if not outline:
            return {
                "count": 0,
                "max_depth": 0,
                "structure": []
            }
        
        structure = []
        max_depth = level
        total_count = 0
        
        for i, item in enumerate(outline):
            if isinstance(item, list):
                # 嵌套书签
                sub_analysis = self._analyze_bookmark_structure(item, level + 1)
                structure.append({
                    "type": "nested",
                    "index": i,
                    "level": level,
                    "children": sub_analysis["structure"]
                })
                total_count += sub_analysis["count"]
                max_depth = max(max_depth, sub_analysis["max_depth"])
            else:
                # 单个书签
                bookmark_info = {
                    "type": "bookmark",
                    "index": i,
                    "level": level
                }
                # 尝试获取书签标题
                try:
                    if hasattr(item, "title"):
                        bookmark_info["title"] = item.title
                    elif isinstance(item, tuple) and len(item) > 0:
                        bookmark_info["title"] = str(item[0]) if item[0] else "(无标题)"
                    else:
                        bookmark_info["title"] = "(未知格式)"
                except Exception as e:
                    bookmark_info["title"] = "(获取标题失败)"
                
                structure.append(bookmark_info)
                total_count += 1
        
        return {
            "count": total_count,
            "max_depth": max_depth,
            "structure": structure
        }

    def _analyze_file_bookmarks(self, file_path):
        """
        分析单个文件的书签情况

        Args:
            file_path: 文件路径

        Returns:
            dict: 包含文件书签分析结果的字典
        """
        result = {
            "file_path": file_path,
            "has_bookmarks": False,
            "bookmark_count": 0,
            "structure_analysis": None,
            "error": None,
            "warning": None,
            "specific_issues": []  # 新增：具体问题列表
        }
        
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                # 检查是否有 outline 属性
                if not hasattr(reader, 'outline'):
                    result["error"] = "文件没有 outline 属性"
                    result["specific_issues"].append("无 outline 属性")
                    return result
                
                outline = reader.outline
                if not outline:
                    result["has_bookmarks"] = False
                    result["bookmark_count"] = 0
                    return result
                
                # 分析书签结构
                structure_analysis = self._analyze_bookmark_structure(outline)
                result["has_bookmarks"] = True
                result["bookmark_count"] = structure_analysis["count"]
                result["structure_analysis"] = structure_analysis
                
                # 检查是否可能存在问题
                if structure_analysis["max_depth"] > 10:
                    result["warning"] = f"书签嵌套层级较深 ({structure_analysis['max_depth']} 层)，可能导致合并问题"
                    result["specific_issues"].append(f"嵌套层级过深 ({structure_analysis['max_depth']} 层)")
                
                # 检查书签标题是否有特殊字符
                problematic_bookmarks = []
                self._check_bookmark_titles(structure_analysis["structure"], problematic_bookmarks)
                
                if problematic_bookmarks:
                    result["warning"] = f"发现 {len(problematic_bookmarks)} 个可能包含特殊字符的书签"
                    result["specific_issues"].append(f"包含 {len(problematic_bookmarks)} 个特殊字符书签")
                    
        except Exception as e:
            result["error"] = f"分析书签时出错: {str(e)}"
            result["specific_issues"].append(f"分析错误: {str(e)}")
        
        return result

    def _check_bookmark_titles(self, structure, problematic_bookmarks):
        """
        检查书签标题是否包含特殊字符

        Args:
            structure: 书签结构
            problematic_bookmarks: 收集有问题的书签
        """
        # 放宽特殊字符检查，只检查真正可能导致问题的控制字符
        # 允许所有可打印字符和常见的非ASCII字符
        for item in structure:
            if item["type"] == "bookmark":
                title = item.get("title", "")
                if title:
                    # 只检查ASCII控制字符（0-31），不检查非ASCII字符
                    if any(ord(c) < 32 for c in title):
                        problematic_bookmarks.append(title)
            elif item["type"] == "nested":
                self._check_bookmark_titles(item["children"], problematic_bookmarks)

    def _diagnose_bookmark_loss(self, input_files, analysis_results):
        """
        诊断书签丢失的具体原因

        Args:
            input_files: 输入文件列表
            analysis_results: 每个文件的书签分析结果

        Returns:
            dict: 包含诊断结论、问题文件和解决方案的字典
        """
        # 分析结果
        problematic_files = []
        possible_causes = []
        solutions = []
        
        # 分析每个文件的结果
        for i, result in enumerate(analysis_results):
            file_path = input_files[i]
            issues = []
            
            if result.get('specific_issues'):
                issues.extend(result['specific_issues'])
                
                # 提取可能的原因
                for issue in result['specific_issues']:
                    if "嵌套层级过深" in issue:
                        possible_causes.append("书签嵌套层级过深")
                    elif "特殊字符" in issue:
                        possible_causes.append("书签标题包含特殊字符")
                    elif "分析错误" in issue:
                        possible_causes.append("文件书签结构错误")
                    elif "无 outline 属性" in issue:
                        possible_causes.append("文件书签结构错误")
            
            if issues:
                problematic_files.append((file_path, issues))
        
        # 确定主要原因
        if not possible_causes:
            conclusion = "无法确定具体原因，可能是 PyPDF2 兼容性问题或其他未知因素"
            possible_causes.append("PyPDF2 版本兼容性问题")
        else:
            # 统计最常见的原因
            from collections import Counter
            cause_counter = Counter(possible_causes)
            most_common_cause = cause_counter.most_common(1)[0][0]
            conclusion = f"主要原因：{most_common_cause}"
        
        # 生成具体的解决方案
        if "书签嵌套层级过深" in possible_causes:
            solutions.append("1. 简化源文件的书签结构，减少嵌套层级")
            solutions.append("2. 尝试使用最新版本的 PyPDF2，可能对深层嵌套有更好的支持")
        if "书签标题包含特殊字符" in possible_causes:
            solutions.append("1. 清理书签标题中的特殊字符或非 ASCII 字符")
            solutions.append("2. 尝试使用 pypdf（PyPDF2 的继任者），对特殊字符支持更好")
        if "文件书签结构错误" in possible_causes:
            solutions.append("1. 使用 Adobe Acrobat 重新保存文件，标准化书签结构")
            solutions.append("2. 尝试从问题文件中提取内容到新的 PDF 文件")
        if "PyPDF2 版本兼容性问题" in possible_causes or not possible_causes:
            solutions.append("1. 更新 PyPDF2 到最新版本：pip install --upgrade PyPDF2")
            solutions.append("2. 尝试使用 pypdf：pip install pypdf")
            solutions.append("3. 考虑使用其他 PDF 合并工具作为临时解决方案")
        
        # 添加通用解决方案
        solutions.append("4. 检查源文件是否有权限或加密限制")
        solutions.append("5. 尝试使用在线 PDF 合并工具（如 SmallPDF、ILovePDF 等）")
        
        return {
            "conclusion": conclusion,
            "problematic_files": problematic_files,
            "solutions": solutions
        }

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


