import os
import re
import sys
from typing import List, Tuple, Dict, Any, Optional

def main():
    should_exit = False
    
    while not should_exit:
        print("请输入要处理的目录路径：")
        target_directory = input().strip()
        
        if not target_directory:
            print("输入不能为空。")
            return
        
        if not os.path.isdir(target_directory):
            print(f"指定的目录不存在: {target_directory}")
            return
        
        process_directory(target_directory)
        
        print("\n请选择操作：")
        print("1. 重新运行程序")
        print("2. 退出程序")
        print("请输入选择:")
        
        choice = input().strip()
        if choice == "1":
            continue
        elif choice == "2":
            should_exit = True
        else:
            print("无效输入，默认退出程序。")
            should_exit = True

def process_directory(directory_path: str):
    print(f"正在处理目录: {directory_path}")
    try:
        file_count = 0
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".ani") or file.endswith(".als"):
                    file_path = os.path.join(root, file)
                    print(f"处理文件: {file_path}")
                    format_file(file_path)
                    file_count += 1
        print(f"找到 {file_count} 个文件。")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

def format_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 移除每行末尾的换行符
    lines = [line.rstrip('\n') for line in lines]
    
    # 处理图像路径块
    lines = process_image_path_blocks(lines)
    
    new_lines = []
    for line in lines:
        if not line.strip():
            new_lines.append("")
            continue
        
        if line.strip().startswith("[use animation]"):
            processed_line = process_use_animation_line(line)
            new_lines.append(processed_line)
        elif line.strip().startswith("[") and "]" in line:
            processed_lines = process_bracket_lines(line)
            new_lines.extend(processed_lines)
        else:
            new_lines.append(line)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

def process_image_path_blocks(lines: List[str]) -> List[str]:
    image_path_content = ""
    lines_to_remove = []
    frame_indices = []
    
    # 收集帧索引和图像路径内容
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[FRAME"):
            frame_indices.append(i)
        elif stripped.startswith("[IMAGE PATH]"):
            parts = stripped.split("[IMAGE PATH]", 1)
            if len(parts) > 1:
                image_path_content = parts[1].strip()
            lines_to_remove.append(i)
        elif stripped.startswith("[/IMAGE PATH]"):
            lines_to_remove.append(i)
    
    # 按降序排序要删除的行
    lines_to_remove.sort(reverse=True)
    
    # 删除图像路径块
    for index in lines_to_remove:
        if index < len(lines):
            del lines[index]
    
    # 在帧块后添加图像路径
    for frame_index in frame_indices:
        insert_index = frame_index + 1
        if insert_index < len(lines):
            if lines[insert_index].startswith("[IMAGE EX] -1"):
                lines[insert_index] = "[IMAGE]\n\t``"
            else:
                parts = lines[insert_index].split("] 0 ", 1)
                if len(parts) > 1:
                    ex_content = parts[1]
                else:
                    ex_content = ""
                lines[insert_index] = f"[IMAGE]\n\t{image_path_content}\n\t{ex_content}"
    
    return lines

def process_use_animation_line(line: str) -> str:
    result = []
    in_brackets = False
    new_line = True
    
    for char in line:
        if char == '[':
            in_brackets = True
            result.append(char)
            new_line = False
        elif char == ']':
            in_brackets = False
            result.append(char)
        elif char == ' ' and not in_brackets:
            result.append('\n\t')
            new_line = True
        else:
            if new_line:
                result.append('\t')
                new_line = False
            result.append(char)
    
    return ''.join(result)

def process_bracket_lines(line: str) -> List[str]:
    result_lines = []
    stripped = line.strip()
    
    # 跳过特定类型的行
    if "static" in stripped or "SHADER" in stripped or "create draw" in stripped:
        result_lines.append("")
        return result_lines
    
    # 提取括号内容
    start_bracket = stripped.find('[')
    end_bracket = stripped.find(']', start_bracket)
    
    if start_bracket >= 0 and end_bracket > start_bracket:
        bracket_content = stripped[start_bracket:end_bracket+1]
        result_lines.append(bracket_content)
        
        remaining = stripped[end_bracket+1:].strip()
        if remaining:
            elements = remaining.split()
            grouped = []
            current_group = []
            last_type = None
            
            for elem in elements:
                try:
                    float(elem)
                    current_type = "number"
                except ValueError:
                    current_type = "string"
                
                if last_type is None:
                    last_type = current_type
                    current_group.append(elem)
                elif current_type == last_type:
                    current_group.append(elem)
                else:
                    grouped.append((last_type, current_group))
                    current_group = [elem]
                    last_type = current_type
            
            if current_group:
                grouped.append((last_type, current_group))
            
            for g_type, items in grouped:
                if g_type == "number":
                    result_lines.append("\t" + "\t".join(items))
                else:
                    for item in items:
                        result_lines.append("\t" + item)
        else:
            result_lines.append("\t")
    else:
        result_lines.append(line)
    
    return result_lines

if __name__ == "__main__":
    main()