# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 02:32:01 2025

@author: txwuw
"""

import PyPDF2
import re
import os

def split_pdf_by_tables(input_pdf, output_folder='output'):
    """
    按房屋编码拆分PDF，两个编码之间的所有页面作为一个表格
    并在文件名中添加总页数信息
    参数:
        input_pdf: 输入PDF文件路径
        output_folder: 输出文件夹路径
    """
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 读取PDF文件
    pdf_reader = PyPDF2.PdfReader(input_pdf)
    total_pages = len(pdf_reader.pages)
    
    current_table_pages = []  # 当前表格的页面列表
    current_code = None       # 当前表格的编码
    table_count = 0           # 表格计数器
    
    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        
        # 查找房屋编码
        match = re.search(r'房屋编码[:：]?\s*(\w+)', text)
        if match:
            new_code = match.group(1)
            
            # 如果已经有缓存的表格页面，先保存
            if current_table_pages:
                # 确保有有效的编码
                save_code = current_code if current_code else f"未识别表格_{table_count+1}"
                
                # 创建安全的文件名（添加总页数信息）
                safe_code = re.sub(r'[\\/*?:"<>|]', '_', save_code)
                page_count = len(current_table_pages)
                output_path = os.path.join(output_folder, f"{safe_code}_{page_count}页.pdf")
                
                # 处理可能的重复文件名
                counter = 1
                while os.path.exists(output_path):
                    output_path = os.path.join(output_folder, f"{safe_code}_{page_count}页_{counter}.pdf")
                    counter += 1
                
                # 保存当前表格
                pdf_writer = PyPDF2.PdfWriter()
                for p in current_table_pages:
                    pdf_writer.add_page(p)
                
                with open(output_path, 'wb') as out_file:
                    pdf_writer.write(out_file)
                
                print(f"已保存表格 {table_count+1}: {output_path}")
                table_count += 1
                
                # 重置当前表格
                current_table_pages = []
            
            # 开始新表格
            current_code = new_code
        
        # 将当前页面添加到表格中
        current_table_pages.append(page)
    
    # 处理最后一个表格
    if current_table_pages:
        save_code = current_code if current_code else f"未识别表格_{table_count+1}"
        safe_code = re.sub(r'[\\/*?:"<>|]', '_', save_code)
        page_count = len(current_table_pages)
        output_path = os.path.join(output_folder, f"{safe_code}_{page_count}页.pdf")
        
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_folder, f"{safe_code}_{page_count}页_{counter}.pdf")
            counter += 1
        
        pdf_writer = PyPDF2.PdfWriter()
        for p in current_table_pages:
            pdf_writer.add_page(p)
        
        with open(output_path, 'wb') as out_file:
            pdf_writer.write(out_file)
        
        print(f"已保存表格 {table_count+1}: {output_path}")

# 使用示例
split_pdf_by_tables(
    input_pdf="scan.pdf",
    output_folder="拆分结果"
)