import pandas as pd
import os

def find_target_columns(columns):
    """根据关键字查找目标列"""
    column_mapping = {}
    for col in columns:
        col_str = str(col).lower()
        if '钢卷号' in col_str:
            column_mapping[col] = '钢卷号Product ID'
        elif '生产日期' in col_str:
            column_mapping[col] = '生产日期'
        elif '名义' in col_str:
            column_mapping[col] = '名义尺寸（mm）'
        elif '实际' in col_str:
            column_mapping[col] = '实际尺寸（mm）'
        elif '边部' in col_str:
            column_mapping[col] = '边部状态'
        elif '净重' in col_str:
            column_mapping[col] = '净重（kg）'
    return column_mapping

def find_company_name(excel_file, sheet_name):
    """在Excel的整个sheet中查找公司名称，包括前7行"""
    # 读取前10行（通常公司名称会在文件头部）
    header_df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=10)
    
    # 将所有单元格的值转换为字符串并连接
    header_text = ' '.join(header_df.astype(str).values.flatten())
    
    # 添加调试信息
    print(f"\n在{sheet_name}中搜索的文本内容：")
    print(header_text)
    
    # 规范化文本（移除多余的空格和特殊字符）
    header_text = ' '.join(header_text.split())
    
    # 检查中英文公司名称
    if '印尼永旺有限公司' in header_text:
        print(f"找到印尼永旺有限公司，位置：{header_text.find('印尼永旺有限公司')}")
        return '印尼永旺有限公司'
    elif 'Shandong Hongwang Industrial' in header_text:
        print(f"找到山东宏旺实业有限公司（英文名），位置：{header_text.find('Shandong Hongwang Industrial')}")
        return '山东宏旺实业有限公司'
    elif '山东宏旺实业有限公司' in header_text:
        print(f"找到山东宏旺实业有限公司，位置：{header_text.find('山东宏旺实业有限公司')}")
        return '山东宏旺实业有限公司'
    
    # 如果完整名称没找到，尝试查找部分名称
    if 'Shandong Hongwang' in header_text:
        print(f"找到部分匹配：Shandong Hongwang，位置：{header_text.find('Shandong Hongwang')}")
        return '山东宏旺实业有限公司'
    elif '山东宏旺' in header_text:
        print(f"找到部分匹配：山东宏旺，位置：{header_text.find('山东宏旺')}")
        return '山东宏旺实业有限公司'
    elif '宏旺实业' in header_text:
        print(f"找到部分匹配：宏旺实业，位置：{header_text.find('宏旺实业')}")
        return '山东宏旺实业有限公司'
    
    print("未找到任何公司名称匹配")
    return ''

def find_end_row(df):
    """查找数据结束行的索引（合计行或Total行）"""
    for idx, row in df.iterrows():
        # 将行中的所有值转换为字符串并连接
        row_text = ' '.join(str(cell).strip() for cell in row if pd.notna(cell))
        # 检查是否包含"合计"或"Total"
        if '合计' in row_text or 'Total' in row_text:
            print(f"在第 {idx} 行找到终止标记：{row_text}")
            return idx
    return None

def process_excel(input_file, output_file):
    # 创建一个空的DataFrame来存储所有sheet的数据
    all_data = pd.DataFrame()
    
    # 读取Excel文件中的所有sheet
    excel_file = pd.ExcelFile(input_file)
    
    for sheet_name in excel_file.sheet_names:
        print(f"\n处理 {sheet_name} 表...")
        
        # 在整个sheet中查找公司名称
        company_name = find_company_name(input_file, sheet_name)
        print(f"检测到的公司名称：{company_name if company_name else '未检测到公司名称'}")
        
        # 根据公司名称决定跳过的行数
        skip_rows = 9 if company_name == '印尼永旺有限公司' else 7
        print(f"跳过前 {skip_rows} 行")
        
        try:
            # 读取当前sheet，根据公司类型跳过不同行数
            df = pd.read_excel(input_file, sheet_name=sheet_name, skiprows=skip_rows)
            
            # 查找数据结束行（合计行或Total行）
            end_row_index = find_end_row(df)
            
            # 如果找到了结束行，只保留其之前的数据
            if end_row_index is not None:
                df = df.iloc[:end_row_index]
                print(f"在第 {end_row_index} 行找到结束标记，保留之前的数据")
            
            # 查找目标列
            column_mapping = find_target_columns(df.columns)
            
            if not column_mapping:
                print(f"警告：在 {sheet_name} 中未找到任何目标列")
                print("实际列名：", df.columns.tolist())
                continue
            
            # 只选择需要的列
            df_selected = df[list(column_mapping.keys())].copy()
            
            # 重命名列
            df_selected.rename(columns=column_mapping, inplace=True)
            
            # 删除全为空的行
            df_selected.dropna(how='all', inplace=True)
            
            # 添加公司列（确保公司名称不为空字符串）
            if company_name:
                df_selected.insert(0, '公司', company_name)
            else:
                df_selected.insert(0, '公司', '')
            
            # 打印调试信息
            print(f"处理后的数据行数：{len(df_selected)}")
            print(f"处理后的列名：{df_selected.columns.tolist()}")
            print(f"公司列的唯一值：{df_selected['公司'].unique()}")
            
            # 将当前sheet的数据添加到总数据中
            if not df_selected.empty:
                all_data = pd.concat([all_data, df_selected], ignore_index=True)
                print(f"成功处理 {sheet_name} 表，提取了 {len(df_selected)} 行数据")
            
        except Exception as e:
            print(f"警告：处理 {sheet_name} 时出错：{str(e)}")
    
    if not all_data.empty:
        # 打印最终数据的信息
        print(f"\n最终数据统计：")
        print(f"总行数：{len(all_data)}")
        print(f"列名：{all_data.columns.tolist()}")
        print(f"公司列的唯一值：{all_data['公司'].unique()}")
        
        # 将结果保存为Excel文件
        all_data.to_excel(output_file, index=False)
        print(f"\n总共提取了 {len(all_data)} 行数据，已保存到 {output_file}")
        return True
    else:
        print("错误：没有找到任何匹配的数据")
        return False

def get_valid_path(prompt, is_input=True):
    """获取有效的文件路径"""
    while True:
        path = input(prompt).strip()
        
        # 如果是输入文件，检查文件是否存在
        if is_input:
            if not os.path.exists(path):
                print(f"错误：文件 '{path}' 不存在，请重新输入")
                continue
            if not path.lower().endswith('.xlsx'):
                print("错误：输入文件必须是 .xlsx 格式，请重新输入")
                continue
        # 如果是输出文件，检查目录是否存在且可写
        else:
            dir_path = os.path.dirname(path) or '.'
            if not os.path.exists(dir_path):
                print(f"错误：目录 '{dir_path}' 不存在，请重新输入")
                continue
            if not os.access(dir_path, os.W_OK):
                print(f"错误：没有权限写入目录 '{dir_path}'，请重新输入")
                continue
            if not path.lower().endswith('.xlsx'):
                path += '/outputs.xlsx'
        
        return path

def main():
    print("欢迎使用Excel数据提取工具！")
    print("\n请按照提示输入文件路径：")
    
    # 获取输入文件路径
    input_file = get_valid_path("请输入Excel文件路径：")
    
    # 获取输出文件路径
    output_file = get_valid_path("请输入保存结果的文件路径（.xlsx）：", is_input=False)
    
    try:
        print(f"\n开始处理文件：{input_file}")
        if process_excel(input_file, output_file):
            print(f'\n处理完成！数据已保存到 {output_file}')
        else:
            print('\n处理失败：未能提取任何数据')
    except Exception as e:
        print(f'\n处理过程中出现错误：{str(e)}')
    
    input("\n按回车键退出...")

if __name__ == '__main__':
    main()