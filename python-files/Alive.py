import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw, ImageFont

class PhotoEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Простой фоторедактор")
        self.geometry("800x600")
        
        # Переменная для хранения текущего изображения
        self.current_image = None
        self.image_label = None
        
        # Кнопки для основных операций
        btn_load = tk.Button(self, text="Открыть изображение", command=self.load_image)
        btn_save = tk.Button(self, text="Сохранить изображение", command=self.save_image)
        btn_brightness = tk.Button(self, text="Яркость +", command=lambda: self.adjust_brightness(1.5))
        btn_contrast = tk.Button(self, text="Контраст +", command=lambda: self.adjust_contrast(1.8))
        btn_rotate = tk.Button(self, text="Поворот на 90°", command=lambda: self.rotate_image(90))
        btn_flip_hor = tk.Button(self, text="Отражение горизонт.", command=lambda: self.flip_image(mode='horizontal'))
        btn_add_watermark = tk.Button(self, text="Водяной знак", command=self.add_watermark)
        
        # Размещаем кнопки
        btn_load.pack()
        btn_save.pack()
        btn_brightness.pack()
        btn_contrast.pack()
        btn_rotate.pack()
        btn_flip_hor.pack()
        btn_add_watermark.pack()
        
    def load_image(self):
        file_path = filedialog.askopenfilename(title="Выберите изображение",
                                               filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            try:
                self.current_image = Image.open(file_path)
                photo = ImageTk.PhotoImage(self.current_image)
                
                if self.image_label is None:
                    self.image_label = tk.Label(self, image=photo)
                    self.image_label.image = photo
                    self.image_label.pack(expand=True, anchor=tk.CENTER)
                else:
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Невозможно открыть изображение: {e}")
            
    def show_image(self):
        if self.current_image:
            photo = ImageTk.PhotoImage(self.current_image)
            if self.image_label is None:
                self.image_label = tk.Label(self, image=photo)
                self.image_label.image = photo
                self.image_label.pack(expand=True, anchor=tk.CENTER)
            else:
                self.image_label.configure(image=photo)
                self.image_label.image = photo
    
    def save_image(self):
        if self.current_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                    filetypes=[("JPEG", "*.jpg"),
                                                               ("PNG", "*.png"),
                                                               ("JFIF", "*.jfif"),
                                                               ("GIF", "*.gif"),
                                                               ("WMF", "*.wmf"),
                                                               ("SVG", "*.svg"),
                                                               ("EMF", "*.emf")])
            if file_path:
                self.current_image.save(file_path)
                messagebox.showinfo("Успех", "Изображение успешно сохранено!")
        else:
            messagebox.showwarning("Предупреждение", "Нет открытого изображения для сохранения.")
    
    def adjust_brightness(self, factor=1.0):
        if self.current_image:
            enhancer = ImageEnhance.Brightness(self.current_image)
            self.current_image = enhancer.enhance(factor)
            self.show_image()
    
    def adjust_contrast(self, factor=1.0):
        if self.current_image:
            enhancer = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer.enhance(factor)
            self.show_image()
    
    def rotate_image(self, angle=0):
        if self.current_image:
            self.current_image = self.current_image.rotate(angle, expand=True)
            self.show_image()
    
    def flip_image(self, mode='horizontal'):
        if self.current_image:
            if mode.lower() == 'horizontal':
                self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            elif mode.lower() == 'vertical':
                self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.show_image()
    
    def add_watermark(self):
        if self.current_image:
            draw = ImageDraw.Draw(self.current_image)
            font = ImageFont.truetype("arial.ttf", size=36)
            draw.text((10, 10), "Copyright 2025", fill=(255, 255, 255, 128), font=font)
            self.show_image()

if __name__ == "__main__":
    app = PhotoEditorApp()
    app.mainloop()