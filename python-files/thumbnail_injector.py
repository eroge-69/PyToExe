import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def add_thumbnail_to_gcode(image_path, gcode_path):
    encoded_image = encode_image_to_base64(image_path)
    thumbnail_header = f";thumbnail: data:image/png;base64,{encoded_image}\n"

    with open(gcode_path, "r", encoding="utf-8") as gcode_file:
        gcode_content = gcode_file.read()

    new_gcode_content = thumbnail_header + gcode_content

    base_name = os.path.basename(gcode_path)
    dir_name = os.path.dirname(gcode_path)
    new_file_name = os.path.splitext(base_name)[0] + "_with_thumbnail.gcode"
    new_file_path = os.path.join(dir_name, new_file_name)

    with open(new_file_path, "w", encoding="utf-8") as new_gcode_file:
        new_gcode_file.write(new_gcode_content)

    messagebox.showinfo("Success", f"Thumbnail added and saved as:\n{new_file_name}")

def main():
    root = tk.Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(title="Select PNG or JPG image", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if not image_path:
        return

    gcode_path = filedialog.askopenfilename(title="Select G-code file", filetypes=[("G-code files", "*.gcode")])
    if not gcode_path:
        return

    add_thumbnail_to_gcode(image_path, gcode_path)

if __name__ == "__main__":
    main()
