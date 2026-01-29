"""
PDF 分割逻辑 - 智能书签保留版
功能：仅保留与当前分割块相关的书签分支，剔除无关内容。
"""
import os
import PyPDF2
from pathlib import Path
from .file_handler import FileHandler



class PDFSplitter:
    def __init__(self):
        self.file_handler = FileHandler()

    def split_by_pages(self, input_path, pages_per_split, output_dir=None, split_mode='fixed'):
        if output_dir is None:
            output_dir = str(Path(input_path).parent)
        
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)

            if split_mode == 'equal':
                pages_per_split = 1 if pages_per_split >= total_pages else (total_pages + pages_per_split - 1) // pages_per_split
            
            output_paths, part_num, current_page = [], 1, 0
            while current_page < total_pages:
                target_end = min(current_page + pages_per_split, total_pages)
                end_page = target_end

                out_p = self.file_handler.generate_output_filename(input_path, part_num, '.pdf')
                self._write_pdf(reader, current_page, end_page, out_p)
                output_paths.append(out_p)
                part_num += 1
                current_page = end_page
        return output_paths

    def split_by_equal_parts(self, input_path, parts_count, output_dir=None):
        return self.split_by_pages(input_path, parts_count, output_dir, split_mode='equal')

    def split_by_chars(self, input_path, chars_per_split, output_dir=None):
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            cumulative_chars = []
            current_total = 0
            for page in reader.pages:
                text = page.extract_text()
                current_total += len(text) if text else 0
                cumulative_chars.append(current_total)

            total_chars = cumulative_chars[-1]
            split_ranges, cur_pos, start_p = [], 0, 0
            while cur_pos < total_chars:
                target = cur_pos + chars_per_split
                end_p = next((i + 1 for i, s in enumerate(cumulative_chars) if s >= target), len(reader.pages))
                split_ranges.append((start_p, end_p))
                cur_pos = cumulative_chars[end_p - 1] if end_p < len(reader.pages) else total_chars
                start_p = end_p

            output_paths = []
            for idx, (s, e) in enumerate(split_ranges, 1):
                out_p = self.file_handler.generate_output_filename(input_path, idx, '.pdf')
                self._write_pdf(reader, s, e, out_p)
                output_paths.append(out_p)
        return output_paths

    def _write_pdf(self, reader, start_page, end_page, output_path):
        writer = PyPDF2.PdfWriter()
        page_map = {old: new for new, old in enumerate(range(start_page, end_page))}
        
        for old_idx in range(start_page, end_page):
            writer.add_page(reader.pages[old_idx])

        # 仅在有大纲时处理书签
        if reader.outline:
            try:
                # 预处理：扁平化大纲，用于快速检查分支是否有效
                self._reconstruct_smart_outline(reader.outline, reader, writer, page_map, start_page, end_page)
            except Exception as e:
                print(f"书签处理警告: {e}")

        with open(output_path, 'wb') as f:
            writer.write(f)

    def _reconstruct_smart_outline(self, outline, reader, writer, page_map, start, end, parent=None):
        """
        智能递归：
        1. 检查当前书签项或其【任意后代】是否在 [start, end) 范围内。
        2. 若无任何后代在范围内，直接舍弃整个分支。
        3. 若有后代在范围内，则保留当前书签作为“路径”。
        """
        last_node = None
        # 预先扫描当前层级及其子列表，确定哪些索引包含有效内容
        for i, item in enumerate(outline):
            if isinstance(item, list):
                # 如果是列表，它是上一个有效 item 的子项
                if last_node:
                    self._reconstruct_smart_outline(item, reader, writer, page_map, start, end, parent=last_node)
                continue

            # 核心检查：该书签本身或其后续紧跟的列表（子项）是否有落在范围内的页面
            # 获取当前项下属的所有子列表（如果有的话）
            sub_outline = outline[i+1] if (i+1 < len(outline) and isinstance(outline[i+1], list)) else []
            
            if self._is_branch_relevant(item, sub_outline, reader, start, end):
                try:
                    orig_p = reader.get_destination_page_number(item)
                    # 如果当前项在范围内，精准跳转；如果只是作为父级路径保留，指向 0
                    target_p = page_map[orig_p] if start <= orig_p < end else 0
                    
                    last_node = writer.add_outline_item(
                        title=item.title,
                        page_number=target_p,
                        parent=parent
                    )
                except:
                    last_node = None
            else:
                last_node = None

    def _is_branch_relevant(self, item, sub_outline, reader, start, end):
        """递归检查整个书签分支是否与当前页面范围有关"""
        # 检查当前项
        try:
            p = reader.get_destination_page_number(item)
            if start <= p < end:
                return True
        except:
            pass
        
        # 检查所有子项
        for sub in sub_outline:
            if isinstance(sub, list):
                if self._is_branch_relevant(None, sub, reader, start, end): return True
            else:
                try:
                    p = reader.get_destination_page_number(sub)
                    if start <= p < end: return True
                except:
                    continue
        return False