import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import sys

class TextSenderApp:
    def __init__(self, root):
        self.root = root
        root.title("Text Sender for Messengers")
        root.geometry("500x450")

        # Переменная для контроля выполнения потока
        self.is_running = False
        self.send_thread = None

        # Создание и размещение виджетов
        self.create_widgets()
        self.setup_clipboard_support()

    def create_widgets(self):
        # Метка и поле для ввода текста
        text_label = ttk.Label(self.root, text="Введите текст для отправки:")
        text_label.pack(pady=(10, 5))

        self.text_field = tk.Text(self.root, height=8, width=60)
        self.text_field.pack(pady=5, padx=10)
        
        # Добавляем контекстное меню для текстового поля
        self.setup_context_menu(self.text_field)
        
        # Привязываем горячие клавиши к текстовому полю
        self.bind_shortcuts(self.text_field)
        
        # Фрейм для задержек
        delays_frame = ttk.Frame(self.root)
        delays_frame.pack(pady=10, fill='x', padx=10)

        # Задержка перед стартом
        ttk.Label(delays_frame, text="Задержка перед стартом (сек):").grid(row=0, column=0, sticky='w', padx=5)
        self.delay_before_start_entry = ttk.Entry(delays_frame, width=10)
        self.delay_before_start_entry.insert(0, "3")
        self.delay_before_start_entry.grid(row=0, column=1, padx=5, sticky='w')

        # Задержка между словами
        ttk.Label(delays_frame, text="Задержка между словами (сек):").grid(row=1, column=0, sticky='w', padx=5)
        self.delay_between_words_entry = ttk.Entry(delays_frame, width=10)
        self.delay_between_words_entry.insert(0, "0.5")
        self.delay_between_words_entry.grid(row=1, column=1, padx=5, sticky='w')

        # Количество повторов
        ttk.Label(delays_frame, text="Количество повторов:").grid(row=2, column=0, sticky='w', padx=5)
        self.repeats_entry = ttk.Entry(delays_frame, width=10)
        self.repeats_entry.insert(0, "1")
        self.repeats_entry.grid(row=2, column=1, padx=5, sticky='w')

        # Бесконечный повтор
        self.infinite_repeat_var = tk.BooleanVar()
        self.infinite_repeat_check = ttk.Checkbutton(delays_frame, text="Бесконечно", variable=self.infinite_repeat_var)
        self.infinite_repeat_check.grid(row=2, column=2, padx=10)

        # Фрейм для кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        # Кнопка Старт
        self.start_button = ttk.Button(button_frame, text="Старт", command=self.start_sending)
        self.start_button.pack(side='left', padx=10)

        # Кнопка Стоп
        self.stop_button = ttk.Button(button_frame, text="Стоп", state='disabled', command=self.stop_sending)
        self.stop_button.pack(side='left', padx=10)

        # Информационное сообщение
        info_label = ttk.Label(self.root, text="Перед стартом переключитесь в окно мессенджера!", foreground="gray")
        info_label.pack(pady=(20, 5))

    def setup_context_menu(self, widget):
        # Создаем контекстное меню
        context_menu = tk.Menu(widget, tearoff=0)
        context_menu.add_command(label="Вырезать", command=lambda: self.cut_text(widget))
        context_menu.add_command(label="Копировать", command=lambda: self.copy_text(widget))
        context_menu.add_command(label="Вставить", command=lambda: self.paste_text(widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выделить все", command=lambda: self.select_all_text(widget))
        
        # Привязываем меню к правому клику
        widget.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu))

    def bind_shortcuts(self, widget):
        """Привязываем горячие клавиши к виджету"""
        # Привязываем комбинации клавиш с явным возвратом "break" чтобы предотвратить стандартную обработку
        widget.bind("<Control-a>", lambda event: self.select_all_text(widget))
        widget.bind("<Control-A>", lambda event: self.select_all_text(widget))  # Для Caps Lock
        widget.bind("<Control-c>", lambda event: self.copy_text(widget))
        widget.bind("<Control-C>", lambda event: self.copy_text(widget))
        widget.bind("<Control-v>", lambda event: self.paste_text(widget))
        widget.bind("<Control-V>", lambda event: self.paste_text(widget))
        widget.bind("<Control-x>", lambda event: self.cut_text(widget))
        widget.bind("<Control-X>", lambda event: self.cut_text(widget))
        
        # Устанавливаем фокус на текстовое поле при запуске
        widget.focus_set()

    def setup_clipboard_support(self):
        # Инициализация буфера обмена
        try:
            self.root.clipboard_get()
        except:
            pass  # Буфер обмена пуст

    def show_context_menu(self, event, menu):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def cut_text(self, widget):
        try:
            widget.event_generate("<<Cut>>")
            return "break"  # Предотвращаем дальнейшую обработку события
        except:
            pass

    def copy_text(self, widget):
        try:
            widget.event_generate("<<Copy>>")
            return "break"  # Предотвращаем дальнейшую обработку события
        except:
            pass

    def paste_text(self, widget):
        try:
            widget.event_generate("<<Paste>>")
            return "break"  # Предотвращаем дальнейшую обработку события
        except:
            # Резервный метод, если стандартный не работает
            try:
                clipboard_text = self.root.clipboard_get()
                widget.insert(tk.INSERT, clipboard_text)
                return "break"  # Предотвращаем дальнейшую обработку события
            except:
                pass

    def select_all_text(self, widget):
        """Выделяет весь текст в виджете"""
        try:
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
            return "break"  # Предотвращаем дальнейшую обработку события
        except:
            pass

    def start_sending(self):
        try:
            delay_before_start = float(self.delay_before_start_entry.get())
            delay_between_words = float(self.delay_between_words_entry.get())
            
            if not self.infinite_repeat_var.get():
                repeats = int(self.repeats_entry.get())
                if repeats < 1:
                    raise ValueError
            else:
                repeats = float('inf')

            text = self.text_field.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Предупреждение", "Поле текста не может быть пустым!")
                return

        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных числовых значений!")
            return

        self.toggle_ui_state('disabled')
        self.is_running = True

        self.send_thread = threading.Thread(target=self.sending_thread, args=(text, delay_before_start, delay_between_words, repeats))
        self.send_thread.daemon = True
        self.send_thread.start()

    def sending_thread(self, text, delay_before_start, delay_between_words, repeats):
        words = text.split()
        time.sleep(delay_before_start)

        count = 0
        while count < repeats and self.is_running:
            for word in words:
                if not self.is_running:
                    break
                
                # Добавляем небольшую задержку перед вводом каждого слова
                time.sleep(0.1)
                keyboard.write(word)
                time.sleep(0.1)
                keyboard.press_and_release('enter')
                time.sleep(delay_between_words)

            count += 1

        self.root.after(0, self.on_sending_finished)

    def stop_sending(self):
        self.is_running = False

    def on_sending_finished(self):
        self.is_running = False
        self.toggle_ui_state('normal')

    def toggle_ui_state(self, state):
        widgets = [
            self.text_field, 
            self.delay_before_start_entry, 
            self.delay_between_words_entry, 
            self.repeats_entry,
            self.infinite_repeat_check,
            self.start_button
        ]
        
        for widget in widgets:
            widget.config(state=state)
            
        self.stop_button.config(state='normal' if state == 'disabled' else 'disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = TextSenderApp(root)
    root.mainloop()