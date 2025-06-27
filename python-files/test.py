import numpy as np
from skimage import io
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

def rgb_to_cmyk(image_rgb):
    """Кастомное преобразование RGB в CMYK с контролем черного канала."""
    # Нормализация RGB (0-255 -> 0-1)
    rgb_normalized = image_rgb / 255.0
    
    # Вычисляем черный канал (K) как минимальное значение (1 - max(R,G,B))
    k = 1 - np.max(rgb_normalized, axis=2)
    
    # Избегаем деления на ноль
    k = np.clip(k, 0, 1)
    divisor = np.where(k < 1, 1 - k, 1)  # Если k=1, используем 1 для избежания деления на 0
    
    # Вычисляем CMY
    c = (1 - rgb_normalized[:, :, 0] - k) / divisor
    m = (1 - rgb_normalized[:, :, 1] - k) / divisor
    y = (1 - rgb_normalized[:, :, 2] - k) / divisor
    
    # Ограничиваем значения и масштабируем в 0-255
    c = np.clip(c, 0, 1) * 255
    m = np.clip(m, 0, 1) * 255
    y = np.clip(y, 0, 1) * 255
    k = np.clip(k, 0, 1) * 255
    
    # Собираем CMYK-каналы
    cmyk = np.stack([c, m, y, k], axis=2).astype(np.uint8)
    return cmyk

def separate_cmyk_channels(image_path, output_dir, output_format="PNG"):
    """Разделение изображения на CMYK-каналы с сохранением в черно-белом виде."""
    try:
        # Читаем изображение
        img = io.imread(image_path)
        
        # Проверяем формат
        if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise ValueError("Изображение должно быть в формате PNG или JPG.")
        
        # Проверяем, что изображение в RGB
        if img.shape[-1] not in [3, 4]:
            raise ValueError("Изображение должно быть в RGB (3 канала) или RGBA (4 канала).")
        
        # Если RGBA, отбрасываем альфа-канал
        if img.shape[-1] == 4:
            img = img[:, :, :3]
        
        # Конвертируем в CMYK
        cmyk_data = rgb_to_cmyk(img)
        
        # Создаём директорию для сохранения каналов
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Определяем CMYK-каналы
        channels = ["cyan", "magenta", "yellow", "black"]
        
        # Диагностика значений каналов
        status_text = ""
        for i, channel_name in enumerate(channels):
            channel = cmyk_data[:, :, i]
            status_text += f"{channel_name.capitalize()} канал - мин: {channel.min()}, макс: {channel.max()}\n"
            if channel_name == "black" and channel.min() == channel.max() == 255:
                status_text += "Предупреждение: Черный канал полностью черный. Попробуйте скорректировать входное изображение.\n"
        
        # Обновляем статус в интерфейсе
        status_label.config(text=status_text)
        
        # Сохраняем каналы
        for i, channel_name in enumerate(channels):
            channel = cmyk_data[:, :, i]
            io.imsave(os.path.join(output_dir, f"{channel_name}_channel.{output_format.lower()}"), channel)
            status_text += f"Сохранён канал: {channel_name}_channel.{output_format.lower()}\n"
        
        status_label.config(text=status_text + "\nЦветоделение завершено! Черно-белые каналы сохранены.")
        messagebox.showinfo("Успех", f"Цветоделение завершено! Каналы сохранены в {output_dir}")

    except Exception as e:
        status_label.config(text=f"Ошибка: {str(e)}")
        messagebox.showerror("Ошибка", str(e))

def select_file():
    """Открытие диалогового окна для выбора файла."""
    file_path = filedialog.askopenfilename(
        title="Выберите изображение",
        filetypes=[("Image files", "*.png *.jpg *.jpeg")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
        status_label.config(text="Файл выбран: " + file_path)

def start_processing():
    """Запуск обработки изображения."""
    image_path = file_entry.get()
    if not image_path:
        messagebox.showwarning("Предупреждение", "Выберите файл!")
        return
    
    # Определяем выходную папку (рядом с входным файлом)
    output_dir = os.path.join(os.path.dirname(image_path), "cmyk_channels")
    output_format = format_var.get()  # Получаем выбранный формат (PNG или TIFF)
    
    status_label.config(text="Обработка начата...")
    separate_cmyk_channels(image_path, output_dir, output_format)

# Создаём GUI
root = tk.Tk()
root.title("CMYK Цветоделение")
root.geometry("600x400")

# Поле для отображения пути к файлу
tk.Label(root, text="Выберите изображение (PNG/JPG):").pack(pady=10)
file_entry = tk.Entry(root, width=50)
file_entry.pack(pady=5)

# Кнопка для выбора файла
tk.Button(root, text="Обзор...", command=select_file).pack(pady=5)

# Выбор формата выхода
tk.Label(root, text="Формат выходных файлов:").pack(pady=10)
format_var = tk.StringVar(value="PNG")
tk.Radiobutton(root, text="PNG", variable=format_var, value="PNG").pack()
tk.Radiobutton(root, text="TIFF", variable=format_var, value="TIFF").pack()

# Кнопка для запуска обработки
tk.Button(root, text="Начать цветоделение", command=start_processing).pack(pady=20)

# Поле для отображения статуса
status_label = tk.Label(root, text="Ожидание выбора файла...", wraplength=500)
status_label.pack(pady=10)

# Запуск GUI
root.mainloop()
