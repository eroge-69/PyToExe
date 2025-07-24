#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热转印图案排版工具
作者: Hang
版本: 2.0
"""

import PySimpleGUI as sg
import os
from PIL import Image, ImageOps
import re

# 配置
SIZE_MAP = {
    'XS': (2.5, 52), 'S': (2.5, 62), 'S-wide': (2.9, 62),
    'M': (2.9, 77), 'L': (2.9, 87), 'XL': (2.9, 97),
}
DPI = 300
PAGE_WIDTH_CM = 30
SPACING_CM = 0.5
MARGIN_CM = 2
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

sg.theme('LightGrey1')

def create_layout():
    layout = [
        [sg.Text('热转印图案排版工具 v2.0', font=('Arial', 14, 'bold'), 
                 justification='center', expand_x=True, background_color='#4472C4', 
                 text_color='white', pad=(0,10))],
        
        [sg.Frame('图案文件夹', [
            [sg.Text('选择目录:'), 
             sg.Input(key='-FOLDER-', size=(50,1), enable_events=True, readonly=True), 
             sg.FolderBrowse('浏览')]
        ], pad=(5,5))],
        
        [sg.Frame('添加图案', [
            [sg.Text('快速批量输入 (格式: N1S3,N17S2,N25S1):')],
            [sg.Multiline(key='-BATCH_INPUT-', size=(70,3), font=('Consolas', 10))],
            [sg.Button('批量添加', key='-ADD_BATCH-', button_color=('white', '#28a745')),
             sg.Text('或单个添加:'),
             sg.Text('文件夹:'), sg.Input('N1', key='-SINGLE_FOLDER-', size=(6,1)),
             sg.Text('图案:'), sg.Combo(['S1','S2','S3','S4'], key='-SINGLE_PATTERN-', size=(5,1)),
             sg.Text('尺寸:'), sg.Combo(list(SIZE_MAP.keys()), key='-SINGLE_SIZE-', size=(8,1)),
             sg.Button('添加', key='-ADD_SINGLE-')]
        ], pad=(5,5))],
        
        [sg.Column([
            [sg.Frame('当前图案列表', [
                [sg.Listbox(values=[], key='-PATTERN_LIST-', size=(42,12), 
                           font=('Consolas', 10))],
                [sg.Button('删除选中', key='-DELETE_SELECTED-'),
                 sg.Button('清空列表', key='-CLEAR_ALL-')]
            ])]
        ]),
         sg.Column([
            [sg.Frame('分页预览', [
                [sg.Button('◀ 上一页', key='-PREV_PAGE-'),
                 sg.Text('第 1 页 / 共 1 页', key='-PAGE_INFO-', justification='center'),
                 sg.Button('下一页 ▶', key='-NEXT_PAGE-')],
                [sg.Multiline('请添加图案开始预览', key='-PREVIEW_TEXT-', size=(50,8), 
                             disabled=True, font=('Consolas', 8))],
                [sg.Text('页面容量:'), sg.Text('', key='-CAPACITY_INFO-', font=('Consolas', 9))]
            ])],
            [sg.Frame('导出操作', [
                [sg.Text('导出路径:'), 
                 sg.Input(key='-OUTPUT_PATH-', size=(25,1), readonly=True),
                 sg.FolderBrowse('选择路径')],
                [sg.Button('导出当前页PNG', key='-EXPORT_SINGLE-', 
                          button_color=('white', '#007bff'), font=('Arial', 10, 'bold'))],
                [sg.Button('导出所有页PNG', key='-EXPORT_ALL-', 
                          button_color=('white', '#dc3545'), font=('Arial', 10, 'bold'))],
                [sg.Checkbox('打开输出文件夹', key='-OPEN_FOLDER-', default=True)]
            ])]
         ])],
        
        [sg.StatusBar('程序启动完成', key='-STATUS-', font=('Arial', 9))],
        [sg.Push(), sg.Button('使用说明'), sg.Button('关于程序'), sg.Button('退出'), sg.Push()]
    ]
    return layout

def load_pattern_image(img_path):
    if not os.path.exists(img_path):
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
        if src.mode == 'RGBA':
            background = Image.new('RGB', src.size, (255, 255, 255))
            background.paste(src, mask=src.split()[-1])
            src = background
        elif src.mode != 'RGB':
            src = src.convert('RGB')
        return src
    except Exception as e:
        print(f"无法加载图片 {img_path}: {e}")
        return None

def parse_pattern_input(input_text):
    patterns = []
    items = [item.strip() for item in input_text.split(',') if item.strip()]
    
    for item in items:
        match = re.match(r'^([A-Z]?\d+)([S]\d+)$', item.upper())
        if match:
            folder = match.group(1)
            pattern = match.group(2)
            patterns.append((folder, pattern, 'M'))
        else:
            print(f"跳过无效格式: {item}")
    return patterns

def calculate_pages(pattern_list):
    if not pattern_list:
        return []
    
    pages = []
    current_page = []
    current_width = 0
    
    for folder, pattern, size in pattern_list:
        if size not in SIZE_MAP:
            continue
            
        single_width = SIZE_MAP[size][0]
        actual_width = single_width * 2
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

def create_page_image(page_patterns, root_folder):
    if not page_patterns:
        return None
    
    max_height = max(SIZE_MAP[size][1] for _, _, size in page_patterns)
    canvas_height_cm = max_height + 2 * MARGIN_CM
    
    canvas_width_px = int(PAGE_WIDTH_CM / 2.54 * DPI)
    canvas_height_px = int(canvas_height_cm / 2.54 * DPI)
    canvas = Image.new('RGB', (canvas_width_px, canvas_height_px), 'white')
    
    total_content_width = 0
    for i, (folder, pattern, size) in enumerate(page_patterns):
        single_width = SIZE_MAP[size][0]
        actual_width = single_width * 2
        total_content_width += actual_width
        if i > 0:
            total_content_width += SPACING_CM
    
    center_offset_cm = (PAGE_WIDTH_CM - total_content_width) / 2
    center_offset_px = int(center_offset_cm / 2.54 * DPI)
    
    x_offset = center_offset_px
    margin_px = int(MARGIN_CM / 2.54 * DPI)
    success_count = 0
    
    for i, (folder, pattern, size) in enumerate(page_patterns):
        base_path = os.path.join(root_folder, folder, pattern)
        src = None
        
        for ext in SUPPORTED_FORMATS:
            img_path = base_path + ext
            src = load_pattern_image(img_path)
            if src:
                break
        
        if not src:
            print(f"警告: 找不到图片 {base_path}.*")
            continue
        
        try:
            w_cm, h_cm = SIZE_MAP[size]
            w_px = int(w_cm / 2.54 * DPI)
            h_px = int(h_cm / 2.54 * DPI)
            
            src.thumbnail((w_px, h_px), Image.LANCZOS)
            
            strip = Image.new('RGB', (w_px, h_px), (255, 255, 255))
            x_center = (w_px - src.width) // 2
            y_center = (h_px - src.height) // 2
            strip.paste(src, (x_center, y_center))
            
            mirrored = ImageOps.mirror(strip)
            
            if i > 0:
                x_offset += int(SPACING_CM / 2.54 * DPI)
            
            y_position = margin_px
            canvas.paste(strip, (x_offset, y_position))
            canvas.paste(mirrored, (x_offset + w_px, y_position))
            
            x_offset += w_px * 2
            success_count += 1
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
            continue
    
    return canvas if success_count > 0 else None

def generate_preview_text(pages, current_page_index):
    if not pages or current_page_index >= len(pages):
        return "无预览内容"
    
    current_page = pages[current_page_index]
    preview_lines = []
    
    preview_lines.append(f"第 {current_page_index + 1} 页 / 共 {len(pages)} 页")
    preview_lines.append("=" * 50)
    preview_lines.append(f"纸张宽度: {PAGE_WIDTH_CM}cm (长条竖直放置)")
    preview_lines.append("")
    preview_lines.append("图案排列 (从左到右，向上对齐):")
    preview_lines.append("-" * 30)
    
    total_width = 0
    for i, (folder, pattern, size) in enumerate(current_page):
        w_cm, h_cm = SIZE_MAP[size]
        actual_width = w_cm * 2
        total_width += actual_width
        if i > 0:
            total_width += SPACING_CM
        
        preview_lines.append(f"{i+1}. {folder}{pattern} ({size})")
        preview_lines.append(f"   单条尺寸: {w_cm}cm × {h_cm}cm")
        preview_lines.append(f"   镜像后宽度: {actual_width}cm")
        preview_lines.append("")
    
    remaining = PAGE_WIDTH_CM - total_width
    usage_percent = int((total_width / PAGE_WIDTH_CM) * 100)
    
    preview_lines.append("页面使用情况:")
    preview_lines.append("-" * 20)
    preview_lines.append(f"已用宽度: {total_width:.1f}cm ({usage_percent}%)")
    preview_lines.append(f"剩余宽度: {remaining:.1f}cm")
    
    return "\n".join(preview_lines)

def update_status(window, message):
    window['-STATUS-'].update(message)
    window.refresh()

def show_help():
    help_text = """热转印图案排版工具 - 使用说明

1. 文件夹结构:
   D:\\Patterns\\
   ├── N1\\
   │   ├── S1.png
   │   ├── S2.png
   │   ├── S3.png
   │   └── S4.png
   ├── N15\\
   │   └── ...

2. 快速输入格式:
   • N1S3,N17S2,N25S1,N107S4

3. 尺寸说明:
   • XS: 2.5×52cm    • S: 2.5×62cm    • S-wide: 2.9×62cm
   • M: 2.9×77cm     • L: 2.9×87cm    • XL: 2.9×97cm

4. 自动分页:
   • 程序根据30cm纸张宽度自动分页
   • 所有图案向上对齐，便于热转印操作

作者: Hang"""
    sg.popup_scrolled('使用说明', help_text, size=(60, 20))

def show_about():
    about_text = """热转印图案排版工具 v2.0

专业的热转印图案批量排版工具

核心功能:
• 批量处理热转印图案
• 自动按30cm宽度分页
• 图案向上对齐排列
• 原图+镜像并排输出
• 300 DPI专业输出

开发: Hang
技术: Python + PySimpleGUI + Pillow

感谢使用！"""
    sg.popup(about_text, title='关于程序')

def main():
    print("启动热转印图案排版工具...")
    
    layout = create_layout()
    window = sg.Window('热转印图案排版工具 v2.0', layout, finalize=True, resizable=True)
    
    pattern_list = []
    current_page_index = 0
    root_folder = ""
    
    update_status(window, "程序就绪 - 请选择图案文件夹开始使用")
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, '退出'):
            break
        
        try:
            if event == '-FOLDER-':
                root_folder = values['-FOLDER-']
                if os.path.isdir(root_folder):
                    default_output = os.path.join(root_folder, 'Output')
                    window['-OUTPUT_PATH-'].update(default_output)
                    update_status(window, f"已选择文件夹: {root_folder}")
            
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
                    current_page_index = 0
                    update_status(window, f"成功添加 {len(new_patterns)} 个图案")
                    
                    pages = calculate_pages(pattern_list)
                    preview_text = generate_preview_text(pages, current_page_index)
                    window['-PREVIEW_TEXT-'].update(preview_text)
                else:
                    sg.popup_error('输入格式错误!\n正确格式: N1S3,N17S2,N25S1')
            
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
                
                match = re.match(r'^([A-Z]?)(\d+)$', folder)
                if match:
                    prefix = match.group(1)
                    number = int(match.group(2)) + 1
                    window['-SINGLE_FOLDER-'].update(f'{prefix}{number}')
                
                update_status(window, f"已添加: {folder}{pattern} ({size})")
                
                pages = calculate_pages(pattern_list)
                preview_text = generate_preview_text(pages, current_page_index)
                window['-PREVIEW_TEXT-'].update(preview_text)
            
            elif event in ('-PREV_PAGE-', '-NEXT_PAGE-'):
                pages = calculate_pages(pattern_list)
                total_pages = len(pages)
                
                if event == '-PREV_PAGE-' and current_page_index > 0:
                    current_page_index -= 1
                elif event == '-NEXT_PAGE-' and current_page_index < total_pages - 1:
                    current_page_index += 1
                
                if total_pages > 0:
                    window['-PAGE_INFO-'].update(f'第 {current_page_index + 1} 页 / 共 {total_pages} 页')
                    
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
                    
                    preview_text = generate_preview_text(pages, current_page_index)
                    window['-PREVIEW_TEXT-'].update(preview_text)
            
            elif event == '-DELETE_SELECTED-':
                selected = values['-PATTERN_LIST-']
                if selected:
                    pattern_text = selected[0]
                    for i, (f, p, s) in enumerate(pattern_list):
                        if f"{f}{p} ({s})" == pattern_text:
                            pattern_list.pop(i)
                            break
                    
                    display_list = [f"{f}{p} ({s})" for f, p, s in pattern_list]
                    window['-PATTERN_LIST-'].update(display_list)
                    current_page_index = 0
                    
                    pages = calculate_pages(pattern_list)
                    preview_text = generate_preview_text(pages, current_page_index)
                    window['-PREVIEW_TEXT-'].update(preview_text)
                    
                    update_status(window, f"已删除图案: {pattern_text}")
                else:
                    sg.popup_error('请先选择要删除的图案!')
            
            elif event == '-CLEAR_ALL-':
                if pattern_list and sg.popup_yes_no('确定要清空所有图案吗?') == 'Yes':
                    pattern_list.clear()
                    current_page_index = 0
                    window['-PATTERN_LIST-'].update([])
                    window['-PAGE_INFO-'].update('第 1 页 / 共 0 页')
                    window['-CAPACITY_INFO-'].update('')
                    window['-PREVIEW_TEXT-'].update('请添加图案开始预览')
                    update_status(window, "已清空所有图案")
            
            elif event == '-EXPORT_SINGLE-':
                if not pattern_list:
                    sg.popup_error('请先添加图案!')
                    continue
                
                if not root_folder:
                    sg.popup_error('请选择图案文件夹!')
                    continue
                
                output_path = values['-OUTPUT_PATH-'] or os.path.join(root_folder, 'Output')
                os.makedirs(output_path, exist_ok=True)
                
                pages = calculate_pages(pattern_list)
                if current_page_index >= len(pages):
                    sg.popup_error('当前页面无效!')
                    continue
                
                update_status(window, "正在生成单页PNG...")
                
                page_patterns = pages[current_page_index]
                canvas = create_page_image(page_patterns, root_folder)
                
                if canvas:
                    filename = f'thermal_page_{current_page_index + 1:02d}.png'
                    full_path = os.path.join(output_path, filename)
                    canvas.save(full_path, dpi=(DPI, DPI))
                    
                    if values['-OPEN_FOLDER-']:
                        try:
                            os.startfile(output_path)
                        except:
                            pass
                    
                    pattern_names = [f"{f}{p}({s})" for f, p, s in page_patterns]
                    sg.popup('导出成功!', f'单页PNG已保存:\n{filename}\n\n包含图案: {", ".join(pattern_names)}\n\n保存位置: {output_path}')
                    update_status(window, f"单页导出完成: {filename}")
                else:
                    sg.popup_error('导出失败! 请检查图片文件是否存在')
            
            elif event == '-EXPORT_ALL-':
                if not pattern_list:
                    sg.popup_error('请先添加图案!')
                    continue
                
                if not root_folder:
                    sg.popup_error('请选择图案文件夹!')
                    continue
                
                output_path = values['-OUTPUT_PATH-'] or os.path.join(root_folder, 'Output')
                os.makedirs(output_path, exist_ok=True)
                
                pages = calculate_pages(pattern_list)
                if not pages:
                    sg.popup_error('无有效图案可导出!')
                    continue
                
                update_status(window, f"正在生成 {len(pages)} 页PNG...")
                
                saved_files = []
                for page_num, page_patterns in enumerate(pages):
                    canvas = create_page_image(page_patterns, root_folder)
                    
                    if canvas:
                        filename = f'thermal_page_{page_num + 1:02d}.png'
                        full_path = os.path.join(output_path, filename)
                        canvas.save(full_path, dpi=(DPI, DPI))
                        saved_files.append(filename)
                
                if saved_files:
                    if values['-OPEN_FOLDER-']:
                        try:
                            os.startfile(output_path)
                        except:
                            pass
                    
                    file_list = '\n'.join(saved_files)
                    sg.popup('批量导出成功!', f'已导出 {len(saved_files)} 个PNG文件:\n\n{file_list}\n\n保存位置: {output_path}')
                    update_status(window, f"批量导出完成: {len(saved_files)} 个文件")
                else:
                    sg.popup_error('导出失败! 请检查图片文件是否存在')
            
            elif event == '使用说明':
                show_help()
            
            elif event == '关于程序':
                show_about()
        
        except Exception as e:
            error_msg = f"程序错误: {str(e)}"
            print(error_msg)
            update_status(window, error_msg)
    
    window.close()

if __name__ == '__main__':
    main()