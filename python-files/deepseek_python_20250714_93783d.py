import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

def load_image():
    file_path = filedialog.askopenfilename(
        title="Выберите изображение",
        filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.bmp"), ("Все файлы", "*.*")]
    )
    if file_path:
        try:
            image = Image.open(file_path)
            return image
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")
    return None

def convert_to_rgb_txt(image, scale_factor=0.5):
    # Уменьшаем размер для удобства (опционально)
    width, height = image.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    image = image.resize((new_width, new_height))
    
    # Конвертируем в RGB-матрицу
    rgb_array = np.array(image)
    txt_content = ""
    for row in rgb_array:
        for pixel in row:
            r, g, b = pixel[:3]  # Берём первые 3 канала (игнорируем альфа, если есть)
            txt_content += f"({r:3d},{g:3d},{b:3d}) "
        txt_content += "\n"
    return txt_content

def convert_to_ascii(image, scale_factor=0.5, chars="@%#*+=-:. "):
    # Уменьшаем размер и конвертируем в градации серого
    image = image.resize((
        int(image.size[0] * scale_factor),
        int(image.size[1] * scale_factor)
    )).convert("L")  # L - режим grayscale
    
    # Сопоставляем яркость с символами
    pixels = np.array(image)
    ascii_str = ""
    for row in pixels:
        for pixel in row:
            index = int(pixel / 255 * (len(chars) - 1))
            ascii_str += chars[index]
        ascii_str += "\n"
    return ascii_str

def save_to_txt(content, default_name="image_data.txt"):
    save_path = filedialog.asksaveasfilename(
        title="Сохранить как TXT",
        defaultextension=".txt",
        initialfile=default_name,
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if save_path:
        with open(save_path, "w") as file:
            file.write(content)
        messagebox.showinfo("Успех", f"Файл сохранён:\n{save_path}")

def main():
    root = tk.Tk()
    root.title("Image to TXT Converter")
    root.geometry("400x200")

    def process_image(mode):
        image = load_image()
        if image:
            if mode == "rgb":
                content = convert_to_rgb_txt(image)
            elif mode == "ascii":
                content = convert_to_ascii(image)
            save_to_txt(content, f"image_{mode}.txt")

    tk.Label(root, text="Выберите режим конвертации:").pack(pady=10)
    tk.Button(root, text="RGB-матрица", command=lambda: process_image("rgb")).pack(fill=tk.X, padx=50, pady=5)
    tk.Button(root, text="ASCII-арт", command=lambda: process_image("ascii")).pack(fill=tk.X, padx=50, pady=5)
    tk.Button(root, text="Выход", command=root.quit).pack(fill=tk.X, padx=50, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()