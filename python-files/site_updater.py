
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import ftplib
import os
import time
import json
import zipfile

CONFIG_FILE = "config.json"

class SiteUpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙ Планировщик обновлений сайта")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.bg_image = tk.PhotoImage(file="background.png")
        self.background_label = tk.Label(root, image=self.bg_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.zip_path = tk.StringVar()
        self.ftp_host = tk.StringVar()
        self.ftp_user = tk.StringVar()
        self.ftp_pass = tk.StringVar()
        self.remote_dir = tk.StringVar()
        self.datetime_str = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Путь к ZIP-архиву:", bg="#000", fg="#fff").place(x=30, y=30)
        tk.Entry(self.root, textvariable=self.zip_path, width=50).place(x=180, y=30)
        tk.Button(self.root, text="Выбрать", command=self.browse_zip).place(x=500, y=27)

        tk.Label(self.root, text="FTP-хост:", bg="#000", fg="#fff").place(x=30, y=70)
        tk.Entry(self.root, textvariable=self.ftp_host, width=30).place(x=180, y=70)

        tk.Label(self.root, text="FTP-пользователь:", bg="#000", fg="#fff").place(x=30, y=100)
        tk.Entry(self.root, textvariable=self.ftp_user, width=30).place(x=180, y=100)

        tk.Label(self.root, text="FTP-пароль:", bg="#000", fg="#fff").place(x=30, y=130)
        tk.Entry(self.root, textvariable=self.ftp_pass, width=30, show="*").place(x=180, y=130)

        tk.Label(self.root, text="Папка на сервере:", bg="#000", fg="#fff").place(x=30, y=160)
        tk.Entry(self.root, textvariable=self.remote_dir, width=30).place(x=180, y=160)

        tk.Label(self.root, text="Дата и время обновления (ГГГГ-ММ-ДД ЧЧ:ММ):", bg="#000", fg="#fff").place(x=30, y=190)
        tk.Entry(self.root, textvariable=self.datetime_str, width=30).place(x=370, y=190)

        tk.Button(self.root, text="Запланировать обновление", command=self.schedule_update).place(x=200, y=230)

    def browse_zip(self):
        path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if path:
            self.zip_path.set(path)

    def schedule_update(self):
        try:
            run_time = datetime.strptime(self.datetime_str.get(), "%Y-%m-%d %H:%M")
            delay = (run_time - datetime.now()).total_seconds()
            if delay < 0:
                raise ValueError("Указано прошедшее время.")
            threading.Timer(delay, self.run_update).start()
            messagebox.showinfo("Успех", "Обновление запланировано!")
            self.save_config()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный формат даты или ошибка: {e}")

    def run_update(self):
        try:
            ftp = ftplib.FTP(self.ftp_host.get())
            ftp.login(self.ftp_user.get(), self.ftp_pass.get())
            ftp.cwd(self.remote_dir.get())

            with zipfile.ZipFile(self.zip_path.get(), 'r') as zip_ref:
                extract_path = "temp_extract"
                zip_ref.extractall(extract_path)
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, extract_path)
                        with open(full_path, 'rb') as f:
                            ftp.storbinary(f'STOR ' + rel_path.replace("\", "/"), f)
                messagebox.showinfo("Готово", "Обновление выполнено!")
                os.system(f"rmdir /s /q {extract_path}")
                ftp.quit()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить сайт: {e}")

    def save_config(self):
        config = {
            "zip_path": self.zip_path.get(),
            "ftp_host": self.ftp_host.get(),
            "ftp_user": self.ftp_user.get(),
            "ftp_pass": self.ftp_pass.get(),
            "remote_dir": self.remote_dir.get(),
            "datetime_str": self.datetime_str.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

def main():
    root = tk.Tk()
    app = SiteUpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
