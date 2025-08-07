
import sys
from PIL import Image
import os
import ctypes
from tkinter import Tk, filedialog

def convert_to_ico(image_path, output_path, size=(256, 256)):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    img.save(output_path, format='ICO', sizes=[size])

def set_folder_icon(folder_path, icon_path):
    desktop_ini_path = os.path.join(folder_path, "desktop.ini")
    with open(desktop_ini_path, 'w') as f:
        f.write(f"[.ShellClassInfo]\nIconResource={icon_path},0\n")
    os.system(f'attrib +h "{desktop_ini_path}"')
    os.system(f'attrib +s "{folder_path}"')
    # Force refresh
    ctypes.windll.shell32.SHChangeNotify(0x8000000, 0x1000, None, None)

def main():
    root = Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(title="اختر صورة (JPG, PNG)", filetypes=[("Images", "*.jpg *.png")])
    if not image_path:
        print("لم يتم اختيار صورة.")
        return

    folder_path = filedialog.askdirectory(title="اختر الفولدر الذي تريد تغيير أيقونته")
    if not folder_path:
        print("لم يتم اختيار فولدر.")
        return

    icon_path = os.path.join(folder_path, "folder_icon.ico")
    convert_to_ico(image_path, icon_path)
    set_folder_icon(folder_path, icon_path)
    print("✅ تم تغيير أيقونة الفولدر بنجاح!")

if __name__ == "__main__":
    main()
