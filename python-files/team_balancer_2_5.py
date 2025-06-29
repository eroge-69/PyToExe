import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import itertools
import json
import os

class TeamBalancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Team Balancer PRO v2.5")
        self.players = []  # Текущие игроки для балансировки
        self.saved_players = []  # Сохраненный список игроков
        self.team_a = []
        self.team_b = []
        self.rating_diff_limit = None
        self.special_diff_limit = None
        self.use_rating_limit = False
        self.use_special_limit = False
        self.manage_dialog = None  # Ссылка на окно управления базой
        self.last_search_query = ""
        self.last_sorted_column = None
        self.last_sort_state = None
        self.sort_state_a = None
        self.sort_state_b = None
        
        # Загрузка сохраненных игроков
        self.load_players()
        
        # Настройка тегов для Treeview
        self.style = ttk.Style()
        self.create_teams_interface() # This now calls apply_entry_bindings internally
        
        # Инициализация состояний сортировки
        self.sort_states = {
            'name': {'type': None, 'direction': None},
            'rating': {'type': None, 'direction': None},
            'special': {'type': None, 'direction': None}
        }
        
        # Привязка события перемещения окна
        self.root.bind("<Configure>", self.on_root_move)

    def apply_entry_bindings(self, widget):
        """
        Применяет стандартные бинды для полей ввода (Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X).
        Использует event.keycode для устойчивости к раскладкам клавиатуры.
        """
        def handle_control_keys_with_keycode(event):
            # Отладочный вывод для проверки keysym и keycode
            # print(f"Event: {event.type}, Keysym: {event.keysym}, Keycode: {event.keycode}")

            # Ctrl+A (Select All) - Keycode для 'A' (или 'a') всегда 65
            if event.keycode == 65:
                widget.selection_range(0, tk.END)
                return "break" # Предотвратить дальнейшую обработку Tkinter

            # Ctrl+C (Copy) - Keycode для 'C' (или 'c') всегда 67
            elif event.keycode == 67 and event.keysym != 'c': # Дополнительная проверка на keysym для избежания дублирования в англ. раскладке
                widget.event_generate('<<Copy>>')
                return "break"

            # Ctrl+V (Paste) - Keycode для 'V' (или 'v') всегда 86
            elif event.keycode == 86 and event.keysym != 'v': # Дополнительная проверка на keysym
                widget.event_generate('<<Paste>>')
                return "break"

            # Ctrl+X (Cut) - Keycode для 'X' (или 'x') всегда 88
            elif event.keycode == 88 and event.keysym != 'x': # Дополнительная проверка на keysym
                widget.event_generate('<<Cut>>')
                return "break"

        # Привязываем к общему событию нажатия клавиши с Ctrl
        # Это событие будет срабатывать для всех полей ввода, к которым применяется apply_entry_bindings
        widget.bind("<Control-Key>", handle_control_keys_with_keycode)
    def player_name_exists(self, name, exclude_player=None):
        """Проверяет, существует ли игрок с таким именем в базе"""
        for player in self.saved_players:
            if exclude_player and player is exclude_player:
                continue  # Пропускаем проверку самого игрока при редактировании
            if player['name'].lower() == name.lower():
                return True
        return False

    def on_root_move(self, event):
        """Обработчик перемещения основного окна"""
        if self.manage_dialog and self.manage_dialog.winfo_exists():
            # Обновляем позицию дочернего окна
            self.position_manage_dialog()

    def position_manage_dialog(self):
        """Позиционирование окна управления справа от основного окна"""
        if not self.manage_dialog:
            return
            
        # Обновляем геометрию основного окна
        self.root.update_idletasks()
        
        # Получаем позицию и размеры основного окна
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        
        # Устанавливаем позицию окна управления
        self.manage_dialog.geometry(f"+{root_x + root_width + 10}+{root_y}")
        
        # Поднимаем окно управления на передний план
        self.manage_dialog.lift()

    def load_players(self):
        """Загрузка сохраненных игроков из файла"""
        try:
            if os.path.exists("players.json"):
                with open("players.json", "r", encoding="utf-8") as f:
                    self.saved_players = json.load(f)
            else:
                self.saved_players = []
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить базу игроков: {str(e)}")
            self.saved_players = []
    
    def save_players(self):
        """Сохранение игроков в файл"""
        try:
            with open("players.json", "w", encoding="utf-8") as f:
                json.dump(self.saved_players, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить базу игроков: {str(e)}")
            
    def get_special_style(self, value):
        if 1 <= value <= 4999:
            return "red"
        elif 5000 <= value <= 7499:
            return "orange"
        elif 7500 <= value <= 12000:
            return "green"
        return ""

    def on_treeview_click(self, event):
        widget = event.widget
        item = widget.identify_row(event.y)
        region = widget.identify_region(event.x, event.y)
        if region == "nothing" or not item:
            widget.selection_remove(widget.selection())

    def toggle_manage_dialog(self):
        """Переключение состояния окна управления базой игроков"""
        if self.manage_dialog and self.manage_dialog.winfo_exists():
            self.close_manage_dialog()
        else:
            self.manage_saved_players()

    def close_manage_dialog(self):
        """Закрытие окна управления базой игроков"""
        if self.manage_dialog:
            self.manage_dialog.destroy()
            self.manage_dialog = None
            # Сбрасываем состояния сортировки при закрытии окна
            self.sort_states = {
                'name': {'type': None, 'direction': None},
                'rating': {'type': None, 'direction': None},
                'special': {'type': None, 'direction': None}
            }

    def manage_saved_players(self):
        """Окно управления сохраненными игроками"""
        self.manage_dialog = tk.Toplevel(self.root)
        self.manage_dialog.title("Управление базой игроков")
        self.manage_dialog.geometry("600x450")  # Увеличим высоту для поля поиска
        self.manage_dialog.transient(self.root)  # Делаем окно дочерним
        
        # При закрытии окна
        self.manage_dialog.protocol("WM_DELETE_WINDOW", self.close_manage_dialog)
        
        # Позиционируем окно справа от основного
        self.position_manage_dialog()
        
        # Фрейм для элементов управления
        control_frame = ttk.Frame(self.manage_dialog)
        control_frame.pack(pady=10, fill='x')
        
        # Кнопки управления
        ttk.Button(control_frame, text="Добавить", command=self.add_player_dialog).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_saved_player).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Перенести в балансировку", command=self.add_to_balance).pack(side='left', padx=5)
        
        # Фрейм для поиска
        search_frame = ttk.Frame(self.manage_dialog)
        search_frame.pack(padx=10, pady=(0, 10), fill='x')
        
        ttk.Label(search_frame, text="Поиск:").pack(side='left', padx=(0, 5))
        
        # Поле для поиска
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<KeyRelease>', self.filter_players)
        
        # Применяем привязки к полю поиска
        self.apply_entry_bindings(search_entry) # <--- Apply bindings here
        # Кнопка очистки поиска
        ttk.Button(search_frame, text="×", width=2, command=self.clear_search).pack(side='left', padx=(5, 0))
        
        # Таблица игроков
        self.saved_tree = ttk.Treeview(self.manage_dialog, columns=('name', 'rating', 'special'), show='headings')
        
        # Настройка заголовков с привязкой сортировки
        self.saved_tree.heading('name', text='Имя', command=lambda: self.sort_saved_tree('name'))
        self.saved_tree.heading('rating', text='Рейтинг', command=lambda: self.sort_saved_tree('rating'))
        self.saved_tree.heading('special', text='Порядочность', command=lambda: self.sort_saved_tree('special'))
        
        self.saved_tree.column('name', width=200)
        self.saved_tree.column('rating', width=100)
        self.saved_tree.column('special', width=100)
        
        # Настройка цветов
        self.saved_tree.tag_configure('red', background='#ff4a4a')
        self.saved_tree.tag_configure('orange', background='#b88d3b')
        self.saved_tree.tag_configure('green', background='#46bc60')
        
        # Заполнение таблицы
        self.update_saved_tree()
        
        scrollbar = ttk.Scrollbar(self.manage_dialog, orient="vertical", command=self.saved_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.saved_tree.configure(yscrollcommand=scrollbar.set)
        self.saved_tree.pack(fill='both', expand=True, padx=10, pady=(0, 5))
        
        # Обработка кликов
        self.saved_tree.bind('<Button-1>', self.on_treeview_click)
        self.saved_tree.bind('<Double-1>', lambda e: self.edit_saved_player())
    
    def filter_players(self, event=None):
        """Фильтрация игроков по введенному тексту"""
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
        
        self.last_search_query = self.search_var.get().strip().lower()
        self.update_saved_tree()  # Обновляем дерево с учетом фильтра
    
    def clear_search(self):
        """Очистка поля поиска и восстановление списка"""
        # Проверяем существование виджета
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        self.search_var.set("")
        self.saved_tree.yview_moveto(0) # Сбрасываем прокрутку
        self.update_saved_tree()  # Обновляем вместо вызова filter_players
    
    def sort_saved_tree(self, column):
        """Расширенная сортировка с несколькими режимами"""
        # Проверяем существование виджета
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        self.last_sorted_column = column    
        # Определяем циклы сортировки для разных колонок
        if column == 'name':
            # Цикл для колонки "Имя"
            states_cycle = [
                {'type': 'alphabet', 'direction': 'asc'},    # A→Z
                {'type': 'alphabet', 'direction': 'desc'},   # Z→A
                {'type': 'length', 'direction': 'asc'},      # Короткие→Длинные
                {'type': 'length', 'direction': 'desc'},     # Длинные→Короткие
                None                                         # Сброс
            ]
        else:
            # Цикл для числовых колонок
            states_cycle = [
                {'type': 'numeric', 'direction': 'asc'},     # По возрастанию
                {'type': 'numeric', 'direction': 'desc'},    # По убыванию
                None                                         # Сброс
            ]
        
        # Находим текущую позицию в цикле
        current_state = self.sort_states[column]
        try:
            current_index = states_cycle.index(current_state)
        except ValueError:
            current_index = -1
        
        # Переходим к следующему состоянию
        next_index = (current_index + 1) % len(states_cycle)
        new_state = states_cycle[next_index]
        self.sort_states[column] = new_state
        
        # Обновляем заголовки
        self.update_column_headers()
        
        # Применяем сортировку
        if new_state is None:
            # При сбросе сортировки просто обновляем список
            self.update_saved_tree()
        else:
            self.apply_sorting(column, new_state)
            
    def update_column_headers(self):
        """Обновление заголовков с индикаторами сортировки"""
        # Проверяем существование виджета
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        columns = {
            'name': 'Имя',
            'rating': 'Рейтинг',
            'special': 'Порядочность'
        }
        
        for col, text in columns.items():
            state = self.sort_states[col]
            header_text = text
            
            if state:
                # Добавляем индикатор направления
                indicator = " ▲" if state['direction'] == 'asc' else " ▼"
                header_text += indicator
                
                # Добавляем тип сортировки для колонки "Имя"
                if col == 'name':
                    if state['type'] == 'alphabet':
                        header_text += " (A-Я)" if state['direction'] == 'asc' else " (Я-A)"
                    elif state['type'] == 'length':
                        header_text += " (короткие)" if state['direction'] == 'asc' else " (длинные)"
            
            self.saved_tree.heading(col, text=header_text)
    
    def apply_sorting(self, column, state):
        """Применение выбранной сортировки"""
        # Проверяем существование виджета
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        items = []
        for item in self.saved_tree.get_children(''):
            values = self.saved_tree.item(item, 'values')
            items.append((values, item))
        
        # Определяем функцию сравнения в зависимости от типа сортировки
        if state['type'] == 'alphabet':
            # Алфавитная сортировка (учитываем русский и английский)
            items.sort(key=lambda x: x[0][0].lower(), reverse=(state['direction'] == 'desc'))
        elif state['type'] == 'length':
            # Сортировка по длине имени
            items.sort(key=lambda x: len(x[0][0]), reverse=(state['direction'] == 'desc'))
        else:  # numeric
            # Определяем индекс колонки
            col_index = {'rating': 1, 'special': 2}.get(column)
            if col_index is not None:
                # Числовая сортировка
                items.sort(key=lambda x: int(x[0][col_index]), reverse=(state['direction'] == 'desc'))
        
        # Перемещаем элементы в отсортированном порядке
        for index, (_, item) in enumerate(items):
            self.saved_tree.move(item, '', index)
    
    def update_saved_tree(self):
        """Обновление списка с сохранением сортировки и поиска"""
        if hasattr(self, 'saved_tree') and self.saved_tree.winfo_exists():
            # Сохраняем позицию прокрутки
            scroll_position = self.saved_tree.yview()
            
            # Сохраняем текущее состояние перед обновлением
            current_search = self.search_var.get()
            last_sorted_col = self.last_sorted_column
            last_sort_state = self.sort_states.get(last_sorted_col) if last_sorted_col else None
            
            # Обновляем заголовки
            self.update_column_headers()
            
            # Очищаем текущее содержимое
            self.saved_tree.delete(*self.saved_tree.get_children())
            
            # Добавляем игроков с фильтрацией
            search_text = current_search.strip().lower()
            for idx, player in enumerate(self.saved_players):
                # Применяем фильтр поиска
                if search_text and search_text not in player['name'].lower():
                    continue
                    
                style = self.get_special_style(player['special'])
                self.saved_tree.insert('', 'end', iid=f"{idx}_{player['name']}",
                                      values=(player['name'], player['rating'], player['special']),
                                      tags=(style,))
            
            # Восстанавливаем состояние сортировки
            if last_sorted_col and last_sort_state:
                self.sort_states[last_sorted_col] = last_sort_state
                self.last_sorted_column = last_sorted_col
                self.apply_sorting(last_sorted_col, last_sort_state)
                
            # Восстанавливаем позицию прокрутки
            self.saved_tree.yview_moveto(scroll_position[0])
    
    def add_player_dialog(self):
        """Диалог добавления нового игрока в базу"""
        # Проверяем существование окна управления
        if not self.manage_dialog or not self.manage_dialog.winfo_exists():
            return
            
        dialog = tk.Toplevel(self.manage_dialog)
        dialog.title("Добавить игрока")
        dialog.transient(self.manage_dialog)
        dialog.grab_set()

        # Bug fix: Handle WM_DELETE_WINDOW and minimize/restore events for the dialog
        def on_dialog_close():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass # Already released or destroyed
            dialog.destroy()

        def on_dialog_iconify(event):
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            
        def on_dialog_deiconify(event):
            dialog.grab_set()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Unmap>", on_dialog_iconify)
        dialog.bind("<Map>", on_dialog_deiconify)
        
        entries = []
        labels = ['Имя:', 'Рейтинг (1-17000):', 'Порядочность (1-12000):']
        for i, text in enumerate(labels):
            ttk.Label(dialog, text=text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=20)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            self.apply_entry_bindings(entry) # <--- Apply bindings here
        def add():
            try:
                name = entries[0].get().strip()
                rating = int(entries[1].get())
                special = int(entries[2].get())
                
                if not name:
                    raise ValueError("Введите имя игрока")
                if not 1 <= rating <= 17000:
                    raise ValueError("Рейтинг должен быть от 1 до 17000")
                if not 1 <= special <= 12000:
                    raise ValueError("Порядочность должна быть от 1 до 12000")
                
                # Проверка на уникальность имени
                if self.player_name_exists(name):
                    raise ValueError("Игрок с таким именем уже существует в базе")
                    
                new_player = {
                    'name': name,
                    'rating': rating,
                    'special': special
                }
                
                self.saved_players.append(new_player)
                self.save_players()
                self.update_saved_tree()  # Обновляем список
                on_dialog_close()
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Добавить", command=add).grid(row=3, columnspan=2, pady=10)

    def edit_saved_player(self):
        """Редактирование сохраненного игрока"""
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        selected = self.saved_tree.selection()
        if not selected:
            return
            
        iid = selected[0]
        # Извлекаем индекс из идентификатора
        try:
            idx = int(iid.split('_')[0])
        except:
            messagebox.showerror("Ошибка", "Неверный идентификатор игрока")
            return
            
        if idx < len(self.saved_players):
            player = self.saved_players[idx]
        else:
            messagebox.showerror("Ошибка", "Игрок не найден в базе!")
            return
    
        # Создаем диалоговое окно для редактирования
        dialog = tk.Toplevel(self.manage_dialog)
        dialog.title("Редактирование игрока")
        dialog.transient(self.manage_dialog)
        dialog.grab_set()

        # Bug fix: Handle WM_DELETE_WINDOW and minimize/restore events for the dialog
        def on_dialog_close():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            dialog.destroy()

        def on_dialog_iconify(event):
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            
        def on_dialog_deiconify(event):
            dialog.grab_set()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Unmap>", on_dialog_iconify)
        dialog.bind("<Map>", on_dialog_deiconify)
        
        entries = []
        fields = [
            ('Имя:', player['name']),
            ('Рейтинг:', player['rating']),
            ('Порядочность:', player['special'])
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=20)
            entry.insert(0, str(value))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            self.apply_entry_bindings(entry) # <--- Apply bindings here
    
        def save():
            try:
                name = entries[0].get().strip()
                rating = int(entries[1].get())
                special = int(entries[2].get())
                
                if not name:
                    raise ValueError("Введите имя игрока")
                if not 1 <= rating <= 17000:
                    raise ValueError("Рейтинг должен быть от 1 до 17000")
                if not 1 <= special <= 12000:
                    raise ValueError("Порядочность должна быть от 1 до 12000")
                    
                # Проверка на уникальность имени (исключая текущего игрока)
                if name != player['name'] and self.player_name_exists(name, exclude_player=player):
                    raise ValueError("Игрок с таким именем уже существует в базе")
                    
                # Обновляем данные
                player['name'] = name
                player['rating'] = rating
                player['special'] = special
                
                self.save_players()
                
                # Сохраняем текущий поиск
                current_search = self.search_var.get()
                
                # Обновляем с сохранением сортировки
                self.update_saved_tree()
                self.filter_players()
                
                # Восстанавливаем поиск
                self.search_var.set(current_search)
                
                on_dialog_close()
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e), parent=dialog)
    
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, columnspan=2, pady=10)

    def delete_saved_player(self):
        """Удаление сохраненного игрока"""
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        selected = self.saved_tree.selection()
        if not selected:
            return
        
        # Сохраняем текущий поисковый запрос
        current_search = self.search_var.get()
        
        # Собираем индексы для удаления
        indices_to_delete = []
        for iid in selected:
            idx = int(iid.split('_')[0])
            indices_to_delete.append(idx)
        
        # Сортируем в обратном порядке для безопасного удаления
        indices_to_delete.sort(reverse=True)
        
        for idx in indices_to_delete:
            if idx < len(self.saved_players):
                del self.saved_players[idx]
        
        self.save_players()
        
        # Обновляем список с сохранением сортировки и поиска
        self.update_saved_tree()

    def add_to_balance(self):
        """Добавление игроков в текущий баланс"""
        if not hasattr(self, 'saved_tree') or not self.saved_tree.winfo_exists():
            return
            
        selected = self.saved_tree.selection()
        if not selected:
            return
        
        # Сохраняем текущий поиск
        current_search = self.search_var.get()
        
        # Используем текущие команды
        current_team_a = self.team_a.copy()
        current_team_b = self.team_b.copy()
        
        for iid in selected:
            try:
                idx = int(iid.split('_')[0])
                if idx < len(self.saved_players):
                    player = self.saved_players[idx]
                    
                    # Создаем копию игрока для текущей сессии
                    new_player = {
                        'name': player['name'],
                        'rating': player['rating'],
                        'special': player['special'],
                        'fixed': False
                    }
                    
                    # Проверяем, не добавлен ли уже игрок
                    if not any(p['name'] == new_player['name'] for p in self.players):
                        self.players.append(new_player)
                        
                        # Распределяем в команду с меньшим количеством игроков
                        if len(current_team_a) <= len(current_team_b):
                            current_team_a.append(new_player)
                        else:
                            current_team_b.append(new_player)
            except:
                continue
        
        # Обновляем команды без балансировки
        self.team_a = current_team_a
        self.team_b = current_team_b
        self.update_saved_tree()
        self.update_display()

    def create_teams_interface(self):
        # Основной контейнер
        self.teams_frame = ttk.Frame(self.root)
        self.teams_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Панель управления
        self.controls_top = ttk.Frame(self.root) # Renamed to avoid conflict with self.controls below
        self.controls_top.pack(pady=10, fill='x')

        # Фрейм для ограничений
        self.limit_controls = ttk.Frame(self.controls_top) # Changed parent to controls_top
        self.limit_controls.pack(side='left', padx=15)

        # Ограничение рейтинга
        self.rating_limit_var = tk.BooleanVar()
        self.rating_limit_entry = ttk.Entry(self.limit_controls, width=7)
        ttk.Checkbutton(self.limit_controls, 
                      text="Макс. Δ рейтинга:", 
                      variable=self.rating_limit_var).pack(side='left')
        self.rating_limit_entry.pack(side='left', padx=5)
        self.apply_entry_bindings(self.rating_limit_entry) # <--- Apply bindings here

        # Ограничение порядочности
        self.special_limit_var = tk.BooleanVar()
        self.special_limit_entry = ttk.Entry(self.limit_controls, width=7)
        ttk.Checkbutton(self.limit_controls, 
                      text="Макс. Δ порядочности:", 
                      variable=self.special_limit_var).pack(side='left', padx=10)
        self.special_limit_entry.pack(side='left')
        self.apply_entry_bindings(self.special_limit_entry) # <--- Apply bindings here


        # Команда A
        self.team_a_frame = ttk.LabelFrame(self.teams_frame, text="Команда A")
        self.team_a_frame.pack(side='left', padx=5, pady=5, fill='both', expand=True)
        
        # Список игроков команды A
        self.list_a = ttk.Treeview(self.team_a_frame, columns=('info',), show='headings')
        self.list_a.heading('info', text='Игроки команды A', command=self.sort_team_a)
        self.list_a.column('info', width=250)
        self.list_a.bind('<Button-1>', self.on_treeview_click)
    
        # Настройка цветов
        self.list_a.tag_configure('red', background='#ff4a4a')
        self.list_a.tag_configure('orange', background='#b88d3b')
        self.list_a.tag_configure('green', background='#46bc60')
        self.list_a.pack(padx=5, pady=5, fill='both', expand=True)
        self.list_a.bind('<Double-1>', lambda e: self.edit_player('A'))
        
        # Суммы для команды A
        self.sum_a_frame = ttk.Frame(self.team_a_frame)
        self.sum_a_frame.pack(pady=5, fill='x')
        
        ttk.Label(self.sum_a_frame, text="Сумма рейтинга:", width=16).pack(side='left')
        self.sum_rating_a = ttk.Label(self.sum_a_frame, text="0", width=10)
        self.sum_rating_a.pack(side='left', padx=5)
        
        ttk.Label(self.sum_a_frame, text="Сумма порядочности:", width=21).pack(side='left')
        self.sum_special_a = ttk.Label(self.sum_a_frame, text="0", width=10)
        self.sum_special_a.pack(side='left')

        # Команда B
        self.team_b_frame = ttk.LabelFrame(self.teams_frame, text="Команда B")
        self.team_b_frame.pack(side='right', padx=5, pady=5, fill='both', expand=True)
        
        # Список игроков команды B
        self.list_b = ttk.Treeview(self.team_b_frame, columns=('info',), show='headings')
        self.list_b.heading('info', text='Игроки команды B', command=self.sort_team_b)
        self.list_b.bind('<Button-1>', self.on_treeview_click)
    
        # Настройка цветов
        self.list_b.tag_configure('red', background='#ff4a4a')
        self.list_b.tag_configure('orange', background='#b88d3b')
        self.list_b.tag_configure('green', background='#46bc60')
        self.list_b.pack(padx=5, pady=5, fill='both', expand=True)
        self.list_b.bind('<Double-1>', lambda e: self.edit_player('B'))
        
        # Суммы для команды B
        self.sum_b_frame = ttk.Frame(self.team_b_frame)
        self.sum_b_frame.pack(pady=5, fill='x')
        
        ttk.Label(self.sum_b_frame, text="Сумма рейтинга:", width=16).pack(side='left')
        self.sum_rating_b = ttk.Label(self.sum_b_frame, text="0", width=10)
        self.sum_rating_b.pack(side='left', padx=5)
        
        ttk.Label(self.sum_b_frame, text="Сумма порядочности:", width=21).pack(side='left')
        self.sum_special_b = ttk.Label(self.sum_b_frame, text="0", width=10)
        self.sum_special_b.pack(side='left')

        # Панель управления (нижняя)
        self.controls_bottom = ttk.Frame(self.root) # Renamed to avoid conflict
        self.controls_bottom.pack(pady=10, fill='x')
        
        control_buttons = [
            ("→", self.move_to_b),
            ("←", self.move_to_a),
            ("Фикс/Снять", self.toggle_fix),
            ("Балансировать", self.balance_teams),
            ("База игроков", self.toggle_manage_dialog),
            ("Внести в базу", self.add_to_database),
            ("Добавить игрока", self.add_player_dialog_balance),
            ("Удалить игрока", self.delete_player_dialog)
        ]
        
        for text, command in control_buttons:
            ttk.Button(self.controls_bottom, text=text, command=command).pack(side='left', padx=5)
            
    def sort_team(self, team_letter):
        """Сортировка команды по рейтингу"""
        if team_letter == 'A':
            team = self.team_a
            current_state = self.sort_state_a
        else:
            team = self.team_b
            current_state = self.sort_state_b
            
        # Определяем новое состояние сортировки
        if current_state is None:
            new_state = 'desc'
        elif current_state == 'desc':
            new_state = 'asc'
        else:
            new_state = None
            
        # Применяем сортировку
        if new_state == 'desc':
            team.sort(key=lambda p: p['rating'], reverse=True)
        elif new_state == 'asc':
            team.sort(key=lambda p: p['rating'])
        # При new_state=None оставляем исходный порядок
        
        # Обновляем состояние и заголовок
        if team_letter == 'A':
            self.sort_state_a = new_state
            self.update_team_header('A')
        else:
            self.sort_state_b = new_state
            self.update_team_header('B')
            
        self.update_display()

    def sort_team_a(self):
        """Сортировка команды A"""
        self.sort_team('A')

    def sort_team_b(self):
        """Сортировка команды B"""
        self.sort_team('B')

    def update_team_header(self, team_letter):
        """Обновление заголовка с индикатором сортировки"""
        if team_letter == 'A':
            tree = self.list_a
            state = self.sort_state_a
            base_text = "Игроки команды A"
        else:
            tree = self.list_b
            state = self.sort_state_b
            base_text = "Игроки команды B"
            
        if state == 'desc':
            text = base_text + " ▼"
        elif state == 'asc':
            text = base_text + " ▲"
        else:
            text = base_text
            
        tree.heading('info', text=text)

    def balance_teams(self, initial=False):
        try:
            self.use_rating_limit = self.rating_limit_var.get()
            self.use_special_limit = self.special_limit_var.get()
            
            self.rating_diff_limit = int(self.rating_limit_entry.get()) if self.use_rating_limit else None
            self.special_diff_limit = int(self.special_limit_entry.get()) if self.use_special_limit else None
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные значения ограничений")
            return

        if not self.players:
            messagebox.showinfo("Информация", "Добавьте игроков из базы")
            return
            
        if initial or not self.team_a or not self.team_b:
            sorted_players = sorted(self.players, key=lambda x: (-x['special'], -x['rating']))
            self.team_a = sorted_players[::2]
            self.team_b = sorted_players[1::2]
        else:
            fixed_a = [p for p in self.team_a if p['fixed']]
            fixed_b = [p for p in self.team_b if p['fixed']]
            movable = [p for p in self.team_a + self.team_b if not p['fixed']]
            
            total_rating = sum(p['rating'] for p in self.players)
            total_special = sum(p['special'] for p in self.players)
            need_a = max(0, (len(self.team_a) + len(self.team_b)) // 2 - len(fixed_a))
            
            best_combo = None
            best_score = (float('inf'), float('inf'))  # Инициализируем как кортеж
            
            for combo in itertools.combinations(movable, need_a):
                current_rating = sum(p['rating'] for p in combo) + sum(p['rating'] for p in fixed_a)
                current_special = sum(p['special'] for p in combo) + sum(p['special'] for p in fixed_a)
                
                rating_diff = abs(total_rating - 2 * current_rating)
                special_diff = abs(total_special - 2 * current_special)
                
                valid = True
                if self.use_rating_limit and self.rating_diff_limit is not None:
                    if rating_diff > self.rating_diff_limit:
                        valid = False
                if self.use_special_limit and self.special_diff_limit is not None:
                    if special_diff > self.special_diff_limit:
                        valid = False

                if valid:
                    score = (rating_diff, special_diff)
                else:
                    r_penalty = max(0, rating_diff - self.rating_diff_limit) if self.use_rating_limit else 0
                    s_penalty = max(0, special_diff - self.special_diff_limit) if self.use_special_limit else 0
                    score = (float('inf'), r_penalty * 1000 + s_penalty)
                
                if score < best_score:
                    best_score = score
                    best_combo = combo

            if best_combo:
                self.team_a = fixed_a + list(best_combo)
                self.team_b = fixed_b + [p for p in movable if p not in best_combo]
        self.sort_state_a = None
        self.sort_state_b = None
        self.update_display()
        self.highlight_limits()
        self.update_team_header('A')
        self.update_team_header('B')

    def highlight_limits(self):
        rating_diff = abs(int(self.sum_rating_a['text']) - int(self.sum_rating_b['text']))
        special_diff = abs(int(self.sum_special_a['text']) - int(self.sum_special_b['text']))
        
        color = 'red' if self.use_rating_limit and rating_diff > self.rating_diff_limit else 'black'
        self.sum_rating_a.config(foreground=color)
        self.sum_rating_b.config(foreground=color)
        
        color = 'red' if self.use_special_limit and special_diff > self.special_diff_limit else 'black'
        self.sum_special_a.config(foreground=color)
        self.sum_special_b.config(foreground=color)

    def update_display(self):
        for list_widget, team in [(self.list_a, self.team_a), (self.list_b, self.team_b)]:
            list_widget.delete(*list_widget.get_children())
            total_rating = 0
            total_special = 0
            for p in team:
                style = self.get_special_style(p['special'])
                status = " ✓" if p['fixed'] else ""
                list_widget.insert('', 'end', 
                    values=(f"{p['name']} (Рейтинг:{p['rating']} Порядочность:{p['special']}{status})",),
                    tags=(style,))
                total_rating += p['rating']
                total_special += p['special']
            
            if list_widget == self.list_a:
                self.sum_rating_a.config(text=str(total_rating))
                self.sum_special_a.config(text=str(total_special))
            else:
                self.sum_rating_b.config(text=str(total_rating))
                self.sum_special_b.config(text=str(total_special))

    def add_player_dialog_balance(self):
        """Добавление игрока непосредственно в балансировку"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить игрока")
        dialog.transient(self.root)
        dialog.grab_set()

        # Bug fix: Handle WM_DELETE_WINDOW and minimize/restore events for the dialog
        def on_dialog_close():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            dialog.destroy()

        def on_dialog_iconify(event):
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            
        def on_dialog_deiconify(event):
            dialog.grab_set()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Unmap>", on_dialog_iconify)
        dialog.bind("<Map>", on_dialog_deiconify)
        
        entries = []
        labels = ['Имя:', 'Рейтинг (1-17000):', 'Порядочность (1-12000):']
        for i, text in enumerate(labels):
            ttk.Label(dialog, text=text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=20)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            self.apply_entry_bindings(entry) # <--- Apply bindings here
        
        def add():
            try:
                name = entries[0].get().strip()
                rating = int(entries[1].get())
                special = int(entries[2].get())
                
                if not name:
                    raise ValueError("Введите имя игрока")
                if not 1 <= rating <= 17000:
                    raise ValueError("Рейтинг должен быть от 1 до 17000")
                if not 1 <= special <= 12000:
                    raise ValueError("Порядочность должна быть от 1 до 12000")
                    
                # Проверка на уникальность имени в текущем балансе
                if any(p['name'].lower() == name.lower() for p in self.players):
                    raise ValueError("Игрок с таким именем уже добавлен в балансировку")
                    
                new_player = {
                    'name': name,
                    'rating': rating,
                    'special': special,
                    'fixed': False
                }
                
                # Добавляем в общий список игроков (текущий баланс)
                self.players.append(new_player)
                
                # Распределяем в команду с меньшим количеством
                if len(self.team_a) <= len(self.team_b):
                    self.team_a.append(new_player)
                else:
                    self.team_b.append(new_player)
                if len(self.team_a) > len(self.team_b):
                    self.sort_state_b = None
                    self.update_team_header('B')
                else:
                    self.sort_state_a = None
                    self.update_team_header('A')
                
                self.update_display()
                on_dialog_close() # Use the handler to close and release grab
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Добавить", command=add).grid(row=3, columnspan=2, pady=10)

    def add_to_database(self):
        """Перенос игроков из балансировки в базу"""
        selected_a = self.list_a.selection()
        selected_b = self.list_b.selection()
        
        players_to_add = []
        duplicates = []
        
        # Собираем выбранных игроков
        for item in selected_a:
            index = self.list_a.index(item)
            player = self.team_a[index]
            players_to_add.append(player)
            
        for item in selected_b:
            index = self.list_b.index(item)
            player = self.team_b[index]
            players_to_add.append(player)
            
        # Добавляем в базу только уникальных игроков
        added_count = 0
        for player_data in players_to_add:
            # Создаем копию без поля 'fixed'
            player_copy = {
                'name': player_data['name'],
                'rating': player_data['rating'],
                'special': player_data['special']
            }
            
            if not self.player_name_exists(player_copy['name']):
                self.saved_players.append(player_copy)
                added_count += 1
            else:
                duplicates.append(player_copy['name'])
                
        self.save_players()
        
        # Формируем сообщение о результате
        message = f"Добавлено игроков: {added_count}"
        if duplicates:
            message += f"\nНе добавлены (дубликаты): {', '.join(duplicates)}"
        
        messagebox.showinfo("Результат", message, parent=self.root)
        self.update_saved_tree()

    def delete_player_dialog(self):
        """Удаление игроков из текущего баланса"""
        selected_a = self.list_a.selection()
        selected_b = self.list_b.selection()
        
        # Собираем всех выбранных игроков
        players_to_remove = []
        for item in selected_a:
            index = self.list_a.index(item)
            player = self.team_a[index]
            players_to_remove.append(player['name'])
            
        for item in selected_b:
            index = self.list_b.index(item)
            player = self.team_b[index]
            players_to_remove.append(player['name'])
        
        # Удаляем из всех списков
        self.players = [p for p in self.players if p['name'] not in players_to_remove]
        self.team_a = [p for p in self.team_a if p['name'] not in players_to_remove]
        self.team_b = [p for p in self.team_b if p['name'] not in players_to_remove]
        
        # Только обновляем отображение, без балансировки
        self.sort_state_a = None
        self.sort_state_b = None
        self.update_display()
        self.update_team_header('A')
        self.update_team_header('B')

    def edit_player(self, team):
        tree = self.list_a if team == 'A' else self.list_b
        team_data = self.team_a if team == 'A' else self.team_b
        
        selected = tree.selection()
        if not selected:
            return
            
        item = selected[0]
        index = tree.index(item)
        player = team_data[index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование игрока")
        dialog.transient(self.root)
        dialog.grab_set()

        # Bug fix: Handle WM_DELETE_WINDOW and minimize/restore events for the dialog
        def on_dialog_close():
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            dialog.destroy()

        def on_dialog_iconify(event):
            try:
                dialog.grab_release()
            except tk.TclError:
                pass
            
        def on_dialog_deiconify(event):
            dialog.grab_set()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Unmap>", on_dialog_iconify)
        dialog.bind("<Map>", on_dialog_deiconify)
        
        entries = []
        fields = [
            ('Имя:', player['name']),
            ('Рейтинг:', player['rating']),
            ('Порядочность:', player['special'])
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=20)
            entry.insert(0, str(value))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            self.apply_entry_bindings(entry) # <--- Apply bindings here
        
        def save():
            try:
                name = entries[0].get().strip()
                rating = int(entries[1].get())
                special = int(entries[2].get())
                
                if not name:
                    raise ValueError("Введите имя игрока")
                if not 1 <= rating <= 17000:
                    raise ValueError("Некорректный рейтинг")
                if not 1 <= special <= 12000:
                    raise ValueError("Некорректная порядочность")
                    
                # Проверка на уникальность имени в текущем балансе
                if name != player['name'] and any(p['name'].lower() == name.lower() for p in self.players):
                    raise ValueError("Игрок с таким именем уже есть в текущем балансе")
                    
                player.update({
                    'name': name,
                    'rating': rating,
                    'special': special
                })
                if team == 'A':
                    self.sort_state_a = None
                    self.update_team_header('A')
                else:
                    self.sort_state_b = None
                    self.update_team_header('B')
                self.update_display()
                on_dialog_close()
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e), parent=dialog)
            if team == 'A':
                self.sort_state_a = None
                self.update_team_header('A')
            else:
                self.sort_state_b = None
                self.update_team_header('B')
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=3, columnspan=2, pady=10)

    def move_players(self, from_tree, to_team, from_team):
        selected = from_tree.selection()
        indices = [from_tree.index(item) for item in selected]
        
        for i in reversed(sorted(indices)):
            if not from_team[i]['fixed']:
                to_team.append(from_team.pop(i))
        self.sort_state_a = None
        self.sort_state_b = None
        self.update_team_header('A')
        self.update_team_header('B')
        self.update_display()

    def move_to_b(self):
        self.move_players(self.list_a, self.team_b, self.team_a)

    def move_to_a(self):
        self.move_players(self.list_b, self.team_a, self.team_b)

    def toggle_fix(self):
        for item in self.list_a.selection():
            index = self.list_a.index(item)
            self.team_a[index]['fixed'] = not self.team_a[index]['fixed']
            
        for item in self.list_b.selection():
            index = self.list_b.index(item)
            self.team_b[index]['fixed'] = not self.team_b[index]['fixed']
            
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = TeamBalancerApp(root)
    root.mainloop()