import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import platform
import json
import os


class ConnectionCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pingip")
        self.root.geometry("800x800")

        # Файл для сохранения данных
        self.config_file = "connection_checks.json"

        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('roboto', 10))
        self.style.configure('TButton', font=('roboto', 10))
        self.style.configure('TEntry', font=('roboto', 10))
        self.style.configure('Success.TLabel', foreground='green')
        self.style.configure('Error.TLabel', foreground='red')
        self.style.configure('Warning.TLabel', foreground='orange')

        # Основной контейнер с прокруткой
        container = ttk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill=tk.BOTH, expand=True)
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заголовок
        ttk.Label(scrollable_frame, text="PINGIP",
                  font=('roboto', 14, 'bold')).grid(row=0, column=0, columnspan=6, pady=10)

        # Заголовки столбцов
        headers = ["Название", "IP-адрес", "Порт", "Статус", "Детали", "Действия"]
        for col, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, font=('roboto', 10, 'bold')).grid(
                row=1, column=col, padx=5, pady=5)

        # Создаем 20 строк для проверок
        self.checks = []
        for i in range(20):
            self.add_check_row(scrollable_frame, i + 2)

        # Загружаем сохраненные данные
        self.load_saved_data()

        # Кнопки управления
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=22, column=0, columnspan=6, pady=15)

        check_all_btn = ttk.Button(btn_frame, text="Проверить все",
                                   command=self.check_all, style='Accent.TButton')
        check_all_btn.pack(side=tk.LEFT, padx=10)

        save_btn = ttk.Button(btn_frame, text="Сохранить настройки",
                              command=self.save_data)
        save_btn.pack(side=tk.LEFT, padx=10)

        # Стиль для акцентной кнопки
        self.style.configure('Accent.TButton', font=('roboto', 10, 'bold'), foreground='blue')

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=10, pady=5)

        # Сохраняем данные при закрытии программы
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_check_row(self, parent, row):
        """Добавляет строку для проверки подключения"""
        # Название проверки
        name_var = tk.StringVar()
        name_entry = ttk.Entry(parent, textvariable=name_var, width=20)
        name_entry.grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)

        # IP-адрес
        ip_var = tk.StringVar()
        ip_entry = ttk.Entry(parent, textvariable=ip_var, width=15)
        ip_entry.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)

        # Порт
        port_var = tk.StringVar()
        port_entry = ttk.Entry(parent, textvariable=port_var, width=10)
        port_entry.grid(row=row, column=2, padx=5, pady=2, sticky=tk.W)

        # Статус
        status_var = tk.StringVar(value="Не проверено")
        status_label = ttk.Label(parent, textvariable=status_var)
        status_label.grid(row=row, column=3, padx=5, pady=2, sticky=tk.W)

        # Детали
        details_var = tk.StringVar()
        details_label = ttk.Label(parent, textvariable=details_var, wraplength=300)
        details_label.grid(row=row, column=4, padx=5, pady=2, sticky=tk.W)

        # Прогресс и кнопки
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=row, column=5, padx=5, pady=2, sticky=tk.W)

        progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        progress.pack(side=tk.TOP, fill=tk.X)

        check_btn = ttk.Button(action_frame, text="Проверить",
                               command=lambda i=row - 2: self.start_check(i))
        check_btn.pack(side=tk.LEFT, padx=2)

        self.checks.append({
            'name_var': name_var,
            'ip_var': ip_var,
            'port_var': port_var,
            'status_var': status_var,
            'details_var': details_var,
            'progress': progress,
            'check_btn': check_btn,
            'status_label': status_label,
            'details_label': details_label,
            'active': False
        })

    def load_saved_data(self):
        """Загружает сохраненные данные из файла"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for i, check_data in enumerate(data):
                        if i < len(self.checks):
                            self.checks[i]['name_var'].set(check_data.get('name', ''))
                            self.checks[i]['ip_var'].set(check_data.get('ip', ''))
                            self.checks[i]['port_var'].set(check_data.get('port', ''))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить сохраненные данные: {str(e)}")

    def save_data(self):
        """Сохраняет текущие данные в файл"""
        data = []
        for check in self.checks:
            data.append({
                'name': check['name_var'].get(),
                'ip': check['ip_var'].get(),
                'port': check['port_var'].get()
            })

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_var.set("Настройки успешно сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def on_close(self):
        """Обработчик закрытия окна"""
        self.save_data()
        self.root.destroy()

    def start_check(self, index):
        """Запускает проверку для конкретного индекса"""
        check = self.checks[index]
        name = check['name_var'].get().strip()
        ip = check['ip_var'].get().strip()
        port = check['port_var'].get().strip()

        if not ip or not port:
            messagebox.showerror("Ошибка", f"Для проверки #{index + 1} введите IP-адрес и порт")
            return

        if not name:
            name = f"Проверка #{index + 1}"
            check['name_var'].set(name)

        if check['active']:
            return

        check['active'] = True
        check['check_btn'].config(state=tk.DISABLED)
        check['status_var'].set("Проверяется...")
        check['details_var'].set("")
        check['progress']['value'] = 0

        # Запускаем в отдельном потоке
        threading.Thread(target=self.do_check, args=(index,), daemon=True).start()

    def do_check(self, index):
        """Выполняет проверку подключения"""
        check = self.checks[index]
        name = check['name_var'].get().strip()
        ip = check['ip_var'].get().strip()
        port_str = check['port_var'].get().strip()

        try:
            port = int(port_str)

            # Имитация прогресса
            for i in range(5):
                self.root.after(100, lambda: check['progress'].step(20))
                threading.Event().wait(0.1)

            # Проверяем подключение
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                try:
                    s.connect((ip, port))
                    result = "Есть подключение"
                    style = "Success.TLabel"
                    details = f"Успешное подключение"
                except socket.timeout:
                    result = "Нет подключения"
                    style = "Error.TLabel"
                    details = "Таймаут соединения"
                except ConnectionRefusedError:
                    result = "Нет подключения"
                    style = "Error.TLabel"
                    details = "Соединение отклонено"
                except Exception as e:
                    result = "Ошибка"
                    style = "Warning.TLabel"
                    details = str(e)

                self.root.after(0, self.update_status, index, result, style, details)

        except ValueError:
            self.root.after(0, self.update_status,
                            index, "Ошибка", "Warning.TLabel",
                            "Неверный номер порта")
        except Exception as e:
            self.root.after(0, self.update_status,
                            index, "Ошибка", "Warning.TLabel",
                            str(e))
        finally:
            check['active'] = False
            self.root.after(0, lambda: check['check_btn'].config(state=tk.NORMAL))
            check['progress']['value'] = 100

    def update_status(self, index, result, style, details):
        """Обновляет статус проверки"""
        check = self.checks[index]
        check['status_var'].set(result)
        check['details_var'].set(details)
        check['status_label'].configure(style=style)
        check['details_label'].configure(style=style)

    def check_all(self):
        """Запускает проверку для всех заполненных полей"""
        has_checks = False

        for i, check in enumerate(self.checks):
            ip = check['ip_var'].get().strip()
            port = check['port_var'].get().strip()

            if ip and port and not check['active']:
                has_checks = True
                self.start_check(i)

        if not has_checks:
            messagebox.showinfo("Информация", "Нет заполненных проверок для запуска")
            return

        self.status_var.set("Запущена проверка всех подключений")

    def clear_all(self):
        """Очищает все поля и результаты"""
        for check in self.checks:
            check['name_var'].set("")
            check['ip_var'].set("")
            check['port_var'].set("")
            check['status_var'].set("Не проверено")
            check['details_var'].set("")
            check['status_label'].configure(style='TLabel')
            check['details_label'].configure(style='TLabel')
            check['progress']['value'] = 0

        self.status_var.set("Все поля очищены")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectionCheckerApp(root)
    root.mainloop()