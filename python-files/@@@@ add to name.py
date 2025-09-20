import os

def replace_zzz_with_words_between(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if len(lines) >= 3:
                line_parts = lines[2].split("Title:")[1].split("#")[0].strip()
                modified_lines = [line.replace('@@@@@', line_parts) for line in lines]
                modified_content = ''.join(modified_lines)

                with open(file_path, 'w', encoding='utf-8') as modified_file:
                    modified_file.write(modified_content)
        return True
    except Exception as e:
        print(f"Failed to process file: {file_path}. Error: {e}")
        return False

# Specify the directory path containing the .ass files
directory_path = r'C:\Users\waruna\Pictures\Video'

success_count = 0
failed_count = 0
failed_files = []

# Iterate over each file in the directory
for file_name in os.listdir(directory_path):
    if file_name.endswith('.ass'):
        file_path = os.path.join(directory_path, file_name)
        if replace_zzz_with_words_between(file_path):
            success_count += 1
        else:
            failed_count += 1
            failed_files.append(file_name)

print(f"Success count: {success_count}")
print(f"Failed count: {failed_count}")
print("Failed files:")
for file_name in failed_files:
    print(file_name)
