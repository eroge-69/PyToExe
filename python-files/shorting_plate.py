import os
import shutil
from tkinter import Tk, filedialog
import re

# Step 1: User selects the extracted testplan folder
Tk().withdraw()
source_folder = filedialog.askdirectory(title="Select Extracted Testplan Folder")

if not source_folder:
    print("No folder selected.")
    exit()

# Step 2: Create 'shorting_plate' folder inside selected folder
shorting_plate_path = os.path.join(source_folder, 'shorting_plate')
os.makedirs(shorting_plate_path, exist_ok=True)
print(f"'shorting_plate' folder created at: {shorting_plate_path}")

# Step 3: Define required files and folders to copy
files_to_copy = [
    "board", "board.o",
    "config", "config.o",
    "wirelist", "wirelist.o",
    "Board.xy", "Board_xy.o", "testplan"
]

folders_to_copy = [
    "Analog",
    "Fixture",
    "Debug"
]

# Step 4: Copy files
for file in files_to_copy:
    src = os.path.join(source_folder, file)
    dst = os.path.join(shorting_plate_path, file)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied file: {file}")
    else:
        print(f"File not found: {file}")

# Step 5: Copy folders
for folder in folders_to_copy:
    src = os.path.join(source_folder, folder)
    dst = os.path.join(shorting_plate_path, folder)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"Copied folder: {folder}")
    else:
        print(f"Folder not found: {folder}")

# Step 6: Rename 'testplan' file to 'testplan_shorting_plate'
old_testplan_path = os.path.join(shorting_plate_path, "testplan")
new_testplan_path = os.path.join(shorting_plate_path, "testplan_shorting_plate")

if os.path.exists(old_testplan_path):
    os.rename(old_testplan_path, new_testplan_path)
    print("Renamed 'testplan' to 'testplan_shorting_plate'")
else:
    print("'testplan' file not found in shorting_plate")

# Step 7: Extract and insert test lines
def get_test_lines_from_section(file_lines, section_name):
    inside_section = False
    test_lines = []
    for file_line in file_lines:
        if re.match(rf"^\s*sub\s+{section_name}\s*$", file_line, re.IGNORECASE):
            inside_section = True
            continue
        if inside_section:
            if re.match(r"^\s*sub\s+", file_line, re.IGNORECASE):
                break
            if file_line.strip().startswith("test"):
                test_lines.append(file_line)
    return test_lines

def insert_into_analog_tests(file_lines, new_test_lines):
    updated_lines = []
    inside_analog = False
    inserted = False
    for file_line in file_lines:
        updated_lines.append(file_line)
        if re.match(r"^\s*sub\s+Analog_Tests\s*$", file_line, re.IGNORECASE):
            inside_analog = True
            continue
        if inside_analog and not inserted and re.match(r"^\s*test\s", file_line):
            updated_lines = updated_lines[:-1] + new_test_lines + [file_line]
            inserted = True
    return updated_lines

if os.path.exists(new_testplan_path):
    with open(new_testplan_path, 'r') as f:
        plan_lines = f.readlines()

    pre_shorts_tests = get_test_lines_from_section(plan_lines, 'Pre_shorts')
    plan_lines = insert_into_analog_tests(plan_lines, pre_shorts_tests)

    with open(new_testplan_path, 'w') as f:
        f.writelines(plan_lines)

    print("Modified 'testplan_shorting_plate' successfully.")
else:
    print("'testplan_shorting_plate' not found for modification.")

# Step 8: Modify test files in Analog folder
analog_path = os.path.join(shorting_plate_path, "Analog")

for analog_file in os.listdir(analog_path):
    file_path = os.path.join(analog_path, analog_file)

    if not os.path.isfile(file_path) or not re.fullmatch(r'[a-zA-Z]+\d+', analog_file):
        print(f"Skipped: {analog_file}")
        continue

    with open(file_path, 'r') as f:
        analog_lines = f.readlines()

    node_s = None
    node_i = None

    for analog_line in analog_lines:
        match_s = re.match(r'connect\s+s\s+to\s+"([^"]+)"', analog_line, re.IGNORECASE)
        if match_s:
            node_s = match_s.group(1)
        match_i = re.match(r'connect\s+i\s+to\s+"([^"]+)"', analog_line, re.IGNORECASE)
        if match_i:
            node_i = match_i.group(1)

    node_s = node_s or "/PIN1"
    node_i = node_i or "/PIN2"

    replacement_block = [
        '! P-PIN check test automation tool\n',
        'on failure\n',
        f'   report "check nodes {node_s} P-Pin resistance"\n',
        f'   report "check nodes {node_i} P-Pin resistance"\n',
        'end on failure\n',
        'disconnect all\n',
        f'connect s to "{node_s}"\n',
        f'connect i to "{node_i}"\n',
        'resistor 9, 20, 100, rel, ar100m, ed\n',
        'off failure\n'
    ]

    with open(file_path, 'w') as f:
        f.writelines(replacement_block)

    print(f"Modified: {analog_file}")

# Step 9: Comment out non-Analog call lines in Test_sections
if os.path.exists(new_testplan_path):
    with open(new_testplan_path, 'r') as f:
        section_lines = f.readlines()

    inside_test_sections = False
    updated_section_lines = []

    for section_line in section_lines:
        if re.match(r'^\s*sub\s+Test_sections\s*$', section_line, re.IGNORECASE):
            inside_test_sections = True
            updated_section_lines.append(section_line)
            continue
        if inside_test_sections and re.match(r'^\s*sub\s+', section_line, re.IGNORECASE):
            inside_test_sections = False

        if inside_test_sections and re.match(r'^\s*call\s+', section_line, re.IGNORECASE):
            if 'Analog_Tests' not in section_line:
                updated_section_lines.append('!! ' + section_line.lstrip())
            else:
                updated_section_lines.append(section_line)
        else:
            updated_section_lines.append(section_line)

    with open(new_testplan_path, 'w') as f:
        f.writelines(updated_section_lines)

    print("Commented non-Analog_Tests call lines in Test_sections.")
else:
    print("Testplan not found for Test_sections commenting.")

# Step 10: Remove all test lines from sub characterize
if os.path.exists(new_testplan_path):
    with open(new_testplan_path, 'r') as f:
        char_lines = f.readlines()

    inside_char = False
    updated_char_lines = []

    for char_line in char_lines:
        if re.match(r'^\s*sub\s+characterize\s*$', char_line, re.IGNORECASE):
            inside_char = True
            updated_char_lines.append(char_line)
            continue
        if inside_char and re.match(r'^\s*sub\s+', char_line, re.IGNORECASE):
            inside_char = False
        if inside_char and re.match(r'^\s*test\s+', char_line, re.IGNORECASE):
            continue
        updated_char_lines.append(char_line)

    with open(new_testplan_path, 'w') as f:
        f.writelines(updated_char_lines)

    print("Removed test lines from characterize.")
else:
    print("Cannot modify characterize section: file missing.")

# Step 11: Create compile list
compile_list_path = os.path.join(shorting_plate_path, "compile_list.txt")

test_files = sorted([
    f for f in os.listdir(analog_path)
    if os.path.isfile(os.path.join(analog_path, f)) and re.fullmatch(r'[a-zA-Z]+\d+', f)
])

total_tests = len(test_files)

with open(compile_list_path, 'w') as f:
    for i, test_file in enumerate(test_files, start=1):
        f.write(f'print"{i}/{total_tests}"\n')
        f.write(f'compile"analog/{test_file}" ,ERR\n')

print(f"Compile list written with {total_tests} tests: {compile_list_path}")

