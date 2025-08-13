import os
import threading
import queue
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image
import piexif
import pyinstaller

class ImageCompressorApp:
    def __init__(self, master):
        self.master = master
        master.title("图片压缩工具 v1.3")
        master.geometry("600x400")

        self.create_widgets()
        self.status_queue = queue.Queue()
        self.master.after(100, self.process_status_queue)

    def create_widgets(self):
        """创建界面组件"""
        frame = Frame(self.master)
        frame.pack(pady=10)

        Label(frame, text="目标文件夹:").pack(side=LEFT)
        self.folder_path = Entry(frame, width=50)
        self.folder_path.pack(side=LEFT, padx=5)
        Button(frame, text="浏览", command=self.browse_folder).pack(side=LEFT)

        Button(self.master, text="开始压缩", command=self.start_compression).pack(pady=5)

        self.status_text = Text(self.master, wrap=WORD, state='disabled')
        scrollbar = Scrollbar(self.master)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.status_text.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

    def browse_folder(self):
        """选择文件夹"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.delete(0, END)
            self.folder_path.insert(0, folder_selected)

    def start_compression(self):
        """启动压缩线程"""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("错误", "请先选择文件夹")
            return

        if not os.path.exists(folder):
            messagebox.showerror("错误", "文件夹不存在")
            return

        threading.Thread(target=self.compress_images, args=(folder,), daemon=True).start()

    def compress_images(self, folder):
        """遍历并压缩图片"""
        target_size = 9 * 1024 * 1024  # 9MB
        supported_formats = ('.jpg', '.jpeg', '.png')

        self.add_status("=== 开始处理 ===")
        self.add_status(f"扫描文件夹: {folder}")

        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file_path)[1].lower()

                if ext not in supported_formats:
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    if file_size < target_size:
                        self.add_status(f"跳过 {file} (大小符合)")
                        continue

                    self.add_status(f"处理 {file} - 原大小: {self.format_size(file_size)}")

                    img = self.fix_orientation(Image.open(file_path), file_path)
                    if ext in ('.jpg', '.jpeg'):
                        success = self.compress_jpeg(img, file_path, target_size)
                    elif ext == '.png':
                        success = self.compress_png(img, file_path, target_size)

                    if success:
                        new_size = os.path.getsize(file_path)
                        self.add_status(f"压缩成功 - 新大小: {self.format_size(new_size)}")
                    else:
                        self.add_status("压缩失败：无法达到目标大小")

                except Exception as e:
                    self.add_status(f"处理错误: {str(e)}")

        self.add_status("=== 处理完成 ===")

    def fix_orientation(self, img, file_path):
        """修正图片的 EXIF 方向信息"""
        try:
            exif_dict = piexif.load(file_path)
            if '0th' in exif_dict and piexif.ImageIFD.Orientation in exif_dict['0th']:
                orientation = exif_dict['0th'].pop(piexif.ImageIFD.Orientation)
                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img

    def compress_jpeg(self, img, path, target_size):
        """压缩 JPEG 文件"""
        temp_path = path + ".tmp"
        quality_low, quality_high = 1, 95
        success = False

        while quality_low <= quality_high:
            mid_quality = (quality_low + quality_high) // 2
            img.save(temp_path, format="JPEG", quality=mid_quality, optimize=True)
            size = os.path.getsize(temp_path)

            if size < target_size:
                success = True
                quality_low = mid_quality + 1
            else:
                quality_high = mid_quality - 1

        if success:
            os.replace(temp_path, path)
            return True

        # 质量调低仍然超出 9MB，则缩小分辨率
        img = self.resize_image(img, target_size)
        img.save(temp_path, format="JPEG", quality=85, optimize=True)

        if os.path.getsize(temp_path) < target_size:
            os.replace(temp_path, path)
            return True

        os.remove(temp_path)
        return False

    def compress_png(self, img, path, target_size):
        """压缩 PNG 文件，若仍大于目标大小，则转换为 JPEG"""
        temp_path = path + ".tmp"

        try:
            img.save(temp_path, format="PNG", optimize=True)
            if os.path.getsize(temp_path) < target_size:
                os.replace(temp_path, path)
                return True

            self.add_status(f"{os.path.basename(path)} PNG 超过限制，转换为 JPEG")

            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            jpeg_path = os.path.splitext(path)[0] + ".jpg"
            return self.compress_jpeg(img, jpeg_path, target_size)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def resize_image(self, img, target_size):
        """调整分辨率来进一步压缩"""
        width, height = img.size
        scale_factor = 0.9

        while True:
            width = int(width * scale_factor)
            height = int(height * scale_factor)
            img = img.resize((width, height), Image.LANCZOS)

            temp_path = "resize_check.jpg"
            img.save(temp_path, format="JPEG", quality=85, optimize=True)

            if os.path.getsize(temp_path) < target_size or width < 500:
                os.remove(temp_path)
                break

        return img

    def format_size(self, size):
        return f"{size / (1024 * 1024):.2f}MB"

    def add_status(self, message):
        self.status_queue.put(message + "\n")

    def process_status_queue(self):
        while not self.status_queue.empty():
            message = self.status_queue.get_nowait()
            self.status_text.config(state='normal')
            self.status_text.insert(END, message)
            self.status_text.see(END)
            self.status_text.config(state='disabled')
        self.master.after(100, self.process_status_queue)


if __name__ == "__main__":
    root = Tk()
    app = ImageCompressorApp(root)
    root.mainloop()
