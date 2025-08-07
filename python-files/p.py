import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageEnhance, ImageTk

# Constants
PASSPORT_WIDTH_CM = 3.5
PASSPORT_HEIGHT_CM = 4.5
DPI = 300
A4_WIDTH = 2480
A4_HEIGHT = 3508

def cm_to_px(cm):
    return int((cm / 2.54) * DPI)

def choose_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    img = Image.open(file_path)
    img = img.convert("RGB")

    # Resize to passport size
    passport_w = cm_to_px(PASSPORT_WIDTH_CM)
    passport_h = cm_to_px(PASSPORT_HEIGHT_CM)
    img = img.resize((passport_w, passport_h))

    # Auto-brightness
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)

    # Show preview
    img_preview = img.resize((passport_w // 4, passport_h // 4))
    img_tk = ImageTk.PhotoImage(img_preview)
    preview_label.config(image=img_tk)
    preview_label.image = img_tk

    # Ask how many copies
    copies = int(copy_var.get())
    layout = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")

    x_spacing = 100
    y_spacing = 100
    x_offset = x_spacing
    y_offset = y_spacing

    for i in range(copies):
        layout.paste(img, (x_offset, y_offset))
        x_offset += passport_w + x_spacing
        if x_offset + passport_w > A4_WIDTH:
            x_offset = x_spacing
            y_offset += passport_h + y_spacing

    layout.save("passport_layout.jpg")
    layout.show()

    status_label.config(text="✅ Done! Saved as 'passport_layout.jpg'")

# Tkinter Window
root = tk.Tk()
root.title("Passport Photo AI Generator")

tk.Label(root, text="Select number of copies:").pack()
copy_var = tk.StringVar(root)
copy_var.set("4")
tk.OptionMenu(root, copy_var, "4", "6").pack()

tk.Button(root, text="Upload Image", command=choose_image).pack(pady=10)

preview_label = tk.Label(root)
preview_label.pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
