import logging
import tkinter as tk
import numpy as np

from tkinter import filedialog
from tkinter import ttk
from ultralytics import YOLO
from torch import cuda
from PIL import ImageTk, Image, ImageDraw, ImageFont
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB


def get_yolo_predictions(img: np.ndarray, device: int | str) -> list:
    """
    Получает предсказания от модели YOLOv11 из numpy массива изображения.
    """
    if model is None:
        logger.warning("Модель не загружена.")
        return []
    try:
        results = model.predict(img, conf=0.5, device=device)
        annotations = []
        for result in results:
            if result.masks is not None:
                for mask, cls, box in zip(result.masks.xy, result.boxes.cls, result.boxes.xyxy):
                    class_id = int(cls)
                    polygon = [(float(x), float(y)) for x, y in mask]
                    x_min, y_min, _, _ = box
                    annotations.append({
                        "class_id": class_id,
                        "polygon": polygon,
                        "label_position": (float(x_min), float(y_min))
                    })
        return annotations

    except Exception as e:
        logger.error(f"Ошибка при выполнении инференса: {e}")
        return []


def draw_masks(img: np.ndarray, annotations: list) -> np.ndarray:
    """
    Отрисовывает маски и подписи классов на изображении (numpy array).
    """
    try:
        pil_img = Image.fromarray(cvtColor(img, COLOR_BGR2RGB)).convert("RGBA")
    except Exception as e:
        logger.error(f"Ошибка при открытии изображения: {e}")
        return img

    mask_layer = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask_layer)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    if not annotations:
        logger.warning("Нет предсказанных масок для изображения.")
    else:
        for ann in annotations:
            class_id = ann["class_id"]
            polygon = ann["polygon"]
            label_position = ann["label_position"]
            color = CLASS_COLORS.get(class_id, (255, 255, 255))
            class_name = CLASS_NAMES.get(class_id, "Unknown")

            if polygon and len(polygon) >= 2:
                draw.polygon(polygon, fill=color + (128,))
                draw.text(label_position, class_name, fill=color + (255,), font=font)

    result = Image.alpha_composite(pil_img, mask_layer)
    result = result.convert("RGB")
    result = np.array(result)
    return result


def open_file() -> None:
    """
    Функция, вызываемая при нажатии кнопки Open file.
    Считывает полный путь до файла из окна выбора файла.
    Обрабатывает и отрисовывает первый кадр видеофайла.
    Returns:
         None
    """
    global cap
    global filepath
    filename = filedialog.askopenfilename()
    if filename:
        filepath = filename
        cap = VideoCapture(filename)
        ret, frame = cap.read()
        if ret:
            frame = cvtColor(frame, COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((512, 512))
            img_tk = ImageTk.PhotoImage(image=img)

            label_video.img = img_tk
            label_video.configure(image=img_tk)

            label_video_segment.img = img_tk
            label_video_segment.configure(image=img_tk)
            logger.info(f"Video file opened, path: {filepath}")
            logger.info(f"used device: {'cuda' if used_device == 0 else 'cpu'}")


def process_video() -> None:
    """
    Функция, вызываемая при нажатии кнопки Play video.
    Обрабатывает видеофайл покадрово и выводит на экран кадр
    исходного видео и кадр с отрисованными сегментационными масками.
    Returns:
         None
    """
    global cap
    global used_device
    global stop_flag
    global restart_flag
    try:
        ret, frame = cap.read()
        if ret and not stop_flag:
            frame = cvtColor(frame, COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((512, 512))
            img_tk = ImageTk.PhotoImage(image=img)

            label_video.img = img_tk
            label_video.configure(image=img_tk)

            segment_annotations = get_yolo_predictions(frame, used_device)
            segment_frame = draw_masks(frame, segment_annotations)
            segment_img = Image.fromarray(segment_frame)
            segment_img = segment_img.resize((512, 512))
            segment_img_tk = ImageTk.PhotoImage(image=segment_img)

            label_video_segment.img = segment_img_tk
            label_video_segment.configure(image=segment_img_tk)
            label_video_segment.after(ms=125, func=process_video)

        elif stop_flag:
            restart_flag = True
            stop_flag = False

        elif not ret and not stop_flag:
            restart_flag = True
            restart_video()

    except Exception as ex:
        logger.error(f"{ex}")


def stop_video() -> None:
    """
    Функция, вызываемая при нажатии кнопки stop_video.
    Присваивает глобальной переменной stop_flag значение True.
    Returns:
        None
    """
    global stop_flag
    stop_flag = True


def restart_video() -> None:
    """
    Функция, вызываемая при нажатии кнопки restart_video.
    Присваивает глобальной переменной restart_flag значение False.
    Создает новый объект VideoCapture и отрисовывает первый кадр из открытого видео.
    Returns:
        None
    """
    global restart_flag
    global cap
    global filepath
    if restart_flag:
        restart_flag = False
        cap = VideoCapture(filepath)
        ret, frame = cap.read()
        if ret:
            frame = cvtColor(frame, COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((512, 512))
            img_tk = ImageTk.PhotoImage(image=img)

            label_video.img = img_tk
            label_video.configure(image=img_tk)

            label_video_segment.img = img_tk
            label_video_segment.configure(image=img_tk)
            logger.info(f"Video file opened, path: {filepath}")
            logger.info(f"used device: {'cuda' if used_device == 0 else 'cpu'}")


# Logger init
logging.basicConfig(
    format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s',
    level=logging.INFO
)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger = logging.getLogger('app_logger')
logger.addHandler(stream_handler)

# Video init
cap = None
stop_flag = False
restart_flag = False
filepath = ""

# Model init
MODEL_PATH = 'models/yolo11n-seg_prod.pt'
model = YOLO(MODEL_PATH)
used_device = 0 if cuda.is_available() else "cpu"

CLASS_NAMES = {0: "FT", 1: "Engine", 2: "Solar Panel"}
CLASS_COLORS = {0: (0, 255, 0), 1: (255, 0, 0), 2: (0, 0, 255)}


# App window init
root = tk.Tk()
root.title('sat viewer')
root.geometry("1280x600")
root.resizable(False, False)
video_frame = tk.Frame(root)

label_video = ttk.Label(video_frame, width=512)
label_video_segment = ttk.Label(video_frame, width=512)
label_video.pack(side="left", padx=10)
label_video_segment.pack(side="right", padx=10)

btn_open_file = ttk.Button(text="Open file", command=open_file)
btn_play_video = ttk.Button(text="Play video", command=process_video)
btn_stop_video = ttk.Button(text="Stop video", command=stop_video)
btn_restart_video = ttk.Button(text="Restart video", command=restart_video)

btn_open_file.place(relx=0.5, rely=0.03, anchor="center")
video_frame.place(relx=0.5, rely=0.5, anchor="center")
btn_play_video.place(relx=0.43, rely=0.97, anchor="center")
btn_stop_video.place(relx=0.5, rely=0.97, anchor="center")
btn_restart_video.place(relx=0.57, rely=0.97, anchor="center")


if __name__ == "__main__":
    root.mainloop()
