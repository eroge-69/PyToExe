import os
from tkinter import filedialog, Tk

def is_valid_uuid_jpg(filename):
    parts = filename.split(".")
    if len(parts) != 2 or parts[1].lower() != "jpg":
        return False
    uuid_part = parts[0]
    return len(uuid_part) == 36 and uuid_part.count("-") == 4

def rename_images_by_uuid(folder_path):
    files = [f for f in os.listdir(folder_path) if is_valid_uuid_jpg(f)]
    files.sort()

    temp_mapping = {}
    for index, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        temp_name = f"temp_{index}.jpg"
        temp_path = os.path.join(folder_path, temp_name)
        os.rename(old_path, temp_path)
        temp_mapping[temp_name] = index + 1

    for temp_name, new_index in temp_mapping.items():
        temp_path = os.path.join(folder_path, temp_name)
        new_name = f"{new_index}.jpg"
        new_path = os.path.join(folder_path, new_name)
        os.rename(temp_path, new_path)

    print(f"✅ 完成：已将 {len(files)} 个文件按UUID排序并重命名为 1.jpg, 2.jpg ...")

# ✅ 用户运行时弹出对话框选择文件夹
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # 不显示主窗口
    folder = filedialog.askdirectory(title="请选择包含 JPG 文件的文件夹")
    
    if folder:
        rename_images_by_uuid(folder)
    else:
        print("❌ 未选择文件夹，程序退出。")
