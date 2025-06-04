import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from ultralytics import YOLO

# Загрузка YOLOv8x модели
model = YOLO('yolov8x.pt')  # Загружаем модель yolov8x

# Классы YOLOv8 (предположительно база COCO)
translation = {
    "person": "человек",
    "cell phone": "Телефон",
    "bicycle": "велосипед",
    "car": "машина",
    "motorbike": "мотоцикл",
    "aeroplane": "самолёт",
    "bus": "автобус",
    "train": "поезд",
    "truck": "грузовик",
    "boat": "лодка",
    "traffic light": "светофор",
    "fire hydrant": "пожарный гидрант",
    "stop sign": "стоп знак",
    "parking meter": "парковочный счётчик",
    "bench": "скамейка",
    "bird": "птица",
    "cat": "кошка",
    "dog": "собака",
    "horse": "лошадь",
    "sheep": "овца",
    "cow": "корова",
    "elephant": "слон",
    "bear": "медведь",
    "zebra": "зебра",
    "giraffe": "жираф",
    "backpack": "рюкзак",
    "umbrella": "зонт",
    "handbag": "сумка",
    "tie": "галстук",
    "suitcase": "чемодан",
    "frisbee": "фрисби",
    "skis": "лыжи",
    "snowboard": "сноуборд",
    "sports ball": "мяч",
    "kite": "кайт",
    "baseball bat": "бита для бейсбола",
    "baseball glove": "перчатка для бейсбола",
    "skateboard": "скейтборд",
    "surfboard": "серфборд",
    "tennis racket": "теннисная ракетка",
    "bottle": "бутылка",
    "wine glass": "бокал для вина",
    "cup": "чашка",
    "fork": "вилка",
    "knife": "нож",
    "spoon": "ложка",
    "bowl": "миска",
    "banana": "банан",
    "apple": "яблоко",
    "sandwich": "сэндвич",
    "orange": "апельсин",
    "broccoli": "брокколи",
    "carrot": "морковь",
    "hot dog": "хот-дог",
    "pizza": "пицца",
    "donut": "пончик",
    "cake": "торт",
    "chair": "стул",
    "couch": "диван",
    "potted plant": "горшечное растение",
    "bed": "кровать",
    "dining table": "обеденный стол",
    "toilet": "туалет",
    "tv": "телевизор",
    "laptop": "ноутбук",
    "mouse": "мышь",
    "remote": "пульт",
    "keyboard": "клавиатура",
    "book": "книга",
    "clock": "часы",
    "vase": "ваза",
    "scissors": "ножницы",
    "teddy bear": "плюшевый медведь",
    "hair drier": "фен",
    "toothbrush": "зубная щётка"
}

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Распознавание объектов (YOLOv8x)")
        self.root.geometry("1920x1080")

        self.image_panel = tk.Label(root)
        self.image_panel.pack(expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Открыть изображение", command=self.open_image).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Распознать объекты", command=self.detect_objects).pack(side="left", padx=5)

        self.text_box = tk.Text(root, height=10, font=("Arial", 12))
        self.text_box.pack(fill="x", padx=10, pady=5)

        self.original_image = None
        self.display_image = None

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg *.bmp")])
        if not path:
            return

        self.original_image = cv2.imread(path)
        self.display_image = self.original_image.copy()
        self.show_image(self.display_image)

    def show_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_pil.thumbnail((1800, 900)) 
        self.tk_img = ImageTk.PhotoImage(img_pil)
        self.image_panel.config(image=self.tk_img)

    def detect_objects(self):
        if self.original_image is None:
            return

        results = model(self.original_image, verbose=False)[0]

        annotated = results.plot()  
        self.show_image(annotated)

        names = model.names
        boxes = results.boxes
        cls_ids = boxes.cls.cpu().numpy().astype(int)

        detected_names = [names[i] for i in cls_ids]

        translated_counts = {}
        for obj in detected_names:
            rus = translation.get(obj, obj)
            translated_counts[rus] = translated_counts.get(rus, 0) + 1

        self.text_box.delete("1.0", tk.END)
        if translated_counts:
            self.text_box.insert(tk.END, "Объекты на изображении:\n\n")
            for name, count in translated_counts.items():
                self.text_box.insert(tk.END, f"- {name} ({count} шт.)\n")
        else:
            self.text_box.insert(tk.END, "Объекты не распознаны.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()
