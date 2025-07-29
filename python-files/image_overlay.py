import tkinter as tk
import os
import sys
import time
from PIL import Image, ImageTk

class ImageOverlay:
    def __init__(self, image_folder, position_x, position_y, delay_seconds):
        self.window = tk.Tk()
        self.image_folder = image_folder
        self.position = (int(position_x), int(position_y))
        self.delay = int(delay_seconds) * 1000  # Конвертация в миллисекунды
        self.background_color = "#abcdef"  # Цвет для прозрачности
        
        self.setup_window()
        self.image_list = self.get_image_list()
        self.current_index = 0
        
        if not self.image_list:
            print("ОШИБКА: В папке нет изображений!")
            self.window.destroy()
            return
            
        self.label = tk.Label(self.window, bg=self.background_color)
        self.label.pack()
        self.show_image()
        self.window.mainloop()

    def setup_window(self):
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-transparentcolor", self.background_color)
        self.window.geometry(f"+{self.position[0]}+{self.position[1]}")
        self.window.config(bg=self.background_color)
        self.window.bind("<Escape>", lambda e: self.window.destroy())

    def get_image_list(self):
        """Получает список изображений в указанном порядке"""
        order_file = os.path.join(self.image_folder, "image_order.txt")
        images = []
        
        # Если есть файл порядка - используем его
        if os.path.exists(order_file):
            with open(order_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        img_path = os.path.join(self.image_folder, line)
                        if os.path.exists(img_path):
                            images.append(img_path)
            return images
        
        # Если файла порядка нет - используем алфавитный порядок
        for filename in os.listdir(self.image_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                images.append(os.path.join(self.image_folder, filename))
        return sorted(images)

    def load_image(self, path):
        """Загружает и обрабатывает изображение"""
        try:
            img = Image.open(path)
            if img.mode == "RGBA":
                background = Image.new("RGBA", img.size, self.background_color)
                background.paste(img, (0, 0), img)
                img = background.convert("RGB")
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки {path}: {str(e)}")
            return None

    def show_image(self):
        """Показывает текущее изображение и планирует следующее"""
        img_path = self.image_list[self.current_index]
        photo = self.load_image(img_path)
        
        if photo:
            self.label.config(image=photo)
            self.label.image = photo  # Сохраняем ссылку
            print(f"Показ: {os.path.basename(img_path)}")
        
        # Переход к следующему изображению
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self.window.after(self.delay, self.show_image)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Использование: image_overlay.exe <папка> <X> <Y> <задержка_в_секундах>")
        sys.exit(1)
    
    ImageOverlay(
        image_folder=sys.argv[1],
        position_x=sys.argv[2],
        position_y=sys.argv[3],
        delay_seconds=sys.argv[4]
    )