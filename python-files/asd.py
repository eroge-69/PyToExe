import cv2
import numpy as np
import mss
from ultralytics import YOLO
import pyttsx3

# --- Инициализация голосового движка ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')
try:
    engine.setProperty('voice', voices[1].id)  # Женский голос
except IndexError:
    engine.setProperty('voice', voices[0].id)  # По умолчанию — мужской
engine.setProperty('rate', 150)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Загрузка модели YOLO ---
model = YOLO("yolov8n.pt")  # Убедись, что модель установлена
class_names = model.names

# --- Настройки захвата экрана ---
with mss.mss() as sct:
    monitor = sct.monitors[1]

    print("🟢 Программа запущена. Выдели область с игрой.")

    while True:
        frame = np.array(sct.grab(monitor))
        results = model(frame)

        detected_cups = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if class_names[cls] in ['cup', 'bottle']:  # фильтруем по типу объекта
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w = x2 - x1
                    h = y2 - y1

                    center_x = x1 + w // 2
                    center_y = y1 + h // 2

                    detected_cups.append((center_x, center_y))

                    # Подсвечиваем стаканы
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Пример простого выбора (ближайший к центру экрана)
        if detected_cups:
            screen_center = (frame.shape[1] // 2, frame.shape[0] // 2)
            closest = min(detected_cups, key=lambda p: (p[0]-screen_center[0])**2 + (p[1]-screen_center[1])**2)
            crystal_x, crystal_y = closest

            # Сообщаем голосом
            speak(f"Кристалл здесь: {crystal_x}, {crystal_y}")

            # Рисуем зелёный круг вокруг найденного стакана
            cv2.circle(frame, (crystal_x, crystal_y), 10, (0, 255, 0), -1)

        cv2.imshow('UPX Crystal AI Tracker', frame)

        if cv2.waitKey(1) == 27:  # ESC
            break

cv2.destroyAllWindows()