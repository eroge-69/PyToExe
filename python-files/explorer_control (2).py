import tkinter as tk
from tkinter import messagebox
import logging
import subprocess
try:
    import win32gui
    import win32con
    import pywintypes
except ImportError as e:
    print("Ошибка: Не удалось импортировать pywin32. Установите библиотеку с помощью 'pip install pywin32'.")
    exit(1)

class ExplorerControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление Проводником")
        self.root.geometry("400x300")  # Фиксированный размер окна
        self.root.configure(bg='#1C2526')

        # Установка окна поверх всех с помощью win32gui (HWND_TOPMOST)
        try:
            hwnd = self.root.winfo_id()
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            logging.info("Окно установлено поверх всех (HWND_TOPMOST)")
        except pywintypes.error as e:
            logging.error(f"Ошибка установки HWND_TOPMOST: {e}")
            messagebox.showerror("Ошибка", "Не удалось установить окно поверх. Проверьте логи.")

        # Настройка логирования
        logging.basicConfig(filename='explorer_control.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # GUI
        self.label = tk.Label(root, text="Управление Проводником Windows", font=("Arial", 16, "bold"),
                              fg="#E8ECEF", bg="#1C2526")
        self.label.pack(pady=30)

        self.close_button = tk.Button(root, text="Закрыть Проводник", command=self.terminate_explorer,
                                      font=("Arial", 14), bg="#FF4C4C", fg="white")
        self.close_button.pack(pady=10)

        self.open_button = tk.Button(root, text="Открыть Проводник", command=self.restart_explorer,
                                     font=("Arial", 14), bg="#28A745", fg="white")
        self.open_button.pack(pady=10)

        # Периодическое обновление HWND_TOPMOST
        self.keep_on_top()

    def terminate_explorer(self):
        """Завершить процесс Проводника."""
        try:
            subprocess.run(['taskkill', '/IM', 'explorer.exe', '/F'], check=True)
            logging.info("Проводник успешно завершён")
            messagebox.showinfo("Успех", "Проводник Windows закрыт")
        except subprocess.CalledProcessError as e:
            logging.error(f"Ошибка при завершении Проводника: {e}")
            messagebox.showerror("Ошибка", "Не удалось завершить Проводник. Проверьте логи.")

    def restart_explorer(self):
        """Перезапустить Проводник."""
        try:
            subprocess.run(['start', 'explorer.exe'], shell=True, check=True)
            logging.info("Проводник успешно перезапущен")
            messagebox.showinfo("Успех", "Проводник Windows запущен")
        except subprocess.CalledProcessError as e:
            logging.error(f"Ошибка при перезапуске Проводника: {e}")
            messagebox.showerror("Ошибка", "Не удалось перезапустить Проводник. Проверьте логи.")

    def keep_on_top(self):
        """Поддерживать окно поверх всех (HWND_TOPMOST)."""
        try:
            hwnd = self.root.winfo_id()
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            self.root.after(100, self.keep_on_top)  # Обновляем каждые 100 мс
        except pywintypes.error as e:
            logging.error(f"Ошибка обновления HWND_TOPMOST: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExplorerControl(root)
    root.mainloop()