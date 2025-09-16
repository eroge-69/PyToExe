import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ExifTags, ImageEnhance, ImageOps
import matplotlib.pyplot as plt

current_image = None
original_image = None
file_path = None

rotated_times = 0


def open_image():
    global current_image, original_image, file_path, cimage_frame
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff")]
    )
    if not file_path:
        return
    try:
        img = Image.open(file_path)
        original_image = img.copy()
        current_image = img.copy()
        show_image(current_image)
        show_info(file_path, img)
        restore_image()

        controls_frame.pack(pady=5)
        scale_frame.pack(pady=5)
        image_frame.pack(pady=5)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

def show_image(img):
    height = root.winfo_screenheight()
    freight = height//3

    imgfr = Image.new('RGB', (freight, freight), 'white')

    img_disp = img.copy()
    img_disp.thumbnail((freight-50, freight-50))
    x = (freight - img_disp.width) // 2
    y = (freight - img_disp.height) // 2

    imgfr.paste(img_disp, (x, y))

    photo = ImageTk.PhotoImage(imgfr)
    image_label.config(image=photo)
    image_label.image = photo

def show_info(path, img):
    info_text.delete(1.0, tk.END)
    file_size = os.path.getsize(path) / 1024
    if img.has_transparency_data:
        htd = "Да"
    else:
        htd = "Нет"

    info_text.insert(tk.END, f"Путь: {path}\n")
    info_text.insert(tk.END, f"Формат: {img.format}\n")
    info_text.insert(tk.END, f"Размер на диске: {file_size:.2f} КБ\n")
    info_text.insert(tk.END, f"Разрешение: {img.width}x{img.height}\n")
    info_text.insert(tk.END, f"Глубина цвета: {len(img.getbands()) * 8} бит\n")
    info_text.insert(tk.END, f"Цветовая модель: {img.mode}\n")
    info_text.insert(tk.END, f"Прозрачный фон: {htd}\n")
    info_text.insert(tk.END, "\nEXIF-информация:\n")

    exif_data = img._getexif()
    if exif_data:
        exif = {}
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            exif[tag_name] = value
        fields = ["DateTime", "Make", "Software", "Model", "Orientation", "FocalLength", "ExposureTime"]
        found = False
        for field in fields:
            if field in exif:
                if field.startswith("Orientation"):
                    if exif[field] == 0:
                        info_text.insert(tk.END, f"{field}: 0 (Vertical)\n")
                    else:
                        info_text.insert(tk.END, f"{field}: 1 (Horizontal)\n")
                else:
                    info_text.insert(tk.END, f"{field}: {exif[field]}\n")
                found = True
        if not found:
            info_text.insert(tk.END, "EXIF-информация отсутствует\n")
    else:
        info_text.insert(tk.END, "EXIF-информация отсутствует\n")
    info_text.pack(pady=5)
    info_text.pack(side="bottom", fill="y", expand=False)

def to_grayscale():
    global current_image
    if current_image:
        current_image = current_image.convert("L")
        show_image(current_image)

def adjust_image():
    global current_image
    if current_image:
        img = original_image.copy()
        for i in range(rotated_times):
            img = img.rotate(90, expand=True)
        img = ImageEnhance.Brightness(img).enhance(brightness_scale.get())
        img = ImageEnhance.Contrast(img).enhance(contrast_scale.get())
        img = ImageEnhance.Color(img).enhance(saturation_scale.get())
        current_image = img
        show_image(current_image)

def restore_image():
    global current_image
    global rotated_times
    if current_image:
        img = original_image.copy()
        current_image = img
        show_image(current_image)
        brightness_scale.set(1.0)
        contrast_scale.set(1.0)
        saturation_scale.set(1.0)
        rotated_times = 0

def show_histogram(before=False):
    global current_image
    if not current_image:
        os.startfile('weird-surreal.gif')
        return
    if before:
        histogram_path = 'before_histogram.png'
        img = original_image.copy()
        img.thumbnail((400, 400))
    else:
        histogram_path = 'after_histogram.png'
        img = current_image.copy()
        img.thumbnail((600, 600))
    if img:
        plt.figure("Гистограмма")
        if img.mode == "L":
            plt.hist(list(img.getdata()), bins=256, color="gray")
        else:
            colors = ("r", "g", "b")
            for i, col in enumerate(colors):
                plt.hist(list(img.getdata(band=i)), bins=256, color=col, alpha=0.5)

        plt.savefig(histogram_path, dpi=150, bbox_inches='tight')
        plt.close()
        os.startfile(histogram_path)

def linear_correction():
    global current_image
    if current_image and current_image.mode == "L":
        current_image = ImageOps.autocontrast(current_image)
        show_image(current_image)

def nonlinear_correction():
    global current_image
    if current_image and current_image.mode == "L":
        lut = [int((i / 255) ** 0.5 * 255) for i in range(256)]
        current_image = current_image.point(lut)
        show_image(current_image)

def rotate_image():
    global current_image
    global rotated_times
    if current_image:
        current_image = current_image.rotate(90, expand=True)
        show_image(current_image)
        rotated_times += 1
        if rotated_times > 3:
            rotated_times = 0

def save_image():
    global current_image
    if current_image:
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            current_image.save(path)

# GUI
root = tk.Tk()
root.title("Редактор изображений")
root.state('zoomed')

open_button = tk.Button(root, text="Загрузить изображение", command=open_image)
open_button.pack(pady=5)

image_label = tk.Label(root)
image_label.pack()

info_text = tk.Text(root, width=128, height=6)
info_text.pack(pady=5)
info_text.forget()

controls_frame = tk.Frame(root)


tk.Button(controls_frame, text="Серый", command=to_grayscale).grid(row=0, column=0, padx=5)
tk.Button(controls_frame, text="Поворот 90°", command=rotate_image).grid(row=0, column=1, padx=5)
tk.Button(controls_frame, text="Линейная коррекция", command=linear_correction).grid(row=0, column=2, padx=5)
tk.Button(controls_frame, text="Нелинейная коррекция", command=nonlinear_correction).grid(row=0, column=3, padx=5)

scale_frame = tk.Frame(root)

brightness_scale = tk.Scale(scale_frame, from_=0.0, to=5.0, resolution=0.1,
                            orient="horizontal", label="Яркость", length=125.0)
brightness_scale.bind("<ButtonRelease-1>", lambda event: adjust_image())
contrast_scale = tk.Scale(scale_frame, from_=0.0, to=5.0, resolution=0.1,
                          orient="horizontal", label="Контраст", length=125.0)
contrast_scale.bind("<ButtonRelease-1>", lambda event: adjust_image())
saturation_scale = tk.Scale(scale_frame, from_=0.0, to=5.0, resolution=0.1,
                            orient="horizontal", label="Насыщенность", length=125.0)
saturation_scale.bind("<ButtonRelease-1>", lambda event: adjust_image())
brightness_scale.set(1.0)
contrast_scale.set(1.0)
saturation_scale.set(1.0)
brightness_scale.pack(side="left", padx=5)
contrast_scale.pack(side="left", padx=5)
saturation_scale.pack(side="left", padx=5)


hist_frame = tk.Frame(scale_frame)
hist_frame.pack(side="left", padx=5)
tk.Button(hist_frame, text="Гистограмма ДО", command=lambda: show_histogram(before=True)).pack(side="top", pady=5)
tk.Button(hist_frame, text="Гистограмма ПОСЛЕ", command=lambda: show_histogram(before=False)).pack(side="top", pady=5)

image_frame = tk.Frame(root)

tk.Button(image_frame, text="Восстановить изображение", command=restore_image).pack(side="left", padx=5)
tk.Button(image_frame, text="Сохранить изображение", command=save_image).pack(side="left", padx=5)

root.mainloop()
