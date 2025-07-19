import os
import json
import tkinter as tk
from tkinter import ttk
# from PIL import Image, ImageTk
import configparser
from functools import partial

class CollapsibleFrame(ttk.Frame):
    
    def __init__(self, parent, title, initial_state, on_toggle, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.show = tk.BooleanVar(value=(initial_state == "opened"))
        self.on_toggle = on_toggle
        
        self.header = ttk.Frame(self)
        self.header.pack(fill="x", pady=(0, 2))
        
        self.toggle_btn = ttk.Button(
            self.header, text=title, command=self.toggle,
            style="Collapsible.TButton"
        )
        self.toggle_btn.pack(side="left", fill="x", expand=True)
        
        self.indicator = ttk.Label(
            self.header, text="▼" if self.show.get() else "▶", style="Collapsible.TLabel"
        )
        self.indicator.pack(side="right", padx=5)
        
        self.content = ttk.Frame(self)
        if self.show.get():
            self.content.pack(fill="x", expand=True)

    def toggle(self):
        if self.show.get():
            self.content.pack_forget()
            self.indicator.config(text="▶")
            self.show.set(False)
            self.on_toggle("closed")
        else:
            self.content.pack(fill="x", expand=True)
            self.indicator.config(text="▼")
            self.show.set(True)
            self.on_toggle("opened")

class JSONEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu author: vk.com/id54162245")

        # Путь: D:/.../Interface/Icons
        # self.base_path = os.path.join(
        #     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        #     "Icons"
        # )
        
        self.base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "Icons"
        )
        
        # print("self.base_path =", self.base_path)

        self.profile_var = tk.StringVar()
        self.icon_cache = {}



        # Загрузка настроек
        self.settings = self.load_settings()

        # Устанавливаем размер и положение окна
        self.root.geometry(self.settings.get("window_size", "300x700"))
        self.root.geometry(f"+{self.settings.get('window_x', '100')}+{self.settings.get('window_y', '100')}")

        # Верхний фиксированный фрейм для кнопок и выпадающего списка
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill="x", pady=5)

        # Кнопка "ПЕРЕРИСОВАТЬ"
        self.refresh_button = tk.Button(self.top_frame, text="ПЕРЕРИСОВАТЬ", command=self.refresh_ui)
        self.refresh_button.pack(side='left', padx=5)

        # Кнопка "Поверх окон"
        self.topmost_button = tk.Button(self.top_frame, text="Поверх всех окон", command=self.toggle_topmost)
        self.topmost_button.pack(side='left', padx=5)
        self.topmost_state = self.settings.getboolean("topmost", False)  # Загружаем состояние "Поверх всех окон"
        self.toggle_topmost(initial=True)  # Применяем состояние

        # Выбор профиля
        self.profile_dropdown = ttk.Combobox(self.top_frame, textvariable=self.profile_var, width=40)
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.on_profile_select)
        self.profile_dropdown.pack(side='left', padx=5)

        # Основной фрейм с поддержкой скроллинга
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Привязка событий для сохранения настроек
        self.root.bind("<Configure>", self.save_window_state)  # Сохраняем размер и положение окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Сохраняем настройки при закрытии

        # Привязка скроллинга к колесику мыши
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Загрузка профилей и выбранного профиля при запуске
        self.load_profiles()
        if self.profile_var.get():  # Если профиль выбран, загружаем его
            self.load_profile()

    def load_settings(self):
        """Загружает настройки из settings.ini."""
        config = configparser.ConfigParser()
        
        # Определяем путь к settings.ini (в папке с программой)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(script_dir, "settings.ini")
        
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as configfile:
                config.read_file(configfile)
            if "Settings" not in config:  # Если секция отсутствует, создаем её
                config["Settings"] = {
                    "last_profile": "",
                    "window_size": "560x500",
                    "window_x": "8",
                    "window_y": "8",
                    "topmost": "False"
                }
                with open(settings_path, "w", encoding="utf-8") as configfile:
                    config.write(configfile)
        else:
            # Создаем файл settings.ini с секцией [Settings]
            config["Settings"] = {
                "last_profile": "",
                "window_size": "560x500",
                "window_x": "8",
                "window_y": "8",
                "topmost": "False"
            }
            with open(settings_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)
        return config["Settings"]

    def save_settings(self):
        """Сохраняет настройки в settings.ini."""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "last_profile": self.profile_var.get(),
            "window_size": self.root.geometry().split("+")[0],
            "window_x": str(self.root.winfo_x()),
            "window_y": str(self.root.winfo_y()),
            "topmost": str(self.topmost_state)
        }
        
        # Определяем путь к settings.ini (в папке с программой)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(script_dir, "settings.ini")
        
        with open(settings_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)

    def save_window_state(self, event=None):
        """Сохраняет размер и положение окна."""
        if event:
            self.settings["window_size"] = self.root.geometry().split("+")[0]
            self.settings["window_x"] = str(self.root.winfo_x())
            self.settings["window_y"] = str(self.root.winfo_y())
            self.save_settings()

    def toggle_topmost(self, initial=False):
        """Переключает режим 'Поверх всех окон'."""
        if not initial:
            self.topmost_state = not self.topmost_state
        self.root.attributes("-topmost", self.topmost_state)
        self.topmost_button.config(
            text="Поверх всех окон" if self.topmost_state else "Обычный режим",
            fg="green" if self.topmost_state else "red"
        )
        self.save_settings()

    def load_profiles(self):
        """Загружает список профилей и выбирает последний использованный."""
        self.profiles = [f for f in os.listdir() if f.endswith('.json')]
        self.profile_dropdown['values'] = self.profiles
        if self.profiles:
            last_profile = self.settings.get("last_profile", "")
            if last_profile in self.profiles:
                self.profile_var.set(last_profile)
                self.profile_dropdown.set(last_profile)
            else:
                self.profile_var.set(self.profiles[0] if self.profiles else "")
                self.profile_dropdown.current(0)

    def on_profile_select(self, event=None):
        """Обрабатывает выбор профиля."""
        self.load_profile()
        self.profile_dropdown.selection_clear()
        self.root.focus()
        self.save_settings()

    def load_profile(self):
        """Загружает выбранный профиль."""
        selected_profile = self.profile_var.get()
        if selected_profile:
            with open(selected_profile, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
            self.create_widgets()

    def load_icon(self, icon_name):
        if icon_name in self.icon_cache:
            return self.icon_cache[icon_name]

        icon_path = os.path.join(self.base_path, icon_name + ".png")
        if os.path.exists(icon_path):
            try:
                image = tk.PhotoImage(file=icon_path).subsample(3, 3)
                self.icon_cache[icon_name] = image
                return image
            except Exception as e:
                print(f"Ошибка при загрузке {icon_name}: {e}")
        else:
            print(f"Файл не найден: {icon_path}")
        return None
    
    def create_widgets(self):
        """Создает виджеты на основе данных из JSON с поддержкой групп."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Разделяем элементы на группы и элементы без группы
        groups = {}
        no_group = {}
        group_states = {}
        
        for key, value in self.data.items():
            group_name = value.get("group")
            if group_name:
                groups.setdefault(group_name, {})[key] = value
                if group_name not in group_states:
                    group_states[group_name] = value.get("state", "opened")
            else:
                no_group[key] = value

        # Создаем список всех элементов для отображения
        all_items = []
        
        # Добавляем группы
        for group_name, items in groups.items():
            state = group_states.get(group_name, "opened")
            all_items.append(("group", group_name, items, state))
            
        # Добавляем элементы без группы
        for key, value in no_group.items():
            all_items.append(("single", key, value))

        # Создаем виджеты
        for item in all_items:
            if item[0] == "group":
                group_name, group_items, state = item[1], item[2], item[3]
                cframe = CollapsibleFrame(
                    self.scrollable_frame, 
                    group_name, 
                    state, 
                    partial(self.set_group_state, group_name)
                )
                cframe.pack(fill="x", pady=5, padx=5)
                
                for k, v in group_items.items():
                    self.create_element_widget(cframe.content, k, v)
            else:
                k, v = item[1], item[2]
                self.create_element_widget(self.scrollable_frame, k, v)

    def set_group_state(self, group_name, new_state):
        """Обновляет состояние группы в данных и сохраняет JSON."""
        changed = False
        for key, value in self.data.items():
            if value.get("group") == group_name:
                if value.get("state") != new_state:
                    value["state"] = new_state
                    changed = True
        if changed:
            self.save_json()

    def create_element_widget(self, parent, key, value):
        """Создает виджет элемента (чекбокс, слайдер и т.д.)"""
        frame = tk.Frame(parent)
        frame.pack(anchor='w', pady=2, padx=5, fill="x")

        # Обработка иконок
        if 'icon' in value or 'icon2' in value:
            icon1 = value.get('icon')
            icon2 = value.get('icon2')
            
            if icon1:
                icon_photo1 = self.load_icon(icon1)
                if icon_photo1:
                    icon_label1 = tk.Label(frame, image=icon_photo1)
                    icon_label1.image = icon_photo1
                    icon_label1.pack(side='left', padx=2)
                    
            if icon2:
                icon_photo2 = self.load_icon(icon2)
                if icon_photo2:
                    icon_label2 = tk.Label(frame, image=icon_photo2)
                    icon_label2.image = icon_photo2
                    icon_label2.pack(side='left', padx=2)

        # Создаем виджеты в зависимости от типа элемента
        if value['type'] == 'checkbutton':
            var = tk.BooleanVar(value=value['isChecked'])
            checkbutton = tk.Checkbutton(
                frame, text=key, variable=var,
                command=lambda k=key, v=var: self.update_json(k, 'isChecked', v.get())
            )
            checkbutton.pack(side='left')

        elif value['type'] == 'slider':
            label = tk.Label(frame, text=key)
            label.pack(side='left', anchor='w')

            var = tk.DoubleVar(value=value['value'])
            slider_min = value.get('min', 0)
            slider_max = value.get('max', 100)
            resolution = value.get('step', 1)

            scale = tk.Scale(
                frame, from_=slider_min, to=slider_max, orient='horizontal', 
                variable=var, length=300, 
                resolution=resolution, 
                command=lambda v, k=key: self.update_json(k, 'value', float(v))
            )
            scale.pack(side='left', fill='x', padx=5)

        elif value['type'] == 'checkbutton&slider':
            var_check = tk.BooleanVar(value=value['isChecked'])
            var_slider = tk.DoubleVar(value=value['value'])
            
            checkbutton = tk.Checkbutton(
                frame, text=key, variable=var_check,
                command=lambda k=key, v=var_check: self.update_json(k, 'isChecked', v.get())
            )
            checkbutton.pack(side='left')
        
            slider_min = value.get('min', 0)
            slider_max = value.get('max', 100)
            resolution = value.get('step', 1)
            
            scale = tk.Scale(
                frame, from_=slider_min, to=slider_max, orient='horizontal', 
                variable=var_slider, length=300, 
                resolution=resolution,
                command=lambda v, k=key: self.update_json(k, 'value', float(v))
            )
            scale.pack(side='left', fill='x', padx=5)

        elif value['type'] == 'dropdownlist':
            label = tk.Label(frame, text=key)
            label.pack(side='left', anchor='w')

            var = tk.StringVar(value=value['selected'])
            dropdown = ttk.Combobox(frame, textvariable=var, values=value['options'], width=40)
            dropdown.bind("<<ComboboxSelected>>", 
                         lambda e, k=key, v=var: self.on_dropdown_select(k, v.get(), dropdown))
            dropdown.pack(fill='x', padx=5)

    def on_dropdown_select(self, key, value, dropdown):
        """Обрабатывает выбор в выпадающем списке."""
        self.update_json(key, 'selected', value)
        dropdown.selection_clear()
        self.root.focus()

    def update_json(self, key, attr, value):
        """Обновляет JSON и сохраняет его."""
        self.data[key][attr] = value
        self.save_json()

    def save_json(self):
        """Сохраняет JSON в файл."""
        selected_profile = self.profile_var.get()
        if selected_profile:
            with open(selected_profile, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)

    def refresh_ui(self):
        """Перерисовывает интерфейс."""
        current_profile = self.profile_var.get()
        self.load_profiles()
        if current_profile in self.profiles:
            self.profile_var.set(current_profile)
            self.profile_dropdown.set(current_profile)
        else:
            self.profile_var.set(self.profiles[0] if self.profiles else "")
            self.profile_dropdown.current(0)
        self.load_profile()

    def on_close(self):
        """Сохраняет настройки при закрытии окна."""
        self.save_settings()
        self.root.destroy()

    def on_mousewheel(self, event):
        """Обрабатывает прокрутку мыши."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONEditor(root)
    root.mainloop()