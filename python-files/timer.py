import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
import pygame

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Таймер")
        self.root.geometry("200x100")
        self.root.attributes("-topmost", True)  # всегда поверх окон

        pygame.mixer.init()

        self.time_left = 0
        self.running = False
        self.alarm_sound = None

        # Ввод минут и секунд
        self.min_var = tk.StringVar(value='0')
        self.sec_var = tk.StringVar(value='0')

        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Label(frame, text="Мин:").grid(row=0, column=0)
        self.min_entry = tk.Entry(frame, width=3, textvariable=self.min_var)
        self.min_entry.grid(row=0, column=1)

        tk.Label(frame, text="Сек:").grid(row=0, column=2)
        self.sec_entry = tk.Entry(frame, width=3, textvariable=self.sec_var)
        self.sec_entry.grid(row=0, column=3)

        # Таймер табло
        self.timer_label = tk.Label(root, text="00:00", font=("Arial", 24))
        self.timer_label.pack()

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="Старт", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="Сброс", command=self.reset_timer)
        self.reset_btn.grid(row=0, column=1, padx=5)

        self.sound_btn = tk.Button(root, text="Выбрать мелодию", command=self.select_sound)
        self.sound_btn.pack()

    def select_sound(self):
        file_path = filedialog.askopenfilename(filetypes=[("Аудио файлы", "*.wav *.mp3")])
        if file_path:
            try:
                self.alarm_sound = file_path
                pygame.mixer.music.load(self.alarm_sound)
                messagebox.showinfo("Мелодия", "Мелодия выбрана успешно!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить аудио: {e}")

    def start_timer(self):
        if self.running:
            return
        try:
            minutes = int(self.min_var.get())
            seconds = int(self.sec_var.get())
            self.time_left = minutes * 60 + seconds
            if self.time_left <= 0:
                messagebox.showwarning("Внимание", "Введите положительное время.")
                return
        except ValueError:
            messagebox.showwarning("Внимание", "Введите корректное число.")
            return

        self.running = True
        threading.Thread(target=self.countdown, daemon=True).start()

    def countdown(self):
        while self.time_left > 0 and self.running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_str)
            time.sleep(1)
            self.time_left -= 1

        if self.time_left == 0 and self.running:
            self.timer_label.config(text="00:00")
            self.running = False
            self.play_alarm()

    def play_alarm(self):
        if self.alarm_sound:
            try:
                pygame.mixer.music.play()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук: {e}")
        else:
            messagebox.showinfo("Таймер", "Время вышло!")

    def reset_timer(self):
        self.running = False
        self.time_left = 0
        self.timer_label.config(text="00:00")
        pygame.mixer.music.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()