import glob
import os
import sys
import re
from openpyxl import Workbook

def natural_sort_key(s):
    # 将字符串中的数字部分分离出来，以自然顺序排序
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def find_max_peaks(path, table_name):
    max_peaks = 0
    for file in glob.glob(os.path.join(path, '*.txt')):
        with open(file, 'r') as f:
            lines = f.readlines()
            for j, line in enumerate(lines):
                if table_name in line:
                    num_peaks = int(lines[j+1].split()[-1])  # 假设 "# of Peaks" 在指定的 Table Name 的下方一行
                    if num_peaks > max_peaks:
                        max_peaks = num_peaks
                    break
    return max_peaks

def extract_area_by_peak_column(path, table_name):
    max_peaks = find_max_peaks(path, table_name)
    headers = ["file name"] + [f"Peak# {i+1}" for i in range(max_peaks)]
    data = []

    for file in glob.glob(os.path.join(path, '*.txt')):
        file_name = os.path.basename(file).replace('.txt', '')
        row = [file_name]
        with open(file, 'r') as f:
            lines = f.readlines()
            area_index = None
            num_peaks = 0
            for j, line in enumerate(lines):
                if table_name in line:
                    num_peaks = int(lines[j+1].split()[-1])
                    headers_line = lines[j+2].split('\t')
                    area_index = headers_line.index("Area")
                    break
            
            if area_index is not None:
                for k in range(j+3, j+3+num_peaks):
                    value = lines[k].split('\t')[area_index].strip()
                    # 将字符串转换为数字，如果可能的话
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    row.append(value)
                while len(row) < max_peaks + 1:  # +1 是因为第一列是文件名
                    row.append('')
            data.append(row)

    # 使用自定义的自然排序键
    data.sort(key=lambda x: natural_sort_key(x[0]))

    # 创建Excel文件
    wb = Workbook()
    ws = wb.active
    ws.append(headers)  # 写入表头
    for row in data:
        ws.append(row)  # 写入数据行

    # 保存数据到 xlsx 文件
    xlsx_file_path = os.path.join(path, 'Area_list.xlsx')
    wb.save(xlsx_file_path)

    print("Extraction and sorting complete. Data saved to:", xlsx_file_path)

if __name__ == "__main__":
    try:
        # 获取当前可执行文件的路径，并将其作为默认路径
        input_path = os.path.dirname(sys.executable)
        table_name = input("请输入要定位的Table Name（如：[Peak Table(Detector A)]）: ")
        extract_area_by_peak_column(input_path, table_name)
    except Exception as e:
        print("An error occurred:", e)
        input("Press Enter to exit...")
