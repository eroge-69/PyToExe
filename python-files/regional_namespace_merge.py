# Author: qwerty3yuiop
# Special Thanks:
#   SilentNightSound#7430 much of this guy's code was used for this
#   bloodreign616#4766 (pirilika) did much of the testing on this script
# V3.1 of Mod Merger/Toggle Creator Script utilizing namespaces

# Merges multiple mods into one, utilizing name spaces

# USAGE: Run this script in a folder which contains all the mods you want to merge
# So if you want to merge mods CharA, CharB, and CharC put all 3 folders in the same folder as this script and run it

# This script will automatically search through all subfolders to find mod ini files.
# It will not use .ini if that ini path/name contains "disabled"

# NOTE: This script will only function properly on mods generated using the 3dmigoto GIMI plugin

import os
import re
import argparse
import hashlib

def main():
    parser = argparse.ArgumentParser(description="Generates a merged mod from several mod folders")
    parser.add_argument("-r", "--root", type=str,  default=".",  help="Location to use to create mod")
    parser.add_argument("-u", "--unmerge", action="store_true", help="unmerge the regional mod")
    parser.add_argument("-v", "--vanilla", action="store_true",  help="exclude vanilla outifit as a part of the mod")
    parser.add_argument("-n", "--name", type=str,  default="master.ini", help="(not functional)")
    args = parser.parse_args()
    swap_unidentified = []
    swap_mondstadt = []
    swap_liyue = []
    swap_dragonspine = []
    swap_inazuma = []
    swap_enkanomiya = []
    swap_chasm = []
    swap_sumeru_forest = []
    swap_sumeru_desert = []
    swap_fontaine = []
    swap_teapot = []
    swap_chenyu = []
    swap_natlan = []
    # run delete mode if delete arguement is used
    if args.unmerge:
        unmerge_main(args.root)
        return
    
    print("\nGenshin Regional Mod Merger/Toggle Creator Script Utilizing Namespaces\n")
    
    print("\nEnsure the .ini files are the names of existing playable characters or how they're referred in modding. Otherwise this script won't detect them.")
    print("'merged' is an exception and works\n")

    # searches for files returns if none found
    print("\nSearching for .ini files")
    ini_files = collect_ini(args.root, args.name)
    if not ini_files:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        return
    # Place holder for the vanilla outfit
    for i, ini_file in enumerate(ini_files):
        print(f"\t{i}:  {ini_file}")
    # order of merge given by sorting the list ini_files
    print("\nThis script will merge using the order listed above (0 is the default the mod will start with, and it will cycle 0,1,2,3,4,0,1...etc)")
    print("If this is fine, please press ENTER. If not, please enter the order you want the script to merge the mods (example: 3 0 1 2)")
    print("If you enter less than the total number, this script will only merge those listed.\n")
    print("Vanilla outfit will be bound to the first value by default. You can list the number wherever you want like with all other files.")
    if args.vanilla:
        print("The vanilla outfit will be removed at the end it is safe to press ENTER or select an order you can still include vanilla if you add it to your order\n")
    ini_files = get_user_order(ini_files)
    if args.vanilla and ini_files[0] == None:
        ini_files.pop(0)
    for i, ini_file in enumerate(ini_files):
        if re.search(r'\b' + 'MON' + r'\b', ini_file):
            swap_mondstadt.append(i)
        if re.search(r'\b' + 'LIY' + r'\b', ini_file):
            swap_liyue.append(i)
        if re.search(r'\b' + 'DRA' + r'\b', ini_file):
            swap_dragonspine.append(i)
        if re.search(r'\b' + 'INA' + r'\b', ini_file):
            swap_inazuma.append(i)
        if re.search(r'\b' + 'ENK' + r'\b', ini_file):
            swap_enkanomiya.append(i)
        if re.search(r'\b' + 'CHA' + r'\b', ini_file):
            swap_chasm.append(i)
        if re.search(r'\b' + 'SUF' + r'\b', ini_file):
            swap_sumeru_forest.append(i)
        if re.search(r'\b' + 'SUD' + r'\b', ini_file):
            swap_sumeru_desert.append(i)
        if re.search(r'\b' + 'FON' + r'\b', ini_file):
            swap_fontaine.append(i)
        if re.search(r'\b' + 'TEA' + r'\b', ini_file):
            swap_teapot.append(i)
        if re.search(r'\b' + 'UNI' + r'\b', ini_file):
            swap_unidentified.append(i)
        if re.search(r'\b' + 'CHE' + r'\b', ini_file):
            swap_chenyu.append(i)
        if re.search(r'\b' + 'NAT' + r'\b', ini_file):
            swap_natlan.append(i)
    
    # the name of the namespace cause I don't want to deal with finding it
    keywords = [ 
        "TravelerGirl", "Lumine", "Aether", "TravelerBoy", "Paimon", "Albedo", "Amber", "AmberCN", "JeanCN", "MonaCN", "RosariaCN", "Barbara", "Bennett", "Diluc", "Diona", "Eula", 
        "Fischl", "FischlHighness", "Jean", "Kaeya", "Klee", "Lisa", "Mika", "Mona", "Noelle", "Razor", "Rosaria", "Sucrose", "Venti", "Wanderer", "Beidou", "Baizhu", "Chongyun", 
        "Ganyu", "HuTao", "Hu Tao", "Keqing", "LanYan", "Lan Yan", "Ningguang", "Qiqi", "Shenhe", "Xiangling", "Xiao", "Xingqiu", "Xinyan", "Yanfei", 
        "Yaoyao", "Yao yao", "Yelan", "YunJin", "Yun Jin", "Zhongli", "AratakiItto", "Itto", "Chiori", "Gorou", "KaedeharaKazuha", "Kazuha", "KamisatoAyaka", "Ayaka", 
        "KamisatoAyato", "Ayato", "Kirara", "KujouSara", "Sara", "Kujou", "Shinobu", "KukiShinobu", "Kuki", "RaidenShogun", "Raiden", "Shogun", "Kokomi", "Furinna",
        "SangonomiyaKokomi", "Sayu", "Heizou", "ShikanoinHeizou", "Thoma", "YaeMiko", "Yae", "Miko", "Yoimiya", "YumemizukiMizuki", "Mizuki",
        "Alhaitham", "Candace", "Collei", "Cyno", "Dehya", "Dori", "Faruzan", "Kaveh", "Layla", "Nahida", "Nilou", "FurinaOusia", "FurinaPneuma",
        "Lyney", "Lynette", "Freminet", "Neuvillette", "Wriothesley", "Furina", "Funingna", "FurinaDark", "FurinaLight", "FurinaWhite", "Navia", "Clorinde", "Charlotte", "Chevreuse", "Sigewinne", "Emilie",
        "Kachina", "Kinich", "Mualani", "Xilonen", "Chasca", "Ororon", "Mavuika", "Citlali", "Iansan", "Childe", "Tartaglia", "Varesa", "Vanesa", "Aloy", "Skirk", "Master", "Dainsleif" 
    ]
    keywords_lower = {k.lower() for k in keywords}

    print("\nPlease enter the name of the object this merged mod is for (no spaces). Be sure the name corresponds exactly, case insensitive, but no typos") 
    print("Otherwise you'll not be able to unmerge it\n")
    
    while True:

        name = input().strip()

        if not name:
            print("\nPlease enter a name.\n")
            continue

        if name.lower() in keywords_lower:
            break

        print("\nNot a name of a playable character or a typo. Enter name again\n")

    # sets key to cycle forward
    print("\nPlease enter the key that will be used to cycle mods. Key must be a single letter")
    print("Be sure the key isn't used by the mods in your regional folder. Or else they'll conflict with one another.\n")
    key = input()
    while not key or len(key) != 1:
        print("\nKey not recognized, must be a single letter\n")
        key = input()
    key = key.lower()

    # generating backup inis
    print("generating backups")
    generate_backup(ini_files)

    # Generates the namespace for the master file
    constants =    f"namespace = {name}\Master\n; Constants ---------------------------\n\n"
    overrides =    "; Overrides ---------------------------\n\n"

    swapvar = "swapvar"
    constants += f"[Constants]\nglobal persist ${swapvar} = 0\n"
    constants +="""global persist $swap_unidentified = -1
global persist $swap_mondstadt = -1
global persist $swap_liyue = -1
global persist $swap_dragonspine = -1
global persist $swap_inazuma = -1
global persist $swap_enkanomiya = -1
global persist $swap_chasm = -1
global persist $swap_sumeru_forest = -1
global persist $swap_sumeru_desert = -1
global persist $swap_fontaine = -1
global persist $swap_teapot = -1
global persist $swapvar_not_assigned = -1
global persist $swap_chenyu = -1
global persist $swap_natlan = -1
global persist $isfirstload = 1
global $not_assigned = 0
global persist $regioncheck 
"""
    constants += f"global $active\n"
    constants += "global $creditinfo = 0\n"
    constants += f"\n[KeySwapMondstadt]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 1)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_mondstadt = "
    constants += ','.join(str(x) for x in swap_mondstadt)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapLiyue]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 2)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_liyue = "
    constants += ','.join(str(x) for x in swap_liyue)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapDragonspine]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 3)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_dragonspine = "
    constants += ','.join(str(x) for x in swap_dragonspine)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapInazuma]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 4)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_inazuma = "
    constants += ','.join(str(x) for x in swap_inazuma)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapEnkanomiya]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 5)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_enkanomiya = "
    constants += ','.join(str(x) for x in swap_enkanomiya)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapChasm]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 6)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_chasm = "
    constants += ','.join(str(x) for x in swap_chasm)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapSumeruForest]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 7)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_sumeru_forest = "
    constants += ','.join(str(x) for x in swap_sumeru_forest)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapSumeruDesert]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 8)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_sumeru_desert = "
    constants += ','.join(str(x) for x in swap_sumeru_desert)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapFontaine]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 9)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_fontaine = "
    constants += ','.join(str(x) for x in swap_fontaine)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapTeapot]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 10)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_teapot = "
    constants += ','.join(str(x) for x in swap_teapot)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapUnidentified]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 0)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_unidentified = "
    constants += ','.join(str(x) for x in swap_unidentified)
    constants += f"\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapNotAssgigned]\n"
    constants += f"condition = ($active == 1 && $not_assigned == 1)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swapvar_not_assigned = "
    constants += ','.join([str(x) for x in range(len(ini_files))])
    constants += f"\n"
    constants += f"$isfirstload = 0\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapChenyu]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 11)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_chenyu = "
    constants += ','.join(str(x) for x in swap_chenyu)
    constants += f"\n"
    constants += f"$isfirstload = 0\n"
    constants += f"$creditinfo = 0\n"
    constants += f"\n[KeySwapNatlan]\n"
    constants += f"condition = ($active == 1 && $regioncheck == 12)||$isfirstload == 1\n"
    constants += f"key = {key}\ntype = cycle\n"
    constants += f"$swap_natlan = "
    constants += ','.join(str(x) for x in swap_natlan)
    constants += f"\n\n"

    constants += f"[Present]\n"
    constants += f"post $active = 0\n"
    constants +=f"post $not_assigned = 0\n"
    constants +=r'$regioncheck = $\global\region\regioncheck'
    constants +=f"\nrun = CommandListCheckAssigned\n"
    constants +=f"run = CommandListSetOutfit\n"
    # this gets the position override and may cause problems if mods for multiple charters are added as that character will not be detected
    overrides += f"[TextureOverride{name}Position]\n"
    for file in ini_files:
        if file != None:
            temp = get_position_hash(str(file))
            if temp != ";None found\n":
                overrides += temp
                break
    overrides += "$active = 1\n"
    overrides  +=    "; CommandList -------------------------\n\n"
    overrides +="""
[CommandListCheckAssigned]
if $regioncheck == 0 && $swap_unidentified == -1
	$not_assigned = 1
else if $regioncheck == 1 && $swap_mondstadt == -1
	$not_assigned = 1
else if $regioncheck == 2 && $swap_liyue == -1
	$not_assigned = 1
else if $regioncheck == 3 && $swap_dragonspine == -1
	$not_assigned = 1
else if $regioncheck == 4 && $swap_inazuma == -1
	$not_assigned = 1
else if $regioncheck == 5 && $swap_enkanomiya == -1
	$not_assigned = 1
else if $regioncheck == 6 && $swap_chasm == -1
	$not_assigned = 1
else if $regioncheck == 7 && $swap_sumeru_forest == -1
	$not_assigned = 1
else if $regioncheck == 8 && $swap_sumeru_desert == -1
	$not_assigned = 1
else if $regioncheck == 9 && $swap_fontaine == -1
	$not_assigned = 1
else if $regioncheck == 10 && $swap_teapot == -1
	$not_assigned = 1
else if $regioncheck == 11 && $swap_chenyu == -1
	$not_assigned = 1
else if $regioncheck == 12 && $swap_natlan == -1
	$not_assigned = 1
endif

[CommandListSetOutfit]
if $regioncheck == 0 && $swap_unidentified != -1
	$swapvar = $swap_unidentified
else if $regioncheck == 1 && $swap_mondstadt != -1
	$swapvar = $swap_mondstadt
else if $regioncheck == 2 && $swap_liyue != -1
	$swapvar = $swap_liyue
else if $regioncheck == 3 && $swap_dragonspine != -1
	$swapvar = $swap_dragonspine		
else if $regioncheck == 4 && $swap_inazuma != -1
	$swapvar = $swap_inazuma
else if $regioncheck == 5 && $swap_enkanomiya != -1
	$swapvar = $swap_enkanomiya
else if $regioncheck == 6 && $swap_chasm != -1
	$swapvar = $swap_chasm
else if $regioncheck == 7 && $swap_sumeru_forest != -1
	$swapvar = $swap_sumeru_forest
else if $regioncheck == 8 && $swap_sumeru_desert != -1
	$swapvar = $swap_sumeru_desert
else if $regioncheck == 9 && $swap_fontaine != -1
	$swapvar = $swap_fontaine
else if $regioncheck == 10 && $swap_teapot != -1
	$swapvar = $swap_teapot
else if $regioncheck == 11 && $swap_chenyu != -1
	$swapvar = $swap_chenyu
else if $regioncheck == 12 && $swap_natlan != -1
	$swapvar = $swap_natlan
else
	$swapvar = $swapvar_not_assigned
endif

"""
    overrides += "\n"
    # adds the neccessary if statements into the ini files
    print("Modifying inis...")
    count = 0
    for ini_file in ini_files:
        if ini_file != None:
            edit_ini(str(ini_file),name,count)
        count += 1
    
    # removes the null value now
    try:
        ini_files.remove(None)
    except ValueError:
        print()
    print("Printing results")
    result = f"; Merged Mod: {', '.join([x for x in ini_files])}\n\n"
    result += constants
    result += overrides
    result += "\n\n"
    result += "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script utilizing namespaces\n"
    result += "; If you have any issues or find any bugs dm qwerty3yuiop on discord or leave a comment on game banana"

    with open(f"Master{name}.ini", "w", encoding="utf-8") as f:
        f.write(result)

    print("All operations completed")

# delete script method
def unmerge_main(root):
    print("\nNamespace Merged Mod Unmerger\n")
    print("\nTHIS SCRIPT WILL UNMERGE YOUR REGIONAL FOLDER BY DELETING THE MASTER INI AND RESTORING INDIVIDUAL MODS")
    print("\nEXPERIMENTAL FEATURE, USE WITH CAUTION AND MAKE BACKUPS")
    print("press ENTER to proceed or enter anything else to exit")
    userin = input()
    if userin != "":
        print("exiting")
        return
    # searches for active files returns if none found
    print("\nSearching for paths containing active inis")
    ini_paths = collect_ini(root, "none")
    restored_ini = collect_inidisabled(root, "none")
    if not ini_paths:
        print("Found no .ini files - make sure the mod folders are in the same folder as this script.")
        return
    if not restored_ini:
        print("Missing backcup .ini files, be sure there are .ini file with 'disablednamespaceregional' for every mod you have in your regional folder")
        return
    # lists all found files
    print("\nFound:")
    for i, ini_file in enumerate(ini_paths):
        print(f"\t{i}:  {ini_file}")
    print("All inis displayed above will be deleted and their backups will be restored")
    print("Press ENTER to proceed with the delete or enter a number to remove a file from the deletion list.")
    print("ONLY ENTER ONE NUMBER! you will be able to remove other paths from deletion list")
    userin = input()
    while userin != "":
        try:
            ini_paths.pop(int(userin))
            print(f"\nremoved path number {userin}")
        except:
            print(f"\nUnable to remove {userin} from deletion list")
        finally:
            print("Current Deletion List:")
            for i, ini_file in enumerate(ini_paths):
                print(f"\t{i}:  {ini_file}")
        print("Press ENTER to proceed with the delete or enter a number to remove a file from the deletion list.")
        print("ONLY ENTER ONE NUMBER! you will be able to remove other paths from deletion list")
        userin = input()
    try:
        for file in ini_paths:
            # deletes the file
            os.remove(str(file))
        
        for file in restored_ini:
            # renames the backup file
            try:
                rename_file(file)
            except:
                print(f"No back up file found for {file}")
            
        print("All operations completed")
    except:
        print("something went wrong")

# Collects all .ini files from current folder and subfolders
def collect_ini(path, ignore):

    keywords = [ 
        "merged", "TravelerGirl", "Lumine", "Aether", "TravelerBoy", "Paimon", "Albedo", "Amber", "AmberCN", "JeanCN", "MonaCN", "RosariaCN", "Barbara", "Bennett", "Diluc", "Diona", "Eula", 
        "Fischl", "FischlHighness", "Jean", "Kaeya", "Klee", "Lisa", "Mika", "Mona", "Noelle", "Razor", "Rosaria", "Sucrose", "Venti", "Wanderer", "Beidou", "Baizhu", "Chongyun", 
        "Ganyu", "HuTao", "Hu Tao", "Keqing", "LanYan", "Lan Yan", "Ningguang", "Qiqi", "Shenhe", "Xiangling", "Xiao", "Xingqiu", "Xinyan", "Yanfei", 
        "Yaoyao", "Yao yao", "Yelan", "YunJin", "Yun Jin", "Zhongli", "AratakiItto", "Itto", "Chiori", "Gorou", "KaedeharaKazuha", "Kazuha", "KamisatoAyaka", "Ayaka", 
        "KamisatoAyato", "Ayato", "Kirara", "KujouSara", "Sara", "Shinobu", "KukiShinobu", "RaidenShogun", "Raiden", "Shogun", "Kokomi", "Furinna", "Frostbound Vengeance - Eula",
        "SangonomiyaKokomi", "Sayu", "Heizou", "ShikanoinHeizou", "Thoma", "Kuki", "Kujou", "YaeMiko", "Yae", "Miko", "Yoimiya", "YumemizukiMizuki", "Mizuki", "Fortune Dreams - Nilou",
        "Alhaitham", "Candace", "Collei", "Cyno", "Dehya", "Dori", "Faruzan", "Kaveh", "Layla", "Nahida", "Nilou", "Harbinger Furina", "FurinaOusia", "FurinaPneuma",
        "Lyney", "Lynette", "Freminet", "Neuvillette", "Wriothesley", "Furina", "Funingna", "FurinaDark", "FurinaLight", "FurinaWhite", "Navia", "Clorinde", "Charlotte", "Chevreuse", "Sigewinne", "Emilie",
        "Kachina", "Kinich", "Mualani", "Xilonen", "Chasca", "Ororon", "Mavuika", "Citlali", "Iansan", "Childe", "Tartaglia", "Varesa", "Vanesa", "Aloy", "BlingYelan", "Skirk", "Master", "Dainsleif" 
    ]
    keywords += ["Master" + name for name in keywords]

    ini_files = []
    keywords = [kw.lower() for kw in keywords]
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if "disabled" in file.lower() or ignore.lower() in file.lower():
                continue
            name, ext = os.path.splitext(file)
            if ext.lower() == ".ini" and any(keyword in name.lower() for keyword in keywords):
                ini_files.append(os.path.join(root, file))
    return ini_files

# Collects all .ini files that has "DISABLEDnamespaceregional"
def collect_inidisabled(path, ignore):
    ini_files = []
    target_string = "disablednamespaceregional".lower()  # Case insensitive match

    for root, _, files in os.walk(path):
        for file in files:
            
            name, ext = os.path.splitext(file)
            if ext.lower() == ".ini" and target_string in name.lower():
                ini_files.append(os.path.join(root, file))
       
    return ini_files

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

# Editing existing inis and adding needed text at the end for shader and texture overrides.
def edit_ini(path, name, num):
    with open(path, 'r') as file:
        lines = file.readlines()
    found = False
    count = 0
    max = len(lines)-1
    block = []
    with open(path, 'w') as file:
        for line in lines:
            # Ends the if when a line with [ or when end of file is reached
            # meant to end on next overide
            if found and line.startswith('[') or count == max:
                block.append(line)
                line = comment_fix(block)
                block = []
                found = False
            # if there is already a match priority remove it
            elif found and line.lower().startswith('match_priority'):
                block.append("")
            # adds a tab to every line in the if
            elif found:
                line = "\t" + line
                block.append(line)
            # looks for lines that start with a hash and starts an if statement.
            elif line.strip().lower().startswith('hash = ') or line.strip().lower().startswith('hash='):
                # adds namespace also this line is by ricochet_7
                line = line + f'match_priority = {num}\n' + f'if $\{name}\Master\swapvar=={num}\n'
                found = True
                block.append(line)
            if not found:
                file.write(line)
            count += 1

# makes sure to place the endif immediatly after code to be enclosed
def comment_fix(block):
    index = len(block) - 1
    # cycle from the bottom
    for line in reversed(block):
        # If text that is not ; "" [ are found, end if is placed there
        if not line.strip().startswith(';') and not line.strip().startswith('[') and not line.strip() == "":
            block[index] = block[index].rstrip()+"\nendif\n\n"
            break
        # removes any indentation given to comments as a result of the previous function
        elif line.strip().startswith(';'):
            block[index] = block[index].lstrip()
        index -= 1
    line = ""
    for x in block:
        line = line + x
    block = []
    return line

# makes a copy of a file that is DISABLED
def generate_backup(file_list):
    for file_path in file_list:
        if file_path != None:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            new_file_path = os.path.join(dir_name, 'DISABLEDnamespaceregional' + base_name)
            with open(file_path, 'r') as original_file, open(new_file_path, 'w') as new_file:
                new_file.write(original_file.read())

# finds the position override of a a character and returns it
def get_position_hash(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        found = False
        for line in lines:
            # Ends the if when a line with [] or ; is found
            if line.startswith('[TextureOverride') and line.endswith('Position]\n'):
                found = True
            if found and (line.strip().lower().startswith('hash = ') or line.strip().lower().startswith('hash=')):
                return line
        return ";None found\n"
    
# renames file
def rename_file(file_path):
    if file_path != None:
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        
        # Define the target string to remove (case insensitive)
        target_string = "DISABLEDnamespaceregional"

        # Remove the target string from the filename (case insensitive)
        new_base_name = base_name.replace(target_string, "").replace(target_string.lower(), "")

        # Construct full paths
        old_path = os.path.join(dir_name, base_name)
        new_path = os.path.join(dir_name, new_base_name)

        # Rename the file
        os.rename(old_path, new_path)

if __name__ == "__main__":
    main()
    
