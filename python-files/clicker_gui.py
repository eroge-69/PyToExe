import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import time
from pynput import keyboard, mouse
from PIL import Image
import pystray
import os
import sys

class AutoClickerApp:
    def __init__(self, master):
        self.master = master
        master.title("Автокликер")
        master.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.interval_entry = self._entry_with_label("Интервал (сек):", "0.5", 0)
        self.x_entry = self._entry_with_label("Координата X:", "", 1)
        self.y_entry = self._entry_with_label("Координата Y:", "", 2)

        tk.Button(master, text="Текущая позиция", command=self.set_current_position).grid(row=3, column=0, columnspan=2, pady=2)
        tk.Button(master, text="Выбрать точку мышью", command=self.pick_position).grid(row=4, column=0, columnspan=2, pady=2)

        self.start_button = tk.Button(master, text="Старт", command=self.start_clicking)
        self.start_button.grid(row=5, column=0, pady=10)

        self.stop_button = tk.Button(master, text="Стоп", command=self.stop_clicking, state=tk.DISABLED)
        self.stop_button.grid(row=5, column=1, pady=10)

        self.running = False
        self.thread = None
        self.icon = None

        self.create_tray_icon()

        # Запускаем глобальный слушатель клавиш в отдельном потоке
        listener_thread = threading.Thread(target=self.global_hotkeys_listener, daemon=True)
        listener_thread.start()

    def _entry_with_label(self, label, default, row):
        tk.Label(self.master, text=label).grid(row=row, column=0, sticky="e")
        entry = tk.Entry(self.master)
        entry.insert(0, default)
        entry.grid(row=row, column=1)
        return entry

    def set_current_position(self):
        x, y = pyautogui.position()
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))
        messagebox.showinfo("Позиция мыши", f"X: {x}, Y: {y}")

    def pick_position(self):
        self.master.withdraw()
        messagebox.showinfo("Выбор точки", "Кликни в нужное место на экране")

        def on_click(x, y, button, pressed):
            if pressed:
                self.x_entry.delete(0, tk.END)
                self.y_entry.delete(0, tk.END)
                self.x_entry.insert(0, str(x))
                self.y_entry.insert(0, str(y))
                self.master.deiconify()
                return False

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def start_clicking(self):
        if self.running:
            return  # Уже работает
        try:
            interval = float(self.interval_entry.get())
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения!")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.thread = threading.Thread(target=self.click_loop, args=(interval, x, y))
        self.thread.daemon = True
        self.thread.start()
        print("▶️ Кликер запущен")

    def stop_clicking(self):
        if not self.running:
            return
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        print("⛔ Кликер остановлен")

    def click_loop(self, interval, x, y):
        while self.running:
            pyautogui.click(x, y)
            time.sleep(interval)

    def hide_window(self):
        self.master.withdraw()

    def show_window(self, icon=None, item=None):
        self.master.deiconify()

    def quit_app(self, icon=None, item=None):
        self.running = False
        if self.icon:
            self.icon.stop()
        self.master.destroy()
        sys.exit()

    def create_tray_icon(self):
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icon.png")
        if not os.path.exists(icon_path):
            print("❌ icon.png не найден")
            return
        image = Image.open(icon_path)

        menu = pystray.Menu(
            pystray.MenuItem("Открыть", self.show_window),
            pystray.MenuItem("Выход", self.quit_app)
        )

        self.icon = pystray.Icon("AutoClicker", image, "Автокликер", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def global_hotkeys_listener(self):
        # Функции для биндов
        def on_press(key):
            try:
                if key == keyboard.Key.f6:
                    self.start_clicking()
                elif key == keyboard.Key.f7:
                    self.stop_clicking()
            except Exception as e:
                print(f"Ошибка в обработчике горячих клавиш: {e}")

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
