import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import threading
import queue
import time

class NLACheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NLA Checker GUI")

        self.results = {}
        self.queue = queue.Queue()
        self.threads = []
        self.stop_flag = False

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Файл с хостами
        tk.Label(frame, text="Файл с хостами/IP:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = tk.Entry(frame, width=50)
        self.file_entry.grid(row=0, column=1, sticky=tk.W)
        tk.Button(frame, text="Обзор...", command=self.browse_file).grid(row=0, column=2, padx=5)

        # Порт
        tk.Label(frame, text="Порт:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_entry = tk.Entry(frame, width=10)
        self.port_entry.grid(row=1, column=1, sticky=tk.W)
        self.port_entry.insert(0, "3389")

        # Скорость (число потоков)
        tk.Label(frame, text="Скорость (число потоков):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.speed_entry = tk.Entry(frame, width=10)
        self.speed_entry.grid(row=2, column=1, sticky=tk.W)
        self.speed_entry.insert(0, "50")  # по умолчанию 50 потоков

        # Кнопки
        self.start_btn = tk.Button(frame, text="Начать проверку", command=self.start_check)
        self.start_btn.grid(row=3, column=0, pady=10)

        self.stop_btn = tk.Button(frame, text="Остановить", command=self.stop_check, state=tk.DISABLED)
        self.stop_btn.grid(row=3, column=1, pady=10, sticky=tk.W)

        # Текстовое поле с прокруткой для результатов
        self.text = scrolledtext.ScrolledText(frame, width=80, height=25)
        self.text.grid(row=4, column=0, columnspan=3, pady=10)

        # Кнопка сохранить результаты
        self.save_btn = tk.Button(frame, text="Сохранить результаты", command=self.save_results, state=tk.DISABLED)
        self.save_btn.grid(row=5, column=0, pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Выберите файл с хостами", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def check_nla(self, host, port, timeout=3):
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def worker(self, hosts_queue, port):
        while not self.stop_flag:
            try:
                host = hosts_queue.get_nowait()
            except queue.Empty:
                break
            result = self.check_nla(host, port)
            text_result = f"{host}: {'NLA поддерживается (порт открыт)' if result else 'Недоступен или NLA не поддерживается'}"
            self.queue.put(text_result)
            hosts_queue.task_done()

    def update_text(self):
        while not self.queue.empty():
            line = self.queue.get()
            self.text.insert(tk.END, line + "\n")
            self.text.see(tk.END)
        if any(t.is_alive() for t in self.threads):
            self.root.after(100, self.update_text)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Готово", "Проверка завершена.")

    def start_check(self):
        filename = self.file_entry.get()
        port_str = self.port_entry.get()
        speed_str = self.speed_entry.get()

        if not filename:
            messagebox.showwarning("Ошибка", "Выберите файл с хостами.")
            return
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректный номер порта (1-65535).")
            return
        try:
            speed = int(speed_str)
            if speed < 1 or speed > 200:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное число потоков (1-200).")
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                hosts = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
            return

        if not hosts:
            messagebox.showwarning("Ошибка", "Файл пустой или содержит только пустые строки.")
            return

        self.text.delete(1.0, tk.END)
        self.results.clear()
        self.stop_flag = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)

        hosts_queue = queue.Queue()
        for host in hosts:
            hosts_queue.put(host)

        self.threads = []
        for _ in range(min(speed, len(hosts))):
            t = threading.Thread(target=self.worker, args=(hosts_queue, port))
            t.daemon = True
            t.start()
            self.threads.append(t)

        self.root.after(100, self.update_text)

    def stop_check(self):
        self.stop_flag = True
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Остановлено", "Проверка остановлена пользователем.")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if not file_path:
            return
        try:
            text = self.text.get(1.0, tk.END).strip()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Успех", f"Результаты сохранены в {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NLACheckerApp(root)
    root.mainloop()

