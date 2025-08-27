import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pillow_heif
import os
import concurrent.futures
import subprocess

file_paths = []
last_save_dir = None

def collect_jpeg_files(paths):
    collected = []
    for p in paths:
        if os.path.isfile(p) and p.lower().endswith((".jpg", ".jpeg")):
            collected.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.lower().endswith((".jpg", ".jpeg")):
                        collected.append(os.path.join(root, f))
    return collected

def update_table():
    """Обновляем таблицу с файлами"""
    for row in table.get_children():
        table.delete(row)

    for path in file_paths:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        table.insert("", "end", values=(os.path.basename(path), f"{size_mb:.2f} МБ", "Ожидает"))

def set_status(filename, status):
    """Меняем статус в таблице"""
    for child in table.get_children():
        values = table.item(child, "values")
        if values[0] == filename:
            table.item(child, values=(values[0], values[1], status))
            break

def convert_file(file_path, save_dir, quality, save_exif, mode):
    try:
        img = Image.open(file_path)

        # Конвертация в HEIC
        if mode == "lossless":
            heif_file = pillow_heif.from_pillow(img, quality=100, save_all=True, lossless=True)
        else:
            heif_file = pillow_heif.from_pillow(img, quality=quality, save_all=True, lossless=False)

        # Сохраняем метаданные
        if save_exif:
            if "exif" in img.info:
                heif_file.info["exif"] = img.info["exif"]
            if "icc_profile" in img.info:
                heif_file.info["icc_profile"] = img.info["icc_profile"]

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(save_dir, f"{base_name}.heic")

        pillow_heif.write_heif(heif_file, output_path)
        return True, os.path.basename(file_path)
    except Exception as e:
        return False, f"{os.path.basename(file_path)}: {e}"

def convert_to_heic():
    global file_paths, last_save_dir
    if not file_paths:
        messagebox.showwarning("Нет файлов", "Сначала выберите или перетащите JPEG файлы или папки.")
        return

    save_dir = filedialog.askdirectory(title="Выберите папку для сохранения")
    if not save_dir:
        return
    last_save_dir = save_dir

    quality = quality_slider.get()
    save_exif = exif_var.get()
    mode = mode_var.get()

    progress_bar["maximum"] = len(file_paths)
    progress_bar["value"] = 0
    status_label.config(text="Начинаем конвертацию...")
    root.update_idletasks()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(convert_file, path, save_dir, quality, save_exif, mode): path
            for path in file_paths
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            ok, msg = future.result()
            progress_bar["value"] = i
            root.update_idletasks()

            if ok:
                set_status(msg, "Готово")
            else:
                set_status(msg.split(":")[0], "Ошибка")

    status_label.config(text="Конвертация завершена!")
    open_folder_btn.config(state="normal")

def drop_files(event):
    global file_paths
    paths = root.splitlist(event.data)
    file_paths = collect_jpeg_files(paths)
    update_table()
    status_label.config(text=f"Выбрано {len(file_paths)} файлов")

def select_files():
    global file_paths
    paths = filedialog.askopenfilenames(title="Выберите JPEG-файлы", filetypes=[("JPEG Images", "*.jpg *.jpeg")])
    file_paths = collect_jpeg_files(paths)
    update_table()
    status_label.config(text=f"Выбрано {len(file_paths)} файлов")

def select_folder():
    global file_paths
    folder = filedialog.askdirectory(title="Выберите папку")
    if folder:
        file_paths = collect_jpeg_files([folder])
        update_table()
        status_label.config(text=f"Найдено {len(file_paths)} файлов")

def on_table_select(event):
    """Предпросмотр выбранного изображения"""
    selected = table.selection()
    if not selected:
        return
    file_name = table.item(selected[0], "values")[0]
    for path in file_paths:
        if os.path.basename(path) == file_name:
            show_preview(path)
            break

def show_preview(path):
    try:
        img = Image.open(path)
        img.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(img)
        preview_label.config(image=photo)
        preview_label.image = photo
    except Exception:
        preview_label.config(text="Ошибка предпросмотра", image="")

def open_folder():
    """Открыть папку с результатами"""
    if last_save_dir and os.path.isdir(last_save_dir):
        os.startfile(last_save_dir)  # только для Windows
    else:
        messagebox.showerror("Ошибка", "Папка не найдена")

# --- GUI ---
root = TkinterDnD.Tk()
root.title("JPEG → HEIC Конвертер")
root.geometry("900x550")

label = tk.Label(root, text="Перетащите JPEG-файлы или папки сюда\nили выберите вручную", font=("Arial", 12))
label.pack(pady=10)

frame_buttons = tk.Frame(root)
frame_buttons.pack()

btn_files = tk.Button(frame_buttons, text="Выбрать файлы", command=select_files, font=("Arial", 10))
btn_files.grid(row=0, column=0, padx=5)

btn_folder = tk.Button(frame_buttons, text="Выбрать папку", command=select_folder, font=("Arial", 10))
btn_folder.grid(row=0, column=1, padx=5)

btn_convert = tk.Button(root, text="Конвертировать в HEIC", command=convert_to_heic, font=("Arial", 11))
btn_convert.pack(pady=10)

# --- Настройки ---
settings_frame = tk.LabelFrame(root, text="Настройки", padx=10, pady=10)
settings_frame.pack(pady=5, fill="x", padx=20)

mode_var = tk.StringVar(value="lossy")
rb_lossy = tk.Radiobutton(settings_frame, text="Lossy (с потерями)", variable=mode_var, value="lossy")
rb_lossless = tk.Radiobutton(settings_frame, text="Lossless (без потерь)", variable=mode_var, value="lossless")
rb_lossy.grid(row=0, column=0, sticky="w")
rb_lossless.grid(row=0, column=1, sticky="w")

quality_label = tk.Label(settings_frame, text="Качество (1–100):", font=("Arial", 10))
quality_label.grid(row=1, column=0, sticky="w")
quality_slider = tk.Scale(settings_frame, from_=1, to=100, orient="horizontal")
quality_slider.set(90)
quality_slider.grid(row=1, column=1, padx=10)

exif_var = tk.BooleanVar(value=True)
exif_checkbox = tk.Checkbutton(settings_frame, text="Сохранять EXIF и ICC-профиль", variable=exif_var, font=("Arial", 10))
exif_checkbox.grid(row=2, column=0, columnspan=2, sticky="w")

# --- Основной фрейм с таблицей и предпросмотром ---
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Таблица файлов
table_frame = tk.Frame(main_frame)
table_frame.pack(side="left", fill="both", expand=True)

columns = ("Имя файла", "Размер", "Статус")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")
table.pack(fill="both", expand=True)

table.bind("<<TreeviewSelect>>", on_table_select)

# Предпросмотр
preview_frame = tk.LabelFrame(main_frame, text="Предпросмотр", width=220, height=220)
preview_frame.pack(side="right", padx=10)
preview_label = tk.Label(preview_frame, text="Нет изображения")
preview_label.pack()

# --- Прогресс ---
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="Ожидание файлов...", font=("Arial", 10))
status_label.pack(pady=5)

open_folder_btn = tk.Button(root, text="Открыть папку с результатами", command=open_folder, state="disabled")
open_folder_btn.pack(pady=5)

# Drag&Drop
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_files)

root.mainloop()
