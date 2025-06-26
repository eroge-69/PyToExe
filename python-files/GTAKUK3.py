import pyautogui
import time
import tkinter as tk
from tkinter import messagebox, END
import threading
import winsound  # Для звука (только Windows), если нужно — можно заменить на playsound или др.

# === Настройки ===
IMAGE_PATHS = {
    'whisk': 'whisk.png',          # Венчик
    'water': 'water.png',          # Вода
    'vegetable_bowl': 'bowl.png',  # Тарелка овощей
    'start_button': 'start_button.png'
}

CONFIDENCE = 0.8  # Точность поиска изображений (от 0 до 1)

# === Логика автоматизации ===
class AutoCooker:
    def __init__(self):
        self.running = False
        self.paused = False
        self.repeats = 1
        self.cycle_logs = []  # Хранение данных по каждому циклу

    def click_image(self, image_path, button='left'):
        location = pyautogui.locateCenterOnScreen(image_path, confidence=CONFIDENCE)
        if location:
            pyautogui.click(location, button=button)
            return True
        return False

    def cook_cycle(self):
        total_start_time = time.time()
        self.cycle_logs.clear()  # Очистка предыдущих записей
        for i in range(self.repeats):
            if not self.running:
                break
            while self.paused:
                time.sleep(0.1)
                if not self.running:
                    break

            cycle_start_time = time.time()

            print(f"\n[Цикл {i + 1} из {self.repeats}]")
            status_label.config(text=f"Цикл {i + 1} из {self.repeats}")

            # ПКМ на венчик
            if self.click_image(IMAGE_PATHS['whisk'], button='right'):
                print("Нажали ПКМ на венчик")
                time.sleep(0.7)
            else:
                print("Не найден венчик!")
                continue

            # ПКМ на воду
            if self.click_image(IMAGE_PATHS['water'], button='right'):
                print("Нажали ПКМ на воду")
                time.sleep(0.7)
            else:
                print("Не найдена вода!")
                continue

            # ПКМ на тарелку овощей
            if self.click_image(IMAGE_PATHS['vegetable_bowl'], button='right'):
                print("Нажали ПКМ на тарелку овощей")
                time.sleep(0.7)
            else:
                print("Не найдена тарелка овощей!")
                continue

            # ЛКМ на кнопку "Начать готовку"
            if self.click_image(IMAGE_PATHS['start_button'], button='left'):
                print("Нажали ЛКМ на кнопку 'Начать готовку'")
                time.sleep(0.3)
            else:
                print("Не найдена кнопка 'Начать готовку'!")
                continue

            # Ждём 6 секунд на готовку
            print("Ожидаем завершения готовки...")
            status_label.config(text="Готовка... Ожидание 6 сек.")
            for _ in range(6):
                if not self.running or self.paused:
                    break
                time.sleep(1)
            print("Готовка завершена.")

            cycle_duration = time.time() - cycle_start_time
            cycle_timer_label.config(text=f"⏱ Цикл: {cycle_duration:.1f} сек")

            log_entry = {
                'number': i + 1,
                'start_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cycle_start_time)),
                'duration': round(cycle_duration, 1)
            }
            self.cycle_logs.append(log_entry)

            print(f"[Цикл {i + 1}] Завершён за {cycle_duration:.1f} сек")
            update_log_display(log_entry)

        total_duration = time.time() - total_start_time
        print("\n✅ Все циклы завершены.")
        status_label.config(text="✅ Все циклы завершены.")
        total_timer_label.config(text=f"⏱ Общее время: {total_duration:.1f} сек")

        # Сохранение лога в файл
        self.save_logs_to_file(total_duration)

        # Громкое уведомление
        self.finish_notification()

    def save_logs_to_file(self, total_duration):
        with open("cooking_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== Новый запуск: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            for log in self.cycle_logs:
                f.write(f"[Цикл {log['number']}] "
                        f"Старт: {log['start_time']} | "
                        f"Длительность: {log['duration']} сек\n")
            f.write(f"Общее время: {total_duration:.1f} сек\n")
            f.write("-" * 50 + "\n")

    def finish_notification(self):
       
        # Всплывающее окно
        messagebox.showinfo("Готово!", "Все циклы успешно завершены!")

    def start(self):
        self.running = True
        self.paused = False
        self.repeats = int(repeat_entry.get())
        thread = threading.Thread(target=self.cook_cycle)
        thread.start()

    def pause(self):
        self.paused = not self.paused
        status_label.config(text="⏸ Пауза" if self.paused else "▶ Возобновлено")

    def stop(self):
        self.running = False
        self.paused = False
        status_label.config(text="⏹ Остановлено")

# === Графический интерфейс ===
def create_gui():
    global repeat_entry, status_label, cycle_timer_label, total_timer_label, log_text

    root = tk.Tk()
    root.title("Автоматизация готовки")
    root.geometry("600x500")
    root.resizable(False, False)

    tk.Label(root, text="Введите количество повторений:", font=("Arial", 12)).pack(pady=10)

    repeat_entry = tk.Entry(root, font=("Arial", 14), justify='center')
    repeat_entry.insert(0, "5")
    repeat_entry.pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    start_btn = tk.Button(frame, text="▶ Старт", width=10, command=lambda: cooker.start())
    pause_btn = tk.Button(frame, text="⏸ Пауза", width=10, command=lambda: cooker.pause())
    stop_btn = tk.Button(frame, text="⏹ Стоп", width=10, command=lambda: cooker.stop())

    start_btn.grid(row=0, column=0, padx=5)
    pause_btn.grid(row=0, column=1, padx=5)
    stop_btn.grid(row=0, column=2, padx=5)

    status_label = tk.Label(root, text="💤 Ожидание запуска", font=("Arial", 12), fg="gray")
    status_label.pack(pady=10)

    cycle_timer_label = tk.Label(root, text="⏱ Цикл: 0.0 сек", font=("Arial", 10), fg="blue")
    cycle_timer_label.pack(pady=5)

    total_timer_label = tk.Label(root, text="⏱ Общее время: 0.0 сек", font=("Arial", 10), fg="green")
    total_timer_label.pack(pady=5)

    tk.Label(root, text="История циклов:", font=("Arial", 12)).pack(pady=5)
    log_text = tk.Text(root, height=10, width=70, font=("Courier", 10), state='disabled')
    log_text.pack(pady=5)

    footer = tk.Label(root, text="by @assistant", font=("Arial", 8), fg="gray")
    footer.pack(side="bottom", pady=5)

    root.mainloop()

def update_log_display(log_entry):
    log_text.config(state='normal')
    log_text.insert(END, f"[Цикл {log_entry['number']}] "
                         f"Старт: {log_entry['start_time']} | "
                         f"Длительность: {log_entry['duration']} сек\n")
    log_text.config(state='disabled')
    log_text.see(END)

# === Запуск программы ===
if __name__ == "__main__":
    cooker = AutoCooker()
    create_gui()