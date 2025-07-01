import os
import time
import random
import threading
import numpy as np
import string
from PIL import Image, ImageTk
import tkinter as tk
import tensorflow as tf

# Параметры
model_input_width, model_input_height = 160, 60
display_width, display_height = 320, 120
captcha_length = 5
characters = string.ascii_letters + string.digits
label_to_char = {i: char for i, char in enumerate(characters)}

# Загрузка модели
model = tf.keras.models.load_model("captcha_model.h5")

def predict_captcha(img_path):
    img = Image.open(img_path).convert("L").resize((model_input_width, model_input_height))
    arr = np.array(img) / 255.0
    arr = arr.reshape(1, model_input_height, model_input_width, 1)

    start_time = time.time()
    predictions = model.predict(arr)
    end_time = time.time()

    predicted_text = ''.join(label_to_char[np.argmax(p)] for p in predictions)
    time_taken = end_time - start_time

    return predicted_text, time_taken

class WorkerFrame(tk.Frame):
    def __init__(self, master, shared_stats, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.shared_stats = shared_stats
        self.configure(bg="#222222", bd=2, relief=tk.RIDGE)

        self.img_label = tk.Label(self, bg="#222222")
        self.img_label.pack(padx=5, pady=5)

        self.result_label = tk.Label(self, text="", font=("Consolas", 12), fg="#e0e0e0", bg="#222222", justify=tk.LEFT)
        self.result_label.pack(padx=5, pady=5)

        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_worker, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def run_worker(self):
        files = [f for f in os.listdir("captchas") if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not files:
            self.result_label.after(0, lambda: self.result_label.config(text="Нет капч в папке."))
            return

        while self.running:
            filename = random.choice(files)
            full_path = os.path.join("captchas", filename)

            display_img = Image.open(full_path).resize((display_width, display_height))
            photo = ImageTk.PhotoImage(display_img)

            self.img_label.after(0, lambda p=photo: self.img_label.config(image=p))
            self.img_label.image = photo

            predicted, delay = predict_captcha(full_path)
            correct = os.path.splitext(filename)[0]

            correct_symbols = sum(p == t for p, t in zip(predicted, correct))

            with self.shared_stats['lock']:
                self.shared_stats['total_symbols'] += captcha_length
                self.shared_stats['total_correct'] += correct_symbols
                self.shared_stats['total_time'] += delay
                self.shared_stats['total_captchas'] += 1
                if correct_symbols == captcha_length:
                    self.shared_stats['correct_captchas'] += 1
                else:
                    self.shared_stats['incorrect_captchas'] += 1

            accuracy = correct_symbols / captcha_length * 100

            result_text = (f"Предсказано: {predicted}\n"
                           f"Правильно:   {correct}\n"
                           f"Точность: {accuracy:.1f}%\n"
                           f"Время: {delay:.2f} сек")

            self.result_label.after(0, lambda t=result_text: self.result_label.config(text=t))


class CaptchaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Распознавание капч - 9 окон")
        self.configure(bg="#111111")

        self.shared_stats = {
            'total_symbols': 0,
            'total_correct': 0,
            'total_time': 0.0,
            'total_captchas': 0,
            'correct_captchas': 0,
            'incorrect_captchas': 0,
            'lock': threading.Lock()
        }

        main_frame = tk.Frame(self, bg="#111111")
        main_frame.pack(padx=10, pady=10)

        # Слева — 3x3 капчи
        self.workers_frame = tk.Frame(main_frame, bg="#111111")
        self.workers_frame.grid(row=0, column=0)

        self.workers = []
        for i in range(9):
            wf = WorkerFrame(self.workers_frame, self.shared_stats)
            wf.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            self.workers.append(wf)

        # Справа — общая статистика
        self.stats_frame = tk.Frame(main_frame, bg="#111111")
        self.stats_frame.grid(row=0, column=1, sticky="n", padx=(20,10))

        self.stats_label = tk.Label(self.stats_frame, text="", font=("Consolas", 16, "bold"), fg="#a0a0a0", bg="#111111", justify=tk.LEFT)
        self.stats_label.pack(pady=20)

        # Кнопки Старт/Стоп
        controls_frame = tk.Frame(self, bg="#111111")
        controls_frame.pack(pady=10)

        self.start_btn = tk.Button(controls_frame, text="Старт", command=self.start_all, bg="#444444", fg="#e0e0e0", font=("Arial", 14, "bold"), width=12)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(controls_frame, text="Стоп", command=self.stop_all, bg="#444444", fg="#e0e0e0", font=("Arial", 14, "bold"), width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.update_stats_loop()

    def start_all(self):
        with self.shared_stats['lock']:
            self.shared_stats['total_symbols'] = 0
            self.shared_stats['total_correct'] = 0
            self.shared_stats['total_time'] = 0.0
            self.shared_stats['total_captchas'] = 0
            self.shared_stats['correct_captchas'] = 0
            self.shared_stats['incorrect_captchas'] = 0

        for worker in self.workers:
            worker.start()

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

    def stop_all(self):
        for worker in self.workers:
            worker.stop()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def update_stats_loop(self):
        with self.shared_stats['lock']:
            total_captchas = self.shared_stats['total_captchas']
            total_symbols = self.shared_stats['total_symbols']
            total_correct = self.shared_stats['total_correct']
            total_time = self.shared_stats['total_time']
            correct_captchas = self.shared_stats['correct_captchas']
            incorrect_captchas = self.shared_stats['incorrect_captchas']

        accuracy = (total_correct / total_symbols * 100) if total_symbols > 0 else 0
        avg_time = (total_time / total_captchas) if total_captchas > 0 else 0

        stats_text = (
            f"Общая точность: {accuracy:.1f}%\n"
            f"Среднее время: {avg_time:.2f} сек\n"
            f"Всего решено капч: {total_captchas}\n"
            f"Полностью верных: {correct_captchas}\n"
            f"С ошибками: {incorrect_captchas}"
        )

        self.stats_label.config(text=stats_text)
        self.after(1000, self.update_stats_loop)

if __name__ == "__main__":
    app = CaptchaApp()
    app.mainloop()
