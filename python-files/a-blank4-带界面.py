import os
import tkinter as tk
from tkinter import filedialog, messagebox

def reorganize_spray_codes(input_file, output_file, n, column_size, blank_count):
    """
    重组喷码数据函数
    参数:
        input_file: 输入文件路径
        output_file: 输出文件路径
        n: 每行产品数量
        column_size: 每列产品数量
        blank_count: 卷前的空标数
    """
    try:
        # 读取原始数据
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        total_lines = len(lines)
        print(f"总行数: {total_lines}")
        
        # 计算完整循环次数和剩余数量
        full_cycles = total_lines // (column_size * n)
        remainder = total_lines % (column_size * n)
        
        reorganized_lines = []
        
               # 处理完整循环部分
        for cycle in range(full_cycles):
            start_idx = cycle * column_size * n
            # 计算原数据中的逗号数量（假设第一行数据具有代表性）
            comma_count = lines[0].count(',') if lines else 0
            # 创建逗号字符串（用空格分隔的逗号）
            comma_str = ' ,' * comma_count
            # 在每列开始前添加逗号字符串
            reorganized_lines.extend([comma_str] * blank_count)
            for row in range(column_size):
                for col in range(n):
                    idx = start_idx + col * column_size + row
                    reorganized_lines.append(lines[idx])

        # 处理剩余部分
        if remainder > 0:
            start_idx = full_cycles * column_size * n
            # 计算需要补齐的空格数量
            padding = (column_size * n - remainder) % (column_size * n)
            # 计算原数据中的逗号数量
            comma_count = lines[0].count(',') if lines else 0
            comma_str = ' ,' * comma_count
            # 用逗号字符串补齐
            padded_lines = lines[start_idx:] + [comma_str] * padding
            
            # 处理补齐后的数据
            # 在每列开始前添加逗号字符串
            reorganized_lines.extend([comma_str] * blank_count)
            for row in range(column_size):
                for col in range(n):
                    idx = col * column_size + row
                    if idx < len(padded_lines):
                        reorganized_lines.append(padded_lines[idx])
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in reorganized_lines:
                f.write(line + '\n')
        
        print(f"重组完成! 结果已保存到: {output_file}")
        print(f"重组后总行数: {len(reorganized_lines)}")
        
        # 验证处理是否正确
        padding = (column_size * n - remainder) % (column_size * n) if remainder > 0 else 0
        expected_lines = total_lines + padding + (full_cycles + (1 if remainder > 0 else 0)) * blank_count
        if expected_lines == len(reorganized_lines):
            print("验证成功: 重组后行数与预期行数相同")
            
            # 验证数据内容是否一致(忽略补齐的空行)
            original_set = set(lines)
            # 只比较非空且不是新增的逗号字符串行
            reorganized_set = set(
                line for line in reorganized_lines 
                if line and not line.startswith(' ,') and line in original_set
            )
            
            if len(original_set) == len(reorganized_set):
                print("验证成功: 重组后数据内容与原始数据相同(忽略空行和新增行)")
            else:
                missing = original_set - reorganized_set
                print(f"验证失败: 缺少以下原始数据内容: {missing}")
        
        return True
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_reorganization():
    input_file = input_entry.get()
    output_file = output_entry.get()
    try:
        n = int(n_entry.get())
        column_size = int(column_size_entry.get())
        blank_count = int(blank_count_entry.get())
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", f"输入文件 '{input_file}' 不存在")
            return
            
        if reorganize_spray_codes(input_file, output_file, n, column_size, blank_count):
            messagebox.showinfo("成功", "处理完成!")
        else:
            messagebox.showerror("错误", "处理失败")
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字参数")

# 创建主窗口
root = tk.Tk()
root.title("喷码数据重组工具")

# 创建输入组件
tk.Label(root, text="输入文件:").grid(row=0, column=0, sticky='e')
input_entry = tk.Entry(root, width=40)
input_entry.grid(row=0, column=1)
tk.Button(root, text="浏览...", command=lambda: input_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2)

tk.Label(root, text="输出文件:").grid(row=1, column=0, sticky='e')
output_entry = tk.Entry(root, width=40)
output_entry.grid(row=1, column=1)
tk.Button(root, text="浏览...", command=lambda: output_entry.insert(0, filedialog.asksaveasfilename())).grid(row=1, column=2)

tk.Label(root, text="每行产品数量:").grid(row=2, column=0, sticky='e')
n_entry = tk.Entry(root)
n_entry.grid(row=2, column=1)

tk.Label(root, text="每列产品数量:").grid(row=3, column=0, sticky='e')
column_size_entry = tk.Entry(root)
column_size_entry.grid(row=3, column=1)

tk.Label(root, text="卷前的空标数:").grid(row=4, column=0, sticky='e')
blank_count_entry = tk.Entry(root)
blank_count_entry.grid(row=4, column=1)

# 运行按钮
tk.Button(root, text="开始处理", command=run_reorganization).grid(row=5, column=1, pady=10)

if __name__ == "__main__":
    root.mainloop()