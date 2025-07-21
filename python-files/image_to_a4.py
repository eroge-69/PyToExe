import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os

# 定义A4纸尺寸 (300dpi)
A4_SIZE = (2480, 3508)

class ImageToA4App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("图片拼接到A4工具")
        self.geometry("400x300")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.image_paths = []

        self.label = ctk.CTkLabel(self, text="选择4张图片拼接到一张A4纸")
        self.label.pack(pady=10)

        self.select_button = ctk.CTkButton(self, text="选择图片", command=self.select_images)
        self.select_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self, text="保存拼接后的图片", command=self.save_image, state="disabled")
        self.save_button.pack(pady=10)

    def select_images(self):
        paths = filedialog.askopenfilenames(
            title="选择4张图片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if len(paths) != 4:
            messagebox.showerror("错误", "请准确选择4张图片！")
            return
        self.image_paths = paths
        self.save_button.configure(state="normal")
        messagebox.showinfo("成功", "4张图片选择成功！")

    def save_image(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG 文件", "*.jpg"), ("PNG 文件", "*.png")]
        )
        if not save_path:
            return

        try:
            a4_image = Image.new("RGB", A4_SIZE, "white")

            # 每张图片的目标尺寸 (A4的1/4)
            target_width, target_height = A4_SIZE[0] // 2, A4_SIZE[1] // 2
            positions = [
                (0, 0), (target_width, 0),
                (0, target_height), (target_width, target_height)
            ]

            for img_path, pos in zip(self.image_paths, positions):
                img = Image.open(img_path)
                img.thumbnail((target_width, target_height), Image.LANCZOS)

                # 居中定位
                x_offset = pos[0] + (target_width - img.width) // 2
                y_offset = pos[1] + (target_height - img.height) // 2
                a4_image.paste(img, (x_offset, y_offset))

            a4_image.save(save_path)
            messagebox.showinfo("完成", f"图片保存成功：{save_path}")
            os.startfile(os.path.dirname(save_path))

        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{str(e)}")

if __name__ == "__main__":
    app = ImageToA4App()
    app.mainloop()
