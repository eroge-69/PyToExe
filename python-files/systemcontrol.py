import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import time

class SystemControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление системой")
        self.root.geometry("350x200")
        
        self.action = tk.StringVar()
        self.seconds = tk.IntVar()
        self.running = False
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Выберите действие:").pack(pady=5)
        
        actions = ("Завершить работу", "Перезагрузить", "Выйти из системы", "Гибернация", "Сменить пользователя")
        ttk.Combobox(self.root, textvariable=self.action, values=actions).pack(pady=5)
        
        tk.Button(self.root, text="Далее", command=self.show_timer).pack(pady=5)

    def show_timer(self):
        if not self.action.get():
            messagebox.showerror("Ошибка", "Выберите действие!")
            return
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text=f"Таймер для {self.action.get()}").pack(pady=5)
        tk.Label(self.root, text="Время (сек):").pack()
        tk.Entry(self.root, textvariable=self.seconds).pack(pady=5)
        
        self.start_btn = tk.Button(self.root, text="Старт", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = tk.Button(self.root, text="Отмена", command=self.cancel, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

    def start(self):
        try:
            sec = self.seconds.get()
            if sec <= 0:
                messagebox.showerror("Ошибка", "Время > 0")
                return
            
            self.running = True
            threading.Thread(target=self.execute, args=(sec,)).start()
            self.start_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.NORMAL)
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное время")

    def execute(self, seconds):
        time.sleep(seconds)
        if self.running:
            cmd = {
                "Завершить работу": "shutdown /s",
                "Перезагрузить": "shutdown /r",
                "Выйти из системы": "shutdown /l",
                "Гибернация": "shutdown /h",
                "Сменить пользоватля": "Rundll32.exe user32.dll,LockWorkStation"  # Правильная команда для блокировки
            }[self.action.get()]
            
            try:
                subprocess.run(cmd, shell=True)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def cancel(self):
        self.running = False
        try:
            subprocess.run("shutdown /a", shell=True)
            messagebox.showinfo("Успех", "Отменено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemControl(root)
    root.mainloop()