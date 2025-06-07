import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab

DATA_DIR = "data"
EXAMPLE_IMAGE = os.path.join(DATA_DIR, "auto1.png")

def resource_path(relative_path):
    """ Получаем абсолютный путь к ресурсу для работы с PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_clipboard_for_image():
    try:
        return ImageGrab.grabclipboard() is not None
    except:
        return False

def save_clipboard_image():
    try:
        img = ImageGrab.grabclipboard()
        if img:
            os.makedirs(DATA_DIR, exist_ok=True)
            img.save(EXAMPLE_IMAGE)
            messagebox.showinfo("Успех", f"Сохранено")
            return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    return False

def show_instruction():
    root = tk.Tk()
    root.title("Инструкция")
    
    tk.Label(root, text="Сделай скриншот (Win+Shift+S) подобно этому:").pack(pady=10)
    
    example_path = resource_path(EXAMPLE_IMAGE) if os.path.exists(EXAMPLE_IMAGE) else None
    
    if example_path and os.path.exists(example_path):
        try:
            img = Image.open(example_path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            tk.Label(root, image=photo).pack(padx=10, pady=10)
            root.image = photo
        except:
            tk.Label(root, text="(Не удалось загрузить пример)").pack()
    else:
        tk.Label(root, text="(Пример изображения отсутствует)").pack()
    
    tk.Button(root, text="Понятно", command=root.destroy, width=15).pack(pady=10)
    root.mainloop()

def main():
    if check_clipboard_for_image():
        if save_clipboard_image():
            return
    
    show_instruction()

if __name__ == "__main__":
    main()
    # -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['screenshot_helper.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('PIL'),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='screenshot_helper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Добавьте свой иконку если нужно
)