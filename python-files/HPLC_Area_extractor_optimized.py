#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPLC Area Extractor - Optimized for Online EXE Conversion
Dependencies: openpyxl
"""

# Import required modules
import glob
import os
import sys
import re

# Try to import openpyxl, provide helpful error message if missing
try:
    from openpyxl import Workbook
except ImportError:
    print("Error: openpyxl package is required but not found.")
    print("Please install it using: pip install openpyxl")
    input("Press Enter to exit...")
    sys.exit(1)

def natural_sort_key(s):
    """将字符串中的数字部分分离出来，以自然顺序排序"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def find_max_peaks(path, table_name):
    """找到所有文件中的最大峰数"""
    max_peaks = 0
    txt_files = glob.glob(os.path.join(path, '*.txt'))
    
    if not txt_files:
        print(f"Warning: No .txt files found in {path}")
        return 0
    
    for file in txt_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for j, line in enumerate(lines):
                    if table_name in line:
                        if j + 1 < len(lines):
                            num_peaks = int(lines[j+1].split()[-1])
                            if num_peaks > max_peaks:
                                max_peaks = num_peaks
                        break
        except Exception as e:
            print(f"Warning: Error reading file {file}: {e}")
            continue
    
    return max_peaks

def extract_area_by_peak_column(path, table_name):
    """提取峰面积数据并生成Excel文件"""
    print(f"Processing files in: {path}")
    print(f"Looking for table: {table_name}")
    
    max_peaks = find_max_peaks(path, table_name)
    if max_peaks == 0:
        print("No peaks found or no matching table name.")
        return False
    
    print(f"Maximum peaks found: {max_peaks}")
    
    headers = ["file name"] + [f"Peak# {i+1}" for i in range(max_peaks)]
    data = []

    txt_files = glob.glob(os.path.join(path, '*.txt'))
    processed_files = 0
    
    for file in txt_files:
        file_name = os.path.basename(file).replace('.txt', '')
        row = [file_name]
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                area_index = None
                num_peaks = 0
                
                for j, line in enumerate(lines):
                    if table_name in line:
                        if j + 1 < len(lines):
                            num_peaks = int(lines[j+1].split()[-1])
                        if j + 2 < len(lines):
                            headers_line = lines[j+2].split('\t')
                            if "Area" in headers_line:
                                area_index = headers_line.index("Area")
                        break
                
                if area_index is not None:
                    for k in range(j+3, min(j+3+num_peaks, len(lines))):
                        line_parts = lines[k].split('\t')
                        if area_index < len(line_parts):
                            value = line_parts[area_index].strip()
                            # 将字符串转换为数字，如果可能的话
                            try:
                                if value.isdigit():
                                    value = int(value)
                                elif value.replace('.', '', 1).isdigit():
                                    value = float(value)
                            except:
                                pass  # Keep as string if conversion fails
                            row.append(value)
                        else:
                            row.append('')
                    
                    # 填充空值以匹配最大峰数
                    while len(row) < max_peaks + 1:  # +1 是因为第一列是文件名
                        row.append('')
                else:
                    print(f"Warning: Area column not found in {file}")
                    # 填充空值
                    while len(row) < max_peaks + 1:
                        row.append('')
                
                data.append(row)
                processed_files += 1
                
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue

    if not data:
        print("No data extracted from files.")
        return False
    
    print(f"Processed {processed_files} files successfully.")
    
    # 使用自定义的自然排序键
    data.sort(key=lambda x: natural_sort_key(x[0]))

    # 创建Excel文件
    try:
        wb = Workbook()
        ws = wb.active
        ws.append(headers)  # 写入表头
        for row in data:
            ws.append(row)  # 写入数据行

        # 保存数据到 xlsx 文件
        xlsx_file_path = os.path.join(path, 'Area_list.xlsx')
        wb.save(xlsx_file_path)
        
        print(f"Extraction and sorting complete. Data saved to: {xlsx_file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        return False

def get_working_directory():
    """获取工作目录，适配不同的运行环境"""
    if getattr(sys, 'frozen', False):
        # 如果是打包的exe文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是普通Python脚本
        return os.path.dirname(os.path.abspath(__file__))

def main():
    """主函数"""
    print("=" * 50)
    print("    HPLC Area Extractor")
    print("=" * 50)
    print()
    
    try:
        # 获取工作目录
        input_path = get_working_directory()
        print(f"Working directory: {input_path}")
        
        # 检查是否有txt文件
        txt_files = glob.glob(os.path.join(input_path, '*.txt'))
        if not txt_files:
            print("No .txt files found in the current directory.")
            print("Please place your HPLC data files (.txt) in the same directory as this program.")
            input("Press Enter to exit...")
            return
        
        print(f"Found {len(txt_files)} .txt files.")
        print()
        
        # 获取用户输入
        while True:
            table_name = input("请输入要定位的Table Name（如：[Peak Table(Detector A)]）: ").strip()
            if table_name:
                break
            print("Table Name不能为空，请重新输入。")
        
        print()
        print("Processing...")
        
        # 执行提取
        success = extract_area_by_peak_column(input_path, table_name)
        
        if success:
            print()
            print("✓ Processing completed successfully!")
            print("✓ Check 'Area_list.xlsx' in the current directory.")
        else:
            print()
            print("✗ Processing failed. Please check your input files and table name.")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your input files and try again.")
    
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 