import os
import sys
import re
import shutil
from collections import defaultdict

# 获取脚本真实路径（即使打包成exe）
# Get the script's true path (even when bundled as an EXE)
def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# 备份文件 - 使用模式感知的命名方案
# Backup file - using a mode-aware naming scheme
def backup_file(file_path, mode):
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    backup_name = f"{basename}.{mode}_bak"
    backup_path = os.path.join(dirname, backup_name)
    shutil.copy2(file_path, backup_path)
    return backup_path

# 还原备份 - 适配新的命名方案
# Revert backup - adapting to the new naming scheme
def revert_backup(file_path):
    # 检查两种模式的备份文件
    # Check for both modes' backup files
    sf_backup = f"{file_path}.SlotFix_bak"
    rf_backup = f"{file_path}.RabbitFX_bak"
    backup_path = None
    
    if os.path.exists(sf_backup):
        backup_path = sf_backup
    elif os.path.exists(rf_backup):
        backup_path = rf_backup
        
    if backup_path:
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(backup_path, file_path)
        return True
    return False

# 处理ini内容 - 模式化
# Process INI content - now mode-aware
def process_ini_content(content, mode):
    # 检查是否已为任一模式处理过
    # Check if already processed by ANY mode
    if re.search(r'^;\s*(SlotFix|RabbitFX)\s+applied', content, re.MULTILINE | re.IGNORECASE):
        return 'skipped'
    
    # 定义不同模式的输出格式
    # Define output formats for different modes
    formats = {
        'SlotFix': {
            'tex_line': "{indent}Resource\\ZZMI\\{tex_type} = ref {value}",
            'run_cmd': "run = CommandList\\ZZMI\\SetTextures",
            'marker': "; SlotFix applied\n",
            'tex_map': { 'Diffuse': 'Diffuse', 'NormalMap': 'NormalMap', 'LightMap': 'LightMap', 'MaterialMap': 'MaterialMap' },
            'tex_line_regex': r'^\s*Resource\\ZZMI\\(Diffuse|NormalMap|LightMap|MaterialMap)\s*='
        },
        'RabbitFX': {
            'tex_line': "{indent}Resource\\RabbitFX\\{tex_type} = ref {value}",
            'run_cmd': "run = Commandlist\\RabbitFX\\SetTextures",
            'marker': "; RabbitFX applied\n",
            'tex_map': { 'Diffuse': 'Diffuse', 'NormalMap': 'Normalmap', 'LightMap': 'Lightmap', 'MaterialMap': 'Materialmap' },
            'tex_line_regex': r'^\s*Resource\\RabbitFX\\(Diffuse|Normalmap|Lightmap|Materialmap)\s*='
        }
    }
    
    mode_format = formats[mode]
    
    # 解析INI结构
    # Parse INI structure
    sections = []
    current_section = None
    lines = content.splitlines()
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section_name = stripped[1:-1].strip()
            current_section = {'name': section_name, 'lines': [line], 'original_lines': [line]}
            sections.append(current_section)
        elif current_section is not None:
            current_section['lines'].append(line)
            current_section['original_lines'].append(line)
        else:
            if not sections or sections[-1]['name'] != '':
                sections.append({'name': '', 'lines': [], 'original_lines': []})
            sections[-1]['lines'].append(line)
            sections[-1]['original_lines'].append(line)

    # --- 阶段1: 全局预扫描与数据收集 ---
    # --- Phase 1: Global Pre-scan and Data Collection ---
    texture_data = defaultdict(dict)
    main_sections_map = defaultdict(lambda: {'ib': [], 'variants': []})
    command_lists = {s['name']: s for s in sections if s['name'].lower().startswith('commandlist')}
    changes_were_made = False # 引入变更检测旗标

    for i, section in enumerate(sections):
        section_name = section['name']
        
        # 识别纹理子节
        tex_match = re.match(r'^TextureOverride(.+?)([A-Z])(Diffuse|NormalMap|LightMap|MaterialMap)(?:\.\d+)?$', 
                           section_name, re.IGNORECASE)
        if tex_match:
            base_obj_name, variant_char, tex_type = tex_match.groups()
            logic_source_section = section
            for line in section['lines']:
                cmd_match = re.match(r'^\s*run\s*=\s*(CommandList.+)', line.strip(), re.IGNORECASE)
                if cmd_match and cmd_match.group(1) in command_lists:
                    logic_source_section = command_lists[cmd_match.group(1)]
                    break
            
            raw_lines = [l for l in logic_source_section['original_lines'] if not (l.strip().startswith('[') or re.match(r'^\s*hash\s*=', l, re.IGNORECASE))]
            
            while raw_lines and (not raw_lines[0].strip() or raw_lines[0].strip().startswith(';')):
                raw_lines.pop(0)
            while raw_lines and (not raw_lines[-1].strip() or raw_lines[-1].strip().startswith(';')):
                raw_lines.pop()

            texture_data[base_obj_name][(variant_char, tex_type)] = {'raw_lines': raw_lines}
            continue

        # 识别IB主节或变体主节
        ib_match = re.match(r'^TextureOverride(.+?)IB$', section_name, re.IGNORECASE)
        if ib_match:
            main_sections_map[ib_match.group(1)]['ib'].append(i)
        elif re.match(r'^TextureOverride(.+?)([A-Z])$', section_name, re.IGNORECASE):
             main_sections_map[re.match(r'^TextureOverride(.+?)([A-Z])$', section_name, re.IGNORECASE).group(1)]['variants'].append(i)

    # --- 阶段2: 决策与处理 ---
    # --- Phase 2: Decision Making and Processing ---
    processed_base_objects = set()

    for base_obj_name in list(texture_data.keys()):
        if base_obj_name in processed_base_objects:
            continue
        
        main_section_info = main_sections_map.get(base_obj_name)
        target_indices = []

        if main_section_info and main_section_info['variants']:
            target_indices = main_section_info['variants']
        elif main_section_info and main_section_info['ib']:
            target_indices = main_section_info['ib']
        elif 'face' in base_obj_name.lower() or 'head' in base_obj_name.lower():
            for i, section in enumerate(sections):
                s_name_lower = section['name'].lower()
                is_tex_sub_section = re.search(r'(diffuse|normalmap|lightmap|materialmap)(?:\.\d+)?$', s_name_lower)
                has_skin_texture_cmd = any(re.search(r'^\s*run\s*=\s*commandlistskintexture', line, re.IGNORECASE) for line in section['lines'])
                if ('face' in s_name_lower or 'head' in s_name_lower) and not is_tex_sub_section and has_skin_texture_cmd:
                    target_indices.append(i)
                    break
        
        if not target_indices:
            continue

        master_texture_set = {}
        for (variant_char, tex_type), tex_info in texture_data[base_obj_name].items():
            if tex_type not in master_texture_set:
                master_texture_set[tex_type] = tex_info

        for section_index in target_indices:
            section = sections[section_index]
            
            ib_found, slot_replacements = False, {}
            source_for_ps_t = section
            is_commandlist_mod = False
            for line in section['lines']:
                cmd_match = re.match(r'^\s*run\s*=\s*(CommandList.+)', line.strip(), re.IGNORECASE)
                if cmd_match and 'skintexture' not in cmd_match.group(1).lower() and cmd_match.group(1) in command_lists:
                    source_for_ps_t = command_lists[cmd_match.group(1)]
                    is_commandlist_mod = True
                    break
            
            if any(re.match(r'^\s*ib\s*=', l, re.IGNORECASE) for l in source_for_ps_t['lines']) or \
               any(re.match(r'^\s*ib\s*=', l, re.IGNORECASE) for l in section['lines']):
                ib_found = True

            processed_ps_t_lines = []
            ps_t_changed = False
            for line in source_for_ps_t['lines']:
                slot_match = re.match(r'^(\s*)(ps-t[3-6])\s*=\s*(.+)', line, re.IGNORECASE)
                if slot_match:
                    indent, slot, value = slot_match.groups()
                    tex_type_key = {'ps-t3': 'Diffuse', 'ps-t4': 'NormalMap', 'ps-t5': 'LightMap', 'ps-t6': 'MaterialMap'}[slot.lower()]
                    tex_type_val = mode_format['tex_map'][tex_type_key]
                    new_line = mode_format['tex_line'].format(indent=indent, tex_type=tex_type_val, value=value.strip())
                    processed_ps_t_lines.append(new_line)
                    slot_replacements[tex_type_key] = True
                    ps_t_changed = True
                else:
                    processed_ps_t_lines.append(line)
            
            if ps_t_changed:
                source_for_ps_t['lines'] = processed_ps_t_lines
                changes_were_made = True

            main_section_lines = list(section['lines'])
            all_insert_lines = []
            for tex_type_key, tex_info in master_texture_set.items():
                if tex_type_key in slot_replacements: continue
                raw_lines, temp_block = tex_info['raw_lines'], []
                for line in raw_lines:
                    this_match = re.match(r'^(\s*)this\s*=\s*(.+)', line, re.IGNORECASE)
                    if this_match:
                        indent, value = this_match.groups()
                        tex_type_val = mode_format['tex_map'][tex_type_key]
                        new_line = mode_format['tex_line'].format(indent=indent, tex_type=tex_type_val, value=value.strip())
                        temp_block.append(new_line)
                    else: temp_block.append(line)
                if temp_block: all_insert_lines.extend(temp_block)
            
            if all_insert_lines:
                changes_were_made = True
                if is_commandlist_mod:
                    last_run_index = -1
                    for i, line in enumerate(main_section_lines):
                        if re.match(r'^\s*run\s*=', line, re.IGNORECASE): last_run_index = i
                    if last_run_index != -1:
                        main_section_lines = main_section_lines[:last_run_index + 1] + all_insert_lines + main_section_lines[last_run_index + 1:]
                    else: main_section_lines.extend(all_insert_lines)
                else:
                    if ib_found:
                        for i, line in enumerate(main_section_lines):
                            if re.match(r'^\s*ib\s*=', line, re.IGNORECASE):
                                main_section_lines = main_section_lines[:i+1] + all_insert_lines + main_section_lines[i+1:]
                                break
                    else:
                        while main_section_lines and not main_section_lines[-1].strip(): main_section_lines.pop()
                        main_section_lines.extend(all_insert_lines)
            
            run_found = any(re.match(fr'^\s*run\s*=\s*{re.escape(mode_format["run_cmd"].split("=")[1].strip())}', l, re.IGNORECASE) for l in main_section_lines)
            if not run_found and (ps_t_changed or all_insert_lines):
                changes_were_made = True
                run_insertion_point, tex_line_regex = -1, mode_format['tex_line_regex']
                last_texture_line_index = -1
                for i, line in enumerate(main_section_lines):
                    if re.match(tex_line_regex, line, re.IGNORECASE): last_texture_line_index = i
                
                if last_texture_line_index != -1:
                    run_insertion_point, if_balance = last_texture_line_index + 1, 0
                    for i in range(last_texture_line_index + 1):
                        stripped_line = main_section_lines[i].strip().lower()
                        if stripped_line.startswith('if '): if_balance += 1
                        elif stripped_line == 'endif': if_balance -= 1
                    if if_balance > 0:
                        for i in range(last_texture_line_index + 1, len(main_section_lines)):
                            stripped_line = main_section_lines[i].strip().lower()
                            run_insertion_point = i + 1
                            if stripped_line.startswith('if '): if_balance += 1
                            elif stripped_line == 'endif': if_balance -= 1
                            if if_balance == 0: break
                    main_section_lines.insert(run_insertion_point, mode_format['run_cmd'])
                else: main_section_lines.append(mode_format['run_cmd'])
            
            section['lines'] = main_section_lines
        processed_base_objects.add(base_obj_name)

    # --- 阶段3: 构建新内容 ---
    # --- Phase 3: Build New Content ---
    if not changes_were_made:
        return 'no_change' # 返回无需更改的信号

    new_content = [mode_format['marker']]
    for i, section in enumerate(sections):
        if i > 0 and new_content and new_content[-1].strip():
            new_content.append('')
        new_content.extend(section['lines'])
    
    return "\n".join(new_content)

# 处理单个INI文件
# Process a single INI file
def process_ini_file(file_path, mode):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 首先进行分析，不执行任何文件操作
    # First, analyze without performing any file operations
    result = process_ini_content(content, mode)

    if result == 'skipped':
        print(f"跳过已处理的文件 (Skipping already processed file): {file_path}")
        return 'skipped'
    elif result == 'no_change':
        print(f"跳过不支持的文件 (Skipping not supported file): {file_path}")
        return 'no_change'
    
    # 只有在确认需要更改后，才执行备份和写入
    # Only after confirming that changes are needed, proceed with backup and writing
    try:
        backup_path = backup_file(file_path, mode)
        print(f"备份已创建 (Backup created): {backup_path}")
    except Exception as e:
        print(f"错误：未能为文件创建备份 (ERROR: Failed to create backup for file): {file_path}")
        print(f"  原因 (Reason): {str(e)}")
        print(f"  为确保安全，已跳过此文件 (Skipping this file to ensure safety).")
        return 'failed'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result) # result 现在是新的文件内容
    print(f"已处理 (Processed): {file_path}")
    return 'processed'

# 主函数
# Main function
def main():
    print("=" * 70)
    print("ZZZ_纹理修复工具v1.22_beta")
    print("作者: 哈米猫特")
    print()
    print("ZZZ_TexFix_Tool_v1.22_beta")
    print("Author: HammyCatte")
    print("-" * 70)
    print("功能: 本工具用于自动修复因纹理槽位问题导致部分mod显示异常的情况。")
    print("此外，HASH格式的纹理节也将被追加纹理修复，用以解决高低显的兼容性问题。")
    print()
    print("兼容性: 本工具仅适用于使用 XXMI 工具制作的mod。")
    print("请确保使用最新版XXMI启动器或RabbitFX插件。")
    print()
    print("Function: This tool automatically fixes display issues in some mods caused by texture slot conflicts.")
    print("In addition, Texture sections in HASH format will also be appended with TexFix to solve the 1024/2048p texture hashes problem.")
    print()
    print("Compatibility: This tool is only intended for mods made with the XXMI-tools.")
    print("Please make sure to use the latest version of XXMI launcher or RabbitFX plugin.")
    print("\n" + "!" * 70)
    print("警告:")
    print("1. 由于不确定修复插件的稳定性，请谨慎使用。")
    print("2. 使用了着色器修改(ShaderFixes)的mod无法使用此工具修复。")
    print("3. 请务必保留生成的 .[模式名]_bak 备份文件！")
    print()
    print("WARNING:")
    print("1. Use with caution, as the stability of the underlying fix plugins is uncertain.)")
    print("2. This tool cannot fix mods that use ShaderFixes.)")
    print("3. It is crucial that you DO NOT delete the generated .[mode_name]_bak backup files!)")
    print("!" * 70)
    
    mode = None
    while not mode:
        print("\n请选择操作模式 (Please select an operating mode):")
        print("1. SlotFix 模式 (SlotFix Mode)")
        print("2. RabbitFX 模式 (RabbitFX Mode)")
        print("3. 还原所有备份 (Revert All Backups)")
        
        choice = input("请输入选项 (1/2/3) 并按回车 / Please enter your choice (1/2/3) and press Enter: ")
        
        if choice == '1': mode = 'SlotFix'
        elif choice == '2': mode = 'RabbitFX'
        elif choice == '3': mode = 'revert'
        else: print("\n无效输入，请重新选择 (Invalid input, please choose again).")
    
    print("-" * 70)
    
    script_dir = get_script_dir()
    
    if mode == 'revert':
        print("正在还原更改... (Reverting changes...)")
        reverted_count = 0
        total_backups_found = 0
        for root, _, files in os.walk(script_dir):
            for file in files:
                m = re.match(r'(.+)\.(SlotFix|RabbitFX)_bak$', file)
                if m:
                    total_backups_found += 1
                    orig_name = m.group(1)
                    orig_path = os.path.join(root, orig_name)
                    
                    if revert_backup(orig_path):
                        print(f"已还原 (Reverted): {orig_path}")
                        reverted_count += 1
        
        if total_backups_found == 0:
            print("未找到可还原的备份文件 (No backups found to revert.)")
        else:
            print(f"\n共找到 {total_backups_found} 个备份文件，成功还原 {reverted_count} 个。")
            print(f"(Found {total_backups_found} backup files, successfully reverted {reverted_count} files.)")
    else:
        print(f"正在以 [{mode}] 模式处理INI文件... (Processing INI files in [{mode}] mode...)")
        actually_processed_count = 0
        skipped_count = 0
        failed_count = 0
        no_change_count = 0
        total_ini_found = 0
        
        for root, _, files in os.walk(script_dir):
            for file in files:
                if file.lower().endswith('.ini') and not file.lower().startswith('disabled') and not file.endswith('_bak'):
                    total_ini_found += 1
                    file_path = os.path.join(root, file)
                    try:
                        result = process_ini_file(file_path, mode)
                        if result == 'processed':
                            actually_processed_count += 1
                        elif result == 'skipped':
                            skipped_count += 1
                        elif result == 'failed':
                            failed_count += 1
                        elif result == 'no_change':
                            no_change_count += 1
                    except Exception as e:
                        print(f"处理文件时发生意外错误 (An unexpected error occurred while processing file) {file_path}: {str(e)}")
                        failed_count += 1

        print(f"\n处理完成。共找到 {total_ini_found} 个可处理文件，成功处理 {actually_processed_count} 个，跳过已处理 {skipped_count} 个，不支持 {no_change_count} 个，失败 {failed_count} 个。")
        print(f"(Processing completed. Found {total_ini_found} files, processed {actually_processed_count}, skipped {skipped_count}, not supported {no_change_count}, failed {failed_count}.)")

    print("-" * 70)
    input("所有操作已完成。按回车键退出... (All operations are complete. Press Enter to exit...)")

if __name__ == "__main__":
    main()