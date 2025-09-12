
import os
from tkinter import filedialog, Tk

def is_valid_hex_line(line):
    if not line.startswith(":"):
        return False
    try:
        byte_count = int(line[1:3], 16)
        expected_length = 11 + byte_count * 2  # : + LL + AAAA + TT + data + CC
        return len(line.strip()) == expected_length
    except:
        return False

def check_hex_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".hex"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if not is_valid_hex_line(line):
                    print(f"[錯誤] 檔案: {filename} 第 {i+1} 行格式錯誤：{line.strip()}")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="選擇 HEX 檔案資料夾")
    if folder_selected:
        print(f"開始檢查資料夾：{folder_selected}
")
        check_hex_files(folder_selected)
    else:
        print("未選擇資料夾，程式結束。")
