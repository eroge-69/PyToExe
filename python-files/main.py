# oh my God, look at dat bumper
# razrab slaboumniy
# vnimanie!!! huyney ne maytes...

# from kernel.Engine import Engine
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime, timezone
import json
import os
import av
from onvif import ONVIFCamera
from zeep.exceptions import Fault
from pathlib import Path
from tkinter import filedialog
import gc
import json
import math
import shutil
import torch
import cv2
from tqdm import tqdm
import time
# from extensions.callbacks import console_time_logger
# from extensions.decorators import benchmark
import os
import numpy as np
import pandas as pd
from ultralytics import YOLO
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
# from kernel.feature_extraction import calculate_angle, fig_to_base64, remove_outliers
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
from pathlib import Path
from datetime import datetime
import av
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import time
from functools import wraps






"""
!!!! feature_extraction !!!!
"""
joint_name_mapping = {
    'left_elbow': 'Левый локоть',
    'right_elbow': 'Правый локоть',
    'left_knee': 'Левое колено',
    'right_knee': 'Правое колено',
    'left_shoulder': 'Левое плечо',
    'right_shoulder': 'Правое плечо',
    'left_torso_thigh': 'Левая связь туловища и бедра',
    'right_torso_thigh': 'Правая связь туловища и бедра'
}


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Вычисляет угол между тремя точками (в градусах)
    """
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 0
    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    return np.degrees(np.arccos(cosine_angle))


def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded


def remove_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return series.clip(lower, upper)







def console_time_logger(function_name, elapsed):
    """
    Коллбэк-функция для декоратора benchmark, печатает в консоль
    :param function_name: имя вызыванной изначально функции
    :param elapsed: рантайм функции
    :return: ничего
    """

    print(f'{function_name} completed in {elapsed*1000:.2f}ms')

def benchmark(callback):

    """
    Декоратор, принимает в параметр коллбэк-функцию, отдает в нее название функции и время выполнения
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            callback(func.__name__, elapsed)
            return result

        return wrapper

    return decorator

def save_to_csv(data: pd.DataFrame, filename: str):
    """
    Сохраняет pd.DataFrame в .csv
    :param data: датафрейм
    :param filename: путь сохранения
    :return: ничого
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data.to_csv(filename, index=False)
    print(f'Результаты сохранены в {filename}')







class FrameHandler:

    """
    Один кадр из видео
    """

    nose = []
    left_eye = []
    right_eye = []
    left_ear = []
    right_ear = []
    left_shoulder = []
    right_shoulder = []
    left_elbow = []
    right_elbow = []
    left_wrist = []
    right_wrist = []
    left_hip = []
    right_hip = []
    left_knee = []
    right_knee = []
    left_ankle = []
    right_ankle = []

    def __init__(self, coords: np.ndarray, conf: np.ndarray):
        self.nose = [coords[0][0][:2], conf[0][0]]
        self.left_eye = [coords[0][1][:2], conf[0][1]]
        self.right_eye = [coords[0][2][:2], conf[0][2]]
        self.left_ear = [coords[0][3][:2], conf[0][3]]
        self.right_ear = [coords[0][4][:2], conf[0][4]]
        self.left_shoulder = [coords[0][5][:2], conf[0][5]]
        self.right_shoulder = [coords[0][6][:2], conf[0][6]]
        self.left_elbow = [coords[0][7][:2], conf[0][7]]
        self.right_elbow = [coords[0][8][:2], conf[0][8]]
        self.left_wrist = [coords[0][9][:2], conf[0][9]]
        self.right_wrist = [coords[0][10][:2], conf[0][10]]
        self.left_hip = [coords[0][11][:2], conf[0][11]]
        self.right_hip = [coords[0][12][:2], conf[0][12]]
        self.left_knee = [coords[0][13][:2], conf[0][13]]
        self.right_knee = [coords[0][14][:2], conf[0][14]]
        self.left_ankle = [coords[0][15][:2], conf[0][15]]
        self.right_ankle = [coords[0][16][:2], conf[0][16]]

    def get_series(self):
        attributes = [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
        data = {}
        for attr in attributes:
            coords_part, conf_part = getattr(self, attr)
            data[f'{attr}_x'] = coords_part[0]
            data[f'{attr}_y'] = coords_part[1]
            data[f'{attr}_conf'] = conf_part
        return pd.Series(data)







class Engine:

    """
    Движок, обрабатывающий видео, хранит о них инфу, загружает, выгружает, считает, делает все (почти).
    Поддерживает любое количество видео на одного пациента.
    """

    # относительные размеры
    _relative_sizes = {
        'shoulder_joint_distance': None,
        'forearm_left': None,
        'forearm_right': None,
        'brachium_left': None,
        'brachium_right': None,
        'pelvis_length': None,
        'thigh_left': None,
        'thigh_right': None,
        'shin_left': None,
        'shin_right': None
    }

    folder_path = None
    frame_rate = None

    # video_files хранит данные по каждому видео: ключ – путь, значение – {'_relative_sizes': ..., 'frames': [FrameHandler, ...]}
    video_files = {}

    # поддерживаемые расширения файлов
    _video_extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')

    model = None

    # модель для изъятия кейпоинтов, как релизнут веса yolo12, можно ее сунуть
    _model_path = 'yolo11x-pose.pt'



    # конструктор
    @benchmark(console_time_logger)
    def __init__(self, folder_path: str, frame_rate: int = 30, load_from_csv: bool = False):
        """

        :param folder_path: папка с видео/.csv файлами для обработки
        :param frame_rate: фпс видоса, критично важная штука (очевидно)
        :param load_from_csv: флаг загрузки уже посчитанных точек из .csv
        """
        self.folder_path = folder_path
        self.frame_rate = frame_rate
        if not load_from_csv:
            self.model = YOLO(self._model_path)
            self.log("Model YOLO installed]]]]]]]]]]]]]]]]]]]]]]]]]]")
            self.get_videos()
        else:
            self._read_raw_frames_from_csv()

    def log(self, msg, level="INFO"):
        os.makedirs(self.folder_path, exist_ok=True)  # создаёт папку при необходимости
        log_file = os.path.join(self.folder_path, "session_log.csv")
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{level.upper()}]"
        full_msg = f"[{timestamp}] {prefix} {msg}"

        try:
            is_new_file = not os.path.exists(log_file)
            with open(log_file, "a", encoding="utf-8") as f:
                if is_new_file:
                    f.write("Time,Level,Message\n")
                f.write(f"{timestamp},{level.upper()},{msg}\n")
        except Exception as e:
            print(f"Ошибка при записи в лог: {e}")


    def get_videos(self):

        """
        Сканит видосы с доступными расширениями в директории.
        Видео должны быть синхронизированы для правильной обработки.
        Поддерживает любое количество видео.
        """

        for file in os.listdir(self.folder_path):
            if file.lower().endswith(self._video_extensions):
                self.video_files[os.path.join(self.folder_path, file)] = {'_relative_sizes': self._relative_sizes, 'frames': []}
            self.log(f"Сканирование файла {file}")


    @benchmark(console_time_logger)
    def trim_videos(self):
        import shutil

        folder = Path(self.folder_path)
        json_path = folder / "video_timestamps.json"

        if not json_path.exists():
            self.log(f"Не найден файл video_timestamps.json!", "ERROR")
            raise FileNotFoundError(json_path)

        with open(json_path, 'r') as f:
            data = json.load(f)

        timestamps = {
            item["camera"]: datetime.fromisoformat(item["timestamp_camera"].replace("Z", "+00:00"))
            for item in data if item["camera"] in ["cam1", "cam2", "cam3"]
        }
        ref_cam = max(timestamps, key=timestamps.get)
        ref_time = timestamps[ref_cam]
        self.log(f"Эталонная камера: {ref_cam}, время старта: {ref_time.isoformat()}", "INFO")

        # 1. Обрезаем cam1, cam2, cam3
        for cam in ["cam1", "cam2", "cam3"]:
            ts = timestamps[cam]
            delta_sec = (ref_time - ts).total_seconds()
            video_file = folder / f"{cam}.mp4"
            trimmed_file = folder / f"{cam}_trimmed.mp4"

            # Удаляем старое обрезанное видео
            if trimmed_file.exists():
                trimmed_file.unlink()

            if not video_file.exists():
                self.log(f"Не найдено видео: {video_file}", "ERROR")
                continue

            try:
                with av.open(str(video_file)) as container:
                    video_stream = container.streams.video[0]
                    fps = float(video_stream.average_rate)

                    if delta_sec < 0:
                        frame_offset = 0
                        self.log(f"{cam} позже эталона на {-delta_sec:.3f} сек. Обрезка не требуется.")
                    else:
                        frame_offset = round(delta_sec * (24.7 if cam == "cam3" else fps))
                        self.log(
                            f"{cam} раньше эталона на {delta_sec:.3f} сек → обрезка {frame_offset} кадров (FPS={fps:.2f})")

                    with av.open(str(trimmed_file), mode='w') as output:
                        in_stream = video_stream
                        in_stream.thread_type = "AUTO"
                        out_stream = output.add_stream("libx264", rate=in_stream.average_rate)
                        out_stream.width = in_stream.width
                        out_stream.height = in_stream.height
                        out_stream.pix_fmt = "yuv420p"
                        out_stream.time_base = in_stream.time_base

                        saved = 0
                        for i, frame in enumerate(container.decode(video=0)):
                            if i >= frame_offset:
                                for packet in out_stream.encode(frame):
                                    output.mux(packet)
                                saved += 1
                        for packet in out_stream.encode():
                            output.mux(packet)
            except Exception as e:
                self.log(f"Ошибка при обрезке видео {video_file}: {e}", "ERROR")

        # cam4.mp4 — просто копируем как cam4_trimmed.mp4
        cam4_src = folder / "cam4.mp4"
        cam4_trimmed = folder / "cam4_trimmed.mp4"
        if cam4_trimmed.exists():
            cam4_trimmed.unlink()
        if cam4_src.exists():
            shutil.copy2(cam4_src, cam4_trimmed)

        # --- ЖДЁМ, чтобы Windows освободил файлы ---
        gc.collect()
        time.sleep(0.5)

        # 2. Теперь удаляем исходные и переименовываем trimmed -> orig
        for cam in ["cam1", "cam2", "cam3", "cam4"]:
            orig_path = folder / f"{cam}.mp4"
            trimmed_path = folder / f"{cam}_trimmed.mp4"
            # Сначала удаляем оригинал (ждём если не отпускает)
            for _ in range(10):
                try:
                    if orig_path.exists():
                        orig_path.unlink()
                    break
                except PermissionError as e:
                    self.log(f"Файл всё ещё занят, жду... {e}", "WARNING")
                    time.sleep(0.3)
                    gc.collect()
            # Переименовываем
            if trimmed_path.exists():
                trimmed_path.rename(orig_path)

        self.log("Обрезка и сохранение всех видео завершены.", "INFO")
        print(f"Видео сохранены в: {folder}")

    # def trim_videos(self):
    #     folder = Path(self.folder_path)
    #     json_path = folder / "video_timestamps.json"
    #
    #     if not json_path.exists():
    #         self.log(f"Не найден файл video_timestamps.json!", "ERROR")
    #         raise FileNotFoundError(json_path)
    #
    #     with open(json_path, 'r') as f:
    #         data = json.load(f)
    #
    #     timestamps = {
    #         item["camera"]: datetime.fromisoformat(item["timestamp_camera"].replace("Z", "+00:00"))
    #         for item in data if item["camera"] in ["cam1", "cam2", "cam3"]
    #     }
    #     ref_cam = max(timestamps, key=timestamps.get)
    #     ref_time = timestamps[ref_cam]
    #     self.log(f"Эталонная камера: {ref_cam}, время старта: {ref_time.isoformat()}", "INFO")
    #
    #     # Обрезаем видео cam1, cam2, cam3
    #     for cam in ["cam1", "cam2", "cam3"]:
    #         ts = timestamps[cam]
    #         delta_sec = (ref_time - ts).total_seconds()
    #         video_file = folder / f"{cam}.mp4"
    #         trimmed_file = folder / f"{cam}_trimmed.mp4"
    #
    #         # Удаляем старое обрезанное видео
    #         if trimmed_file.exists():
    #             trimmed_file.unlink()
    #
    #         if not video_file.exists():
    #             self.log(f"Не найдено видео: {video_file}", "ERROR")
    #             continue
    #
    #         try:
    #             container = av.open(str(video_file))
    #             video_stream = container.streams.video[0]
    #             fps = float(video_stream.average_rate)
    #         except Exception as e:
    #             self.log(f"Ошибка открытия видео {video_file}: {e}", "ERROR")
    #             continue
    #
    #         if delta_sec < 0:
    #             frame_offset = 0
    #             self.log(f"{cam} позже эталона на {-delta_sec:.3f} сек. Обрезка не требуется.")
    #         else:
    #             frame_offset = round(delta_sec * (24.7 if cam == "cam3" else fps))
    #             self.log(f"{cam} раньше эталона на {delta_sec:.3f} сек → обрезка {frame_offset} кадров (FPS={fps:.2f})")
    #
    #         # Обрезка видео
    #         try:
    #             container = av.open(str(video_file))
    #             output = av.open(str(trimmed_file), mode='w')
    #             in_stream = container.streams.video[0]
    #             in_stream.thread_type = "AUTO"
    #             out_stream = output.add_stream("libx264", rate=in_stream.average_rate)
    #             out_stream.width = in_stream.width
    #             out_stream.height = in_stream.height
    #             out_stream.pix_fmt = "yuv420p"
    #             out_stream.time_base = in_stream.time_base
    #
    #             saved = 0
    #             for i, frame in enumerate(container.decode(video=0)):
    #                 if i >= frame_offset:
    #                     for packet in out_stream.encode(frame):
    #                         output.mux(packet)
    #                     saved += 1
    #             for packet in out_stream.encode():
    #                 output.mux(packet)
    #
    #             output.close()
    #             container.close()
    #             time.sleep(0.1)
    #
    #             # if saved == 0:
    #             #     self.log(f"[!] {cam}: не сохранено ни одного кадра!", "WARNING")
    #             # else:
    #             #     self.log(f"{cam}: сохранено кадров: {saved}")
    #
    #                 # === Удаляем исходное видео ===
    #             video_file.unlink()
    #             # self.log(f"Исходное видео удалено: {video_file}")
    #
    #         except Exception as e:
    #             self.log(f"Ошибка при обрезке видео {video_file}: {e}", "ERROR")
    #
    #     # cam4.mp4 — просто копируем как cam4_trimmed.mp4
    #     cam4_src = folder / "cam4.mp4"
    #     cam4_trimmed = folder / "cam4_trimmed.mp4"
    #     if cam4_trimmed.exists():
    #         cam4_trimmed.unlink()
    #
    #     if cam4_src.exists():
    #         shutil.copy2(cam4_src, cam4_trimmed)
    #         # self.log("cam4.mp4 скопирован как cam4_trimmed.mp4")
    #         cam4_src.unlink()
    #         # self.log(f"Исходное видео удалено: {cam4_src}")
    #
    #     self.log("Обрезка и сохранение всех видео завершены.", "INFO")
    #     print(f"Видео сохранены в: {folder}")
    #
    #     for cam in ["cam1", "cam2", "cam3", "cam4"]:
    #         trimmed_path = folder / f"{cam}_trimmed.mp4"
    #         orig_path = folder / f"{cam}.mp4"
    #         if trimmed_path.exists():
    #             if orig_path.exists():
    #                 orig_path.unlink()  # удаляем старый
    #             trimmed_path.rename(orig_path)



    @benchmark(console_time_logger)
    def extract_frames_run(self):

        """
        Запуск извлечения кадров из видео.
        Проходит по всем видео в self.video_files и последовательно извлекает кадры из каждого.
        Сохраняет кадры в экземплярах FrameHandler в self.video_files
        """

        # for video in self.video_files.keys():
        #     pre_open_video = cv2.VideoCapture(video)
        #     total_frames = int(pre_open_video.get(cv2.CAP_PROP_FRAME_COUNT))
        #     pre_open_video.release()
        #     for frame in tqdm(self._extract_frames_generator(video), total=total_frames, desc=f'Processing {video}'):
        #         keypoints = self.model(frame, verbose=False, device='cuda:0')[0].keypoints
        #         if keypoints.has_visible:
        #             self.video_files[video]['frames'].append(FrameHandler(keypoints.xy.cpu().numpy(), keypoints.conf.cpu().numpy()))
        #         else:
        #             self.video_files[video]['frames'].append(FrameHandler(np.zeros((1, 17, 3)), np.zeros((1, 17))))
        #     self.log(f"Извлечение кадров из {video}")
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        # device = 'cpu'

        for video in self.video_files.keys():
            pre_open_video = cv2.VideoCapture(video)
            total_frames = int(pre_open_video.get(cv2.CAP_PROP_FRAME_COUNT))
            pre_open_video.release()

            for frame in tqdm(self._extract_frames_generator(video), total=total_frames, desc=f'Processing {video}'):
                keypoints = self.model(frame, verbose=False, device=device)[0].keypoints

                if keypoints.has_visible:
                    self.video_files[video]['frames'].append(
                        FrameHandler(keypoints.xy.cpu().numpy(), keypoints.conf.cpu().numpy())
                    )
                else:
                    self.video_files[video]['frames'].append(
                        FrameHandler(np.zeros((1, 17, 3)), np.zeros((1, 17)))
                    )

            self.log(f"Извлечение кадров из {video}")





    def save_raw_frames_to_csv(self):

        """
        Сохраняет извлеченные ключевые точки в отдельные .csv.
        Название файлов совпадает с названиями видео.
        Сохраняет в ту же папку, что была передана в конструктор
        """

        for video_path in self.video_files:
            frames = self.video_files[video_path]['frames']
            if not frames:
                self.log(f"No data to save: {video_path}")
                continue
            df = pd.DataFrame([frame.get_series() for frame in frames])
            base_name = os.path.splitext(video_path)[0]
            csv_filename = f"{base_name}_keypoints.csv"
            df.to_csv(csv_filename, index=False)
            self.log(f"Data saved in : {csv_filename}")
            self.log(f"Данные о ключевых точках для видео  {video_path} созранены в {base_name}_keypoints.csv")






    def _read_raw_frames_from_csv(self):

        """
        Срабатывает при load_from_csv=True
        Вместо обработки видосов загружает точки из готовых .csv
        """

        for file in os.listdir(self.folder_path):
            if file.endswith('_keypoints.csv'):
                csv_path = os.path.join(self.folder_path, file)
                video_path = csv_path.replace('_keypoints.csv', '')
                self.video_files[video_path] = {
                    '_relative_sizes': self._relative_sizes.copy(),
                    'frames': []
                }
                df = pd.read_csv(csv_path)
                frames = []
                for _, row in df.iterrows():
                    frame = self._raw_to_frame_handler(row)
                    frames.append(frame)
                self.video_files[video_path]['frames'] = frames
                print(f"Loaded {len(frames)} frames from {csv_path}")
            self.log(f"Чтение ключевых точек из готового файла для {file}")





    def __str__(self):
        return (f'{"-"*100}\nRelative sizes:\n{self._relative_sizes}\n{"-"*100}\nFolder path: {self.folder_path}\n'
                f'{"-"*100}\nVideo files: {self.video_files.keys()} \n{"-"*100}\nSupported ext.: {self._video_extensions}\n{"-"*100}\n')





    ######################################################
    # Новые функции для обработки метрик ключевых точек
    ######################################################





    def combine_synchronized_frames(self) -> pd.DataFrame:
        """
        Объединяет синхронизированные кадры для расчёта углов.
        Возвращает DataFrame с колонками: frame, left_elbow_angle, right_elbow_angle,
        left_knee_angle, right_knee_angle, left_shoulder_angle, right_shoulder_angle,
        left_pelvis_angle, right_pelvis_angle.
        Так сделано по причине долгой реализации нормального варианта
        """
        angle_groups = {
            'left_elbow_angle': ['left_shoulder', 'left_elbow', 'left_wrist'],
            'right_elbow_angle': ['right_shoulder', 'right_elbow', 'right_wrist'],
            'left_knee_angle': ['left_hip', 'left_knee', 'left_ankle'],
            'right_knee_angle': ['right_hip', 'right_knee', 'right_ankle'],
            'left_shoulder_angle': ['left_elbow', 'left_shoulder', 'left_hip'],
            'right_shoulder_angle': ['right_elbow', 'right_shoulder', 'right_hip'],
            'left_pelvis_angle': ['left_shoulder', 'left_hip', 'left_knee'],
            'right_pelvis_angle': ['right_shoulder', 'right_hip', 'right_knee'],
            'left_shoulder_ear_angle' : ['left_ear', 'left_shoulder', 'left_hip'],
            'right_shoulder_ear_angle': ['right_ear', 'right_shoulder', 'right_hip'],
        }

        min_frames = min(len(data['frames']) for data in self.video_files.values())
        combined_rows = []

        for i in range(min_frames):
            row = {'frame': i}
            for angle_name, parts in angle_groups.items():
                best_conf = -1
                best_coords = None

                for video_data in self.video_files.values():
                    frame_handler = video_data['frames'][i]
                    series = frame_handler.get_series()

                    conf_values = [series.get(f'{p}_conf', 0) for p in parts]
                    conf_values = [c if pd.notna(c) else 0 for c in conf_values]

                    mean_conf = sum(conf_values) / len(conf_values)
                    if mean_conf > best_conf:
                        best_conf = mean_conf
                        best_coords = {
                            p: (
                                series.get(f'{p}_x', np.nan),
                                series.get(f'{p}_y', np.nan)
                            ) for p in parts
                        }

                if best_coords and all(pd.notna(pt) for pt in best_coords.values()):
                    pt1, pt2, pt3 = map(np.array, best_coords.values())
                    row[angle_name] = calculate_angle(pt1, pt2, pt3)
                else:
                    row[angle_name] = np.nan  # Заполняем NaN, чтобы потом корректно обрабатывать

            combined_rows.append(row)

        df = pd.DataFrame(combined_rows)
        df.fillna(0, inplace=True)  # Заменяем NaN на 0 в финальном DataFrame

        combined_filename = os.path.join(self.folder_path, "combined_angles.csv")
        print(combined_filename)
        df.to_csv(combined_filename, index=False)

        self.log(f"Формирование общего файла с углами суставов по всем видео -> {combined_filename}")

        return df


    def calculate_flexion_extension_amplitudes(self) -> pd.DataFrame:
        # angle_df = self.combine_synchronized_frames()
        file_path = os.path.join(self.folder_path, "combined_angles.csv")
        angle_df = pd.read_csv(file_path)
        print(type(angle_df))
        amplitude_data = []
        min_counter = 3 # единое минимальное значение кадров для определения фазы

        for col in angle_df.columns:
            if col == 'frame':
                continue

            flexion_amplitudes, extension_amplitudes = [], []
            flexion_frames, extension_frames = [], []
            flexion_speeds, extension_speeds= [], []

            previous = angle_df[col].iloc[0]
            current = angle_df[col].iloc[1]
            phase = 'extension' if current > previous else 'flexion'
            start = previous
            counter = 1
            frame_rate = 25

            for i in range(1, len(angle_df)):
                current = angle_df[col].iloc[i]
                frame = angle_df['frame'].iloc[i]

                if current > previous:  # разгибание
                    if phase == 'flexion':
                        if counter >= min_counter:
                            # flexion_amplitudes.append(abs(start - previous))
                            # flexion_frames.append(frame)
                            amp = abs(start - previous)
                            speed = amp / counter * (1000 / frame_rate) if counter > 0 else 0
                            flexion_amplitudes.append(amp)
                            flexion_frames.append(frame)
                            flexion_speeds.append(speed)
                        else:
                            flexion_amplitudes.append(0)
                            flexion_frames.append(frame)
                            flexion_speeds.append(0)
                        start = previous
                        phase = 'extension'
                        counter = 1
                    else:
                        counter += 1
                elif current < previous:  # сгибание
                    if phase == 'extension':
                        if counter >= min_counter:
                            # extension_amplitudes.append(abs(start - previous))
                            # extension_frames.append(frame)
                            amp = abs(start - previous)
                            speed = amp / counter * (1000 / frame_rate) if counter > 0 else 0
                            extension_amplitudes.append(amp)
                            extension_frames.append(frame)
                            extension_speeds.append(speed)
                        else:
                            extension_amplitudes.append(0)
                            extension_frames.append(frame)
                            extension_speeds.append(0)
                        start = previous
                        phase = 'flexion'
                        counter = 1
                    else:
                        counter += 1
                previous = current

            # обработка последней фазы
            last_frame = angle_df['frame'].iloc[-1]
            if phase == 'flexion' and counter >= min_counter:
                amp = abs(start - previous)
                speed = amp / counter * (1000 / frame_rate) if counter > 0 else 0
                flexion_amplitudes.append(amp)
                flexion_frames.append(last_frame)
                flexion_speeds.append(speed)
            elif phase == 'extension' and counter >= min_counter:
                amp = abs(start - previous)
                speed = amp / counter * (1000 / frame_rate) if counter > 0 else 0
                extension_amplitudes.append(amp)
                extension_frames.append(last_frame)
                extension_speeds.append(speed)

            amplitude_data.append({
                'angle': col,
                'flexion_amplitudes': flexion_amplitudes,
                'flexion_frames': flexion_frames,
                'flexion_speeds': flexion_speeds,
                'extension_amplitudes': extension_amplitudes,
                'extension_frames': extension_frames,
                'extension_speeds': extension_speeds
            })

        amplitude_df = pd.DataFrame(amplitude_data)
        combined_amp_filename = os.path.join(self.folder_path, "amplitudes_refined.csv")
        amplitude_df.to_csv(combined_amp_filename, index=False)

        self.log(f"Формирование общего файла с амплитудами углов суставов по всем видео -> {combined_amp_filename}")

        return amplitude_df


    @benchmark(console_time_logger)
    def generate_full_motion_report(self, generate_video: bool = False):
        """
        Итоговый HTML-отчёт: метрики, все графики по суставам, амплитуды, сводные таблицы.
        Блоки идут строго в нужном порядке.
        """

        file_path = os.path.join(self.folder_path, "combined_angles.csv")
        df_angles = pd.read_csv(file_path)
        for col in df_angles.select_dtypes(include=[np.number]).columns:
            df_angles[col] = remove_outliers(df_angles[col])

        angle_joints = [
            'left_elbow_angle', 'right_elbow_angle',
            'left_knee_angle', 'right_knee_angle',
            'left_shoulder_angle', 'right_shoulder_angle',
            'left_pelvis_angle', 'right_pelvis_angle',
            'left_shoulder_ear_angle', 'right_shoulder_ear_angle',
        ]
        sampling_rate = self.frame_rate

        # --- Блок 1: Таблицы по углам
        joint_metrics = {}
        for joint in angle_joints:
            series = df_angles[joint]
            dt = 1 / sampling_rate
            velocity = np.abs(np.gradient(series, dt))
            acceleration = np.abs(np.gradient(velocity, dt))
            n = len(series)
            fft_vals = np.fft.fft(series)
            freqs = np.fft.fftfreq(n, d=dt)
            mask = freqs > 0
            dominant_freq = freqs[mask][np.argmax(np.abs(fft_vals[mask]))] if np.any(mask) else np.nan
            joint_metrics[joint] = {
                'Среднее значение': np.mean(series),
                'СКО': np.std(series),
                'Минимум': np.min(series),
                'Максимум': np.max(series),
                'Разброс': np.max(series) - np.min(series),
                'Средняя скорость': np.mean(velocity),
                'СКО скорости': np.std(velocity),
                'Среднее ускорение': np.mean(acceleration),
                'СКО ускорения': np.std(acceleration),
                'Доминирующая частота (Гц)': dominant_freq
            }
        metrics_df = pd.DataFrame(joint_metrics).T
        metrics_html = metrics_df.to_html(classes='table table-striped', float_format="%.2f")

        # --- Блок 1: Таблицы по амплитудам
        amplitude_df = self.calculate_flexion_extension_amplitudes()
        amplitude_metrics, amplitude_metrics_speed = {}, {}
        amp_plot_blocks = []  # для сбора всех амплитудных графиков

        for idx, row in amplitude_df.iterrows():
            angle = row['angle']
            flexion_amplitudes = np.array(row['flexion_amplitudes'])
            extension_amplitudes = np.array(row['extension_amplitudes'])
            flexion_frames = row['flexion_frames']
            extension_frames = row['extension_frames']
            flexion_speeds = row.get('flexion_speeds', [0] * len(flexion_amplitudes))
            extension_speeds = row.get('extension_speeds', [0] * len(extension_amplitudes))

            all_amplitudes = np.concatenate([flexion_amplitudes, extension_amplitudes])
            all_frames = np.sort(np.concatenate([flexion_frames, extension_frames]))
            # combined_amplitudes = np.concatenate([flexion_amplitudes, extension_amplitudes])
            # combined_frames = np.concatenate([flexion_frames, extension_frames])
            # mask = combined_frames <= 700
            # all_amplitudes = combined_amplitudes[mask]
            # all_frames = combined_frames[mask]
            # sorted_indices = np.argsort(all_frames)
            # all_amplitudes = all_amplitudes[sorted_indices]
            # all_frames = all_frames[sorted_indices]
            amplitudes_nonzero = all_amplitudes[all_amplitudes > 0]
            velocity = np.gradient(all_amplitudes, edge_order=2)
            acceleration = np.gradient(velocity, edge_order=2)
            dt = 1 / self.frame_rate
            n = len(amplitudes_nonzero)
            fft_vals = np.fft.fft(amplitudes_nonzero)
            freqs = np.fft.fftfreq(n, d=dt)
            mask_f = freqs > 0
            dominant_freq = freqs[mask_f][np.argmax(np.abs(fft_vals[mask_f]))] if np.any(mask_f) else np.nan

            amplitude_metrics[angle] = {
                'Среднее значение': np.mean(amplitudes_nonzero),
                'СКО': np.std(amplitudes_nonzero),
                'Минимум': np.min(amplitudes_nonzero),
                'Максимум': np.max(amplitudes_nonzero),
                'Разброс': np.ptp(amplitudes_nonzero),
                'Средняя скорость': np.mean(np.abs(velocity)),
                'СКО скорости': np.std(np.abs(velocity)),
                'Среднее ускорение': np.mean(np.abs(acceleration)),
                'СКО ускорения': np.std(np.abs(acceleration)),
                'Доминирующая частота (Гц)': dominant_freq
            }

            # --- Графики амплитуды и скорости для блока 2 ---
            # График амплитуд
            fig1, ax1 = plt.subplots(figsize=(8,4))
            ax1.plot(all_frames, all_amplitudes, marker='o', linestyle='-', color = 'lightcoral', label='Амплитуды')
            ax1.set_xlabel('Кадр')
            ax1.set_ylabel('Амплитуда (градусы)')
            ax1.set_title(f'Амплитуда: {angle}')
            ax1.grid(True)
            plt.tight_layout()
            plot_img1 = fig_to_base64(fig1)
            plt.close(fig1)

            # График скоростей амплитуд
            combined_speeds = np.concatenate([flexion_speeds, extension_speeds])
            combined_speed_frames = np.concatenate([flexion_frames, extension_frames])
            sorted_speed_indices = np.argsort(combined_speed_frames)
            all_speeds = combined_speeds[sorted_speed_indices]
            all_frame_speed = combined_speed_frames[sorted_speed_indices]
            fig2, ax2 = plt.subplots(figsize=(8,4))
            ax2.plot(all_frame_speed, all_speeds, marker='o', linestyle='-', color = 'navy', label='Скорости')
            ax2.set_xlabel('Кадр')
            ax2.set_ylabel('Скорость (град/кадр)')
            ax2.set_title(f'Скорость: {angle}')
            ax2.grid(True)
            plt.tight_layout()
            plot_img2 = fig_to_base64(fig2)
            plt.close(fig2)

            amp_plot_blocks.append({
                "angle": angle,
                "amp_plot": plot_img1,
                "speed_plot": plot_img2
            })

        amplitude_metrics_df = pd.DataFrame(amplitude_metrics).T
        amplitude_metrics_html = amplitude_metrics_df.to_html(classes='table table-striped', float_format="%.2f")

        # --- Блок 2: Графики по суставам (3 из углов, 2 из амплитуды)
        plots_html = ""
        for joint in angle_joints:
            series = df_angles[joint]
            frames = df_angles['frame'] if 'frame' in df_angles.columns else df_angles.index
            dt = 1 / sampling_rate
            velocity = np.gradient(series, dt)
            acceleration = np.gradient(velocity, dt)
            fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
            axs[0].plot(frames, series, marker='o', linestyle='-')
            axs[0].set_title(f"{joint.replace('_', ' ').title()}: угол")
            axs[0].set_ylabel('Угол (°)')
            axs[0].grid(True)
            axs[1].plot(frames, velocity, marker='o', linestyle='-', color='orange')
            axs[1].set_title("Угловая скорость")
            axs[1].set_ylabel('Град/сек')
            axs[1].grid(True)
            axs[2].plot(frames, acceleration, marker='o', linestyle='-', color='green')
            axs[2].set_title("Угловое ускорение")
            axs[2].set_ylabel('Град/сек²')
            axs[2].set_xlabel('Кадр')
            axs[2].grid(True)
            plt.tight_layout()
            plot_img = fig_to_base64(fig)
            plt.close(fig)
            # --- 3 графика из подсчета углов ---
            plots_html += f"<h3>{joint.replace('_', ' ').title()}</h3>"
            plots_html += f"<b>Угол</b><br><img src='data:image/png;base64,{plot_img}'><br>"

            # --- 2 графика из амплитуд ---
            ampblock = next((a for a in amp_plot_blocks if a["angle"] == joint), None)
            if ampblock:
                plots_html += f"<b>Амплитуда</b><br><img src='data:image/png;base64,{ampblock['amp_plot']}'><br>"
                plots_html += f"<b>Скорость амплитуды</b><br><img src='data:image/png;base64,{ampblock['speed_plot']}'><br><hr>"

        # --- Оставшиеся блоки: PCA+KMeans, симметрия, координация ---
        data_for_pca = df_angles[angle_joints].fillna(df_angles[angle_joints].mean()).values
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(data_for_pca)
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(data_for_pca)
        fig, ax = plt.subplots(figsize=(8, 6))
        scatter = ax.scatter(pca_result[:, 0], pca_result[:, 1], c=clusters, cmap='viridis', alpha=0.7)
        ax.set_title('PCA + KMeans кластеризация по углам суставов')
        ax.set_xlabel('PCA компонент 1')
        ax.set_ylabel('PCA компонент 2')
        legend1 = ax.legend(*scatter.legend_elements(), title="Кластеры")
        ax.add_artist(legend1)
        pca_plot = fig_to_base64(fig)
        plt.close(fig)
        pca_html = f'<h2>PCA + KMeans кластеризация</h2><img src="data:image/png;base64,{pca_plot}" alt="PCA + KMeans plot"><br>'

        symmetry = {}
        if 'left_elbow_angle' in df_angles.columns and 'right_elbow_angle' in df_angles.columns:
            symmetry['Локти'] = {
                'Средняя разница': np.mean(np.abs(df_angles['left_elbow_angle'] - df_angles['right_elbow_angle'])),
                'Корреляция': np.corrcoef(df_angles['left_elbow_angle'], df_angles['right_elbow_angle'])[0, 1]
            }
        if 'left_knee_angle' in df_angles.columns and 'right_knee_angle' in df_angles.columns:
            symmetry['Колени'] = {
                'Средняя разница': np.mean(np.abs(df_angles['left_knee_angle'] - df_angles['right_knee_angle'])),
                'Корреляция': np.corrcoef(df_angles['left_knee_angle'], df_angles['right_knee_angle'])[0, 1]
            }
        if 'left_shoulder_angle' in df_angles.columns and 'right_shoulder_angle' in df_angles.columns:
            symmetry['Плечи'] = {
                'Средняя разница': np.mean(
                    np.abs(df_angles['left_shoulder_angle'] - df_angles['right_shoulder_angle'])),
                'Корреляция': np.corrcoef(df_angles['left_shoulder_angle'], df_angles['right_shoulder_angle'])[0, 1]
            }
        if 'left_pelvis_angle' in df_angles.columns and 'right_pelvis_angle' in df_angles.columns:
            symmetry['Таз'] = {
                'Средняя разница': np.mean(np.abs(df_angles['left_pelvis_angle'] - df_angles['right_pelvis_angle'])),
                'Корреляция': np.corrcoef(df_angles['left_pelvis_angle'], df_angles['right_pelvis_angle'])[0, 1]
            }
        symmetry_df = pd.DataFrame(symmetry).T
        symmetry_html = symmetry_df.to_html(classes='table table-striped', float_format="%.2f")

        coordination = {}
        if 'left_elbow_angle' in df_angles.columns and 'left_shoulder_angle' in df_angles.columns:
            coordination['Левая рука (локоть-плечо)'] = \
                np.corrcoef(df_angles['left_elbow_angle'], df_angles['left_shoulder_angle'])[0, 1]
        if 'right_elbow_angle' in df_angles.columns and 'right_shoulder_angle' in df_angles.columns:
            coordination['Правая рука (локоть-плечо)'] = \
                np.corrcoef(df_angles['right_elbow_angle'], df_angles['right_shoulder_angle'])[0, 1]
        coordination_df = pd.DataFrame.from_dict(coordination, orient='index', columns=['Коэффициент корреляции'])
        coordination_html = coordination_df.to_html(classes='table table-striped', float_format="%.2f")

        # --- Сводный график по амплитудам (в самом конце)
        summary_df = amplitude_metrics_df.copy()
        angles = summary_df.index.tolist()
        means = summary_df['Среднее значение'].values
        mins = summary_df['Минимум'].values
        maxs = summary_df['Максимум'].values
        dominant_freqs = summary_df['Доминирующая частота (Гц)'].values
        x = np.arange(len(angles))
        width = 0.6
        vmin = np.nanmin(dominant_freqs)
        vmax = np.nanmax(dominant_freqs)
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap('coolwarm')
        bar_colors = [cmap(norm(freq)) if not np.isnan(freq) else (0.7, 0.7, 0.7, 1.0) for freq in dominant_freqs]
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(x, means, width=width, color=bar_colors, edgecolor='black', label='Средняя амплитуда')
        ax.scatter(x, mins, color='red', marker='v', label='Минимум')
        ax.scatter(x, maxs, color='green', marker='^', label='Максимум')
        ax.set_xticks(x)
        ax.set_xticklabels(angles, rotation=45, ha='right')
        ax.set_ylabel("Амплитуда (градусы)")
        ax.set_title("Сводный график по амплитудам суставов")
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)
        ax.legend()
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label("Доминирующая частота (Гц)")
        plt.tight_layout()
        summary_img = fig_to_base64(fig)
        plt.close(fig)

        # --- HTML ---
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Объединённый отчёт по анализу движений</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                .table th {{ background-color: #f2f2f2; }}
                h2 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h1>Объединённый отчёт по анализу движений</h1>
            <h2>Сводные метрики по углам суставов</h2>
            {metrics_html}
            <h2>Сводные метрики амплитуд</h2>
            {amplitude_metrics_html}

            <h2>Графики по суставам</h2>
            {plots_html}

            {pca_html}
            <h2>Метрики симметрии</h2>
            {symmetry_html}
            <h2>Метрики координации</h2>
            {coordination_html}

            <h2>Сводный график по амплитудам</h2>
            <img src="data:image/png;base64,{summary_img}" alt="Сводный график"><br>
        </body>
        </html>
        """
        report_filename = os.path.join(self.folder_path, "full_motion_report.html")
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Объединённый отчёт сохранён в {report_filename}")
        return report_filename


    def compute_relative_sizes(self, angle_threshold: float = 175.0):
        """
        Для каждого синхронизированного момента (индекс кадра от 0 до min_frames),
        перебирает кадры из всех видео.
        Если в моменте i обнаружено хотя бы два кадра, где
          - угол в колене (и угол между корпусом и ногой) удовлетворяет условию,
        вычисляются относительные размеры:
          pelvis_ratio = (расстояние между тазовыми точками) / (длина бедра)
          shoulder_ratio = (расстояние между плечевыми точками) / (длина бедра)
        Для каждого момента вычисляются средние значения этих отношений по всем видео,
        где данные валидны.
        Далее выбирается момент, где среднее отношение для таза и для плеч наиболее близко к 1.
        Результаты сохраняются в self._relative_sizes.

        Возвращаемое значение:
          (best_pelvis_info, best_shoulder_info),
          где каждый элемент – кортеж вида (frame_idx, valid_video_list),
          valid_video_list – список video_key, в которых кадр валиден.
        Если ни для одного момента условия не выполнены, возвращается None.
        """
        import math
        import numpy as np

        # Сначала выбираем минимальное число кадров среди всех видео
        min_frames = min(len(video_data['frames']) for video_data in self.video_files.values())
        # Список кандидатов для каждого синхронного момента:
        # Каждый элемент: (frame_idx, best_pelvis_ratio, best_shoulder_ratio, valid_video_keys)
        candidates = []

        for frame_idx in range(min_frames):
            valid_pelvis = []
            valid_shoulder = []
            valid_videos = []  # видео, в которых в момент frame_idx кадр валиден

            for video_key, video_data in self.video_files.items():
                frame = video_data['frames'][frame_idx]
                # Извлекаем координаты (берём первый элемент из списка)
                left_hip = frame.left_hip[0]
                right_hip = frame.right_hip[0]
                left_knee = frame.left_knee[0]
                right_knee = frame.right_knee[0]
                left_ankle = frame.left_ankle[0]
                right_ankle = frame.right_ankle[0]
                left_shoulder = frame.left_shoulder[0]
                right_shoulder = frame.right_shoulder[0]

                # Вычисляем углы коленей
                left_knee_angle = calculate_angle(np.array(left_hip), np.array(left_knee), np.array(left_ankle))
                right_knee_angle = calculate_angle(np.array(right_hip), np.array(right_knee), np.array(right_ankle))
                # Вычисляем углы между плечевыми и тазовыми точками
                left_hip_angle = calculate_angle(np.array(left_shoulder), np.array(left_hip), np.array(left_knee))
                right_hip_angle = calculate_angle(np.array(right_shoulder), np.array(right_hip), np.array(right_knee))

                hip_size = None
                # Если левая нога подходит
                if left_knee_angle >= angle_threshold and left_hip_angle >= angle_threshold:
                    hip_size = math.hypot(left_hip[0] - left_knee[0], left_hip[1] - left_knee[1])
                # Если правая нога подходит (перезаписываем hip_size, если условие выполнено)
                if right_knee_angle >= angle_threshold and right_hip_angle >= angle_threshold:
                    hip_size = math.hypot(right_hip[0] - right_knee[0], right_hip[1] - right_knee[1])

                # Если hip_size не определён, пропускаем этот кадр для текущего видео
                if hip_size is None:
                    continue

                # Вычисляем расстояния между ключевыми точками
                pelvis_distance = math.hypot(left_hip[0] - right_hip[0], left_hip[1] - right_hip[1])
                shoulder_distance = math.hypot(left_shoulder[0] - right_shoulder[0],
                                               left_shoulder[1] - right_shoulder[1])

                # Вычисляем относительные отношения
                pelvis_ratio = pelvis_distance / hip_size
                shoulder_ratio = shoulder_distance / hip_size

                valid_pelvis.append(pelvis_ratio)
                valid_shoulder.append(shoulder_ratio)
                valid_videos.append(video_key)

            # Если на данном моменте обнаружено хотя бы два валидных кадра из разных видео
            if len(valid_videos) == len(self.video_files.keys()):
                best_pelvis = min(valid_pelvis, key=lambda det: abs(det - 1))
                best_shoulder = min(valid_shoulder, key=lambda det: abs(det - 1))
                # best_pelvis = np.mean(valid_pelvis)
                # best_shoulder = np.mean(valid_shoulder)
                candidates.append((frame_idx, best_pelvis, best_shoulder, valid_videos))

        if not candidates:
            print(
                "Не удалось вычислить относительные размеры, поскольку для ни одного момента не найдено хотя бы два валидных кадра.")
            return None

        # Выбираем момент, где отношение наиболее близко к 1 (для таза и плеч) отдельно
        best_pelvis_candidate = None  # (frame_idx, best_pelvis, valid_videos)
        best_shoulder_candidate = None  # (frame_idx, best_shoulder, valid_videos)

        for cand in candidates:
            frame_idx, best_pelvis, best_shoulder, valid_videos = cand
            if best_pelvis_candidate is None or abs(best_pelvis - 1) < abs(best_pelvis_candidate[1] - 1):
                best_pelvis_candidate = (frame_idx, best_pelvis, valid_videos)
            if best_shoulder_candidate is None or abs(best_shoulder - 1) < abs(best_shoulder_candidate[1] - 1):
                best_shoulder_candidate = (frame_idx, best_shoulder, valid_videos)

        # Сохраняем результаты в _relative_sizes
        if best_pelvis_candidate and best_shoulder_candidate:
            pelvis_frame_idx, pelvis_ratio, pelvis_videos = best_pelvis_candidate
            shoulder_frame_idx, shoulder_ratio, shoulder_videos = best_shoulder_candidate

            self._relative_sizes['pelvis_length'] = pelvis_ratio
            self._relative_sizes['shoulder_joint_distance'] = shoulder_ratio

            print("Вычисленные относительные размеры:")
            print(f"Pelvis (таз): {pelvis_ratio} на кадре {pelvis_frame_idx} (Видео: {pelvis_videos})")
            print(f"Shoulder (плечи): {shoulder_ratio} на кадре {shoulder_frame_idx} (Видео: {shoulder_videos})")

            # Возвращаем информацию о выбранных моментах:
            # Каждый элемент – кортеж (frame_idx, [video_key1, video_key2, ...])
            return (pelvis_frame_idx, pelvis_videos), (shoulder_frame_idx, shoulder_videos)
        else:
            print("Не удалось вычислить относительные размеры.")
            return None






    #########################################################
    # Вспомогательные статикметоды
    #########################################################





    @staticmethod
    def _raw_to_frame_handler(row):

        """
        Метод для преобразования считанного кадра из .csv в объект FrameHandler
        """

        coords = np.zeros((1, 17, 3))
        conf = np.zeros((1, 17))
        attributes = [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
        for idx, attr in enumerate(attributes):
            x = row.get(f'{attr}_x', 0)
            y = row.get(f'{attr}_y', 0)
            conf_val = row.get(f'{attr}_conf', 0)
            coords[0][idx] = [x, y, 0]
            conf[0][idx] = conf_val
        return FrameHandler(coords, conf)






    @staticmethod
    def _extract_frames_generator(video_path: str):

        """
        Возвращает по одному кадры из видео для экономии памяти.
        :param video_path: путь к видео
        :return: один кадр из видео
        """

        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise RuntimeError(f'Не удалось открыть видео: {video_path}')
        try:
            while True:
                success, frame = video.read()
                if not success:
                    break
                yield frame
        finally:
            video.release()


def draw_keypoints_on_frame(video_path, frame_idx, keypoints_obj, point_color=(0, 255, 0), radius=5):
    """
    Открывает видео, извлекает кадр с номером frame_idx,
    затем по координатам из keypoints_obj (объекта FrameHandler) рисует круги.

    :param video_path: путь к видеофайлу
    :param frame_idx: индекс кадра, который требуется извлечь
    :param keypoints_obj: объект FrameHandler с координатами ключевых точек
    :param point_color: цвет отрисовки ключевых точек (B, G, R)
    :param radius: радиус кружка
    :return: изменённое изображение (numpy array) или None, если не удалось извлечь кадр
    """
    cap = cv2.VideoCapture(video_path+'.mp4')
    if not cap.isOpened():
        print(f"Не удалось открыть видео: {video_path}")
        return None

    # Перейти к требуемому кадру
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    success, frame = cap.read()
    if not success:
        print(f"Не удалось прочитать кадр {frame_idx} из видео {video_path}")
        cap.release()
        return None

    # Список имен ключевых точек (те, что присутствуют в классе FrameHandler)
    points_list = ["nose", "left_eye", "right_eye",
                   "left_ear", "right_ear",
                   "left_shoulder", "right_shoulder",
                   "left_elbow", "right_elbow",
                   "left_wrist", "right_wrist",
                   "left_hip", "right_hip",
                   "left_knee", "right_knee",
                   "left_ankle", "right_ankle"]

    for pt in points_list:
        # Получаем координаты и уровень доверия (если нужно можно добавить проверку)
        coords, conf = getattr(keypoints_obj, pt)
        x, y = int(coords[0]), int(coords[1])
        cv2.circle(frame, (x, y), radius, point_color, -1)

    cap.release()
    return frame














def record_videos():
    # === Конфигурация ===
    NTP_SERVER_IP = "192.168.88.254"

    CAMERAS = [
        {"name": "cam1", "ip": "172.16.204.88", "port": 80, "user": "admin", "password": "Masterkey9600612"},
        {"name": "cam2", "ip": "172.16.204.58", "port": 80, "user": "admin", "password": "admin"},
        {"name": "cam3", "ip": "172.16.204.85", "port": 80, "user": "Admin", "password": "1234"},
        {"name": "cam4", "ip": "172.16.204.14", "port": 80, "user": "admin", "password": "1234"},
    ]

    RTSP_STREAMS = {
        "cam1": "rtsp://admin:Masterkey9600612@172.16.204.88/Streaming/Channels/101",
        "cam2": "rtsp://admin:admin@172.16.204.58:554/stream1",
        "cam3": "rtsp://Admin:1234@172.16.204.85/stream1",
        "cam4": "rtsp://172.16.204.14:554/user=admin_password=d2gNs1nj_channel=1_stream=0.sdp?real_stream",
    }

    stop_recording = threading.Event()
    results = {}
    threads = []
    # save_dir = None
    # log_file = None


    # === Вспомогательные функции ===

    # def log(msg):
    #     timestamp = datetime.now().strftime("%H:%M:%S")
    #     log_box.insert(tk.END, f"[{timestamp}] {msg}\n")
    #     log_box.see(tk.END)
    def log(msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{level.upper()}]"
        full_msg = f"[{timestamp}] {prefix} {msg}"

        # Вывод в окно
        log_box.insert(tk.END, full_msg + "\n")
        log_box.see(tk.END)

        # Запись в файл
        # if log_file:
        #     try:
        #         with open(log_file, "a", encoding="utf-8") as f:
        #             f.write(full_msg + "\n")
        #     except Exception as e:
        #         log_box.insert(tk.END, f"[{timestamp}] [ERROR] Ошибка записи лога: {e}\n")
        try:
            is_new_file = not os.path.exists(log_file)
            with open(log_file, "a", encoding="utf-8") as f:
                if is_new_file:
                    f.write("Time,Level,Message\n")
                f.write(f"{timestamp},{level.upper()},{msg}\n")
        except Exception as e:
            print(f"Ошибка при записи в лог: {e}")



    def sync_ntp(cam):
        try:
            devicemgmt = cam.create_devicemgmt_service()
            devicemgmt.SetNTP({
                "FromDHCP": False,
                "NTPManual": [{"Type": "IPv4", "IPv4Address": NTP_SERVER_IP}],
            })
            log(" → NTP OK")
        except Fault as e:
            log(f" ⚠ NTP fault: {e}")
        except Exception as e:
            log(f" ⚠ NTP err : {e}")

    def set_gop_one(cam):
        try:
            media = cam.create_media_service()
            profiles = media.GetProfiles()
            if not profiles or not profiles[0].VideoEncoderConfiguration:
                log("Нет VideoEncoderConfiguration в профиле", level="WARNING")
                return
            token = profiles[0].VideoEncoderConfiguration.token
            cfg = media.GetVideoEncoderConfiguration({"ConfigurationToken": token})
            if hasattr(cfg, "H264") and cfg.H264:
                cfg.H264.GovLength = 1
            cfg.Name = cfg.Name or "AutoSetGOP"
            cfg.Encoding = "H264"
            cfg.Quality = cfg.Quality or 5.0
            media.SetVideoEncoderConfiguration({"Configuration": cfg, "ForcePersistence": True})
            log(" → GOP=1 OK")
        except Exception as e:
            log(f" → GOP err: {e}", level="ERROR")

    def record_with_pts_v2(camera_name, rtsp_url, save_dir, file_name):
        save_dir.mkdir(parents=True, exist_ok=True)
        out_path = save_dir / f"{camera_name}.mp4"
        result = {"camera": camera_name, "video_path": str(out_path)}
        first_pts_time = None
        input_container = None
        output_container = None

        try:
            input_container = av.open(rtsp_url)
            input_stream = input_container.streams.video[0]
            input_stream.thread_type = "AUTO"
            output_container = av.open(str(out_path), mode='w', format='mp4')
            output_stream = output_container.add_stream("libx264", rate=25)
            output_stream.width = input_stream.codec_context.width
            output_stream.height = input_stream.codec_context.height
            output_stream.pix_fmt = "yuv420p"
            output_stream.time_base = input_stream.time_base

            log(f"[{camera_name}] ▶ Начата запись")
            for packet in input_container.demux(input_stream):
                for frame in packet.decode():
                    if first_pts_time is None and frame.pts is not None:
                        first_pts_time = float(frame.pts * input_stream.time_base)
                        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                        result["timestamp_camera"] = ts
                        log(f"[{camera_name}] 🟢 Первый кадр в {ts}")
                    frame.time_base = input_stream.time_base
                    for packet in output_stream.encode(frame):
                        output_container.mux(packet)
                    if stop_recording.is_set():
                        raise KeyboardInterrupt
            for packet in output_stream.encode():
                output_container.mux(packet)

        except KeyboardInterrupt:
            log(f"[{camera_name}] ⏹ Остановлено пользователем")
        except Exception as e:
            log(f"[{camera_name}] ❌ Ошибка: {e}", level="ERROR")
            result["timestamp_camera"] = None
            result["error"] = str(e)
        finally:
            if input_container:
                try: input_container.close()
                except: pass
            if output_container:
                try: output_container.close()
                except: pass

        results[camera_name] = result

    # === Управление интерфейсом ===

    def start_recording():
        global save_dir
        name_session = file_name_entry.get().strip()

        if not name_session:
            # log(" Не указано имя сессии — запуск записи отменён", level="WARNING")
            messagebox.showwarning("Внимание", "Введите имя файла перед началом записи!")
            return

        # save_dir = Path.cwd() / Path(name_session).name
        raw_path = selected_path.get()
        if not raw_path or raw_path == "(путь не выбран)":
            # log(" Не выбран путь для сохранения — запуск записи отменён", level="WARNING")
            messagebox.showwarning("Внимание", "Выберите папку для сохранения!")
            return

        try:
            base_path = Path(raw_path).expanduser().resolve()
        except Exception as e:
            messagebox.showerror("Ошибка пути", f"Некорректный путь: {e}")
            return

        save_dir = base_path / Path(name_session).name
        global log_file
        save_dir.mkdir(parents=True, exist_ok=True)
        log_file = save_dir / "session_log.csv"
        log(f" Создание папки для сессии: {save_dir}")

        stop_recording.clear()
        results.clear()
        log(" Запуск записи с камер...")
        for info in CAMERAS:
            log(f"[{info['name']}] подключаемся к {info['ip']}...")
            try:
                cam = ONVIFCamera(info["ip"], info["port"], info["user"], info["password"])
                sync_ntp(cam)
                set_gop_one(cam)
            except Exception as e:
                log(f"[{info['name']}] Ошибка подключения: {e}", level="ERROR")

            log(f"[{info['name']}] → Пытаемся записать в: {repr(str(save_dir))}")

        def runner(name, rtsp):
            record_with_pts_v2(name, rtsp, save_dir, name_session)

        for name, rtsp in RTSP_STREAMS.items():
            t = threading.Thread(target=runner, args=(name, rtsp))
            t.start()
            threads.append(t)

    def stop_recording_all():
        def _stop():
            log("🛑 Завершение записи...")
            stop_recording.set()

            for t in threads:
                t.join()

            log("✅ Запись завершена. Сохраняем...")

            if save_dir:
                json_path = save_dir / "video_timestamps.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [
                            {**entry, "video_path": str(entry.get("video_path", ""))}
                            for entry in results.values()
                        ],
                        f, indent=2, ensure_ascii=False
                    )

                log(" Данные сохранены в video_timestamps.json")

            file_name_entry.delete(0, tk.END)
        threading.Thread(target=_stop).start()

    # === Интерфейс ===

    rec_win = tk.Toplevel(root)
    rec_win.title("Запись с камер")

    selected_path = tk.StringVar(value="(путь не выбран)")
    def choose_folder():
        folder_selected = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_selected:
            selected_path.set(folder_selected)
    path_frame = tk.Frame(rec_win)
    path_frame.pack(pady=5)
    tk.Label(path_frame, text="Папка для сохранения:").pack(side=tk.LEFT)
    tk.Label(path_frame, textvariable=selected_path, width=50, anchor="w", relief="sunken").pack(side=tk.LEFT, padx=5)
    tk.Button(path_frame, text="Выбрать...", command=choose_folder).pack(side=tk.LEFT)


    frame = tk.Frame(rec_win)
    frame.pack(pady=10)
    tk.Label(frame, text="Имя файла / сессии:").pack(side=tk.LEFT)
    file_name_entry = tk.Entry(frame, width=30)
    file_name_entry.pack(side=tk.LEFT, padx=5)

    start_button = tk.Button(rec_win, text="▶ Начать запись", command=start_recording, bg="green", fg="white")
    start_button.pack(pady=10)

    stop_button = tk.Button(rec_win, text="⏹ Завершить запись", command=stop_recording_all, bg="red", fg="white")
    stop_button.pack(pady=10)

    log_box = scrolledtext.ScrolledText(rec_win, width=80, height=20)
    log_box.pack(padx=10, pady=10)







def process_folders():
    def dir_pac():
        folder = filedialog.askdirectory(title="Выберите ПАПКУ, содержащую папки с видео")
        if not folder:
            return
        # перебираем подпапки и обрабатываем каждую
        for subfolder in Path(folder).iterdir():
            print(subfolder)
            if subfolder.is_dir():
                worker = Engine(str(subfolder), frame_rate=25, load_from_csv=False)
                worker.trim_videos()
                time.sleep(0.1)
                worker.extract_frames_run()
                time.sleep(0.1)
                worker.save_raw_frames_to_csv()
                time.sleep(0.1)
                worker.combine_synchronized_frames()
                time.sleep(0.1)
                worker.generate_full_motion_report()
        messagebox.showinfo("Готово", "Обработка всех папок завершена!")

    def dir_one_pac():
        folder = filedialog.askdirectory(title="Выберите ПАПКУ, содержащую папки с видео")
        print(type(folder))
        if not folder:
            return
        worker = Engine(folder, frame_rate=25, load_from_csv=False)
        worker.trim_videos()
        time.sleep(0.1)
        worker.extract_frames_run()
        print("Пытаемся extract_frames_run")
        time.sleep(0.1)
        worker.save_raw_frames_to_csv()
        time.sleep(0.1)
        worker.combine_synchronized_frames()
        time.sleep(0.1)
        worker.generate_full_motion_report()
        messagebox.showinfo("Готово", "Обработка всех папок завершена!")

    rec_win_obr = tk.Toplevel(root)
    rec_win_obr.title("Запись с камер")

    btn1 = tk.Button(rec_win_obr, text="Обработать одного пациента", command=dir_one_pac)
    btn1.pack(padx=20, pady=20)

    btn2 = tk.Button(rec_win_obr, text="Обработать группу пациентов", command=dir_pac)
    btn2.pack(padx=20, pady=20)





# === Глобальные переменные ===
log_file = None
save_dir = None

root = tk.Tk()
root.title("Главное меню")

btn1 = tk.Button(root, text="Записать видео", command=record_videos)
btn1.pack(padx=20, pady=20)

btn2 = tk.Button(root, text="Обработать видео", command=process_folders)
btn2.pack(padx=20, pady=20)

root.mainloop()

# worker = Engine('examples//123//', frame_rate=25, load_from_csv=False)
# worker.trim_videos()
# worker.extract_frames_run()
# worker.save_raw_frames_to_csv()
#
# worker.generate_full_motion_report()
# worker.generate_report()
# worker.generate_amplitude_report(False)

