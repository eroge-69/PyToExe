import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import threading

class LoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bound loader")
        self.root.geometry("500x300")
        self.root.configure(bg="black")

        # Логотип / Заголовок
        label = tk.Label(root, text="BOUND LOADER", fg="lime", bg="black", font=("Consolas", 20, "bold"))
        label.pack(pady=10)

        # Память (RAM) ввод
        self.mem_label = tk.Label(root, text="Enter amount of RAM (in GB):", fg="lime", bg="black", font=("Consolas", 12))
        self.mem_label.pack(pady=(10,0))
        self.mem_entry = tk.Entry(root, font=("Consolas", 12))
        self.mem_entry.insert(0, "2")
        self.mem_entry.pack()

        # Прогрессбар
        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=20)

        # Статус
        self.status_label = tk.Label(root, text="", fg="lime", bg="black", font=("Consolas", 10))
        self.status_label.pack()

        # Кнопка запуска
        self.start_button = tk.Button(root, text="Launch", command=self.start_loading, font=("Consolas", 12))
        self.start_button.pack(pady=10)

    def start_loading(self):
        try:
            memory = int(self.mem_entry.get())
            if memory < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number >= 1 for RAM.")
            return

        self.start_button.config(state="disabled")
        self.progress['value'] = 0
        self.status_label.config(text="Starting checks...")

        # Запускаем проверку и запуск в отдельном потоке, чтобы не блокировать GUI
        threading.Thread(target=self.run_process, args=(memory,), daemon=True).start()

    def run_process(self, memory):
        steps = [
            ("Checking java.exe", r"C:\Program Files\Java\jdk-17\bin\java.exe"),
            ("Checking suicide.jar", r"C:\suicide\client\suicide.jar"),
            ("Checking natives directory", r"C:\suicide\client\natives"),
            ("Checking libraries directory", r"C:\suicide\client\libraries"),
            ("Checking assets directory", r"C:\suicide\client\assets"),
            ("Checking game directory", r"C:\suicide\client\game"),
        ]

        for i, (desc, path) in enumerate(steps, 1):
            self.update_status(f"{desc}...")
            if not os.path.exists(path):
                self.update_status(f"[ERROR] Not found: {path}")
                messagebox.showerror("Error", f"{desc} not found at:\n{path}")
                self.enable_button()
                return
            self.update_progress(i * 100 / len(steps))
            # Немного паузы, чтобы визуально видеть прогресс
            import time
            time.sleep(0.3)

        self.update_status("All checks passed.")

        # Формируем команду запуска
        java_exe = r"C:\Program Files\Java\jdk-17\bin\java.exe"
        jar_file = r"C:\suicide\client\suicide.jar"
        natives_dir = r"C:\suicide\client\natives"
        libraries_dir = r"C:\suicide\client\libraries"
        assets_dir = r"C:\suicide\client\assets"
        game_dir = r"C:\suicide\client\game"

        command = [
            java_exe,
            f"-Xmx{memory}G",
            f"-Djava.library.path={natives_dir}",
            "-cp", f"{libraries_dir}\\*;{jar_file}",
            "net.minecraft.client.main.Main",
            "--username", "korta",
            "--width", "854",
            "--height", "480",
            "--version", "xyipenis141",
            "--gameDir", game_dir,
            "--assetsDir", assets_dir,
            "--assetIndex", "1.16",
            "--accessToken", "0",
        ]

        self.update_status("Launching client...")

        try:
            # Запуск Java клиента и ожидание завершения
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.update_status(f"[ERROR] Failed to launch client.\nSee console for details.")
                messagebox.showerror("Launch error", f"Client failed with code {process.returncode}.\n\n{stderr.decode()}")
            else:
                self.update_status("Client launched successfully! Have fun!")
                messagebox.showinfo("Success", "Client launched successfully! Have fun!")

        except Exception as e:
            self.update_status(f"[ERROR] Exception: {e}")
            messagebox.showerror("Error", f"Exception occurred:\n{e}")

        self.enable_button()

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def enable_button(self):
        self.start_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure("TProgressbar", foreground='lime', background='lime')
    app = LoaderApp(root)
    root.mainloop()
