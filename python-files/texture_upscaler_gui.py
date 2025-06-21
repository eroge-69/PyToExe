import os
import cv2
import numpy as np
from PIL import Image, ImageQt
from realesrgan import RealESRGAN
import torch
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
upscale_factor = 4  # фиксированный для простоты
model = RealESRGAN(device, scale=upscale_factor)
model.load_weights(f"RealESRGAN_x{upscale_factor}.pth")

def preserve_black_regions(original, upscaled):
    mask = np.all(original <= 10, axis=2)
    upscaled[mask] = 0
    return upscaled

def process_images(input_folder, output_folder, formats):
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(input_folder):
        if not any(file.lower().endswith(ext) for ext in formats):
            continue

        input_path = os.path.join(input_folder, file)
        print(f"Обработка: {file}")

        # Работа с альфа-каналом (если есть)
        image_cv = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)

        if image_cv.shape[2] == 4:
            bgr, alpha = image_cv[:, :, :3], image_cv[:, :, 3]
        else:
            bgr, alpha = image_cv, None

        image_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb).convert("RGB")
        sr_image = model.predict(pil_image)

        sr_cv = np.array(sr_image)[..., ::-1].copy()
        resized_input = cv2.resize(bgr, sr_cv.shape[:2][::-1])
        sr_cv = preserve_black_regions(resized_input, sr_cv)

        if alpha is not None:
            alpha_up = cv2.resize(alpha, sr_cv.shape[:2][::-1], interpolation=cv2.INTER_LINEAR)
            sr_cv = cv2.merge((sr_cv, alpha_up.astype(np.uint8)))

        save_path = os.path.join(output_folder, file)
        cv2.imwrite(save_path, sr_cv)
        print(f"Сохранено: {save_path}")

def start_processing():
    input_folder = input_entry.get()
    output_folder = output_entry.get()
    selected_formats = [fmt.get() for fmt in format_vars if fmt.get()]
    if not input_folder or not output_folder or not selected_formats:
        messagebox.showerror("Ошибка", "Заполните все поля и выберите форматы.")
        return
    threading.Thread(target=process_images, args=(input_folder, output_folder, selected_formats), daemon=True).start()

def browse_folder(entry):
    path = filedialog.askdirectory()
    if path:
        entry.delete(0, tk.END)
        entry.insert(0, path)

# GUI
root = tk.Tk()
root.title("Texture Upscaler GUI")

tk.Label(root, text="Папка с текстурами:").grid(row=0, column=0, sticky="w")
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1)
tk.Button(root, text="Обзор", command=lambda: browse_folder(input_entry)).grid(row=0, column=2)

tk.Label(root, text="Папка для сохранения:").grid(row=1, column=0, sticky="w")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1)
tk.Button(root, text="Обзор", command=lambda: browse_folder(output_entry)).grid(row=1, column=2)

tk.Label(root, text="Форматы:").grid(row=2, column=0, sticky="w")
format_vars = [tk.StringVar(value=ext) for ext in [".png", ".jpg", ".jpeg", ".tga"]]
for i, var in enumerate(format_vars):
    cb = ttk.Checkbutton(root, text=var.get(), variable=var, onvalue=var.get(), offvalue="")
    cb.grid(row=2, column=i+1, sticky="w")

tk.Button(root, text="Начать обработку", command=start_processing, bg="#4CAF50", fg="white").grid(row=3, column=1, pady=10)

root.mainloop()
