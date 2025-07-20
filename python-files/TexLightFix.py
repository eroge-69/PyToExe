import sys
import os
from colorama import Fore, Back, init
import shutil

def generate_unique_backup_filename(f):
    base, ext = os.path.splitext(os.path.basename(f))
    backup_dir = os.path.dirname(f)
    i = 1
    backup_filename = f"disabled_backup_{base}.ini"
    backup_filepath = os.path.join(backup_dir, backup_filename)
    
    while os.path.exists(backup_filepath):
        backup_filename = f"disabled_backup_{base}_{i}.ini"
        backup_filepath = os.path.join(backup_dir, backup_filename)
        i += 1
    
    return backup_filepath

def list_all_files_and_dirs(directory):
    all_files_and_dirs = []
    ini_files = []
    for root, dirs, files in os.walk(directory):
        # Skip directories containing 'SlotFix' (case-insensitive)
        dirs[:] = [d for d in dirs if 'slotfix' not in d.lower()]
        for file in files:
            full_path = os.path.join(root, file)
            all_files_and_dirs.append(full_path)
            # Skip SlotFix.ini and RabbitFX.ini, and files containing 'SlotFix' in their name (case-insensitive)
            if (
                file.endswith('.ini')
                and 'disabled' not in file.lower()
                and 'Materia' not in file
                and 'slotfix' not in file.lower()
                and file not in ['SlotFix.ini', 'RabbitFX.ini']
            ):
                ini_files.append(full_path)
    return all_files_and_dirs, ini_files

def comment_out_if_ps_t7_block(lines):
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith(';'):
            i += 1
            continue
        # Handle if ps-t7 == 1
        if 'if ps-t7 == 1' in line:
            if_start = i
            stack = []
            else_idx = None
            endif_idx = None
            j = i
            while j < n:
                l = lines[j]
                l_strip = l.strip()
                if l_strip.startswith('if '):
                    stack.append('if')
                if l_strip.startswith('else') and len(stack) == 1 and else_idx is None:
                    else_idx = j
                if l_strip.startswith('endif'):
                    if stack:
                        stack.pop()
                    if len(stack) == 0:
                        endif_idx = j
                        break
                j += 1
            if else_idx is not None and endif_idx is not None:
                # Comment out from if to else (including if, else), and endif
                for k in range(if_start, else_idx + 1):
                    if not lines[k].strip().startswith(';'):
                        lines[k] = ';' + lines[k]
                if not lines[endif_idx].strip().startswith(';'):
                    lines[endif_idx] = ';' + lines[endif_idx]
                i = endif_idx + 1
                continue
        # Handle if $censor == 0
        if 'if $censor == 0' in line:
            if_start = i
            stack = []
            else_idx = None
            endif_idx = None
            j = i
            while j < n:
                l = lines[j]
                l_strip = l.strip()
                if l_strip.startswith('if '):
                    stack.append('if')
                if l_strip.startswith('else') and len(stack) == 1 and else_idx is None:
                    else_idx = j
                if l_strip.startswith('endif'):
                    if stack:
                        stack.pop()
                    if len(stack) == 0:
                        endif_idx = j
                        break
                j += 1
            if else_idx is not None and endif_idx is not None:
                # Comment out the if line itself
                if not lines[if_start].strip().startswith(';'):
                    lines[if_start] = ';' + lines[if_start]
                # Comment out from else to endif (including else, endif)
                for k in range(else_idx, endif_idx + 1):
                    if not lines[k].strip().startswith(';'):
                        lines[k] = ';' + lines[k]
                i = endif_idx + 1
                continue
        i += 1
    return lines

def replace_strings_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        lines = comment_out_if_ps_t7_block(lines)  # First handle comment logic
        replaced_lines = []
        i = 0
        n = len(lines)
        ps_keys = ['ps-t3', 'ps-t4', 'ps-t5', 'ps-t6']
        while i < n:
            line = lines[i]
            replaced = False
            # Skip already commented lines
            if line.strip().startswith(';'):
                replaced_lines.append(line)
                i += 1
                continue
            # Replacement logic
            if any(key in line for key in ['ps-t3 =', 'ps-t3= ', 'ps-t3=']):
                line = line.replace('ps-t3 =', 'Resource\\ZZMI\\Diffuse = ref ').replace('ps-t3=', 'Resource\\ZZMI\\Diffuse = ref ')
                replaced = True
            elif any(key in line for key in ['ps-t4 =', 'ps-t4= ', 'ps-t4=']):
                line = line.replace('ps-t4 =', 'Resource\\ZZMI\\NormalMap = ref ').replace('ps-t4=', 'Resource\\ZZMI\\NormalMap = ref ')
                replaced = True
            elif any(key in line for key in ['ps-t5 =', 'ps-t5= ', 'ps-t5=']):
                line = line.replace('ps-t5 =', 'Resource\\ZZMI\\LightMap = ref ').replace('ps-t5=', 'Resource\\ZZMI\\LightMap = ref ')
                replaced = True
            elif any(key in line for key in ['ps-t6 =', 'ps-t6= ', 'ps-t6=']):
                line = line.replace('ps-t6 =', 'Resource\\ZZMI\\MaterialMap = ref ').replace('ps-t6=', 'Resource\\ZZMI\\MaterialMap = ref ')
                replaced = True
            replaced_lines.append(line)
            # Check if the next non-empty, non-comment line is a new ps-t3/4/5/6, and insert run if not
            if replaced:
                j = i + 1
                while j < n and (lines[j].strip() == '' or lines[j].strip().startswith(';')):
                    j += 1
                if j >= n or not any(lines[j].strip().startswith(key) for key in ps_keys):
                    import re
                    indent = re.match(r'^(\s*)', line).group(1)
                    replaced_lines.append(f'{indent}run = CommandList\\ZZMI\\SetTextures\n')
            i += 1
        return replaced_lines
    except (IOError, OSError) as e:
        print(f"Failed to read file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Unknown error occurred: {e}")
        return []
    
def write_replaced_content_to_file(file_path, replaced_lines):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            original_lines = file.readlines()

        if replaced_lines != original_lines:  # Check if content was modified
            temp_file_path = file_path + '.tmp'
            with open(temp_file_path, 'w', encoding='utf-8-sig') as temp_file:
                temp_file.writelines(replaced_lines)

            with open(temp_file_path, 'r', encoding='utf-8-sig') as temp_file:
                temp_content = temp_file.readlines()

            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.writelines(temp_content)

            backup_filepath = generate_unique_backup_filename(file_path)
            shutil.copy2(file_path, backup_filepath)
            print(Fore.GREEN + Back.WHITE + f"File {file_path} has been backed up to {backup_filepath}." + Fore.RESET + Back.RESET)

            shutil.move(temp_file_path, file_path)
            print(Fore.GREEN + Back.WHITE + f"File {file_path} has been successfully modified." + Fore.RESET + Back.RESET)
        else:
            print(Fore.YELLOW + Back.WHITE + f"File {file_path} was not modified, no backup needed." + Fore.RESET + Back.RESET)
    except (IOError, OSError) as e:
        print(f"Failed to write file {file_path}: {e}")
    except Exception as e:
        print(f"Unknown error occurred: {e}")

if __name__ == "__main__":
    # Compatible with both exe and py script
    if getattr(sys, 'frozen', False):
        work_dir = os.path.dirname(sys.executable)
    else:
        work_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(work_dir)
    print(f"Current working directory switched to: {work_dir}")

    init()

    print(Fore.MAGENTA + Back.WHITE + "IMPORTANT: Please backup your files before running this tool to avoid data loss. (The tool will automatically backup ini files)" + Fore.RESET + Back.RESET)
    print(Fore.MAGENTA + Back.WHITE + "Please read the instructions carefully before use." + Fore.RESET + Back.RESET)
    input("Press Enter to continue...")

    try:
        all_files_and_dirs, ini_files = list_all_files_and_dirs('.')
    except (IOError, OSError) as e:
        print(f"Failed to access or list INI files: {e}")
        input("Press Enter to exit")
        exit()
    
    if not ini_files:
        print("No .ini files found that need modification.")
        input("Press Enter to exit")
        exit()

    for f in ini_files:
        try:
            replaced_lines = replace_strings_in_file(f)
            if replaced_lines:
                write_replaced_content_to_file(f, replaced_lines)
        except (IOError, OSError) as e:
            print(f"Failed to read file {f}: {e}")
        except Exception as e:
            print(f"Unknown error occurred: {e}")

    input("Press Enter to exit")
    exit()