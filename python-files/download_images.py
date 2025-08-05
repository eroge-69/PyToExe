import requests
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import zipfile
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_images(codes):
    output_dir = Path("downloaded_images")
    output_dir.mkdir(exist_ok=True)
    url_template = "https://editor.gainhow.tw/product/fixedcalendar/xml/{code}/cal_00.jpg"

    success = []
    failed = []

    for code in codes:
        code = code.strip()
        if not code:
            continue
        url = url_template.format(code=code)
        filename = output_dir / f"{code}.jpg"
        try:
            r = requests.get(url, verify=False)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
                success.append(str(filename))
            else:
                failed.append(f"{code} (HTTP {r.status_code})")
        except Exception as e:
            failed.append(f"{code} ({e})")

    if success:
        zip_path = Path("images.zip")
        with zipfile.ZipFile(zip_path, "w") as z:
            for fn in success:
                z.write(fn)
        messagebox.showinfo("下載完成", f"成功下載 {len(success)} 張圖片\n失敗 {len(failed)} 張\n已打包為 images.zip")
    else:
        messagebox.showwarning("下載失敗", "所有代號皆失敗或無效")

    if failed:
        print("\n無法下載以下代號：")
        for f in failed:
            print("  ", f)

def on_submit():
    raw_text = text_input.get("1.0", tk.END)
    codes = []
    for line in raw_text.strip().splitlines():
        parts = line.replace(",", " ").replace("\t", " ").split()
        codes.extend(parts)
    if codes:
        download_images(codes)
    else:
        messagebox.showwarning("錯誤", "請輸入至少一個代號")

root = tk.Tk()
root.title("批次下載圖片工具")
root.geometry("480x320")

label = tk.Label(root, text="請貼上代號（多行可）:")
label.pack(pady=5)

text_input = tk.Text(root, height=10, width=60)
text_input.pack()

submit_btn = tk.Button(root, text="開始下載", command=on_submit)
submit_btn.pack(pady=10)

note = tk.Label(root, text="下載的圖片會存到 'downloaded_images' 資料夾，並打包成 images.zip")
note.pack(pady=5)

root.mainloop()
