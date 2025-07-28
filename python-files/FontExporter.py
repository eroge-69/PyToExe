import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageDraw, ImageFont

def export_glyphs():
    font_path = filedialog.askopenfilename(
        title="Select TTF Font",
        filetypes=[("Font Files", "*.ttf *.otf")]

    )

    if not font_path:
        return

    chars = simpledialog.askstring(
        "Characters",
        "Enter characters to export (default: A–Z, 0–9):"
    )

    if not chars:
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    output_dir = filedialog.askdirectory(
        title="Select Output Folder"
    )

    if not output_dir:
        return

    try:
        font_size = 128
        font = ImageFont.truetype(font_path, font_size)

        for char in chars:
            img = Image.new("RGBA", (font_size, font_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Use textbbox instead of textsize (Pillow >=10)
            bbox = draw.textbbox((0, 0), char, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]

            draw.text(
                ((font_size - w) / 2, (font_size - h) / 2),
                char,
                font=font,
                fill=(255, 255, 255, 255)
            )


            safe_char = char if char.isalnum() else f"U{ord(char)}"
            img.save(os.path.join(output_dir, f"{safe_char}.png"))

        messagebox.showinfo("Done", f"Exported {len(chars)} characters to:\n{output_dir}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.withdraw()

export_glyphs()
