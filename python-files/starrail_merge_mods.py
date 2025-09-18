# Author: SilentNightSound#7430
# Modified by Sora_
# Special Thanks:
#   Takoyaki#0697 (for demonstrating principle and creating the first proof of concept)
#   HazrateGolabi#1364 (for implementing the code to limit toggles to the on-screen character)

# Merges multiple mods into one for star rail, which can be toggled in-game by pressing a key

# USAGE: Run this script in a folder which contains all the mods you want to merge
# So if you want to merge mods CharA, CharB, and CharC put all 3 folders in the same folder as this script and run it

# This script will automatically search through all subfolders to find mod ini files.
# It will not use .ini if that ini path/name contains "disabled"

# NOTE: This script will only function on mods generated using the 3dmigoto GIMI plugin

import os
import re
import argparse
import hashlib

def get_max_vertex_count(ini_files):
    max_vertex_count = 0
    for ini_file in ini_files:
        with open(ini_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 查找override_vertex_count的值
            match = re.search(r'override_vertex_count\s*=\s*(\d+)', content)
            if match:
                vertex_count = int(match.group(1))
                if vertex_count > max_vertex_count:
                    max_vertex_count = vertex_count
    return max_vertex_count

def is_file_identical(file1, file2):
    """比较两个文件是否完全相同"""
    if not os.path.exists(file1) or not os.path.exists(file2):
        return False
    
    if os.path.getsize(file1) != os.path.getsize(file2):
        return False
    
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            while True:
                chunk1 = f1.read(4096)
                chunk2 = f2.read(4096)
                if chunk1 != chunk2:
                    return False
                if not chunk1:
                    break
        return True
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Generates a merged mod from several mod folders")
    parser.add_argument("-r", "--root", type=str,  default=".",  help="Location to use to create mod")
    parser.add_argument("-s", "--store", action="store_true", help="Use to keep the original .ini files enabled after completion")
    parser.add_argument("-e", "--enable", action="store_true", help="Re-enable disabled .ini files")
    parser.add_argument("-n", "--name", type=str,  default="merged.ini", help="Name of final .ini file")
    parser.add_argument("-k", "--key", type=str, default="", help="Key to press to switch mods")
    parser.add_argument("-c", "--compress",  action="store_true", help="Makes the output mods as small as possible (warning: difficult to reverse, have backups)")
    parser.add_argument("-a", "--active", action="store_true",  default=True, help="Only active character gets swapped when swapping)")
    parser.add_argument("-ref", "--reflection", action="store_true", help="Applies reflection fix for 3.0+ characters")

    args = parser.parse_args()
    print("\nStar Rail Mod Merger/Toggle Creator Script\n")

    if args.active:
        print("Setting to swap only the active(on-screen) character")

    if args.enable:
        print("Re-enabling all .ini files")
        enable_ini(args.root)
        print()

    if not args.store:
        print("\nWARNING: Once this script completes, it will disable all .ini files used to generate the merged mod (which is required in order for the final version to work without conflicts)")
        print("You can prevent this behaviour by using the -s flag")
        print("This script also has the ability to re-enable all mods in the current folder and all subfolders by using the -e flag - use this flag if you need to regenerate the merged ini again")

    if args.compress:
        print("\nWARNING2: The -c/--compress option makes the output smaller, but it will be difficult to retrieve the original mods from the merged one. MAKE SURE TO HAVE BACKUPS, and consider only using option after you are sure everything is good")

    print("\nSearching for .ini files")
    ini_files = collect_ini(args.root, args.name)

    max_vertex_count = get_max_vertex_count(ini_files)
    print(f"Max vertex count found: {max_vertex_count}")

    if not ini_files:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        print("If using this script on a group of files that are already part of a toggle mod, use -e to enable .ini and regenerate the merge ini")
        return

    print("\nFound:")
    for i, ini_file in enumerate(ini_files):
        print(f"\t{i}:  {ini_file}")

    print("\nThis script will merge using the order listed above (0 is the default the mod will start with, and it will cycle 0,1,2,3,4,0,1...etc)")
    print("If this is fine, please press ENTER. If not, please enter the order you want the script to merge the mods (example: 3 0 1 2)")
    print("If you enter less than the total number, this script will only merge those listed.\n")
    ini_files = get_user_order(ini_files)

    if args.key:
        key = args.key
    else:
        print("\nPlease enter the key that will be used to cycle mods (can also enter this with -k flag, or set later in .ini). Key must be a single letter\n")
        key = input()
        while not key or len(key) != 1:
            print("\nKey not recognized, must be a single letter\n")
            key = input()
        key = key.lower()

    constants =    "; Constants ---------------------------\n\n"
    overrides =    "; Overrides ---------------------------\n\n"
    shader    =    "; Shader ------------------------------\n\n"
    commands  =    "; CommandList -------------------------\n\n"
    resources =    "; Resources ---------------------------\n\n"

    swapvar = "swapvar"
    constants += f"[Constants]\nglobal persist ${swapvar} = 0\n"
    if args.active:
        constants += f"global $active\n"
    if args.reflection:
        constants += f"global $reflection\n"
    constants += "global $creditinfo = 0\n"
    constants += f"\n[KeySwap]\n"
    if args.active:
        constants += f"condition = $active == 1\n"
    constants += f"key = {key}\ntype = cycle\n${swapvar} = {','.join([str(x) for x in range(len(ini_files))])}\n$creditinfo = 0\n\n"
    if args.active or args.reflection:
        constants += f"[Present]\n"
    if args.active:
        constants += f"post $active = 0\n"
    if args.reflection:
        constants += f"post $reflection = 0\n"



    print("Parsing ini sections")
    all_mod_data = []
    ini_group = 0
    for ini_file in ini_files:
        with open(ini_file, "r", encoding="utf-8") as f:
            ini_text = ["["+x.strip() for x in f.read().split("[")]
            for section in ini_text[1:]:
                mod_data = parse_section(section)
                mod_data["location"] = os.path.dirname(ini_file)
                mod_data["ini_group"] = ini_group
                all_mod_data.append(mod_data)
        ini_group += 1

    if [x for x in all_mod_data if "name" in x and x["name"].lower() == "creditinfo"]:
        constants += "run = CommandListCreditInfo\n\n"
    else:
        constants += "\n"

    #
    # Albedo Code Trying to adapt for multipleShaderFixes
    #
    
    seen = set()

    for i in range(0, 100):
        transparency_value = f"transparency{i:02d}"
        
        # Initialize the transparency_blends
        blend_factor = [None] * 4
        
        # Initialize a flag to indicate when we found a matching transparency configuration
        found_transparency = False
        
        # Initialize a flag to indicate when a duplicate blend factor group is found
        duplicate_found = False

        for data in all_mod_data:
            # If the current data is a matching transparency configuration
            if "name" in data and data["name"].lower() == transparency_value.lower():
                found_transparency = True
                print(f"Found CustomShaderTransparency{i}")
                print(data)
            
            # If we found a matching transparency configuration and the current data has a blend factor
            if found_transparency and "[0]" in data:
                blend_factor[0] = float(data.get("[0]"))
            elif found_transparency and "[1]" in data:
                blend_factor[1] = float(data.get("[1]"))
            elif found_transparency and "[2]" in data:
                blend_factor[2] = float(data.get("[2]"))
            elif found_transparency and "[3]" in data:
                blend_factor[3] = float(data.get("[3]"))
            
            # If we have fetched all blend factors
            if None not in blend_factor:
                # Convert blend_factor list to a tuple to make it hashable
                blend_factor_tuple = tuple(blend_factor)
                
                if blend_factor_tuple in seen:
                    # Set the duplicate_found flag to True and skip this iteration if we've seen this blend factor group before
                    duplicate_found = True
                    break
                
                # Add the current blend_factor group to the seen set
                seen.add(blend_factor_tuple)
                
                print(blend_factor[0])
                print(blend_factor[1])
                
                # Construct the CustomShaderTransparency block with the extracted blend factors
                shader += f"""[CustomShaderTransparency{i:02d}]\nblend = ADD BLEND_FACTOR INV_BLEND_FACTOR\nblend_factor[0] = {blend_factor[0]}\nblend_factor[1] = {blend_factor[1]}\nblend_factor[2] = {blend_factor[2]}\nblend_factor[3] = {blend_factor[3]}\nhandling = skip\ndrawindexed = auto\n\n"""
                
                # Reset the flag and the blend factors for the next iteration
                found_transparency = False
                blend_factor = [None] * 4
        
        # If a duplicate blend factor group was found, skip this iteration of the outer loop
        if duplicate_found:
            continue



    print("Calculating overrides and resources")
    command_data = {}
    seen_hashes = {}
    reflection = {}
    n = 1
    
    # 创建一个字典来存储Draw类型的Override信息
    draw_overrides = {}
    
    for i in range(len(all_mod_data)):
        # Overrides. Since we need these to generate the command lists later, need to store the data
        if "hash" in all_mod_data[i]:
            index = -1
            if "match_first_index" in all_mod_data[i]:
                index = all_mod_data[i]["match_first_index"]
            
            # 如果是Draw类型的Override，先存储起来，后面单独处理
            if "Draw" in all_mod_data[i]["name"]:
                hash_key = (all_mod_data[i]["hash"], index)
                if hash_key not in draw_overrides:
                    draw_overrides[hash_key] = {"max_vertex_count": 0, "data": None}
                
                if "override_vertex_count" in all_mod_data[i]:
                    vertex_count = int(all_mod_data[i]["override_vertex_count"])
                    if vertex_count > draw_overrides[hash_key]["max_vertex_count"]:
                        draw_overrides[hash_key]["max_vertex_count"] = vertex_count
                        draw_overrides[hash_key]["data"] = all_mod_data[i]
                continue
            
            # First time we have seen this hash, need to add it to overrides
            if (all_mod_data[i]["hash"], index) not in command_data:
                command_data[(all_mod_data[i]["hash"], index)] = [all_mod_data[i]]
                overrides += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}]\nhash = {all_mod_data[i]['hash']}\n"
                if index != -1:
                    overrides += f"match_first_index = {index}\n"
                # These are custom commands GIMI implements, they do not need a corresponding command list
                if "VertexLimitRaise" not in all_mod_data[i]["name"]:
                    overrides += f"run = CommandList{all_mod_data[i]['name']}\n"
                if index != -1 and args.reflection:
                    overrides += f"ResourceRef{all_mod_data[i]['name']}Diffuse = reference ps-t1\nResourceRef{all_mod_data[i]['name']}LightMap = reference ps-t2\n$reflection = {n}\n"
                    reflection[all_mod_data[i]['name']] = f"ResourceRef{all_mod_data[i]['name']}Diffuse,ResourceRef{all_mod_data[i]['name']}LightMap,{n}"
                    n+=1
                if args.active:
                    if "Blend" in all_mod_data[i]["name"]:
                        overrides += f"$active = 1\n"

                overrides += "\n"
            # Otherwise, we have seen the hash before and we just need to append it to the commandlist
            else:
                command_data[(all_mod_data[i]["hash"], index)].append(all_mod_data[i])
        elif "header" in all_mod_data[i] and "CommandList" in all_mod_data[i]["header"]:
            command_data.setdefault((all_mod_data[i]["name"],0),[]).append(all_mod_data[i])
        # Resources
        elif "filename" in all_mod_data[i] or "type" in all_mod_data[i]:
            resources += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}.{all_mod_data[i]['ini_group']}]\n"
            for command in all_mod_data[i]:
                if command in ["header", "name", "location", "ini_group"]:
                    continue
                if command == "filename":
                    file_path = f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}"
                    
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        # 文件已被删除，查找替代路径
                        found_alternative = False
                        for alt_id, alt_path in seen_hashes.items():
                            if os.path.basename(file_path) == os.path.basename(alt_path) and os.path.exists(alt_path):
                                resources += f"{command} = {alt_path}\n"
                                found_alternative = True
                                break
                        
                        if not found_alternative:
                            # 如果找不到替代文件，保留原始路径（即使文件不存在）
                            resources += f"{command} = {file_path}\n"
                        continue
                    
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    try:
                        # 读取文件内容计算哈希
                        with open(file_path, "rb") as f:
                            file_content = f.read()
                            file_hash = hashlib.sha1(file_content).hexdigest()
                        
                        # 对于.buf文件，使用更严格的比较
                        if file_ext == '.buf':
                            # 检查是否有相同哈希但内容可能不同的文件
                            identical_found = False
                            existing_path = None
                            
                            for existing_id, existing_file in seen_hashes.items():
                                if existing_id.startswith(file_hash) and os.path.exists(existing_file) and is_file_identical(file_path, existing_file):
                                    identical_found = True
                                    existing_path = existing_file
                                    break
                            
                            if identical_found and args.compress:
                                resources += f"{command} = {existing_path}\n"
                                if file_path != existing_path and os.path.exists(file_path):
                                    print(f"Removing duplicate .buf file: {file_path}")
                                    os.remove(file_path)
                            else:
                                # 使用哈希+文件名作为唯一标识
                                unique_id = f"{file_hash}_{os.path.basename(file_path)}"
                                seen_hashes[unique_id] = file_path
                                resources += f"{command} = {file_path}\n"
                        else:
                            # 对于其他文件，使用标准哈希比较
                            if file_hash in seen_hashes and args.compress and os.path.exists(seen_hashes[file_hash]):
                                resources += f"{command} = {seen_hashes[file_hash]}\n"
                                if file_path != seen_hashes[file_hash] and os.path.exists(file_path):
                                    print(f"Removing duplicate file: {file_path}")
                                    os.remove(file_path)
                            else:
                                seen_hashes[file_hash] = file_path
                                resources += f"{command} = {file_path}\n"
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
                        resources += f"{command} = {file_path}\n"
                else:
                    resources += f"{command} = {all_mod_data[i][command]}\n"
            resources += "\n"

    # 处理Draw类型的Override，将它们插入到正确的位置
    for hash_key, draw_data in draw_overrides.items():
        hash_value, index = hash_key
        model = draw_data["data"]
        if model:
            # 找到Draw类型Override应该插入的位置
            override_name = f"{model['header']}{model['name']}"
            insert_pos = overrides.find(f"[{override_name}]")
            
            if insert_pos != -1:
                # 找到该Override的结束位置
                end_pos = overrides.find("\n\n", insert_pos)
                if end_pos == -1:
                    end_pos = len(overrides)
                
                # 构建新的Override内容
                new_override = f"[{override_name}]\n"
                new_override += f"hash = {hash_value}\n"
                if index != -1:
                    new_override += f"match_first_index = {index}\n"
                
                # 添加所有属性，但使用最大的vertex_count
                for command in model:
                    if command in ["header", "name", "hash", "match_first_index", "location", "ini_group", "run"]:
                        continue
                    if command == "override_vertex_count":
                        new_override += f"{command} = {draw_data['max_vertex_count']}\n"
                    else:
                        new_override += f"{command} = {model[command]}\n"
                new_override += "\n"
                
                # 替换原有的Override
                overrides = overrides[:insert_pos] + new_override + overrides[end_pos+2:]
            else:
                # 如果没有找到现有的Override，则在末尾添加
                overrides += f"[{override_name}]\n"
                overrides += f"hash = {hash_value}\n"
                if index != -1:
                    overrides += f"match_first_index = {index}\n"
                
                for command in model:
                    if command in ["header", "name", "hash", "match_first_index", "location", "ini_group", "run"]:
                        continue
                    if command == "override_vertex_count":
                        overrides += f"{command} = {draw_data['max_vertex_count']}\n"
                    else:
                        overrides += f"{command} = {model[command]}\n"
                overrides += "\n"

    if args.reflection:
        print("Character Shader Fix")
        refresources = ''
        CommandPart = ['ReflectionTexture', 'Outline']
        shadercode = """
[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
discard_n\w+ r\d\.\w+\\n
lt r\d\.\w+, l\(0\.010000\), r\d\.\w+\\n
and r\d\.\w+, r\d\.\w+, r\d\.\w+\\n

[ShaderRegexCharOutline]
shader_model = ps_5_0
run = CommandListOutline
[ShaderRegexCharOutline.pattern]
mov o0\.w, l\(0\)\\n
mov o1\.xyz, r0\.xyzx\\n
        """
        shader += f"{shadercode}\n"
        for i in range(len(CommandPart)):
            ref  = f"[CommandList{CommandPart[i]}]\n"
            ref += f"if $reflection != 0\n\tif "
            for x in reflection:
                r = reflection[x].split(",")
                ref += f"$reflection == {r[2]}\n"
                ps = [['ps-t0','ps-t1'],['ps-t1','ps-t2']]
                ref += f"\t\t{ps[i][0]} = copy {r[0]}\n\t\t{ps[i][1]} = copy {r[1]}\n"
                ref += f"\telse if "
                if i == 0:
                    refresources += f"[{r[0]}]\n[{r[1]}]\n"
            ref = ref.rsplit("else if",1)[0] + "endif\n"
            ref += f"drawindexed=auto\n"
            ref += f"$reflection = 0\n"
            ref += f"endif\n\n"
            commands += ref

    print("Constructing command lists")
    tabs = 1

    for hash, index in command_data:
        commands += f"[CommandList{command_data[(hash, index)][0]['name']}]\nif "
        for model in command_data[(hash, index)]:
            commands += f"${swapvar} == {model['ini_group']}\n"
            for command in model:
                if command in ["header", "name", "hash", "match_first_index", "location", "ini_group"]:
                    continue

                if command == "endif":
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    commands += f"{command}"
                elif "else if" in command or "elif" in command:
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    # 修复等号问题
                    command_value = model[command]
                    # 更精确地修复 DRAW_TYPE 的等号问题
                    if "DRAW_TYPE" in command_value:
                        # 使用正则表达式来确保精确匹配和替换
                        command_value = re.sub(r'(DRAW_TYPE)\s*=\s*(\d+)', r'\1 == \2', command_value)
                    commands += f"{command} = {command_value}"
                    tabs += 1
                else:
                    for i in range(tabs):
                        commands += "\t"
                    if command[:2] == "if" or command[:7] == "else if":
                        commands += f"{command} == {model[command]}"
                    else:
                        commands += f"{command} = {model[command]}"
                    if command[:2] == "if":
                        tabs += 1
                    elif (command[:2] in ["vb", "ib", "ps", "vs", "th"] or "Resource" in model[command]) and model[command].lower() != "null":
                        commands += f".{model['ini_group']}"
                commands += "\n"
            commands += "else if "
        commands = commands.rsplit("else if",1)[0] + "endif\n\n"

    print("Printing results")
    result = f"; Merged Mod: {', '.join([x for x in ini_files])}\n\n"
    if args.reflection:
        result += f"{refresources}\n"
    result += constants
    result += shader
    result += overrides
    result += commands
    result += resources
    if args.reflection:
        result += "\n\n; For fixing green reflections and broken outlines colors on 3.0+ characters\n"
    else:
        result += "\n\n"
    result += "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script\n"

    result += "; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord"

    # 添加等号修复
    result = result.replace("elif DRAW_TYPE = 8", "elif DRAW_TYPE == 8")

    with open(args.name, "w", encoding="utf-8") as f:
        f.write(result)

    if not args.store:
        print("Cleanup and disabling ini")
        for file in ini_files:
            os.rename(file, os.path.join(os.path.dirname(file), "DISABLED") + os.path.basename(file))


    print("All operations completed")


# Collects all .ini files from current folder and subfolders
def collect_ini(path, ignore):
    ini_files = []
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if "disabled" in file.lower() or ignore.lower() in file.lower():
                continue
            if os.path.splitext(file)[1] == ".ini":
                ini_files.append(os.path.join(root, file))
    return ini_files

# Re-enables disabled ini files
def enable_ini(path):
    for root, dir, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == ".ini" and ("disabled" in root.lower() or "disabled" in file.lower()):
                print(f"\tRe-enabling {os.path.join(root, file)}")
                new_path = re.compile("disabled", re.IGNORECASE).sub("", os.path.join(root, file))
                os.rename(os.path.join(root, file), new_path)


# Gets the user's preferred order to merge mod files
def get_user_order(ini_files):

    choice = input()

    # User entered data before pressing enter
    while choice:
        choice = choice.strip().split(" ")

        if len(choice) > len(ini_files):
            print("\nERROR: please only enter up to the number of the original mods\n")
            choice = input()
        else:
            try:
                result = []
                choice = [int(x) for x in choice]
                if len(set(choice)) != len(choice):
                    print("\nERROR: please enter each mod number at most once\n")
                    choice = input()
                elif max(choice) >= len(ini_files):
                    print("\nERROR: selected index is greater than the largest available\n")
                    choice = input()
                elif min(choice) < 0:
                    print("\nERROR: selected index is less than 0\n")
                    choice = input()
                    print()
                else:
                    for x in choice:
                        result.append(ini_files[x])
                    return result
            except ValueError:
                print("\nERROR: please only enter the index of the mods you want to merge separated by spaces (example: 3 0 1 2)\n")
                choice = input()

    # User didn't enter anything and just pressed enter
    return ini_files


# Parses a section from the .ini file
def parse_section(section):
    mod_data = {}
    recognized_header = ("[TextureOverride", "[ShaderOverride", "[Resource", "[Constants", "[Present", "[CommandList", "[CustomShader")
    for line in section.splitlines():
        if not line.strip() or line[0] == ";":  # comments and empty lines
            continue

        # Headers
        for header in recognized_header:
            if header in line:
                # I give up on trying to merge the reflection fix, it's way too much work. Just re-apply after merging
                if "CommandListReflectionTexture" in line or "CommandListOutline" in line:
                    return {}
                mod_data["header"] = header[1:]
                mod_data["name"] = line.split(header)[1][:-1]
                break
        # Conditionals
        if "==" in line:
            key, data = line.split("==",1)
            mod_data[key.strip()] = data.strip()
        elif "endif" in line:
            key, data = "endif", ""
            mod_data[key.strip()] = data.strip()
        # Properties
        elif "=" in line:
            key, data = line.split("=")
            # See note on reflection fix above
            if "CharacterIB" in key or "ResourceRef" in key:
                continue

            mod_data[key.strip()] = data.strip()

    return mod_data


if __name__ == "__main__":
    main()