import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import cv2
import pandas as pd
from ultralytics import YOLO
import sys


# === Настройка модели YOLO ===
model = YOLO(r"C:\Users\Арсений\Desktop\PycharmProjects\Practice\output\runs\detect\train\weights\best.pt")

# === Интерфейс приложения ===
class ImageToExcelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений в Excel")
        self.root.geometry("700x500")

        self.file_paths = []

        # Кнопки
        self.select_button = tk.Button(root, text="Выбрать изображения или папку", command=self.select_images)
        self.select_button.pack(pady=10)

        self.process_button = tk.Button(root, text="Обработать", command=self.process_images)
        self.process_button.pack(pady=10)

        # Поле логов
        self.log = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20)
        self.log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def log_message(self, message, bold=False):
        self.log.insert(tk.END, "\n")
        if bold:
            self.log.insert(tk.END, message + "\n", ("bold",))
        else:
            self.log.insert(tk.END, message + "\n")
        self.log.tag_config("bold", font=("TkDefaultFont", 10, "bold"))
        self.log.see(tk.END)

    def select_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if not paths:
            folder = filedialog.askdirectory()
            if folder:
                paths = [os.path.join(folder, f) for f in os.listdir(folder)
                         if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        self.file_paths = paths
        self.log_message(f"Выбрано файлов: {len(paths)}", bold=True)

    def process_images(self):
        for image_path in self.file_paths:
            try:
                self.log_message(f"\nОбработка: {image_path}")
                image = cv2.imread(image_path)
                results = model.predict(image, conf=0.25)

                boxes = results[0].boxes
                name = 0
                data = []
                for i in range(len(boxes)):
                    label = model.names[int(boxes.cls[i])]
                    if label == 'arrow':
                        continue

                    x1, y1, x2, y2 = map(int, boxes.xyxy[i])
                    width = x2 - x1
                    height = y2 - y1
                    data.append({
                        'Cell ID': f"cell{i}",
                        'Value': label,
                        'Type cell': 'Task',
                        'X': x1,
                        'Y': y1,
                        'Width': width,
                        'Height': height,
                        'Shape': 'rectangle'
                    })

                for row in data:
                    row.update({
                        'Diagram': 'схема 2.1',
                        'Layer Name': '',
                        'Layer ID': '',
                        'html': '',
                        'fontSize': '',
                        'fillColor': '',
                        'labelPosition': '',
                        'verticalLabelPosition': '',
                        'labelBackgroundColor': '',
                        'Класс': ''
                    })

                cells_df = pd.DataFrame(data, columns=[
                    'Diagram', 'Layer Name', 'Layer ID', 'Cell ID', 'Value', 'Type cell',
                    'X', 'Y', 'Width', 'Height', 'html', 'fontSize', 'fillColor', 'Shape',
                    'labelPosition', 'verticalLabelPosition', 'labelBackgroundColor', 'Класс'
                ])

                edges_df = pd.DataFrame(columns=[
                    'Diagram', 'Layer Name', 'Layer ID', 'Edge ID', 'Source', 'Target', 'Value',
                    'Style', 'Edge Style', 'Start Arrow', 'End Arrow', 'Start Fill', 'End Fill',
                    'Stroke Color', 'Stroke Width', 'Rounded', 'Orthogonal', 'Curved',
                    'Label Position', 'Label Background Color', 'Font Size', 'Font Color',
                    'Font Style', 'Font Family', 'Edge Points', 'Breakpoints'
                ])

                output_dir = os.path.join(os.path.dirname(image_path), "обработка изображения эксель")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(image_path))[0] + ".xlsx")

                if os.path.exists(output_path):
                    self.log_message(f"Файл уже существует: {output_path}", bold=True)
                    continue

                try:
                    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                        cells_df.to_excel(writer, sheet_name='Cells', index=False)
                        edges_df.to_excel(writer, sheet_name='Edges', index=False)
                    self.log_message(f"[✓] Успешно сохранено: {output_path}", bold=True)
                except PermissionError:
                    self.log_message(f"[Ошибка] Закрой файл: {output_path} и повтори попытку", bold=True)

            except Exception as e:
                self.log_message(f"[Ошибка] {e}", bold=True)


# === Запуск приложения ===
if __name__ == '__main__':
    root = tk.Tk()
    app = ImageToExcelApp(root)
    root.mainloop()










