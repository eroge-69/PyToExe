# dot_art_app.py
# Dot Art Generator - Desktop App (No Colab, No Internet, No PDF)
# Output: PNG + TXT (row & column pattern)
# Lightweight: Only uses Pillow, numpy, tkinter

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageOps, ImageDraw
import os

class DotArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DotArt Studio - نرم‌افزار طراحی نقطه‌ای")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.image_path = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="🎨 DotArt Studio", font=("Helvetica", 16, "bold"))
        title.pack(pady=10)

        subtitle = ttk.Label(main_frame, text="تبدیل عکس به طرح دستی نقطه‌ای", foreground="gray")
        subtitle.pack(pady=5)

        # Load Image Button
        self.load_btn = ttk.Button(main_frame, text="🖼️ بارگذاری عکس", command=self.load_image)
        self.load_btn.pack(pady=10)

        self.image_label = ttk.Label(main_frame, text="هیچ عکسی انتخاب نشده", foreground="red")
        self.image_label.pack(pady=5)

        # Settings
        ttk.Label(main_frame, text="🔧 تنظیمات", font=("Helvetica", 12)).pack(pady=10)

        # Scale Factor
        ttk.Label(main_frame, text="مقیاس جزئیات:").pack(anchor=tk.W)
        self.scale_var = tk.IntVar(value=2)
        scale_frame = ttk.Frame(main_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        for val, text in [(1, "1x (خیلی دقیق)"), (2, "2x (متعادل)"), (4, "4x (سریع‌تر)")]:
            ttk.Radiobutton(scale_frame, text=text, variable=self.scale_var, value=val).pack(anchor=tk.W)

        # Number of Levels
        ttk.Label(main_frame, text="تعداد سطوح خاکستری (3-10):").pack(anchor=tk.W, pady=(10, 0))
        self.levels_var = tk.IntVar(value=5)
        levels_spin = ttk.Spinbox(main_frame, from_=3, to=10, textvariable=self.levels_var, width=10)
        levels_spin.pack(pady=5)

        # Max Size
        ttk.Label(main_frame, text="حداکثر اندازه (ردیف/ستون):").pack(anchor=tk.W, pady=(10, 0))
        self.max_size_var = tk.IntVar(value=200)
        max_size_entry = ttk.Entry(main_frame, textvariable=self.max_size_var, width=15)
        max_size_entry.pack(pady=5)

        # Generate Button
        self.generate_btn = ttk.Button(main_frame, text="▶️ ایجاد خروجی‌ها", command=self.generate)
        self.generate_btn.pack(pady=20)
        self.generate_btn.config(state=tk.DISABLED)

        # Status
        self.status = ttk.Label(main_frame, text="", foreground="blue")
        self.status.pack(pady=10)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            title="انتخاب عکس",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if self.image_path:
            self.image_label.config(text=os.path.basename(self.image_path), foreground="green")
            self.generate_btn.config(state=tk.NORMAL)
            self.status.config(text="عکس بارگذاری شد.")
        else:
            self.image_label.config(text="هیچ عکسی انتخاب نشده", foreground="red")
            self.status.config(text="")

    def generate(self):
        if not self.image_path:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک عکس انتخاب کنید.")
            return

        try:
            self.status.config(text="در حال پردازش...")
            self.root.update()

            # Load image
            image = Image.open(self.image_path)
            orig_width, orig_height = image.size
            self.status.config(text=f"سایز اصلی: {orig_width}×{orig_height}")
            self.root.update()

            scale_factor = self.scale_var.get()
            num_levels = self.levels_var.get()
            max_size = self.max_size_var.get()

            # Initial grid
            grid_width = orig_width // scale_factor
            grid_height = orig_height // scale_factor

            # Smart downscale
            if grid_width > max_size or grid_height > max_size:
                factor_w = grid_width // max_size if grid_width > max_size else 1
                factor_h = grid_height // max_size if grid_height > max_size else 1
                factor = max(1, factor_w, factor_h)
                new_width = max(1, grid_width // factor)
                new_height = max(1, grid_height // factor)
            else:
                new_width, new_height = grid_width, grid_height

            self.status.config(text=f"شبکه نهایی: {new_width}×{new_height}")
            self.root.update()

            # Gray levels (light to dark)
            gray_values_full = [224, 196, 188, 180, 151, 100, 76, 63, 50, 37]
            gray_hex_full = ['#e0e0e0', '#c4c4c4', '#bcbcbc', '#b4b4b4', '#979797',
                             '#646464', '#4c4c4c', '#3f3f3f', '#323232', '#252525']
            selected_gray_values = gray_values_full[:num_levels]

            # Process image
            image_gray = ImageOps.grayscale(image)
            image_resized = image_gray.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_array = np.array(image_resized)

            if num_levels > 1:
                thresholds = np.linspace(0, 255, num_levels + 1)[1:-1]
                grid = np.digitize(img_array, bins=thresholds)
                grid = num_levels - 1 - grid  # 0 = lightest
            else:
                grid = np.zeros_like(img_array)

            color_code_grid = grid + 1  # 1-based

            # Output folder
            output_dir = filedialog.askdirectory(title="انتخاب پوشه خروجی")
            if not output_dir:
                output_dir = os.path.dirname(self.image_path)
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            base_name = f"{base_name}_dotart_{new_width}x{new_height}"

            # --- Output 1: PNG ---
            pixels_per_cell = 15
            output_width_px = new_width * pixels_per_cell
            output_height_px = new_height * pixels_per_cell

            img_output = np.zeros((new_height, new_width), dtype=np.uint8)
            for level in range(num_levels):
                img_output[grid == level] = selected_gray_values[level]

            pil_img = Image.fromarray(img_output)
            pil_img = pil_img.resize((output_width_px, output_height_px), Image.Resampling.NEAREST)

            draw = ImageDraw.Draw(pil_img)
            cell_w = output_width_px / new_width
            cell_h = output_height_px / new_height
            GRID_COLOR = 170  # Light gray

            for x in range(1, new_width):
                draw.line([(x * cell_w, 0), (x * cell_w, output_height_px)], fill=GRID_COLOR, width=1)
            for y in range(1, new_height):
                draw.line([(0, y * cell_h), (output_width_px, y * cell_h)], fill=GRID_COLOR, width=1)

            png_path = os.path.join(output_dir, f"{base_name}.png")
            pil_img.save(png_path, dpi=(300, 300))

            # --- Output 2: TXT ---
            txt_lines = [
                "🎨 Color Legend (Light to Dark)",
                "-" * 60
            ]
            symbols = ["⬜", "◻️", "◽", "▫️", "⊡", "▩", "◼️", "◾", "▪️", "⬛"]
            for i in range(num_levels):
                txt_lines.append(f"{i+1} = {symbols[i]} {gray_hex_full[i]} (Value: {gray_values_full[i]})")

            txt_lines += [
                f"\n📏 Final Grid Size: {new_width} × {new_height}",
                "",
                "📋 ROW-BY-ROW PATTERN:",
                "=" * 60
            ]
            for i, row in enumerate(color_code_grid):
                txt_lines.append(f"Row {i+1:4d}: {'_'.join(map(str, row))}")

            txt_lines += [
                "",
                "📌 COLUMN-BY-COLUMN PATTERN:",
                "=" * 60
            ]
            for j in range(new_width):
                col_str = "_".join(map(str, color_code_grid[:, j]))
                txt_lines.append(f"Col {j+1:4d}: {col_str}")

            txt_path = os.path.join(output_dir, f"{base_name}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(txt_lines))

            self.status.config(text="✅ تمام خروجی‌ها ایجاد شدند!")
            messagebox.showinfo("موفقیت", f"خروجی‌ها با موفقیت ساخته شدند:\n{output_dir}")

        except Exception as e:
            self.status.config(text="❌ خطا!")
            messagebox.showerror("خطا", f"خطا در پردازش:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DotArtApp(root)
    root.mainloop()