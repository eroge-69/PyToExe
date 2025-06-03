import os
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox
from PIL import Image

def convert_tiff_cmyk_to_rgb_gui(input_folder):
    if not input_folder.lower().endswith("hr") or not os.path.isdir(input_folder):
        messagebox.showerror("Hiba", "Kérlek, egy 'HR' nevű mappát adj meg!")
        return

    parent_dir = os.path.dirname(input_folder)
    output_folder = os.path.join(parent_dir, "RBG")
    os.makedirs(output_folder, exist_ok=True)

    converted = 0
    errors = 0

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".tif", ".tiff")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            try:
                with Image.open(input_path) as img:
                    rgb_image = img.convert("RGB")
                    rgb_image.save(output_path, format="TIFF")
                    converted += 1
            except Exception as e:
                errors += 1

    messagebox.showinfo("Kész", f"✔️ {converted} fájl konvertálva.\n❗ {errors} hibás fájl.")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_path.delete(0, 'end')
        entry_path.insert(0, folder_selected)

def start_conversion():
    folder_path = entry_path.get()
    convert_tiff_cmyk_to_rgb_gui(folder_path)

# GUI létrehozása
root = Tk()
root.title("TIFF CMYK → RGB konvertáló")
root.geometry("500x150")
root.resizable(False, False)

Label(root, text="Add meg a HR mappa elérési útját:").pack(pady=10)
entry_path = Entry(root, width=60)
entry_path.pack()
Button(root, text="Tallózás", command=browse_folder).pack(pady=5)
Button(root, text="Konvertálás indítása", command=start_conversion).pack(pady=10)

root.mainloop()
