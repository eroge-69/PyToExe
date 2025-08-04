import tkinter as tk
from tkinter import messagebox

# 定義檔案路徑和要修改的行號
file_path = r"C:\Users\user\AppData\Roaming\Vencord\themes\NewsPink.theme.css"
line_numbers = [26, 38, 39]

# 定義按鈕對應的句子
sentences = {
    "Dogboy": [
        "  --background-image: url('https://i.imgur.com/XCZEKXa.jpg');\n",
        "  --left-brightness: 0;\n",
        "  --middle-brightness: 0;\n"
    ],
    "Stargirl": [
        "  --background-image: url('https://i.imgur.com/D52HL9O.jpg');\n",
        "  --left-brightness: 0.1;\n",
        "  --middle-brightness: 0.1;\n"
    ],
    "Snow": [
        "  --background-image: url('https://i.imgur.com/bO2wLTW.jpg');\n",
        "  --left-brightness: 0.1;\n",
        "  --middle-brightness: 0.1;\n"
    ],
    "Fox": [
        "  --background-image: url('https://i.imgur.com/1bhQIPA.jpg');\n",
        "  --left-brightness: 0;\n",
        "  --middle-brightness: 0;\n"
    ]
}

# 定義修改檔案的函數
def modify_file(new_lines):
    try:
        # 讀取檔案所有內容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 檢查所有行號是否有效
        max_line = max(line_numbers)
        if max_line <= len(lines):
            # 修改指定的多行內容
            for i, line_num in enumerate(line_numbers):
                lines[line_num - 1] = new_lines[i]
            # 將修改後的內容寫回檔案
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
    except:
        pass  # 靜默處理所有錯誤

# 創建主窗口
root = tk.Tk()
root.title("修改 NewsPink.theme.css 主題")
root.geometry("300x200")

# 創建標籤
label = tk.Label(root, text="選擇主題：")
label.pack(pady=10)

# 創建按鈕
btn_dogboy = tk.Button(root, text="1. Dogboy", command=lambda: modify_file(sentences["Dogboy"]), width=15)
btn_dogboy.pack(pady=5)

btn_stargirl = tk.Button(root, text="2. Stargirl", command=lambda: modify_file(sentences["Stargirl"]), width=15)
btn_stargirl.pack(pady=5)

btn_snow = tk.Button(root, text="3. Snow", command=lambda: modify_file(sentences["Snow"]), width=15)
btn_snow.pack(pady=5)

btn_fox = tk.Button(root, text="4. Fox", command=lambda: modify_file(sentences["Fox"]), width=15)
btn_fox.pack(pady=5)

# 啟動主循環
root.mainloop()