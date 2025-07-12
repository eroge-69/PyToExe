import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import keyboard
import threading
import json
import os

class BinderApp:
    def __init__(self, master):
        self.master = master
        master.title("Binder")

        self.binds = self.load_binds() # Загрузка биндов при инициализации
        self.hotkey_listeners = {} # Словарь для хранения слушателей горячих клавиш по ID
        self.next_bind_id = self.get_next_id() # Инициализация ID

        # Treeview для отображения биндов
        self.tree = ttk.Treeview(master, columns=("ID","Hotkey", "Text"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Hotkey", text="Горячая клавиша")
        self.tree.heading("Text", text="Текст")
        self.tree.column("ID", width=30)  # Установите ширину для столбца ID
        self.tree.column("Hotkey", width=150)
        self.tree.column("Text", width=300)
        self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.tree.bind("<Double-1>", self.edit_bind) # Двойной клик для редактирования
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Кнопки
        self.add_button = tk.Button(master, text="Добавить", command=self.open_add_window)
        self.add_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.edit_button = tk.Button(master, text="Редактировать", command=self.edit_bind)
        self.edit_button.grid(row=1, column=0, padx=5, pady=5, sticky="n")

        self.delete_button = tk.Button(master, text="Удалить", command=self.delete_bind)
        self.delete_button.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.refresh_treeview()  # Заполнение Treeview при запуске

        master.protocol("WM_DELETE_WINDOW", self.on_closing)  # Перехват закрытия окна

    def load_binds(self):
        """Загрузка биндов из файла."""
        filepath = "binds.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Преобразуем все ID в целые числа при загрузке
                    for bind in data:
                        bind['id'] = int(bind['id'])
                    return data
            except Exception as e:
                print(f"Ошибка при загрузке биндов: {e}")
                return []
        else:
            return []

    def save_binds(self):
        """Сохранение биндов в файл."""
        filepath = "binds.json"
        try:
            with open(filepath, "w") as f:
                json.dump(self.binds, f, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении биндов: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при сохранении биндов: {e}")

    def open_add_window(self):
        """Открывает окно добавления бинда."""
        AddBindWindow(self)

    def edit_bind(self, event=None):
        """Открывает окно редактирования бинда."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Внимание", "Выберите биндер для редактирования.")
            return

        try:
            bind_id = int(self.tree.item(selected_item[0], "values")[0])
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ID биндера.")
            return
        EditBindWindow(self, bind_id)

    def delete_bind(self):
        """Удаляет выбранный бинд."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Внимание", "Выберите биндер для удаления.")
            return

        try:
            bind_id = int(self.tree.item(selected_item[0], "values")[0])
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный ID биндера.")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот бинд?"):
            self.unbind_hotkey(bind_id) # Отвязываем горячую клавишу
            self.binds = [bind for bind in self.binds if bind['id'] != bind_id] # Фильтруем список
            self.save_binds()
            self.refresh_treeview()

    def add_bind(self, hotkey, text):
        """Добавляет новый бинд."""
        new_id = self.next_bind_id # Использовать текущий ID
        new_bind = {"id": new_id, "hotkey": hotkey, "text": text}
        self.binds.append(new_bind)
        self.save_binds()
        self.bind_hotkey(new_id, hotkey, text) # Привязываем горячую клавишу сразу
        self.refresh_treeview()
        self.next_bind_id = self.get_next_id() # Обновить следующий ID

    def update_bind(self, bind_id, hotkey, text):
        """Обновляет существующий бинд."""
        for bind in self.binds:
            if bind['id'] == bind_id:
                self.unbind_hotkey(bind_id)  # Отвязываем старую горячую клавишу
                bind['hotkey'] = hotkey
                bind['text'] = text
                self.save_binds()
                self.bind_hotkey(bind_id, hotkey, text) # Привязываем новую горячую клавишу
                self.refresh_treeview()
                return

    def bind_hotkey(self, bind_id, hotkey, text):
        """Привязывает горячую клавишу."""
        try:
            def insert_text():
                try:
                    keyboard.write(text)
                except Exception as e:
                    print(f"Ошибка при вставке текста: {e}")
                    messagebox.showerror("Ошибка", f"Ошибка при вставке текста: {e}")

            keyboard.add_hotkey(hotkey, insert_text)
            self.hotkey_listeners[bind_id] = hotkey  # Сохраняем информацию о слушателе
            print(f"Горячая клавиша {hotkey} привязана к ID {bind_id}")

        except Exception as e:
            print(f"Ошибка при привязке горячей клавиши: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при привязке горячей клавиши: {e}")

    def unbind_hotkey(self, bind_id):
        """Отвязывает горячую клавишу."""
        if bind_id in self.hotkey_listeners:
            hotkey = self.hotkey_listeners[bind_id]
            try:
                keyboard.remove_hotkey(hotkey) #keyboard.unhook_all()
                del self.hotkey_listeners[bind_id]
                print(f"Горячая клавиша {hotkey} отвязана от ID {bind_id}")
            except Exception as e:
                print(f"Ошибка при отвязке горячей клавиши: {e}")
                messagebox.showerror("Ошибка", f"Ошибка при отвязке горячей клавиши: {e}")
        else:
            print(f"Горячая клавиша для ID {bind_id} не найдена.")

    def refresh_treeview(self):
        """Обновляет содержимое Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for bind in self.binds:
            self.tree.insert("", tk.END, values=(bind['id'], bind['hotkey'], bind['text']))

    def get_next_id(self):
         """Находит максимальный ID среди биндов и возвращает следующий."""
         if not self.binds:
             return 1  # Если нет биндов, начинаем с 1
         max_id = max(bind['id'] for bind in self.binds)
         return max_id + 1

    def on_closing(self):
        """Обработчик закрытия окна."""
        # Удаляем все горячие клавиши перед закрытием
        for bind_id in list(self.hotkey_listeners.keys()): # Используем list(), чтобы избежать изменения размера словаря во время итерации
            self.unbind_hotkey(bind_id)
        self.master.destroy()

# Function to simulate inserting text into the hotkey_entry
def insert_text_to_hotkey(entry, text):
    entry.insert(tk.END, text)

class AddBindWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent.master)
        self.parent = parent
        self.title("Добавить биндер")

        self.hotkey_label = tk.Label(self, text="Горячая клавиша:")
        self.hotkey_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.hotkey_entry = tk.Entry(self)
        self.hotkey_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Button to paste text from clipboard
        self.paste_hotkey_button = tk.Button(self, text="Вставить", command=lambda: insert_text_to_hotkey(self.hotkey_entry, self.clipboard_get()))
        self.paste_hotkey_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.text_label = tk.Label(self, text="Текст для вставки:")
        self.text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.text_entry = tk.Text(self, height=5, width=40)
        self.text_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Button to paste text from clipboard
        self.paste_text_button = tk.Button(self, text="Вставить", command=lambda: self.text_entry.insert(tk.END, self.clipboard_get()))
        self.paste_text_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.save_button = tk.Button(self, text="Сохранить", command=self.save_bind)
        self.save_button.grid(row=2, column=0, columnspan=3, pady=10)

    def save_bind(self):
        hotkey = self.hotkey_entry.get()
        text = self.text_entry.get("1.0", tk.END).strip()
        if hotkey and text:
            self.parent.add_bind(hotkey, text)
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")


class EditBindWindow(tk.Toplevel):
    def __init__(self, parent, bind_id):
        super().__init__(parent.master)
        self.parent = parent
        self.bind_id = bind_id
        self.title("Редактировать биндер")

        # Найти бинд по ID
        self.bind_data = next((bind for bind in self.parent.binds if bind['id'] == self.bind_id), None)

        if not self.bind_data:
            messagebox.showerror("Ошибка", "Бинд не найден.")
            self.destroy()
            return

        self.hotkey_label = tk.Label(self, text="Горячая клавиша:")
        self.hotkey_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.hotkey_entry = tk.Entry(self, textvariable=tk.StringVar(value=self.bind_data['hotkey']))
        self.hotkey_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Button to paste text from clipboard
        self.paste_hotkey_button = tk.Button(self, text="Вставить", command=lambda: insert_text_to_hotkey(self.hotkey_entry, self.clipboard_get()))
        self.paste_hotkey_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.text_label = tk.Label(self, text="Текст для вставки:")
        self.text_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.text_entry = tk.Text(self, height=5, width=40)
        self.text_entry.insert("1.0", self.bind_data['text'])
        self.text_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Button to paste text from clipboard
        self.paste_text_button = tk.Button(self, text="Вставить", command=lambda: self.text_entry.insert(tk.END, self.clipboard_get()))
        self.paste_text_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.save_button = tk.Button(self, text="Сохранить", command=self.save_bind)
        self.save_button.grid(row=2, column=0, columnspan=3, pady=10)

    def save_bind(self):
        hotkey = self.hotkey_entry.get()
        text = self.text_entry.get("1.0", tk.END).strip()
        if hotkey and text:
            self.parent.update_bind(self.bind_id, hotkey, text)
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BinderApp(root)
    root.mainloop()
