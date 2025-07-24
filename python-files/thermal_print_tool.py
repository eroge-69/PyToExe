#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热转印图案排版工具 - 完整版
功能: 批量处理热转印图案，自动分页，向上对齐，支持多格式
作者: Hang
版本: 2.0
使用: python thermal_print_tool.py
"""

import PySimpleGUI as sg
import os
from PIL import Image, ImageOps
import re
import subprocess
import sys

# ----------------- 配置区域 -----------------
# 尺码配置（宽cm, 高cm）
SIZE_MAP = {
    'XS':     (2.5, 52),
    'S':      (2.5, 62), 
    'S-wide': (2.9, 62),
    'M':      (2.9, 77),
    'L':      (2.9, 87),
    'XL':     (2.9, 97),
}

# 打印参数
DPI = 300                   # 打印分辨率
PAGE_WIDTH_CM = 30          # 纸张宽度
SPACING_CM = 0.5            # 条与条之间间隔
MARGIN_CM = 2               # 上下边距

# 支持的图片格式
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

# 程序信息
VERSION = "2.0"
PROGRAM_NAME = "热转印图案排版工具"
# --------------------------------------------

# 设置主题
sg.theme('LightGrey1')

def create_layout():
    """创建界面布局"""
    layout = [
        # 标题栏
        [sg.Text(f'{PROGRAM_NAME} v{VERSION}', font=('Arial', 14, 'bold'), 
                 justification='center', expand_x=True, background_color='#4472C4', 
                 text_color='white', pad=(0,10))],
        
        # 文件夹选择区域
        [sg.Frame('图案文件夹', [
            [sg.Text('选择目录:', size=(8,1)), 
             sg.Input(key='-FOLDER-', size=(50,1), enable_events=True, readonly=True), 
             sg.FolderBrowse('浏览', size=(8,1))]
        ], pad=(5,5))],
        
        # 图案输入区域
        [sg.Frame('添加图案', [
            [sg.Text('快速批量输入 (格式: N1S3,N17S2,N25S1):')],
            [sg.Multiline(key='-BATCH_INPUT-', size=(70,3), font=('Consolas', 10),
                         tooltip='支持格式: N1S3,N17S2,N25S1,N107S4\n用逗号分隔多个图案\n文件夹格式: N1, N17, N25等\n图案格式: S1, S2, S3, S4')],
            [sg.Button('批量添加', key='-ADD_BATCH-', size=(10,1), button_color=('white', '#28a745')),
             sg.Text('  或单个添加: '),
             sg.Text('文件夹:'), sg.Input('N1', key='-SINGLE_FOLDER-', size=(6,1)),
             sg.Text('图案:'), sg.Combo(['S1','S2','S3','S4'], key='-SINGLE_PATTERN-', size=(5,1), readonly=True),
             sg.Text('尺寸:'), sg.Combo(list(SIZE_MAP.keys()), key='-SINGLE_SIZE-', size=(8,1), readonly=True),
             sg.Button('添加', key='-ADD_SINGLE-', size=(6,1))]
        ], pad=(5,5))],
        
        # 主要内容区域
        [sg.Column([
            # 左侧 - 图案列表
            [sg.Frame('当前图案列表', [
                [sg.Listbox(values=[], key='-PATTERN_LIST-', size=(42,12), 
                           font=('Consolas', 10), select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                           enable_events=True)],
                [sg.Button('删除选中', key='-DELETE_SELECTED-', size=(10,1)),
                 sg.Button('清空列表', key='-CLEAR_ALL-', size=(10,1)),
                 sg.Button('预览分页', key='-PREVIEW_PAGES-', size=(10,1))]
            ], size=(460,280), pad=(5,5))]
        ], element_justification='left'),
         
         # 右侧 - 预览和操作
         sg.Column([
            [sg.Frame('分页预览 (可滚动查看完整长度)', [
                [sg.Button('◀ 上一页', key='-PREV_PAGE-', size=(8,1)),
                 sg.Text('第 1 页 / 共 1 页', key='-PAGE_INFO-', size=(15,1), justification='center'),
                 sg.Button('下一页 ▶', key='-NEXT_PAGE-', size=(8,1))],
                [sg.Multiline('', key='-PREVIEW_TEXT-', size=(50,8), disabled=True, 
                             font=('Consolas', 8), no_scrollbar=False)],
                [sg.Text('页面容量:', font=('Arial', 9, 'bold')),
                 sg.Text('', key='-CAPACITY_INFO-', size=(35,1), font=('Consolas', 9))]
            ], size=(460,200), pad=(5,5))],
            
            [sg.Frame('导出操作', [
                [sg.Text('导出路径:'), 
                 sg.Input(key='-OUTPUT_PATH-', size=(25,1), readonly=True),
                 sg.FolderBrowse('选择路径', key='-BROWSE_OUTPUT-', size=(10,1))],
                [sg.Button('导出当前页PNG', key='-EXPORT_SINGLE-', size=(18,1), 
                          button_color=('white', '#007bff'), font=('Arial', 10, 'bold'))],
                [sg.Button('导出所有页PNG', key='-EXPORT_ALL-', size=(18,1), 
                          button_color=('white', '#dc3545'), font=('Arial', 10, 'bold'))],
                [sg.Checkbox('打开输出文件夹', key='-OPEN_FOLDER-', default=True),
                 sg.Checkbox('生成预览图', key='-GENERATE_PREVIEW-', default=False)]
            ], size=(460,120), pad=(5,5))]
         ], element_justification='center')],
        
        # 状态栏和底部按钮
        [sg.StatusBar('程序启动完成，请选择图案文件夹开始使用', key='-STATUS-', size=(80,1), font=('Arial', 9))],
        [sg.Push(), 
         sg.Button('使用说明', size=(10,1)), 
         sg.Button('关于程序', size=(10,1)), 
         sg.Button('退出', size=(8,1)), 
         sg.Push()]
    ]
    
    return layout

def load_pattern_image(img_path):
    """加载图案图片，支持多种格式"""
    if not os.path.exists(img_path):
        # 尝试不同格式
        base_path = os.path.splitext(img_path)[0]
        for ext in SUPPORTED_FORMATS:
            test_path = base_path + ext
            if os.path.exists(test_path):
                img_path = test_path
                break
        else:
            return None
    
    try:
        src = Image.open(img_path)
        # 转换为RGB模式
        if src.mode == 'RGBA':
            background = Image.new('RGB', src.size, (255, 255, 255))
            background.paste(src, mask=src.split()[-1] if len(src.split()) == 4 else None)
            src = background
        elif src.mode != 'RGB':
            src = src.convert('RGB')
        
        return src
    except Exception as e:
        print(f"无法加载图片 {img_path}: {e}")
        return None

def parse_pattern_input(input_text):
    """解析图案输入"""
    patterns = []
    items = [item.strip() for item in input_text.split(',') if item.strip()]
    
    for item in items:
        # 匹配格式: N1S3 或 1S3
        match = re.match(r'^([A-Z]?\d+)([S]\d+)$', item.upper())
        if match:
            folder = match.group(1)
            pattern = match.group(2)
            patterns.append((folder, pattern, 'M'))  # 默认M尺寸
        else:
            print(f"跳过无效格式: {item} (正确格式: N1S3)")
    
    return patterns

def calculate_pages(pattern_list):
    """计算自动分页"""
    if not pattern_list:
        return []
    
    pages = []
    current_page = []
    current_width = 0
    
    for folder, pattern, size in pattern_list:
        if size not in SIZE_MAP:
            continue
            
        # 计算镜像后的实际宽度
        single_width = SIZE_MAP[size][0]
        actual_width = single_width * 2  # 镜像
        
        # 检查是否需要新页面
        spacing = SPACING_CM if current_page else 0
        needed_width = current_width + actual_width + spacing
        
        if needed_width > PAGE_WIDTH_CM and current_page:
            pages.append(current_page)
            current_page = [(folder, pattern, size)]
            current_width = actual_width
        else:
            current_page.append((folder, pattern, size))
            current_width = needed_width
    
    if current_page:
        pages.append(current_page)
    
    return pages

def create_page_image(page_patterns, root_folder, add_preview_lines=False):
    """生成单页PNG图像 - 向上对齐"""
    if not page_patterns:
        return None
    
    # 计算页面尺寸
    max_height = max(SIZE_MAP[size][1] for _, _, size in page_patterns)
    canvas_height_cm = max_height + 2 * MARGIN_CM
    
    canvas_width_px = int(PAGE_WIDTH_CM / 2.54 * DPI)
    canvas_height_px = int(canvas_height_cm / 2.54 * DPI)
    
    # 创建画布
    canvas = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
    
    # 计算居中偏移
    total_content_width = 0
    for i, (folder, pattern, size) in enumerate(page_patterns):
        single_width = SIZE_MAP[size][0]
        actual_width = single_width * 2
        total_content_width += actual_width
        if i > 0:
            total_content_width += SPACING_CM
    
    center_offset_cm = (PAGE_WIDTH_CM - total_content_width) / 2
    center_offset_px = int(center_offset_cm / 2.54 * DPI)
    
    # 处理每个图案
    x_offset = center_offset_px
    margin_px = int(MARGIN_CM / 2.54 * DPI)
    success_count = 0
    
    for i, (folder, pattern, size) in enumerate(page_patterns):
        # 尝试加载图片
        base_path = os.path.join(root_folder, folder, pattern)
        src = None
        
        for ext in SUPPORTED_FORMATS:
            img_path = base_path + ext
            src = load_pattern_image(img_path)
            if src:
                break
        
        if not src:
            print(f"警告: 找不到图片 {base_path}.* (支持: {', '.join(SUPPORTED_FORMATS)})")
            continue
        
        try:
            w_cm, h_cm = SIZE_MAP[size]
            w_px = int(w_cm / 2.54 * DPI)
            h_px = int(h_cm / 2.54 * DPI)
            
            # 调整图片尺寸
            src.thumbnail((w_px, h_px), Image.LANCZOS)
            
            # 创建条状画布
            strip = Image.new('RGB', (w_px, h_px), (255, 255, 255))
            x_center = (w_px - src.width) // 2
            y_center = (h_px - src.height) // 2
            strip.paste(src, (x_center, y_center))
            
            # 创建镜像
            mirrored = ImageOps.mirror(strip)
            
            # 添加间隔
            if i > 0:
                x_offset += int(SPACING_CM / 2.54 * DPI)
            
            # 向上对齐 - 从顶部开始贴图
            y_position = margin_px
            
            # 粘贴原图和镜像
            canvas.paste(strip, (x_offset, y_position))
            canvas.paste(mirrored, (x_offset + w_px, y_position))
            
            x_offset += w_px * 2
            success_count += 1
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
            continue
    
    return canvas if success_count > 0 else None

def generate_preview_text(pages, current_page_index):
    """生成文本预览"""
    if not pages or current_page_index >= len(pages):
        return "无预览内容"
    
    current_page = pages[current_page_index]
    preview_lines = []
    
    # 页面信息
    preview_lines.append(f"第 {current_page_index + 1} 页 / 共 {len(pages)} 页")
    preview_lines.append("=" * 50)
    preview_lines.append(f"纸张宽度: {PAGE_WIDTH_CM}cm (竖直放置)")
    preview_lines.append("")
    
    # 图案列表
    preview_lines.append("图案排列 (从左到右，向上对齐):")
    preview_lines.append("-" * 30)
    
    total_width = 0
    for i, (folder, pattern, size) in enumerate(current_page):
        w_cm, h_cm = SIZE_MAP[size]
        actual_width = w_cm * 2  # 镜像后宽度
        total_width += actual_width
        if i > 0:
            total_width += SPACING_CM
        
        preview_lines.append(f"{i+1}. {folder}{pattern} ({size})")
        preview_lines.append(f"   尺寸: {w_cm}cm × {h_cm}cm")
        preview_lines.append(f"   镜像后: {actual_width}cm × {h_cm}cm")
        preview_lines.append(f"   |原图{w_cm}cm|镜像{w_cm}cm|")
        
        # 简单的ASCII预览
        strip_visual = "█" * int(h_cm / 5)  # 按比例显示长度
        preview_lines.append(f"   长度: {strip_visual} ({h_cm}cm)")
        preview_lines.append("")
    
    # 容量信息
    remaining = PAGE_WIDTH_CM - total_width
    usage_percent = int((total_width / PAGE_WIDTH_CM) * 100)
    
    preview_lines.append("页面使用情况:")
    preview_lines.append("-" * 20)
    preview_lines.append(f"已用宽度: {total_width:.1f}cm ({usage_percent}%)")
    preview_lines.append(f"剩余宽度: {remaining:.1f}cm")
    
    if remaining >= 5.0:
        preview_lines.append("剩余空间: 可再添加小尺寸图案")
    else:
        preview_lines.append("剩余空间: 不足，建议新页面")
    
    return "\n".join(preview_lines)

def update_status(window, message):
    """更新状态栏"""
    window['-STATUS-'].update(message)
    window.refresh()

def show_help():
    """显示使用说明"""
    help_text = """
热转印图案排版工具 - 使用说明

1. 文件夹结构:
   D:\\Patterns\\
   ├── N1\\
   │   ├── S1.png (或 .jpg)
   │   ├── S2.png
   │   ├── S3.png
   │   └── S4.png
   ├── N15\\
   │   └── ...
   └── ...

2. 快速输入格式:
   • N1S3,N17S2,N25S1,N107S4
   • 支持任意文件夹编号 (N1, N15, N127等)
   • 图案文件固定为 S1, S2, S3, S4

3. 尺寸说明:
   • XS: 2.5×52cm    • S: 2.5×62cm    • S-wide: 2.9×62cm
   • M: 2.9×77cm     • L: 2.9×87cm    • XL: 2.9×97cm

4. 自动分页:
   • 程序根据30cm纸张宽度自动分页
   • 每页容纳4-5个图案（取决于尺寸）
   • 所有图案向上对齐，便于热转印操作

5. 导出功能:
   • 单页导出: 导出当前预览页面
   • 批量导出: 自动分页导出所有PNG
   • 300 DPI高质量输出，适合专业打印
   • 可自选导出路径

6. 支持格式:
   • 输入: PNG, JPG, JPEG, BMP, TIFF
   • 输出: 300 DPI PNG文件

技巧: 使用预览功能查看分页效果，确认无误后再导出！
"""
    
    sg.popup_scrolled('使用说明', help_text, size=(60, 25), font=('Consolas', 10))

def show_about():
    """显示关于信息"""
    about_text = f"""
{PROGRAM_NAME} v{VERSION}

专业的热转印图案批量排版工具

核心功能:
• 批量处理热转印图案
• 自动按30cm宽度分页  
• 图案向上对齐排列
• 原图+镜像并排输出
• 支持多种图片格式
• 300 DPI专业输出

技术特点:
• 智能容量计算
• 实时分页预览
• 一键批量导出
• 自选导出路径
• 文件格式兼容

适用场景:
• 热转印批量生产
• 服装图案排版
• 纺织品印刷准备

开发: Hang
技术: Python + PySimpleGUI + Pillow
版本: {VERSION}

感谢使用！
"""
    
    sg.popup(about_text, title='关于程序', font=('Arial', 10))

def main():
    """主程序入口"""
    print(f"启动 {PROGRAM_NAME} v{VERSION}...")
    
    # 创建窗口
    layout = create_layout()
    window = sg.Window(f'{PROGRAM_NAME} v{VERSION}', layout, 
                      icon=None, finalize=True, resizable=True,
                      location=(100, 50))
    
    # 初始化变量
    pattern_list = []
    current_page_index = 0
    root_folder = ""
    output_folder = ""
    
    update_status(window, "程序就绪 - 请选择图案文件夹开始使用")
    
    # 主循环
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '退出'):
            break
        
        try:
            # 文件夹选择
            if event == '-FOLDER-':
                root_folder = values['-FOLDER-']
                if os.path.isdir(root_folder):
                    # 自动设置默认输出路径
                    default_output = os.path.join(root_folder, 'Output')
                    window['-OUTPUT_PATH-'].update(default_output)
                    output_folder = default_output
                    update_status(window, f"已选择文件夹: {root_folder}")
                else:
                    update_status(window, "无效的文件夹路径")
            
            # 输出路径选择
            elif event == '-BROWSE_OUTPUT-':
                output_folder = values['-OUTPUT_PATH-']
                if output_folder:
                    update_status(window, f"输出路径已设置: {output_folder}")
            
            # 批量添加
            elif event == '-ADD_BATCH-':
                input_text = values['-BATCH_INPUT-'].strip()
                if not input_text:
                    sg.popup_error('请输入图案序号!')
                    continue
                
                new_patterns = parse_pattern_input(input_text)
                if new_patterns:
                    pattern_list.extend(new_patterns)
                    display_list = [f"{f}{p} ({s})" for f, p, s in pattern_list]
                    window['-PATTERN_LIST-'].update(display_list)
                    window['-BATCH_INPUT-'].update('')
                    current_page_index = 0  # 重置到第一页
                    update_status(window, f"成功添加 {len(new_patterns)} 个图案")
                    
                    # 更新预览
                    pages = calculate_pages(pattern_list)
                    preview_text = generate_preview_text(pages, current_page_index)
                    window['-PREVIEW_TEXT-'].update(preview_text)
                else:
                    sg.popup_error('输入格式错误!\n\n正确格式示例:\nN1S3,N17S2,N25S1,N107S4')
            
            # 单个添加
            elif event == '-ADD_SINGLE-':
                folder = values['-SINGLE_FOLDER-'].strip()
                pattern = values['-SINGLE_PATTERN-']
                size = values['-SINGLE_SIZE-']
                
                if not all([folder, pattern, size]):
                    sg.popup_error('请完整填写文件夹、图案和尺寸!')
                    continue
                
                pattern_list.append((folder, pattern, size))
                display_list = [f"{f}{p} ({s})" for f, p, s in pattern_list]
                window['-PATTERN_LIST-'].update(display_list)
                
                # 自动递增文件夹编号
                match = re.match(r'^([A-Z]?)(\d+)$', folder)
                if match:
                    prefix = match.group(1)
                    number = int(match.group(2)) + 1
                    window['-SINGLE_FOLDER-'].update(f'{prefix}{number}')
                
                update_status(window, f"已添加: {folder}{pattern} ({size})")
                
                # 更新预览
                pages = calculate_pages(pattern_list)
                preview_text = generate_preview_text(pages, current_page_index)
                window['-PREVIEW_TEXT-'].update(preview_text)
            
            # 分页导航和列表更新
            elif event in ('-PREV_PAGE-', '-NEXT_PAGE-', '-PATTERN_LIST-', '-PREVIEW_PAGES-'):
                pages = calculate_pages(pattern_list)
                total_pages = len(pages)
                
                if event == '-PREV_PAGE-' and current_page_index > 0:
                    current_page_index -= 1
                elif event == '-NEXT_PAGE-' and current_page_index < total_pages - 1:
                    current_page_index += 1
                
                # 更新页面信息
                if total_pages > 0:
                    window['-PAGE_INFO-'].update(f'第 {current_page_index + 1} 页 / 共 {total_pages} 页')
                    
                    # 更新容量信息
                    if current_page_index < total_pages:
                        current_page_patterns = pages[current_page_index]
                        total_width = 0
                        for i, (_, _, size) in enumerate(current_page_patterns):
                            single_width = SIZE_MAP[size][0]
                            actual_width = single_width * 2
                            total_width += actual_width
                            if i > 0:
                                total_width += SPACING_CM
                        
                        remaining = PAGE_WIDTH_CM - total_width
                        usage_percent = int((total_width / PAGE_WIDTH_CM) * 100)
                        
                        capacity_text = f'已用: {total_width:.1f}cm ({usage_percent}%)  剩余: {remaining:.1f}cm'
                        window['-CAPACITY_INFO-'].update(capacity_text)
                        
                        # 更新预览文本
                        preview_text = generate_preview_text(pages, current_page_index)
                        window['-PREVIEW_TEXT-'].update(preview_text)
                        
                        # 显示当前页图案
                        page_patterns = [f"{f}{p}({s})" for f, p, s in current_page_patterns]
                        update_status(window, f"第{current_page_index + 1}页: {', '.join(page_patterns)}")
                else:
                    window['-PAGE_INFO-'].update('第 1 页 / 共 0 页')
                    window['-CAPACITY_INFO-'].update('无图案')
                    window['-PREVIEW_TEXT-'].update('请添加图案开始预览')
                    update_status(window, "无图案数据")
            
            # 删除选中
            elif event == '-DELETE_SELECTED-':
                selected = values['-PATTERN_LIST-']
                if selected:
                    pattern_text = selected[0]
                    # 从列表中找到并删除
                    for i, (f, p, s) in enumerate(pattern_list):
                        if f"{f}{p} ({s})" == pattern_text:
                            deleted_pattern = pattern_list.pop(i)
                            break
                    
                    display_list = [f"{f}{p} ({s})" for f, p, s in pattern_list]
                    window['-PATTERN_LIST-'].update(display_list)
                    current_page_index = 0  # 重置到第一页
                    
                    # 更新预览
                    pages = calculate_pages(pattern_list)
                    preview_text = generate_preview_text(pages, current_page_index)
                    window['-PREVIEW_TEXT-'].update(preview_text)
                    
                    update_status(window, f"已删除图案: {pattern_text}")
                else:
                    sg.popup_error('请先选择要删除的图案!')
            
            # 清空列表
            elif event == '-CLEAR_ALL-':
                if pattern_list and sg.popup_yes_no('确定要清空所有图案吗?', title='确认操作') == 'Yes':
                    pattern_list.clear()
                    current_page_index = 0
                    window['-PATTERN_LIST-'].update([])
                    window['-PAGE_INFO-'].update('第 1 页 / 共 0 页')
                    window['-CAPACITY_INFO-'].update('')
                    window['-PREVIEW_TEXT-'].update('请添加图案开始预览')
                    update_status(window, "已清空所有图案")
            
            # 导出单页
            elif event == '-EXPORT_SINGLE-':
                if not pattern_list:
                    sg.popup_error('请先添加图案!')
                    continue
                
                if not root_folder:
                    sg.popup_error('请选择图案文件夹!')
                    continue
                
                # 检查输出路径
                current_output = values['-OUTPUT_PATH-'] or os.path.join(root_folder, 'Output')
                if not os.path.exists(current_output):
                    try:
                        os.makedirs(current_output, exist_ok=True)
                    except:
                        sg.popup_error(f'无法创建输出文件夹: {current_output}')
                        continue
                
                pages = calculate_pages(pattern_list)
                if current_page_index >= len(pages):
                    sg.popup_error('当前页面无效!')
                    continue
                
                update_status(window, "正在生成单页PNG...")
                
                page_patterns = pages[current_page_index]
                canvas = create_page_image(page_patterns, root_folder)
                
                if canvas:
                    filename = f'thermal_page_{current_page_index + 1:02d}.png'
                    output_path = os.path.join(current_output, filename)
                    canvas.save(output_path, dpi=(DPI, DPI))
                    
                    # 生成预览图
                    if values['-GENERATE_PREVIEW-']:
                        preview_canvas = create_page_image(page_patterns, root_folder, add_preview_lines=True)
                        if preview_canvas:
                            preview_path = os.path.join(current_output, f'preview