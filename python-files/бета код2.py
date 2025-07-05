import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from tkinter import ttk
import json
import os
import socket
PORT = 65432
SERVER_ADDRESS = '192.168.31.31'  # Замените на IP-адрес вашего сервера

class NetworkError(Exception):
    """Пользовательское исключение для сетевых ошибок."""
    pass

def send_request(action, payload=None):
    """Отправляет запрос на сервер и возвращает ответ."""
    #server_address = get_server_address()  # Больше не нужно
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_ADDRESS, PORT))  # Используем константу
            request = {'action': action, 'payload': payload or {}}
            s.sendall(json.dumps(request).encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            return json.loads(response)
    except ConnectionRefusedError:
        raise NetworkError("Не удалось подключиться к серверу. Убедитесь, что он запущен и адрес указан верно.")
    except json.JSONDecodeError:
        raise NetworkError("Неверный JSON получен от сервера.")
    except ValueError as e:
        raise NetworkError(str(e))
    except OSError as e:
        raise NetworkError(f"Ошибка подключения: {e}") # Добавлено для обработки общих ошибок сокета
    except Exception as e:
        raise NetworkError(f"Произошла сетевая ошибка: {e}")

class MainForm:
    def __init__(self, master):
        self.master = master
        master.title("Управление базой данных")
        master.geometry("600x400")

        # Центрирование окна
        master.update_idletasks()
        width = master.winfo_width()
        height = master.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (width // 2)
        y = (master.winfo_screenheight() // 2) - (height // 2)
        master.geometry(f"+{x}+{y}")

        # Создание Label (опционально)
        self.label = tk.Label(master, text="Система управления дасье", font=("Arial", 12))
        self.label.pack(pady=10)

        # Создание кнопок
        self.create_button = tk.Button(master, text="Создать дасье", command=self.create_database, width=20)
        self.create_button.pack(pady=5)

        self.search_button = tk.Button(master, text="Поиск по базе", command=self.search_database, width=20)
        self.search_button.pack(pady=5)

        self.exit_button = tk.Button(master, text="Выйти", command=self.exit_application, width=20)
        self.exit_button.pack(pady=5)

        # Treeview для отображения всех досье
        self.tree = ttk.Treeview(master, columns=("Имя", "Прочие данные"), show="headings")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Прочие данные", text="Прочие данные")
        self.tree.column("Имя", width=150)
        self.tree.column("Прочие данные", width=300)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_selected_record)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Контекстное меню
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected_record_from_menu)
        self.context_menu.add_command(label="Удалить", command=self.delete_selected_record)

        # Инициализация данных и обновление Treeview при запуске
        self.data = {} # локальное хранилище данных
        try:
            self.load_data()
        except NetworkError as e:
            messagebox.showerror("Ошибка сети", str(e))
        self.update_treeview()

    def create_database(self):
        """Функция для создания дасье."""
        dialog = AddRecordDialog(self.master, self)
        self.master.wait_window(dialog)
        self.update_treeview()

    def search_database(self):
        """Функция для поиска по базе данных."""
        self.search_name = simpledialog.askstring("Поиск", "Введите имя для поиска:")
        if self.search_name:
            try:
                response = send_request('search_record', {'name': self.search_name})
                if response['status'] == 'success':
                    SearchDialog(self.master, self.search_name, response['data'], self.data, self)
                elif response['status'] == 'not_found':
                    messagebox.showinfo("Поиск", "Запись не найдена.")
                else:
                    messagebox.showerror("Ошибка", f"Ошибка поиска: {response.get('message', 'Неизвестная ошибка')}")

            except NetworkError as e:
                messagebox.showerror("Ошибка сети", str(e))

    def exit_application(self):
        """Функция для выхода из приложения."""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.master.destroy()

    def update_treeview(self):
        """Обновляет содержимое Treeview (таблицы) на основе локальных данных."""
        # Очищаем старые данные
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем новыми данными
        for name, other_data in self.data.items():
            # Ограничиваем отображение прочих данных в Treeview
            display_data = other_data[:50]  # Отображаем только первые 50 символов
            if len(other_data) > 50:
                display_data += "..."  # Добавляем "..." если текст обрезан
            self.tree.insert("", tk.END, values=(name, display_data))


    def edit_selected_record(self, event):
        """Редактирование записи при двойном клике."""
        self.edit_selected_record_internal()

    def edit_selected_record_from_menu(self):
        """Редактирование записи из контекстного меню."""
        self.edit_selected_record_internal()

    def edit_selected_record_internal(self):
        """Внутренняя функция для редактирования записи."""
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            name = self.tree.item(item_id, "values")[0]
            other_data = self.data.get(name, "")

            dialog = EditRecordDialog(self.master, self, name, other_data)
            self.master.wait_window(dialog)
            self.update_treeview() # Обновляем после редактирования

    def delete_selected_record(self):
        """Удаление записи."""
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            name = self.tree.item(item_id, "values")[0]

            if messagebox.askyesno("Удаление", f"Вы уверены, что хотите удалить запись для {name}?"):
                try:
                    response = send_request('delete_record', {'name': name})
                    if response['status'] == 'success':
                        del self.data[name] # Удаляем из локальных данных
                        self.update_treeview() # Обновляем Treeview
                    else:
                        messagebox.showerror("Ошибка", f"Ошибка удаления: {response.get('message', 'Неизвестная ошибка')}")
                except NetworkError as e:
                    messagebox.showerror("Ошибка сети", str(e))

    def show_context_menu(self, event):
        """Показ контекстного меню."""
        try:
            # Выбираем строку по клику правой кнопкой мыши
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)  # Выделяем строку
                self.context_menu.post(event.x_root, event.y_root)
        except:
            pass # Обработка ошибок (например, клик вне строк)

    def load_data(self):
        """Загружает данные с сервера."""
        try:
            response = send_request('get_data')
            if response['status'] == 'success':
                self.data = response['data']  # Обновляем локальные данные
                self.update_treeview()
            else:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {response.get('message', 'Неизвестная ошибка')}")
        except NetworkError as e:
            messagebox.showerror("Ошибка сети", str(e))

class AddRecordDialog(tk.Toplevel):
    def __init__(self, parent, main_form):
        super().__init__(parent)
        self.title("Создание дасье")
        self.geometry("400x250")

        self.main_form = main_form

        self.name_label = tk.Label(self, text="Имя и Фамилия:")
        self.name_label.pack(pady=5)

        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack(pady=5)

        self.other_data_label = tk.Label(self, text="Прочие данные:")
        self.other_data_label.pack(pady=5)

        self.other_data_entry = tk.Text(self, width=40, height=5)
        self.other_data_entry.pack(pady=5)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
        self.ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.cancel_button = tk.Button(self, text="Отмена", command=self.on_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.result = None
        self.parent = parent
        self.parent.withdraw()

    def on_ok(self):
        name_data = self.name_entry.get().strip()
        other_data = self.other_data_entry.get("1.0", tk.END).strip()

        if not name_data:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя и фамилию.")
            return

        try:
            response = send_request('add_record', {'name': name_data, 'other_data': other_data})
            if response['status'] == 'success':
                self.main_form.data[name_data] = other_data # Обновляем локальные данные
                self.result = (name_data, other_data)
                self.destroy()
                self.parent.deiconify()
                self.main_form.update_treeview() # Обновляем Treeview

            else:
                messagebox.showerror("Ошибка", f"Ошибка создания записи: {response.get('message', 'Неизвестная ошибка')}")
        except NetworkError as e:
            messagebox.showerror("Ошибка сети", str(e))

    def on_cancel(self):
        self.result = None
        self.destroy()
        self.parent.deiconify()


class SearchDialog(tk.Toplevel):
    def __init__(self, parent, search_name, other_data, data_dict, main_form):
        super().__init__(parent)
        self.title(f"Результат поиска: {search_name}")
        self.geometry("800x500")

        self.search_name_label = tk.Label(self, text=f"Имя: {search_name}")
        self.search_name_label.pack(pady=5)

        self.other_data_label = tk.Label(self, text="Прочие данные:")
        self.other_data_label.pack(pady=5)

        self.other_data_text = scrolledtext.ScrolledText(self, width=50, height=10)
        self.other_data_text.insert(tk.END, other_data)
        self.other_data_text.config(state=tk.DISABLED)
        self.other_data_text.pack(pady=5)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok_close)
        self.ok_button.pack(pady=10)

        # Treeview для отображения всех досье
        self.tree = ttk.Treeview(self, columns=("Имя", "Прочие данные"), show="headings")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Прочие данные", text="Прочие данные")
        self.tree.column("Имя", width=150)
        self.tree.column("Прочие данные", width=300)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.data_dict = data_dict
        self.populate_treeview()
        self.main_form = main_form

        self.parent = parent # parent = root
        self.parent.withdraw()

    def populate_treeview(self):
        """Заполняет Treeview данными из data."""
        for item in self.tree.get_children():
            self.tree.delete(item)  # Очищаем предыдущие данные

        for name, other_data in self.data_dict.items():
            self.tree.insert("", tk.END, values=(name, other_data)) # Вставляем данные
    def on_ok_close(self):  # Новый метод для закрытия
        self.destroy()  # Закрываем SearchDialog
        self.parent.deiconify() # Показываем главное окно

class EditRecordDialog(tk.Toplevel):  # Новый класс для редактирования
    def __init__(self, parent, main_form, name, other_data):
        super().__init__(parent)
        self.title(f"Редактирование: {name}")
        self.geometry("400x250")

        self.main_form = main_form
        self.old_name = name  # Сохраняем старое имя

        self.name_label = tk.Label(self, text="Имя и Фамилия:")
        self.name_label.pack(pady=5)
        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.insert(0, name)
        self.name_entry.pack(pady=5)


        self.other_data_label = tk.Label(self, text="Прочие данные:")
        self.other_data_label.pack(pady=5)
        self.other_data_text = tk.Text(self, width=40, height=5)
        self.other_data_text.insert(tk.END, other_data)
        self.other_data_text.pack(pady=5)

        self.ok_button = tk.Button(self, text="Сохранить", command=self.on_save)
        self.ok_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.cancel_button = tk.Button(self, text="Отмена", command=self.on_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.parent = parent
        self.parent.withdraw()

    def on_save(self):
        new_name = self.name_entry.get().strip()
        new_other_data = self.other_data_text.get("1.0", tk.END).strip()

        if not new_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя и фамилию.")
            return

        try:
            response = send_request('update_record', {
                'old_name': self.old_name,
                'new_name': new_name,
                'new_other_data': new_other_data
            })

            if response['status'] == 'success':
                # Обновляем локальные данные
                if self.old_name in self.main_form.data:
                    del self.main_form.data[self.old_name]
                self.main_form.data[new_name] = new_other_data
                self.destroy()
                self.main_form.update_treeview()
                self.parent.deiconify()

            else:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {response.get('message', 'Неизвестная ошибка')}")

        except NetworkError as e:
            messagebox.showerror("Ошибка сети", str(e))

    def on_cancel(self):
        self.destroy()
        self.parent.deiconify()

# Создание главного окна
root = tk.Tk()
main_form = MainForm(root)
root.mainloop()
