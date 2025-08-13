import os


def list_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.c', '.h')):
                file_list.append(os.path.join(root, file))
    return file_list


def update_makefile(makefile_path, source_directory):
    files = list_files(source_directory)
    existing_files = set()
    # 读取现有的 makefile 内容，将已有的文件记录下来
    with open(makefile_path, 'r') as makefile:
        makefile_content = makefile.readlines()

    for line in makefile_content:
        if line.startswith(('C_SOURCES', 'H_SOURCES')):
            existing_files.update(line.split()[2:])

    new_files = [os.path.basename(file) for file in files if os.path.basename(file) not in existing_files]

    # 检查新的文件是否已经在 makefile 中存在，如果不存在则添加到生成目标后面
    if new_files:
        with open(makefile_path, 'a') as makefile:
            makefile.write('\n')
            makefile.write(f'C_SOURCES += {" ".join(new_files)}\n')

        print("Makefile 已更新。")
    else:
        print("没有需要更新的文件。")

# 指定makefile路径和源目录路径
makefile_path = 'Makefile.txt'
source_directory = 'src'

# 更新makefile
update_makefile(makefile_path, source_directory)
