import os
import csv
import glob

def process_csv_file(file_path):
    # 读取原始文件
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    
    if not rows:
        return
    
    # 获取标题行
    headers = rows[0]
    
    # 确定要保留的列索引
    keep_columns = []
    target_headers = ['date', 'amount', 'memo', 'category', 'account']
    
    for target in target_headers:
        found = False
        # 检查是否有多个同名列
        indices = [i for i, h in enumerate(headers) if h.lower() == target]
        
        if indices:
            # 对于category，选择有信息的那一列
            if target == 'category' and len(indices) > 1:
                for idx in indices:
                    # 检查该列是否有非空数据
                    for row in rows[1:]:
                        if len(row) > idx and row[idx].strip():
                            keep_columns.append(idx)
                            found = True
                            break
                    if found:
                        break
            else:
                keep_columns.append(indices[0])
                found = True
        
        if not found:
            print(f"警告: 文件 {file_path} 中未找到列 '{target}'")
    
    # 处理数据行
    processed_rows = []
    for row in rows:
        # 只保留需要的列
        processed_row = []
        for idx in keep_columns:
            if idx < len(row):
                processed_row.append(row[idx].strip())
            else:
                processed_row.append('')
        processed_rows.append(processed_row)
    
    # 格式化内容
    # 标题首字母大写
    if processed_rows:
        processed_rows[0] = [h.capitalize() for h in processed_rows[0]]
    
    # 确保我们有需要的列
    if len(processed_rows[0]) < 5:
        print(f"警告: 文件 {file_path} 处理后列数不足5列")
        return
    
    # 将category和account内容转为小写
    category_idx = None
    account_idx = None
    
    for i, header in enumerate(processed_rows[0]):
        if header.lower() == 'category':
            category_idx = i
        elif header.lower() == 'account':
            account_idx = i
    
    for row in processed_rows[1:]:
        if category_idx is not None and category_idx < len(row):
            row[category_idx] = row[category_idx].lower()
        if account_idx is not None and account_idx < len(row):
            row[account_idx] = row[account_idx].lower()
    
    # 写入新文件
    output_path = os.path.splitext(file_path)[0] + '_processed.csv'
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(processed_rows)
    
    print(f"已处理文件: {file_path} -> {output_path}")

def process_folder(folder_path):
    # 查找文件夹中的所有CSV文件
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    for csv_file in csv_files:
        # 跳过已处理的文件
        if '_processed' in csv_file:
            continue
        try:
            process_csv_file(csv_file)
        except Exception as e:
            print(f"处理文件 {csv_file} 时出错: {str(e)}")

if __name__ == '__main__':
    folder_path = input("请输入文件夹路径: ")
    if os.path.isdir(folder_path):
        process_folder(folder_path)
    else:
        print("错误: 指定的路径不是一个有效的文件夹")