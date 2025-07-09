
import os
import imagehash
from PIL import Image
import piexif
from tkinter import filedialog, Tk, messagebox
from collections import defaultdict
from datetime import datetime

# 選擇資料夾
root = Tk()
root.withdraw()
folder = filedialog.askdirectory(title="選擇照片資料夾")
if not folder:
    messagebox.showinfo("取消", "未選擇資料夾，程式結束。")
    exit()

# 照片 Hash 資料儲存
hash_dict = defaultdict(list)

# 掃描與建立 Hash
supported_exts = ('.jpg', '.jpeg', '.png')
for filename in os.listdir(folder):
    if not filename.lower().endswith(supported_exts):
        continue
    path = os.path.join(folder, filename)
    try:
        img = Image.open(path)
        hash_val = str(imagehash.phash(img))
        hash_dict[hash_val].append(path)
    except Exception as e:
        print(f"跳過無法處理的圖片：{filename}，錯誤：{e}")

# 分析重複檔案與 EXIF 拍攝時間
to_delete = []
for paths in hash_dict.values():
    if len(paths) <= 1:
        continue
    photos_with_time = []
    for p in paths:
        try:
            exif = piexif.load(p)
            dt = exif['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
            if dt:
                timestamp = datetime.strptime(dt.decode(), "%Y:%m:%d %H:%M:%S")
                photos_with_time.append((p, timestamp))
            else:
                photos_with_time.append((p, datetime.max))  # 無 EXIF 當最新
        except:
            photos_with_time.append((p, datetime.max))
    photos_with_time.sort(key=lambda x: x[1])
    to_delete.extend([p for p, _ in photos_with_time[1:]])  # 保留最舊的

# 預覽刪除清單
if not to_delete:
    messagebox.showinfo("結果", "未找到重複照片。")
else:
    preview_text = "\n".join([os.path.basename(f) for f in to_delete[:20]])
    msg = f"共發現 {len(to_delete)} 張重複照片，以下是其中幾張將被刪除：\n\n{preview_text}\n\n是否要繼續？"
    if messagebox.askyesno("確認刪除", msg):
        deleted = 0
        for f in to_delete:
            try:
                os.remove(f)
                deleted += 1
            except Exception as e:
                print(f"無法刪除 {f}: {e}")
        messagebox.showinfo("完成", f"已刪除 {deleted} 張重複照片。")
    else:
        messagebox.showinfo("取消", "未執行任何刪除。")
