from tkinter import *
from tkinter import font
from mcquery import mcquery
import re
import threading
import time
from queue import Queue, Empty
import winsound

class App:
    def __init__(self):
        self.root = Tk()
        self.root.configure(bg="black")
        self.root.title("Get Data")
        self.root.geometry("1000x600")
        self.root.minsize(950, 420)

        # --- Шрифты для динамического изменения размера ---
        self.title_font = font.Font(family='Arial', size=12, weight='bold')
        self.button_font = font.Font(family='Arial', size=10, weight='bold')
        self.normal_font = font.Font(family='Arial', size=10)
        self.small_font = font.Font(family='Arial', size=9)
        self.small_button_font = font.Font(family='Arial', size=8, weight='bold')
        
        # Задержка для события изменения размера, чтобы избежать лишней нагрузки
        self._resize_job = None
        self.root.bind('<Configure>', self._on_resize)

        self.auto_search_thread = None
        self.auto_search_stop_event = None
        self.results_queue = Queue()
        self.server_vars = []
        self.sound_played_in_session = False
        self.continuous_sound_var = IntVar(value=0)

        self.root.after(100, self.process_queue)

    def _on_resize(self, event):
        """Обработчик изменения размера окна с задержкой."""
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, self.update_fonts)
        # Минимальные размеры для колонок
        min_widths = [160, 220, 220, 220]
        for i, w in enumerate(min_widths):
            self.root.grid_columnconfigure(i, minsize=w)

    def update_fonts(self):
        """Обновляет размеры шрифтов в зависимости от ширины окна."""
        current_width = self.root.winfo_width()
        # 1000px - эталонная ширина окна
        scale_factor = current_width / 1000.0
        
        # Устанавливаем минимальные размеры, чтобы текст оставался читаемым
        self.title_font.config(size=max(9, int(12 * scale_factor)))
        self.button_font.config(size=max(9, int(10 * scale_factor)))
        self.normal_font.config(size=max(9, int(10 * scale_factor)))
        self.small_font.config(size=max(9, int(9 * scale_factor)))
        self.small_button_font.config(size=max(8, int(8 * scale_factor)))

    def clean_minecraft_text(self, text):
        if not isinstance(text, str):
            text = str(text)
            
        # Заменяем все escape-последовательности на пустую строку
        text = text.encode('utf-8').decode('unicode_escape')
        
        # Удаляем все цветовые коды Minecraft
        text = re.sub(r'§[0-9a-fk-or]', '', text)
        
        # Удаляем все \x последовательности
        text = re.sub(r'\\x[a-f0-9]{2}', '', text)
        
        # Удаляем все \u последовательности
        text = re.sub(r'\\u[a-f0-9]{4}', '', text)
        
        # Удаляем все одиночные символы \x2
        text = re.sub(r'\\x2', '', text)
        
        # Удаляем все одиночные символы \x7
        text = re.sub(r'\\x7', '', text)
        
        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем пробелы в начале и конце
        text = text.strip()
        
        # Специальная обработка для названия сервера
        if "InMine" in text:
            # Сохраняем InMine.ru как есть
            text = re.sub(r'.*?(InMine\.ru).*', r'\1', text)
            # Добавляем номер сервера и версию
            server_num = re.search(r'#\d+', text)
            version = re.search(r'\d+\.\d+-\d+\.\d+', text)
            
            parts = ["InMine.ru"]
            if server_num:
                parts.append(server_num.group(0))
            if version:
                parts.append(f"| {version.group(0)}")
            
            text = ' '.join(parts)
        
        return text

    def update_text_widget(self, widget, text):
        """Вспомогательная функция для обновления текстовых полей"""
        widget.config(state='normal')  # Временно разрешаем редактирование
        widget.delete(0.0, END)
        widget.insert(END, text)
        widget.config(state='disabled')  # Возвращаем состояние только для чтения

    def filter_players(self, *args):
        # Получаем текст поиска
        search_text = self.search_var.get().lower()
        
        # Если текст поиска пустой или это placeholder, показываем всех игроков
        if not search_text or search_text == "поиск игроков":
            if hasattr(self, 'all_players'):
                self.players_label.config(text=f"Игроки онлайн ({len(self.all_players)})")
                self.update_text_widget(self.players_text, '\n'.join(self.all_players))
            return
        
        # Если есть сохраненный список игроков
        if hasattr(self, 'all_players'):
            # Фильтруем игроков по поисковому запросу
            filtered_players = [player for player in self.all_players 
                              if search_text in player.lower()]
            
            # Обновляем заголовок с количеством найденных игроков
            self.players_label.config(text=f"Игроки онлайн ({len(filtered_players)})")
            
            # Выводим отфильтрованных игроков
            self.update_text_widget(self.players_text, '\n'.join(filtered_players) if filtered_players else "Нет данных об игроках")

    def UI(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0, minsize=220)
        self.root.grid_columnconfigure(1, weight=1, minsize=220)
        self.root.grid_columnconfigure(2, weight=1, minsize=220)
        self.root.grid_columnconfigure(3, weight=1, minsize=220)

        # --- Серверы (левая панель) ---
        top_left_frame = Frame(self.root, bg="#111111", padx=1, pady=10, bd=0)
        top_left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        top_left_frame.grid_rowconfigure(0, weight=1)
        top_left_frame.grid_columnconfigure(0, weight=1)
        top_left_frame.grid_columnconfigure(1, weight=0)

        buttons_frame = Frame(top_left_frame, bg="#111111", highlightthickness=0)
        buttons_frame.grid(row=0, column=0, sticky='n', pady=(0, 0))
        # Не делаем grid_rowconfigure для каждой строки, чтобы кнопки не растягивались

        host = "inmine.ru"
        buttons = []
        for i in range(0, 6):
            server_num = i + 1
            port = 19131 if server_num == 1 else int(f"1913{server_num + 1}")
            button = Button(buttons_frame, 
                          text=f"InMine #{server_num}", 
                          command=lambda s=server_num, p=port: self.info(host, p),
                          bg="#E13131",
                          fg="white",
                          font=self.button_font,
                          relief=RAISED)
            button.grid(row=i, column=0, sticky='ew', padx=10, pady=3, ipadx=30)
            buttons.append(button)

        border_frame = Frame(top_left_frame, width=1, bg="white", highlightthickness=0)
        border_frame.grid(row=0, column=1, rowspan=3, sticky='ns')

        top_border = Frame(top_left_frame, height=1, bg="#999999", highlightthickness=0)
        top_border.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10,0))
        footer_label = Label(top_left_frame, text="InMine.ru", bg="#111111", fg="white", font=self.small_font, pady=10)
        footer_label.grid(row=2, column=0, columnspan=2, sticky='ew')

        # --- Информация о сервере ---
        info_frame = Frame(self.root, bg="#111111", highlightthickness=0)
        info_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        info_frame.grid_rowconfigure(1, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        info_label = Label(info_frame, text="Информация о сервере", bg="#111111", fg="white", font=self.title_font)
        info_label.grid(row=0, column=0, sticky='ew', pady=10)
        self.info_text = Text(info_frame, bg="#111111", fg="white", font=self.normal_font, state='disabled')
        self.info_text.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # --- Игроки онлайн ---
        players_frame = Frame(self.root, bg="#111111", highlightthickness=0)
        players_frame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)
        players_frame.grid_rowconfigure(3, weight=1)
        players_frame.grid_columnconfigure(0, weight=1)

        self.players_label = Label(players_frame, text="Игроки онлайн", bg="#111111", fg="white", font=self.title_font)
        self.players_label.grid(row=0, column=0, sticky='ew', pady=10)

        search_frame = Frame(players_frame, bg="#111111")
        search_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)

        self.search_var = StringVar()
        self.search_var.trace('w', self.filter_players)
        search_entry = Entry(search_frame, textvariable=self.search_var, bg="#222222", fg="white", insertbackground="white", font=self.normal_font)
        search_entry.grid(row=0, column=0, sticky='ew', padx=(5,2))
        search_entry.bind('<Control-Cyrillic_em>', self.paste_cyrillic)
        search_entry.bind('<Control-BackSpace>', self.ctrl_backspace)

        self.auto_search_button = Button(search_frame, text="Автопоиск", command=self.toggle_auto_search, bg="#4CAF50", fg="white", font=self.small_button_font, relief=RAISED)
        self.auto_search_button.grid(row=0, column=1, sticky='ew', padx=(2,5))

        def on_focus_in(event):
            if search_entry.get() == "Поиск игроков":
                search_entry.delete(0, END)
                search_entry.config(fg="white")
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Поиск игроков")
                search_entry.config(fg="gray")
                if hasattr(self, 'all_players'):
                    self.players_label.config(text=f"Игроки онлайн ({len(self.all_players)})")
                    self.update_text_widget(self.players_text, '\n'.join(self.all_players))
        search_entry.insert(0, "Поиск игроков")
        search_entry.config(fg="gray")
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)

        self.players_text = Text(players_frame, bg="#111111", fg="white", font=self.normal_font, state='disabled')
        self.players_text.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)

        # --- Автопоиск ---
        auto_search_frame = Frame(self.root, bg="#111111", highlightthickness=0)
        auto_search_frame.grid(row=0, column=3, sticky='nsew', padx=5, pady=5)
        auto_search_frame.grid_rowconfigure(6, weight=1)  # Поле результатов растягивается
        auto_search_frame.grid_columnconfigure(0, weight=1)

        auto_search_label = Label(auto_search_frame, text="Автопоиск по нику", bg="#111111", fg="white", font=self.title_font)
        auto_search_label.grid(row=0, column=0, sticky='ew', pady=10)

        checkbox_frame = Frame(auto_search_frame, bg="#111111")
        checkbox_frame.grid(row=1, column=0, sticky='ew', padx=10)
        checkbox_label = Label(checkbox_frame, text="Выберите серверы:", bg="#111111", fg="white", font=self.small_font)
        checkbox_label.pack(anchor='w')
        for i in range(6):
            var = IntVar(value=1)
            self.server_vars.append(var)
            chk = Checkbutton(checkbox_frame, text=f"InMine #{i + 1}", variable=var, bg="#111111", fg="white", selectcolor="black", activebackground="#111111", activeforeground="white", font=self.small_font, anchor='w')
            chk.pack(anchor='w', fill='x')

        refresh_frame = Frame(auto_search_frame, bg="#111111")
        refresh_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(5, 0))
        refresh_label = Label(refresh_frame, text="Обновлять каждые (сек):", bg="#111111", fg="white", font=self.small_font)
        refresh_label.pack(side=LEFT, padx=(0, 5))
        self.refresh_time_var = StringVar(value="5")
        refresh_entry = Entry(refresh_frame, textvariable=self.refresh_time_var, bg="#222222", fg="white", width=5, insertbackground="white", font=self.small_font)
        refresh_entry.pack(side=LEFT, fill='x', expand=True)

        continuous_sound_check = Checkbutton(auto_search_frame, text="Постоянный звук при нахождении", variable=self.continuous_sound_var, bg="#111111", fg="white", selectcolor="black", activebackground="#111111", activeforeground="white", font=self.small_font)
        continuous_sound_check.grid(row=3, column=0, sticky='ew', padx=10, pady=(5,0))

        separator = Frame(auto_search_frame, height=2, bg="#333333")
        separator.grid(row=4, column=0, sticky='ew', pady=10, padx=5)
        results_label = Label(auto_search_frame, text="Результаты поиска:", bg="#111111", fg="white", font=self.small_font)
        results_label.grid(row=5, column=0, sticky='ew', padx=10)
        self.auto_search_results_text = Text(auto_search_frame, bg="#222222", fg="white", font=self.normal_font, state='disabled', height=10)
        self.auto_search_results_text.grid(row=6, column=0, sticky='nsew', padx=10, pady=5)

    def info(self, host, port, timeout=10):
        if self.auto_search_thread and self.auto_search_thread.is_alive():
            self.toggle_auto_search()
            
        self.update_text_widget(self.info_text, "")  # Очищаем информацию
        self.update_text_widget(self.players_text, "")  # Очищаем список игроков
        self.search_var.set("")  # Очищаем поле поиска
        # Удаляем возврат placeholder текста и смену цвета
        # search_entry = self.root.focus_get()
        # if isinstance(search_entry, Entry):
        #     search_entry.delete(0, END)
        #     search_entry.insert(0, "Поиск игроков")
        #     search_entry.config(fg="gray")
        
        try:
            with mcquery(host, port=port, timeout=timeout) as data:
                # Очищаем hostname отдельно
                server_name = self.clean_minecraft_text(str(data.hostname))
                
                game_list = [
                    ("Название сервера:", server_name),
                    ("Тип игры:", self.clean_minecraft_text(str(data.game_type))),
                    ("IP сервера:", self.clean_minecraft_text(str(data.host_ip))),
                    ("Порт:", self.clean_minecraft_text(str(data.host_port))),
                    ("Карта:", self.clean_minecraft_text(str(data.map))),
                    ("Количество игроков:", f"{self.clean_minecraft_text(str(data.num_players))}/{self.clean_minecraft_text(str(data.max_players))}"),
                    ("Плагины:", self.clean_minecraft_text(str(data.plugins))),
                    ("Движок сервера:", self.clean_minecraft_text(str(data.server_engine))),
                    ("Версия:", self.clean_minecraft_text(str(data.version))),
                    ("Белый список:", self.clean_minecraft_text(str(data.whitelist)))
                ]
                
                # Формируем текст для вывода
                info_text = '\n'.join(f"{i}. {label} {value}" for i, (label, value) in enumerate(game_list, 1))
                self.update_text_widget(self.info_text, info_text)
                
                # Обновляем список игроков
                if hasattr(data, 'players'):
                    # Сохраняем полный список игроков
                    self.all_players = [self.clean_minecraft_text(str(player)) for player in data.players]
                    # Показываем всех игроков
                    self.players_label.config(text=f"Игроки онлайн ({len(self.all_players)})")
                    self.update_text_widget(self.players_text, '\n'.join(self.all_players))
                else:
                    self.all_players = []
                    self.players_label.config(text="Игроки онлайн (0)")
                    self.update_text_widget(self.players_text, "Нет данных об игроках")
        except Exception as e:
            self.all_players = []
            error_text = f"Ошибка подключения к серверу {host}:{port}\nОшибка: {str(e)}"
            self.update_text_widget(self.info_text, error_text)
            self.players_label.config(text="Игроки онлайн (0)")
            self.update_text_widget(self.players_text, "Нет данных об игроках")

    def ctrl_backspace(self, event):
        """Удаляет слово слева от курсора по Ctrl+Backspace."""
        widget = event.widget
        
        # Если поле пустое или курсор в начале, ничего не делаем
        if not widget.get() or widget.index(INSERT) == 0:
            return "break"

        cursor_pos = widget.index(INSERT)
        text = widget.get()[:cursor_pos]

        # Ищем позицию для удаления
        pos = len(text) - 1
        # Пропускаем пробелы в конце
        while pos >= 0 and text[pos].isspace():
            pos -= 1
        # Идем до следующего пробела или начала строки
        while pos >= 0 and not text[pos].isspace():
            pos -= 1
        
        delete_from = pos + 1
        
        widget.delete(delete_from, cursor_pos)
        
        return "break" # Предотвращаем стандартное поведение

    def paste_cyrillic(self, event):
        """Ручная обработка вставки для русской раскладки (Ctrl+м)."""
        try:
            text = event.widget.clipboard_get()
            event.widget.insert('insert', text)
        except TclError:
            # Буфер обмена пуст или содержит не текст
            pass
        return "break"

    def toggle_auto_search(self):
        if self.auto_search_thread and self.auto_search_thread.is_alive():
            if self.auto_search_stop_event:
                self.auto_search_stop_event.set()
            self.auto_search_button.config(text="Автопоиск")
            self.update_text_widget(self.auto_search_results_text, "Автопоиск остановлен.")
        else:
            nickname = self.search_var.get().strip()
            if not nickname or nickname == "Поиск игроков":
                self.update_text_widget(self.auto_search_results_text, "Введите ник для поиска.")
                return

            try:
                refresh_seconds = int(self.refresh_time_var.get())
                if refresh_seconds < 1:
                    refresh_seconds = 1 # Минимальное время обновления
            except ValueError:
                refresh_seconds = 5 # Значение по умолчанию

            self.sound_played_in_session = False  # Сбрасываем флаг звука для нового поиска
            self.auto_search_button.config(text="Стоп")
            self.update_text_widget(self.auto_search_results_text, "Запуск автопоиска...")

            self.auto_search_stop_event = threading.Event()
            self.auto_search_thread = threading.Thread(target=self.run_auto_search, args=(nickname, self.auto_search_stop_event, refresh_seconds), daemon=True)
            self.auto_search_thread.start()

    def run_auto_search(self, nickname, stop_event, refresh_seconds):
        host = "inmine.ru"
        
        while not stop_event.is_set():
            servers_to_check = []
            for i, var in enumerate(self.server_vars):
                if var.get() == 1:
                    server_num = i + 1
                    port = 19131 if server_num == 1 else int(f"1913{server_num + 1}")
                    servers_to_check.append({'num': server_num, 'port': port})

            if not servers_to_check:
                self.results_queue.put("Не выбрано ни одного сервера для поиска.")
                if stop_event.wait(refresh_seconds): break
                continue

            found_on = []
            threads = []
            search_results = Queue()

            def search_on_server(server):
                try:
                    with mcquery(host, port=server['port'], timeout=2) as data:
                        if hasattr(data, 'players'):
                            players = [self.clean_minecraft_text(str(p)) for p in data.players]
                            if any(nickname.lower() in player.lower() for player in players):
                                search_results.put(f"InMine #{server['num']}")
                except Exception:
                    pass # Ignore connection errors

            for server in servers_to_check:
                thread = threading.Thread(target=search_on_server, args=(server,), daemon=True)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            while not search_results.empty():
                found_on.append(search_results.get())

            if found_on:
                if self.continuous_sound_var.get() == 1:
                    winsound.Beep(1000, 300)  # Частота 1000 Гц, длительность 200 мс
                else:
                    if not self.sound_played_in_session:
                        winsound.Beep(1000, 300)  # Частота 1000 Гц, длительность 200 мс
                        self.sound_played_in_session = True
                
                result_message = f"Игрок '{nickname}' найден на:\n" + "\n".join(sorted(found_on))
            else:
                self.sound_played_in_session = False # Сбрасываем флаг, если игрок не найден
                result_message = f"Игрок '{nickname}' не найден."
            
            result_message += f"\n\nОбновлено: {time.strftime('%H:%M:%S')}"
            
            if not stop_event.is_set():
                self.results_queue.put(result_message)
            
            if stop_event.wait(refresh_seconds):
                break

    def process_queue(self):
        try:
            while True:
                message = self.results_queue.get_nowait()
                self.update_text_widget(self.auto_search_results_text, message)
        except Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)


if __name__ == "__main__":
    app = App()
    app.UI()
    app.root.mainloop()