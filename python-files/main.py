import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import winsound  # для Windows, на Linux/Mac используйте другие библиотеки
from scipy.spatial import distance as dist
import json
import os
from PIL import Image, ImageTk


class EyeCareApp:
    def __init__(self):
        # Инициализация MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Переменные для калибровки расстояния
        self.calibrated_distance = None
        self.current_distance = 0
        self.distance_threshold = 5  # см допустимого отклонения

        # Переменные для моргания
        self.last_blink_time = time.time()
        self.blink_threshold = 0.25  # порог для определения моргания
        self.no_blink_limit = 30  # секунд без моргания

        # Индексы ключевых точек глаз для MediaPipe
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

        # Файл настроек
        self.settings_file = "eye_care_settings.json"
        self.load_settings()

        # Инициализация GUI
        self.setup_gui()

        # Флаги
        self.is_monitoring = False
        self.camera_thread = None
        self.current_frame = None

        # Инициализация камеры для предварительного просмотра
        self.init_camera_preview()

    def init_camera_preview(self):
        """Инициализировать предварительный просмотр камеры"""
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.update_camera_preview()
        else:
            self.log_message("Ошибка: Камера недоступна")

    def update_camera_preview(self):
        """Обновить предварительный просмотр камеры"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)

                # Изменить размер для отображения
                display_frame = cv2.resize(frame, (480, 360))

                if self.is_monitoring:
                    # Обработать кадр только если мониторинг включен
                    self.process_frame(display_frame)
                else:
                    # Показать простую направляющую если мониторинг выключен
                    display_frame = self.draw_simple_guide(display_frame)

                # Конвертировать для tkinter
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_frame)
                tk_image = ImageTk.PhotoImage(pil_image)

                self.video_label.configure(image=tk_image)
                self.video_label.image = tk_image

        # Запланировать следующее обновление
        self.root.after(50, self.update_camera_preview)  # 20 FPS

    def process_frame(self, frame):
        """Обработать кадр для детекции лица и моргания"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Получить ключевые точки
                landmarks = []
                for lm in face_landmarks.landmark:
                    landmarks.append(lm)

                # Оценить расстояние
                self.current_distance = self.estimate_distance(landmarks, frame.shape[1])

                # Получить точки глаз для определения моргания
                left_eye_points = []
                right_eye_points = []

                for idx in [362, 385, 387, 263, 373, 380]:  # Упрощенные точки левого глаза
                    if idx < len(landmarks):
                        point = landmarks[idx]
                        left_eye_points.append([point.x, point.y])

                for idx in [33, 160, 158, 133, 153, 144]:  # Упрощенные точки правого глаза
                    if idx < len(landmarks):
                        point = landmarks[idx]
                        right_eye_points.append([point.x, point.y])

                # Вычислить EAR для обоих глаз если есть достаточно точек
                if len(left_eye_points) >= 6 and len(right_eye_points) >= 6:
                    left_ear = self.calculate_eye_aspect_ratio(left_eye_points)
                    right_ear = self.calculate_eye_aspect_ratio(right_eye_points)
                    ear = (left_ear + right_ear) / 2.0

                    # Определить моргание
                    if ear < self.blink_threshold:
                        self.last_blink_time = time.time()

                # Нарисовать направляющие и индикаторы
                frame = self.draw_face_guide(frame, face_landmarks, frame.shape[1], frame.shape[0])

                # Проверки (в отдельном потоке чтобы не блокировать UI)
                self.check_distance_deviation()
                self.check_blink_frequency()

                break  # Обрабатываем только первое найденное лицо
        else:
            # Если лицо не найдено, все равно показать направляющие
            frame = self.draw_face_guide(frame, None, frame.shape[1], frame.shape[0])

        return frame

    def draw_simple_guide(self, frame):
        """Нарисовать простую направляющую когда мониторинг выключен"""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        guide_width, guide_height = 200, 150

        guide_x1 = center_x - guide_width // 2
        guide_y1 = center_y - guide_height // 2
        guide_x2 = center_x + guide_width // 2
        guide_y2 = center_y + guide_height // 2

        # Нарисовать направляющую рамку пунктиром
        dash_length = 10
        for i in range(0, guide_width, dash_length * 2):
            cv2.line(frame, (guide_x1 + i, guide_y1),
                     (min(guide_x1 + i + dash_length, guide_x2), guide_y1), (128, 128, 128), 2)
            cv2.line(frame, (guide_x1 + i, guide_y2),
                     (min(guide_x1 + i + dash_length, guide_x2), guide_y2), (128, 128, 128), 2)

        for i in range(0, guide_height, dash_length * 2):
            cv2.line(frame, (guide_x1, guide_y1 + i),
                     (guide_x1, min(guide_y1 + i + dash_length, guide_y2)), (128, 128, 128), 2)
            cv2.line(frame, (guide_x2, guide_y1 + i),
                     (guide_x2, min(guide_y1 + i + dash_length, guide_y2)), (128, 128, 128), 2)

        # Текст
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Разместите лицо в рамке"
        text_size = cv2.getTextSize(text, font, 0.6, 1)[0]
        text_x = (w - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, guide_y2 + 30), font, 0.6, (200, 200, 200), 2)

        return frame

    def load_settings(self):
        """Загрузить сохраненные настройки"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.calibrated_distance = settings.get('calibrated_distance')
                    self.distance_threshold = settings.get('distance_threshold', 5)
                    self.no_blink_limit = settings.get('no_blink_limit', 30)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        """Сохранить настройки"""
        try:
            settings = {
                'calibrated_distance': self.calibrated_distance,
                'distance_threshold': self.distance_threshold,
                'no_blink_limit': self.no_blink_limit
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def setup_gui(self):
        """Создать интерфейс"""
        self.root = tk.Tk()
        self.root.title("Забота о глазах")
        self.root.geometry("800x700")

        # Основной фрейм для размещения видео и панели управления
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Левая часть - видео с камеры
        video_frame = ttk.LabelFrame(main_frame, text="Предварительный просмотр", padding=5)
        video_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.video_label = ttk.Label(video_frame)
        self.video_label.pack()

        # Индикатор статуса под видео
        self.status_indicator = ttk.Label(video_frame, text="●", font=("Arial", 20), foreground="gray")
        self.status_indicator.pack(pady=5)

        # Правая часть - панель управления
        control_panel = ttk.Frame(main_frame)
        control_panel.pack(side="right", fill="y", padx=(5, 0))

        # Фрейм калибровки
        calibration_frame = ttk.LabelFrame(control_panel, text="Калибровка расстояния", padding=10)
        calibration_frame.pack(fill="x", pady=(0, 5))

        self.distance_label = ttk.Label(calibration_frame, text="Текущее расстояние: - см")
        self.distance_label.pack()

        self.calibrated_label = ttk.Label(calibration_frame,
                                          text=f"Калиброванное: {self.calibrated_distance or '-'} см")
        self.calibrated_label.pack()

        ttk.Button(calibration_frame, text="Калибровать расстояние",
                   command=self.calibrate_distance).pack(pady=5)

        # Настройки расстояния
        ttk.Label(calibration_frame, text="Допустимое отклонение (см):").pack()
        self.threshold_var = tk.StringVar(value=str(self.distance_threshold))
        threshold_spin = ttk.Spinbox(calibration_frame, from_=1, to=20,
                                     textvariable=self.threshold_var, width=10)
        threshold_spin.pack()
        threshold_spin.bind('<KeyRelease>', self.update_threshold)

        # Фрейм моргания
        blink_frame = ttk.LabelFrame(control_panel, text="Контроль моргания", padding=10)
        blink_frame.pack(fill="x", pady=5)

        self.blink_label = ttk.Label(blink_frame, text="Последнее моргание: - сек назад")
        self.blink_label.pack()

        ttk.Label(blink_frame, text="Предел без моргания (сек):").pack()
        self.blink_limit_var = tk.StringVar(value=str(self.no_blink_limit))
        blink_spin = ttk.Spinbox(blink_frame, from_=10, to=120,
                                 textvariable=self.blink_limit_var, width=10)
        blink_spin.pack()
        blink_spin.bind('<KeyRelease>', self.update_blink_limit)

        # Контроль мониторинга
        monitor_frame = ttk.LabelFrame(control_panel, text="Управление", padding=10)
        monitor_frame.pack(fill="x", pady=5)

        self.start_stop_btn = ttk.Button(monitor_frame, text="Начать мониторинг",
                                         command=self.toggle_monitoring)
        self.start_stop_btn.pack(pady=5)

        self.status_label = ttk.Label(monitor_frame, text="Статус: Остановлен")
        self.status_label.pack()

        # Лог уведомлений
        log_frame = ttk.LabelFrame(control_panel, text="Уведомления", padding=10)
        log_frame.pack(fill="both", expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=10, width=30)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_threshold(self, event=None):
        """Обновить порог отклонения расстояния"""
        try:
            self.distance_threshold = int(self.threshold_var.get())
            self.save_settings()
        except ValueError:
            pass

    def update_blink_limit(self, event=None):
        """Обновить лимит времени без моргания"""
        try:
            self.no_blink_limit = int(self.blink_limit_var.get())
            self.save_settings()
        except ValueError:
            pass

    def log_message(self, message):
        """Добавить сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()  # Принудительно обновить GUI

    def calculate_eye_aspect_ratio(self, eye_landmarks):
        """Вычислить коэффициент соотношения сторон глаза для определения моргания"""
        if len(eye_landmarks) < 6:
            return 0.3  # Значение по умолчанию

        # Вертикальные расстояния
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        # Горизонтальное расстояние
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])

        if C == 0:
            return 0.3

        # EAR формула
        ear = (A + B) / (2.0 * C)
        return ear

    def estimate_distance(self, face_landmarks, image_width):
        """Оценить расстояние до лица на основе ширины лица в пикселях"""
        try:
            # Используем расстояние между внешними углами глаз
            left_eye_corner = face_landmarks[33]  # Левый внешний угол правого глаза
            right_eye_corner = face_landmarks[362]  # Правый внешний угол левого глаза

            # Расчет ширины лица в пикселях
            face_width_pixels = abs(left_eye_corner.x - right_eye_corner.x) * image_width

            # Примерная ширина между внешними углами глаз человека ~ 6.5 см
            # Фокусное расстояние камеры (примерное значение для веб-камеры)
            focal_length = 500  # пикселей
            real_face_width = 6.5  # см

            if face_width_pixels > 0:
                distance = (real_face_width * focal_length) / face_width_pixels
                return distance
        except:
            pass
        return 0

    def calibrate_distance(self):
        """Калибровать оптимальное расстояние"""
        if not self.is_monitoring:
            messagebox.showwarning("Предупреждение", "Сначала запустите мониторинг")
            return

        if self.current_distance > 0:
            self.calibrated_distance = self.current_distance
            self.calibrated_label.config(text=f"Калиброванное: {self.calibrated_distance:.1f} см")
            self.save_settings()
            self.log_message(f"Расстояние откалибровано: {self.calibrated_distance:.1f} см")
        else:
            messagebox.showwarning("Ошибка", "Не удается определить лицо для калибровки")

    def check_distance_deviation(self):
        """Проверить отклонение от калиброванного расстояния"""
        if self.calibrated_distance and self.current_distance > 0:
            deviation = abs(self.current_distance - self.calibrated_distance)
            if deviation > self.distance_threshold:
                direction = "слишком близко" if self.current_distance < self.calibrated_distance else "слишком далеко"
                message = f"Расстояние {direction}! Текущее: {self.current_distance:.1f}см, оптимальное: {self.calibrated_distance:.1f}см"
                self.log_message(message)
                self.play_warning_sound()
                return True
        return False

    def check_blink_frequency(self):
        """Проверить частоту моргания"""
        time_since_blink = time.time() - self.last_blink_time
        if time_since_blink > self.no_blink_limit:
            message = f"Не моргали {time_since_blink:.0f} секунд! Поморгайте!"
            self.log_message(message)
            self.play_warning_sound()
            # Сбросить таймер, чтобы не спамить
            self.last_blink_time = time.time() - self.no_blink_limit + 10

    def draw_face_guide(self, frame, face_landmarks, frame_width, frame_height):
        """Рисовать направляющие и индикаторы на видео"""
        # Цвета для разных состояний
        color_good = (0, 255, 0)  # Зеленый
        color_warning = (0, 255, 255)  # Желтый
        color_bad = (0, 0, 255)  # Красный

        # Определить текущее состояние
        distance_ok = True
        if self.calibrated_distance and self.current_distance > 0:
            deviation = abs(self.current_distance - self.calibrated_distance)
            distance_ok = deviation <= self.distance_threshold

        # Время с последнего моргания
        time_since_blink = time.time() - self.last_blink_time
        blink_ok = time_since_blink < (self.no_blink_limit * 0.8)  # Предупреждение за 20% до лимита

        # Выбрать цвет рамки лица
        if distance_ok and blink_ok:
            face_color = color_good
            status_text = "✓ ВСЁ ХОРОШО"
            indicator_color = "green"
        elif not distance_ok and blink_ok:
            face_color = color_warning
            status_text = "⚠ РАССТОЯНИЕ"
            indicator_color = "orange"
        elif distance_ok and not blink_ok:
            face_color = color_warning
            status_text = "⚠ МОРГАНИЕ"
            indicator_color = "orange"
        else:
            face_color = color_bad
            status_text = "✗ ПРОБЛЕМЫ"
            indicator_color = "red"

        # Обновить индикатор статуса
        self.status_indicator.configure(foreground=indicator_color)

        # Нарисовать рамку вокруг лица
        h, w = frame.shape[:2]
        if face_landmarks:
            # Найти границы лица
            x_coords = [int(lm.x * w) for lm in face_landmarks.landmark]
            y_coords = [int(lm.y * h) for lm in face_landmarks.landmark]

            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            # Расширить рамку
            margin = 30
            x_min = max(0, x_min - margin)
            y_min = max(0, y_min - margin)
            x_max = min(w, x_max + margin)
            y_max = min(h, y_max + margin)

            # Нарисовать рамку
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), face_color, 3)

            # Нарисовать ключевые точки глаз
            for idx in [33, 362, 133, 263]:  # Углы глаз
                if idx < len(face_landmarks.landmark):
                    point = face_landmarks.landmark[idx]
                    x, y = int(point.x * w), int(point.y * h)
                    cv2.circle(frame, (x, y), 3, face_color, -1)

        # Центральная направляющая зона (идеальная позиция)
        center_x, center_y = w // 2, h // 2
        guide_width, guide_height = 200, 150

        guide_x1 = center_x - guide_width // 2
        guide_y1 = center_y - guide_height // 2
        guide_x2 = center_x + guide_width // 2
        guide_y2 = center_y + guide_height // 2

        # Нарисовать направляющую рамку пунктиром
        dash_length = 10
        for i in range(0, guide_width, dash_length * 2):
            cv2.line(frame, (guide_x1 + i, guide_y1),
                     (min(guide_x1 + i + dash_length, guide_x2), guide_y1), (128, 128, 128), 2)
            cv2.line(frame, (guide_x1 + i, guide_y2),
                     (min(guide_x1 + i + dash_length, guide_x2), guide_y2), (128, 128, 128), 2)

        for i in range(0, guide_height, dash_length * 2):
            cv2.line(frame, (guide_x1, guide_y1 + i),
                     (guide_x1, min(guide_y1 + i + dash_length, guide_y2)), (128, 128, 128), 2)
            cv2.line(frame, (guide_x2, guide_y1 + i),
                     (guide_x2, min(guide_y1 + i + dash_length, guide_y2)), (128, 128, 128), 2)

        # Текстовая информация
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Статус в верхней части
        text_size = cv2.getTextSize(status_text, font, 0.7, 2)[0]
        text_x = (w - text_size[0]) // 2
        cv2.putText(frame, status_text, (text_x, 30), font, 0.7, face_color, 2)

        # Информация о расстоянии
        if self.current_distance > 0:
            distance_text = f"Расстояние: {self.current_distance:.1f} см"
            cv2.putText(frame, distance_text, (10, h - 80), font, 0.5, (255, 255, 255), 1)

        if self.calibrated_distance:
            calib_text = f"Оптимальное: {self.calibrated_distance:.1f} см"
            cv2.putText(frame, calib_text, (10, h - 60), font, 0.5, (255, 255, 255), 1)

        # Информация о моргании
        blink_text = f"Моргание: {time_since_blink:.1f}с назад"
        cv2.putText(frame, blink_text, (10, h - 40), font, 0.5, (255, 255, 255), 1)

        # Инструкция по позиционированию
        instruction = "Разместите лицо в пунктирной рамке"
        inst_size = cv2.getTextSize(instruction, font, 0.4, 1)[0]
        inst_x = (w - inst_size[0]) // 2
        cv2.putText(frame, instruction, (inst_x, guide_y2 + 25), font, 0.4, (200, 200, 200), 1)

        return frame

    def play_warning_sound(self):
        """Воспроизвести предупреждающий звук"""
        try:
            # Проигрываем звук в отдельном потоке чтобы не блокировать UI
            threading.Thread(target=lambda: winsound.Beep(800, 300), daemon=True).start()
        except:
            # Альтернатива для других ОС
            print("\a")  # Системный звук

    def update_ui(self):
        """Обновить элементы интерфейса"""
        try:
            self.distance_label.config(text=f"Текущее расстояние: {self.current_distance:.1f} см")

            time_since_blink = time.time() - self.last_blink_time
            self.blink_label.config(text=f"Последнее моргание: {time_since_blink:.1f} сек назад")
        except:
            pass  # Игнорируем ошибки обновления UI

    def toggle_monitoring(self):
        """Включить/выключить мониторинг"""
        self.is_monitoring = not self.is_monitoring

        if self.is_monitoring:
            self.start_stop_btn.config(text="Остановить мониторинг")
            self.status_label.config(text="Статус: Работает")
            self.log_message("Мониторинг запущен")
            # Сбросить время последнего моргания
            self.last_blink_time = time.time()
        else:
            self.start_stop_btn.config(text="Начать мониторинг")
            self.status_label.config(text="Статус: Остановлен")
            self.status_indicator.configure(foreground="gray")
            self.log_message("Мониторинг остановлен")

        # Запланировать обновление UI
        self.root.after(100, self.update_ui_periodic)

    def update_ui_periodic(self):
        """Периодическое обновление UI"""
        if self.is_monitoring:
            self.update_ui()
            self.root.after(100, self.update_ui_periodic)

    def on_closing(self):
        """Обработка закрытия приложения"""
        self.is_monitoring = False
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()

    def run(self):
        """Запустить приложение"""
        self.root.mainloop()


# Точка входа
if __name__ == "__main__":
    app = EyeCareApp()
    app.run()