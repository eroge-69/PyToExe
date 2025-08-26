import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files_in_folder(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        files.sort()
        
        for index, filename in enumerate(files):
            name, ext = os.path.splitext(filename)
            new_filename = f"{index}{ext}"
            
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            
            os.rename(old_file, new_file)
            
    except Exception as e:
        return f"錯誤: {str(e)}"
    return None

def process_all_subfolders(root_folder):
    error = rename_files_in_folder(root_folder)
    if error:
        return error
        
    for foldername, subfolders, filenames in os.walk(root_folder):
        for subfolder in subfolders:
            subfolder_path = os.path.join(foldername, subfolder)
            error = rename_files_in_folder(subfolder_path)
            if error:
                return error
    return None

def select_folder():
    folder = filedialog.askdirectory(title="選擇要命名的文件夾")
    if folder:
        result = process_all_subfolders(folder)
        if result:
            messagebox.showerror("錯誤!!", result)
        else:
            messagebox.showinfo("完成", "所有圖片已成功命名!")

# 创建GUI界面
root = tk.Tk()
root.title("H團隊專用命名工具")
root.geometry("800x400")

label = tk.Label(root, text="H團隊專用命名工具", font=("Arial", 18))
label.pack(pady=20)

desc = tk.Label(root, text="選定文件夾後就會重新命名", font=("Arial", 19))
desc.pack(pady=10)

btn = tk.Button(root, text="請選擇資料夾", command=select_folder, height=2, width=20)
btn.pack(pady=20)

warning = tk.Label(root, text="建議先備份 軟體可能存在未知bug!!!", fg="red")
warning.pack(pady=10)

root.mainloop()