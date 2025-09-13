import sys
import cv2
import numpy as np
import pyautogui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import threading
import random
import re
import time

# Настройки безопасности PyAutoGUI
pyautogui.FAILSAFE = True  # Переместите мышь в левый верхний угол для остановки
pyautogui.PAUSE = 0.1  # Задержка для действий

class SmartTextAI(QMainWindow):
    def init(self):
        super().init()
        self.setWindowTitle("Умный ИИ с текстовыми командами")
        self.setGeometry(100, 100, 800, 600)

        # GUI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(640, 480)
        self.layout.addWidget(self.image_label)

        self.status_label = QLabel("Статус: Ожидание")
        self.layout.addWidget(self.status_label)

        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("Введите команду, например: 'кликни по красному объекту' или 'нажми W 5 раз'")
        self.layout.addWidget(self.command_input)

        self.start_button = QPushButton("Запустить ИИ")
        self.start_button.clicked.connect(self.start_ai)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Остановить ИИ")
        self.stop_button.clicked.connect(self.stop_ai)
        self.layout.addWidget(self.stop_button)

        # ИИ состояние
        self.ai_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # Обновление каждые 100 мс

        # Простая нейросеть для принятия решений
        self.weights = [random.uniform(-1, 1) for _ in range(9)]  # 3 входа, 3 скрытых, 3 выхода

        # Список команд для NLP
        self.commands = {
            r"клик(ни|ать)? по (красн|син|зелен|желт|бел|черн)\S*": self.click_by_color,
            r"нажми (\w+) (\d+) раз\S*": self.press_key,
            r"двигай(ся)? (влево|вправо|вверх|вниз) (\d+) пиксел\S*": self.move_mouse,
            r"клик(ни|ать)? (\d+) раз\S*": self.click_multiple,
            r"напиши (\w+)": self.type_text
        }

        # Цвета для детекции
        self.colors = {
            "красн": ([0, 120, 70], [10, 255, 255]),  # HSV для красного
            "син": ([100, 100, 100], [130, 255, 255]),  # Синий
            "зелен": ([40, 100, 100], [80, 255, 255]),  # Зеленый
            "желт": ([20, 100, 100], [30, 255, 255]),  # Желтый
            "бел": ([0, 0, 200], [179, 50, 255]),  # Белый
            "черн": ([0, 0, 0], [179, 255, 50])  # Черный
        }

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def predict(self, inputs):
        # Нейросеть: 3 входа (объекты, расстояние, активность) -> 3 выхода (клик, движение, пауза)
        hidden = [0] * 3
        for h in range(3):
            hidden[h] = self.sigmoid(sum(inputs[i] * self.weights[i * 3 + h] for i in range(3)))
        outputs = [0] * 3
        for o in range(3):
            outputs[o] = self.sigmoid(sum(hidden[h] * self.weights[3 + h * 3 + o] for h in range(3)))
        return outputs  # [click_prob, move_prob, pause_prob]

    def update_frame(self):
        if self.ai_running:
            # Захват экрана
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Обработка кадра
            processed_frame, _ = self.process_frame(frame)

            # Отображение в GUI
            height, width, channel = processed_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_image))
def process_frame(self, frame, color_range=None):
        # Детекция объектов по цвету (если указан)
        targets = []
        if color_range:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_bound, upper_bound = color_range
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 500:  # Фильтр мелких объектов
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    targets.append((x + w // 2, y + h // 2))
        return frame, targets

    def click_by_color(self, match):
        color_key = match.group(2)[:5]  # Урезаем до корня слова (красн, син, etc.)
        if color_key in self.colors:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame, targets = self.process_frame(frame, self.colors[color_key])
            if targets:
                target_x, target_y = targets[0]
                pyautogui.moveTo(target_x, target_y, duration=0.2)
                pyautogui.click()
                self.status_label.setText(f"Статус: Клик по {color_key}ому объекту ({target_x}, {target_y})")
            else:
                self.status_label.setText(f"Статус: {color_key}ый объект не найден")
        else:
            self.status_label.setText("Статус: Цвет не распознан")

    def press_key(self, match):
        key = match.group(1)
        times = int(match.group(2))
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(0.1)
        self.status_label.setText(f"Статус: Нажал {key} {times} раз")

    def move_mouse(self, match):
        direction = match.group(2)
        pixels = int(match.group(3))
        moves = {
            "влево": (-pixels, 0),
            "вправо": (pixels, 0),
            "вверх": (0, -pixels),
            "вниз": (0, pixels)
        }
        dx, dy = moves.get(direction, (0, 0))
        pyautogui.moveRel(dx, dy, duration=0.2)
        self.status_label.setText(f"Статус: Движение {direction} на {pixels} пикселей")

    def click_multiple(self, match):
        times = int(match.group(2))
        for _ in range(times):
            pyautogui.click()
            time.sleep(0.1)
        self.status_label.setText(f"Статус: Кликнул {times} раз")

    def type_text(self, match):
        text = match.group(1)
        pyautogui.write(text)
        self.status_label.setText(f"Статус: Написал '{text}'")

    def process_command(self, command):
        command = command.lower().strip()
        for pattern, action in self.commands.items():
            match = re.match(pattern, command)
            if match:
                action(match)
                return True
        self.status_label.setText("Статус: Команда не распознана")
        return False

    def ai_loop(self):
        while self.ai_running:
            command = self.command_input.toPlainText().strip()
            if command:
                self.process_command(command)
            else:
                # Автономный режим: поиск ярких объектов
                screenshot = pyautogui.screenshot()
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame, targets = self.process_frame(frame, ([0, 100, 100], [179, 255, 255]))
                
                num_targets = len(targets)
                nearest_dist = min([((x - frame.shape[1] // 2)  2 + (y - frame.shape[0] // 2)  2) ** 0.5 for x, y in targets] or [1000])
                activity_level = num_targets / 10
inputs = [num_targets / 10, nearest_dist / 1000, activity_level]
                
                outputs = self.predict(inputs)
                click_prob, move_prob, pause_prob = outputs
                
                if targets and click_prob > 0.6:
                    target_x, target_y = targets[0]
                    pyautogui.moveTo(target_x, target_y, duration=0.2)
                    pyautogui.click()
                    self.status_label.setText(f"Статус: Автоклик по цели ({target_x}, {target_y})")
                elif move_prob > 0.5:
                    pyautogui.moveRel(random.randint(-50, 50), random.randint(-50, 50))
                    self.status_label.setText("Статус: Случайное движение")
                time.sleep(random.uniform(0.2, 0.5))

    def start_ai(self):
        self.ai_running = True
        self.status_label.setText("Статус: ИИ запущен")
        threading.Thread(target=self.ai_loop, daemon=True).start()

    def stop_ai(self):
        self.ai_running = False
        self.status_label.setText("Статус: Ожидание")

if name == "main":
    app = QApplication(sys.argv)
    window = SmartTextAI()
    window.show()
    sys.exit(app.exec_())
