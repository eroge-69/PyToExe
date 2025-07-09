import pydicom
import os
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog

# Tạo cửa sổ chọn thư mục
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính

folder_path = filedialog.askdirectory(
    title="Chọn thư mục chứa file DICOM"
)

if not folder_path:
    print("Bạn chưa chọn thư mục. Kết thúc chương trình.")
    exit()

# Tạo thư mục output
output_folder = os.path.join(folder_path, "tiff_output")
os.makedirs(output_folder, exist_ok=True)

# Duyệt từng file
for idx in sorted(os.listdir(folder_path)):
    img_path = os.path.join(folder_path, idx)
    
    if os.path.isfile(img_path) and idx.lower().endswith(".dcm"):
        # Đọc DICOM
        ds = pydicom.dcmread(img_path)
        img_data = ds.pixel_array

        # Scale về 0-255
        img_min = np.min(img_data)
        img_max = np.max(img_data)

        img_scaled = (img_data - img_min) / (img_max - img_min) * 255
        img_uint8 = img_scaled.astype(np.uint8)

        # Tạo ảnh PIL
        im = Image.fromarray(img_uint8)

        # Tạo tên file output
        output_filename = os.path.splitext(idx)[0] + ".tif"
        output_path = os.path.join(output_folder, output_filename)

        # Lưu TIFF
        im.save(output_path)

        print("Đã lưu:", output_path)

print("✅ Hoàn tất convert tất cả file DICOM trong thư mục.")