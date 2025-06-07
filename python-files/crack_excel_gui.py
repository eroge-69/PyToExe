import msoffcrypto
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def crack_excel():
    file_path = filedialog.askopenfilename(
        title="請選擇上鎖的 Excel 檔案",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not file_path:
        return

    status = tk.Label(root, text="準備開始破解...", font=("Arial", 12))
    status.pack(pady=10)
    root.update()

    with open(file_path, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)

        for i in range(10000):
            pw = f"{i:04d}"
            status.config(text=f"目前測試：{pw} / 9999")
            root.update()
            try:
                office_file.load_key(password=pw)
                output_path = os.path.join(os.path.dirname(file_path), "unlocked.xlsx")
                with open(output_path, "wb") as out:
                    office_file.decrypt(out)
                messagebox.showinfo("成功", f"✅ 找到密碼：{pw}\n已解密為：unlocked.xlsx")
                return
            except Exception:
                continue

    messagebox.showwarning("失敗", "❌ 無法在 0000~9999 內找到正確密碼")

root = tk.Tk()
root.title("又有人忘記給你密碼了嗎")
root.geometry("400x150")
btn = tk.Button(root, text="選取 Excel 檔案開始破解", font=("Arial", 12), command=crack_excel)
btn.pack(pady=30)
root.mainloop()
