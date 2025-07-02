import os
import shutil
import tempfile
import zipfile
import win32clipboard
import win32com.client as win32
import tkinter as tk
from tkinter import messagebox

def has_gvml_clipboard():
    win32clipboard.OpenClipboard()
    formats = []
    try:
        fmt = 0
        while True:
            fmt = win32clipboard.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            formats.append(fmt)
    finally:
        win32clipboard.CloseClipboard()
    return any(49300 <= f <= 49400 for f in formats)

def save_shape_from_clipboard(save_name=None, index=301, log_fn=None):
    if not has_gvml_clipboard():
        log_fn("❌ Нет GVML-фигуры в буфере обмена.")
        return False

    log_fn("✅ Обнаружена GVML-фигура. Сохраняю...")

    app = win32.Dispatch("PowerPoint.Application")
    temp_dir = tempfile.mkdtemp()
    temp_pptx = os.path.join(temp_dir, "temp.pptx")

    pres = app.Presentations.Add()
    slide = pres.Slides.Add(1, 1)
    slide.Shapes.Paste()
    pres.SaveAs(temp_pptx)
    pres.Close()

    base_name = save_name if save_name else f"shape_{index}"
    extract_folder = os.path.join(".", base_name)
    zip_folder = os.path.join(extract_folder, "clipboard")
    media_folder = os.path.join(zip_folder, "media")

    with zipfile.ZipFile(temp_pptx, 'r') as z:
        z.extractall(extract_folder)

    os.makedirs(os.path.join(zip_folder, "drawings", "_rels"), exist_ok=True)
    os.makedirs(os.path.join(zip_folder, "theme"), exist_ok=True)
    os.makedirs(media_folder, exist_ok=True)

    try:
        shutil.move(os.path.join(extract_folder, "ppt", "drawings", "drawing1.xml"),
                    os.path.join(zip_folder, "drawings", "drawing1.xml"))
        shutil.move(os.path.join(extract_folder, "ppt", "drawings", "_rels", "drawing1.xml.rels"),
                    os.path.join(zip_folder, "drawings", "_rels", "drawing1.xml.rels"))
        shutil.move(os.path.join(extract_folder, "ppt", "media", "image1.png"),
                    os.path.join(media_folder, "image1.png"))
        shutil.move(os.path.join(extract_folder, "ppt", "theme", "theme1.xml"),
                    os.path.join(zip_folder, "theme", "theme1.xml"))
        shutil.move(os.path.join(extract_folder, "[Content_Types].xml"),
                    os.path.join(extract_folder, "[Content_Types].xml"))
        shutil.move(os.path.join(extract_folder, "_rels", ".rels"),
                    os.path.join(extract_folder, "_rels", ".rels"))
    except Exception as e:
        log_fn(f"⚠️ Ошибка при сборке структуры: {e}")
        return False

    pres = app.Presentations.Open(temp_pptx, WithWindow=False)
    pres.Slides(1).Shapes(1).Export(os.path.join(".", f"{base_name}.png"), 2)
    pres.Close()

    shutil.rmtree(temp_dir)

    log_fn(f"✅ Сохранено: {base_name}.png и папка /{base_name}/")
    return True

def run_gui():
    root = tk.Tk()
    root.title("PPT Shape Exporter")

    tk.Label(root, text="Имя для PNG и папки:").pack(pady=5)
    entry = tk.Entry(root, width=30)
    entry.pack()

    log_box = tk.Text(root, height=10, width=50, state='disabled')
    log_box.pack(pady=5)

    def log(msg):
        log_box.config(state='normal')
        log_box.insert('end', msg + "\n")
        log_box.see('end')
        log_box.config(state='disabled')

    def on_save():
        name = entry.get().strip()
        if not name:
            name = None
        success = save_shape_from_clipboard(save_name=name, log_fn=log)
        if not success:
            messagebox.showwarning("Ошибка", "Скопируйте фигуру из PowerPoint перед сохранением.")

    tk.Button(root, text="📥 Сохранить фигуру", command=on_save).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
