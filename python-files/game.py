
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import time
from datetime import datetime, timedelta
import database as db # Импортируем наш модуль базы данных

# --- Константы ---
MAX_ENERGY = 100
ENERGY_RESTORE_INTERVAL_HOURS = 1
SNESKER_SHOP_REFRESH_SECONDS = 99
SNESKER_SHOP_REFRESH_EVENT = '<RefreshSneakerShop>' # Пользовательское событие
BOX_OPEN_STEPS_COST = 100
SNEAKER_REPAIR_COST = 10

# --- Классы ---

class Character:
    def __init__(self, character_id, name, coins, energy, steps_today, last_energy_restore):
        self.id = character_id
        self.name = name
        self.coins = coins
        self.energy = energy
        self.steps_today = steps_today
        self.last_energy_restore = datetime.fromisoformat(last_energy_restore) if last_energy_restore else datetime.now()
        self.current_sneaker = None # Объект кроссовок, который одет

    def check_energy_restore(self):
        """Проверяет, нужно ли восстановить энергию."""
        now = datetime.now()
        time_since_last_restore = now - self.last_energy_restore
        if time_since_last_restore >= timedelta(hours=ENERGY_RESTORE_INTERVAL_HOURS):
            # Восстанавливаем энергию до максимума
            self.energy = MAX_ENERGY
            self.last_energy_restore = now
            db.update_character_progress(self.id, energy=self.energy, last_energy_restore=self.last_energy_restore.isoformat())
            return True
        return False

    def add_coins(self, amount):
        self.coins += amount
        db.update_character_progress(self.id, coins=self.coins)

    def spend_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            db.update_character_progress(self.id, coins=self.coins)
            return True
        return False

    def add_steps(self, amount):
        self.steps_today += amount
        db.update_character_progress(self.id, steps_today=self.steps_today)

    def restore_energy(self, amount):
        self.energy = min(MAX_ENERGY, self.energy + amount)
        db.update_character_progress(self.id, energy=self.energy)

    def spend_energy(self, amount):
        if self.energy >= amount:
            self.energy -= amount
            db.update_character_progress(self.id, energy=self.energy)
            return True
        return False

    def equip_sneaker(self, sneaker_obj):
        self.current_sneaker = sneaker_obj

    def unequip_sneaker(self):
        self.current_sneaker = None

class Sneaker:
    def __init__(self, sneaker_id, name, luck, durability, max_durability, level, character_id=None):
        self.id = sneaker_id
        self.character_id = character_id
        self.name = name
        self.luck = luck
        self.durability = durability
        self.max_durability = max_durability
        self.level = level

    def improve_luck(self):
        self.level += 1
        self.luck += random.randint(1, 3) # Удача улучшается при повышении уровня
        # Прочность может также слегка улучшаться или оставаться
        db.update_sneaker(self.id, luck=self.luck, level=self.level)

    def decrease_durability(self, amount):
        self.durability -= amount
        self.durability = max(0, self.durability) # Прочность не может быть отрицательной
        db.update_sneaker(self.id, durability=self.durability)
        if self.durability == 0:
            print(f"Кроссовки '{self.name}' сломались!") # Можно добавить уведомление

    def repair(self, repair_amount):
        self.durability = min(self.max_durability, self.durability + repair_amount)
        db.update_sneaker(self.id, durability=self.durability)

    def __str__(self):
        return f"{self.name} (Удача: {self.luck}, Прочность: {self.durability}/{self.max_durability}, Уровень: {self.level})"

# --- Основной класс игры ---

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Шагомер Игра")

self.root.geometry("800x600")

        self.current_character = None
        self.character_id = None
        self.sneakers_in_shop = []

        self.create_menu()
        self.create_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Обработка закрытия окна

    def create_menu(self):
        """Создает главное меню."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Меню", menu=file_menu)
        file_menu.add_command(label="Создать персонажа", command=self.create_character_dialog)
        file_menu.add_command(label="Загрузить персонажа", command=self.load_character_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Магазин", command=self.open_shop)
        file_menu.add_command(label="Одеть кроссовки", command=self.equip_sneaker_dialog)
        file_menu.add_command(label="Починить кроссовки", command=self.repair_sneaker_dialog)
        file_menu.add_command(label="Идти", command=self.start_walking)
        file_menu.add_command(label="Восстановить энергию (ручное)", command=self.manual_restore_energy)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить прогресс", command=self.save_game)
        file_menu.add_command(label="Выйти", command=self.on_closing)

    def create_ui(self):
        """Создает основной пользовательский интерфейс."""
        self.info_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        self.info_frame.pack(pady=10, padx=10, fill=tk.X)

        self.coins_label = tk.Label(self.info_frame, text="Монеты: 0", font=("Arial", 12))
        self.coins_label.pack(side=tk.LEFT, padx=10)

        self.energy_label = tk.Label(self.info_frame, text="Энергия: 0/100", font=("Arial", 12))
        self.energy_label.pack(side=tk.LEFT, padx=10)

        self.steps_label = tk.Label(self.info_frame, text="Шаги сегодня: 0", font=("Arial", 12))
        self.steps_label.pack(side=tk.LEFT, padx=10)

        self.sneaker_status_label = tk.Label(self.info_frame, text="Кроссовки: Нет", font=("Arial", 12))
        self.sneaker_status_label.pack(side=tk.LEFT, padx=10)

        self.main_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        self.main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.status_text = tk.Text(self.main_frame, wrap=tk.WORD, font=("Arial", 11), state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_message("Добро пожаловать в Шагомер Игру!")

        # Запуск таймеров
        self.start_timers()

    def log_message(self, message):
        """Добавляет сообщение в текстовое поле статуса."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END) # Прокрутка вниз
        self.status_text.config(state=tk.DISABLED)

    def update_info_labels(self):
        """Обновляет отображаемую информацию о персонаже."""
        if self.current_character:
            self.coins_label.config(text=f"Монеты: {self.current_character.coins}")
            self.energy_label.config(text=f"Энергия: {self.current_character.energy}/{MAX_ENERGY}")
            self.steps_label.config(text=f"Шаги сегодня: {self.current_character.steps_today}")

            sneaker_info = "Нет"
            if self.current_character.current_sneaker:
                sneaker_info = str(self.current_character.current_sneaker)
            self.sneaker_status_label.config(text=f"Кроссовки: {sneaker_info}")
        else:
            self.coins_label.config(text="Монеты: N/A")
            self.energy_label.config(text="Энергия: N/A")
            self.steps_label.config(text="Шаги сегодня: N/A")
            self.sneaker_status_label.config(text="Кроссовки: N/A")

    def create_character_dialog(self):
        """Открывает диалоговое окно для создания персонажа."""
        if

self.current_character:
            messagebox.showinfo("Информация", "У вас уже есть персонаж. Сначала выйдите или загрузите другого.")
            return

        name = simpledialog.askstring("Создать персонажа", "Введите имя вашего персонажа:")
        if name:
            created_id = db.create_character(name)
            if created_id:
                self.log_message(f"Персонаж '{name}' успешно создан.")
                # Автоматически загружаем созданного персонажа
                self.load_character(created_id)
            else:
                messagebox.showerror("Ошибка", f"Не удалось создать персонажа '{name}'. Возможно, имя уже занято.")
        else:
            self.log_message("Создание персонажа отменено.")

    def load_character_dialog(self):
        """Открывает диалоговое окно для выбора и загрузки персонажа."""
        if self.current_character:
            if not messagebox.askyesno("Внимание", "У вас есть несохраненный прогресс. Хотите продолжить загрузку другого персонажа? (Несохраненные данные будут потеряны)"):
                return
            self.save_game() # Сохраняем текущего персонажа перед загрузкой другого

        characters = db.get_all_characters()
        if not characters:
            messagebox.showinfo("Информация", "В базе данных нет персонажей. Пожалуйста, создайте нового.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Загрузить персонажа")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Выберите персонажа:").pack(pady=10)

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE)
        for char_id, char_name in characters:
            listbox.insert(tk.END, f"{char_id}: {char_name}")
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def on_select():
            selected_item = listbox.get(tk.ACTIVE)
            if selected_item:
                char_id = int(selected_item.split(":")[0])
                self.load_character(char_id)
                dialog.destroy()

        tk.Button(dialog, text="Загрузить", command=on_select).pack(pady=5)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def load_character(self, character_id):
        """Загружает данные персонажа из базы данных."""
        character_data = db.load_game_state(character_id)
        if character_data:
            sneaker_list = []
            for s_data in character_data.get('sneakers', []):
                sneaker = Sneaker(s_data[0], s_data[2], s_data[3], s_data[4], s_data[5], s_data[6], s_data[1])
                sneaker_list.append(sneaker)

            self.current_character = Character(
                character_id,
                character_data['name'],
                character_data['coins'],
                character_data['energy'],
                character_data['steps_today'],
                character_data['last_energy_restore']
            )
            self.character_id = character_id
            self.log_message(f"Персонаж '{self.current_character.name}' загружен.")
            self.update_info_labels()
            self.check_energy_restore_on_load() # Проверяем энергию при загрузке
            self.load_equiped_sneaker() # Загружаем одетые кроссовки
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить персонажа с ID {character_id}.")

    def check_energy_restore_on_load(self):
        """Проверяет и восстанавливает энергию при загрузке персонажа."""
        if self.current_character and self.current_character.check_energy_restore():
            self.log_message("Ваша энергия была автоматически восстановлена.")
            self.update_info_labels()

    def load_equiped_sneaker(self):
        """Загружает одетые кроссовки для текущего персонажа."""
        if self.current_character:
            all_sneakers = db.get_sneakers_by_character(self.current_character.id)
            # Предполагаем, что если кроссовок несколько, мы должны решить, какой

"одет".
            # Пока что, если есть кроссовки, возьмем первый попавшийся как "одетый".
            # В реальной игре может быть флаг "is_equipped".
            if all_sneakers:
                # Берем первый кроссовок из списка (по ID)
                first_sneaker_data = all_sneakers[0]
                sneaker_obj = Sneaker(
                    first_sneaker_data[0], first_sneaker_data[2], first_sneaker_data[3],
                    first_sneaker_data[4], first_sneaker_data[5], first_sneaker_data[6],
                    first_sneaker_data[1]
                )
                self.current_character.equip_sneaker(sneaker_obj)
            else:
                self.current_character.current_sneaker = None
            self.update_info_labels()

    def open_shop(self):
        """Открывает окно магазина."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        if not hasattr(self, 'shop_window') or not self.shop_window.winfo_exists():
            self.shop_window = tk.Toplevel(self.root)
            self.shop_window.title("Магазин Кроссовок")
            self.shop_window.geometry("500x400")

            tk.Label(self.shop_window, text="Доступные кроссовки:", font=("Arial", 14)).pack(pady=10)

            self.shop_list_frame = tk.Frame(self.shop_window)
            self.shop_list_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

            self.refresh_shop_items()
            self.start_shop_refresh_timer() # Запускаем таймер обновления магазина
        else:
            self.shop_window.lift() # Поднимаем окно, если оно уже открыто

    def refresh_shop_items(self):
        """Обновляет список кроссовок в магазине."""
        # Очищаем предыдущие виджеты
        for widget in self.shop_list_frame.winfo_children():
            widget.destroy()

        self.sneakers_in_shop = [] # Обновляем список доступных кроссовок
        num_sneakers_to_generate = random.randint(2, 5) # Генерируем случайное количество
        for _ in range(num_sneakers_to_generate):
            sneaker_name = random.choice(["Speedy", "Comfort", "Racer", "Trailblazer", "Urban Stompers"])
            luck = random.randint(1, 5)
            durability = random.randint(80, 120)
            max_durability = durability
            level = random.randint(1, 3)
            # Не сохраняем кроссовки в БД до покупки, это просто "предложения"
            self.sneakers_in_shop.append(Sneaker(None, sneaker_name, luck, durability, max_durability, level))

        if not self.sneakers_in_shop:
            tk.Label(self.shop_list_frame, text="Магазин временно пуст.").pack()
            return

        for i, sneaker in enumerate(self.sneakers_in_shop):
            frame = tk.Frame(self.shop_list_frame, bd=1, relief=tk.GROOVE)
            frame.pack(fill=tk.X, padx=5, pady=2)

            tk.Label(frame, text=f"{sneaker.name} (Удача: {sneaker.luck}, Прочность: {sneaker.durability}, Уровень: {sneaker.level})").pack(side=tk.LEFT, padx=5)

            # Стоимость покупки зависит от уровня и характеристик
            buy_cost = 50 + sneaker.level * 15 + sneaker.luck * 5
            buy_button = tk.Button(frame, text=f"Купить ({buy_cost} монет)", command=lambda s=sneaker, cost=buy_cost, idx=i: self.buy_sneaker(s, cost, idx))
            buy_button.pack(side=tk.RIGHT, padx=5)

    def buy_sneaker(self, sneaker_to_buy, cost, index_in_shop):
        """Покупка кроссовок из магазина."""
        if self.current_character.spend_coins(cost):
            # Добавляем кроссовки в БД персонажа
            new_sneaker_id = db.add_sneaker(
                self.current_character.id,
                sneaker_to_buy.name,
                sneaker_to_buy.luck,
                sneaker_to_buy.durability,
                sneaker_to_buy.max_durability,
                sneaker_to_buy.level
            )
            if new_sneaker_id:
                self.log_message(f"Вы купили

 кроссовки '{sneaker_to_buy.name}' за {cost} монет.")
                self.sneakers_in_shop.pop(index_in_shop) # Удаляем из списка магазина
                self.refresh_shop_items() # Обновляем отображение магазина
                self.update_info_labels()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить кроссовки в инвентарь.")
        else:
            messagebox.showwarning("Недостаточно средств", "У вас недостаточно монет для покупки.")

    def start_shop_refresh_timer(self):
        """Запускает таймер для обновления кроссовок в магазине."""
        self.root.after(SNESKER_SHOP_REFRESH_SECONDS * 1000, self.trigger_shop_refresh)

    def trigger_shop_refresh(self):
        """Вызывает событие обновления магазина."""
        if hasattr(self, 'shop_window') and self.shop_window.winfo_exists():
            self.log_message("В магазине появились новые кроссовки!")
            self.refresh_shop_items()
            self.start_shop_refresh_timer() # Перезапускаем таймер

    def equip_sneaker_dialog(self):
        """Открывает диалоговое окно для выбора кроссовок для экипировки."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        owned_sneakers_data = db.get_sneakers_by_character(self.current_character.id)
        if not owned_sneakers_data:
            messagebox.showinfo("Информация", "У вас нет кроссовок для экипировки.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Экипировать кроссовки")
        dialog.geometry("400x300")

        tk.Label(dialog, text="Выберите кроссовки для экипировки:", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE)
        sneaker_objects = []
        for s_data in owned_sneakers_data:
            sneaker = Sneaker(s_data[0], s_data[2], s_data[3], s_data[4], s_data[5], s_data[6], s_data[1])
            sneaker_objects.append(sneaker)
            listbox.insert(tk.END, str(sneaker))
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def on_equip():
            selected_index = listbox.curselection()
            if selected_index:
                sneaker_to_equip = sneaker_objects[selected_index[0]]
                self.current_character.equip_sneaker(sneaker_to_equip)
                self.log_message(f"Вы экипировали кроссовки: {sneaker_to_equip.name}.")
                self.update_info_labels()
                dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите кроссовки.")

        tk.Button(dialog, text="Экипировать", command=on_equip).pack(pady=5)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def repair_sneaker_dialog(self):
        """Открывает диалоговое окно для ремонта кроссовок."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        owned_sneakers_data = db.get_sneakers_by_character(self.current_character.id)
        if not owned_sneakers_data:
            messagebox.showinfo("Информация", "У вас нет кроссовок для ремонта.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Ремонт кроссовок")
        dialog.geometry("400x300")

        tk.Label(dialog, text="Выберите кроссовки для ремонта:", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE)
        sneaker_objects = []
        for s_data in owned_sneakers_data:
            sneaker = Sneaker(s_data[0], s_data[2], s_data[3], s_data[4], s_data[5], s_data[6], s_data[1])
            sneaker_objects.append(sneaker)
            listbox.insert(tk.END, f"{sneaker} (Прочность: {sneaker.durability}/{sneaker.max_durability})")
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def on_repair():

     selected_index = listbox.curselection()
            if selected_index:
                sneaker_to_repair = sneaker_objects[selected_index[0]]
                cost = SNEAKER_REPAIR_COST # Стоимость починки
                if self.current_character.spend_coins(cost):
                    # Восстанавливаем прочность (можно восстановить полностью или частично)
                    repair_amount = sneaker_to_repair.max_durability - sneaker_to_repair.durability
                    sneaker_to_repair.repair(repair_amount)
                    db.update_sneaker(sneaker_to_repair.id, durability=sneaker_to_repair.durability) # Сохраняем обновленную прочность
                    self.log_message(f"Вы починили кроссовки '{sneaker_to_repair.name}' за {cost} монет.")
                    self.update_info_labels()
                    dialog.destroy()
                else:
                    messagebox.showwarning("Недостаточно средств", "У вас недостаточно монет для ремонта.")
            else:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите кроссовки для ремонта.")

        tk.Button(dialog, text="Починить", command=on_repair).pack(pady=5)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)

    def start_walking(self):
        """Начинает процесс ходьбы."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        if self.current_character.energy < 10: # Требуется минимум 10 энергии для ходьбы
            messagebox.showwarning("Недостаточно энергии", "У вас недостаточно энергии для ходьбы. Попробуйте восстановить энергию.")
            return

        if not self.current_character.current_sneaker:
            messagebox.showwarning("Кроссовки не найдены", "Пожалуйста, экипируйте кроссовки, чтобы идти.")
            return

        if self.current_character.current_sneaker.durability <= 0:
            messagebox.showwarning("Кроссовки сломаны", "Ваши кроссовки сломаны и не могут быть использованы. Почините их.")
            return

        self.log_message("Вы начали идти...")
        # Имитируем ходьбу (можно сделать цикл или просто разовое действие)
        self.perform_walk_step()

    def perform_walk_step(self):
        """Выполняет один шаг ходьбы."""
        if not self.current_character:
            return

        # Расход энергии и прочности
        energy_cost = 5
        durability_cost = random.randint(1, 3)

        if self.current_character.spend_energy(energy_cost):
            self.current_character.current_sneaker.decrease_durability(durability_cost)
            self.current_character.add_steps(1) # Добавляем один шаг

            # Проверка на поломку кроссовок
            if self.current_character.current_sneaker.durability == 0:
                self.log_message("Ваши кроссовки сломались! Нужно их починить.")
                self.current_character.unequip_sneaker() # Автоматически снимаем сломанные кроссовки
                self.update_info_labels()
                return # Прекращаем ходьбу, если кроссовки сломались

            # Случайные события во время ходьбы
            self.handle_random_events()

            # Улучшение кроссовок (например, каждые 50 шагов)
            if self.current_character.steps_today % 50 == 0:
                self.current_character.current_sneaker.improve_luck()
                self.log_message(f"Удача ваших кроссовок '{self.current_character.current_sneaker.name}' улучшилась!")

            self.log_message(f"Вы сделали шаг. Энергия: -{energy_cost}. Прочность: -{durability_cost}.")
            self.update_info_labels()

            # Можно добавить паузу, чтобы имитировать движение, или сделать ходьбу интерактивной
            # Например, кнопка "Продолжить идти"

        else:
            self.log_message("Недостаточно энергии для продолжения ходьбы.")
            self.update_info_labels()

    def

handle_random_events(self):
        """Обрабатывает случайные события во время ходьбы."""
        event_chance = random.random() # Случайное число от 0.0 до 1.0

        if event_chance < 0.05: # 5% шанс найти банку
            self.find_energy_can()
        elif event_chance < 0.10: # 5% шанс найти монеты
            self.find_coins()
        elif event_chance < 0.12: # 2% шанс найти коробку
            self.find_mystery_box()

    def find_energy_can(self):
        """Персонаж находит банку с энергией."""
        energy_gain = random.randint(10, 30)
        self.current_character.restore_energy(energy_gain)
        self.log_message(f"Вы нашли банку и получили {energy_gain} энергии!")
        self.update_info_labels()

    def find_coins(self):
        """Персонаж находит монеты."""
        coins_gain = random.randint(20, 50)
        self.current_character.add_coins(coins_gain)
        self.log_message(f"Вы нашли {coins_gain} монет!")
        self.update_info_labels()

    def find_mystery_box(self):
        """Персонаж находит таинственную коробку."""
        self.log_message("Вы нашли таинственную коробку!")
        # В данной реализации коробка пока не добавляется в инвентарь,
        # а предлагается открыть сразу (если есть шаги).
        # Для этого нужен будет отдельный UI или диалог.

        # Добавим кнопку "Открыть коробку" прямо в лог, если это возможно,
        # или будем ждать, пока игрок сам нажмет кнопку "Открыть коробку" (если она будет в меню).
        # Пока что, просто уведомляем.

        # Для интерактивности, можно добавить кнопку в главное меню: "Открыть коробку".
        # Предположим, что игрок сам найдет эту кнопку.

    def open_mystery_box(self):
        """Открывает таинственную коробку."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        if self.current_character.steps_today >= BOX_OPEN_STEPS_COST:
            self.current_character.steps_today -= BOX_OPEN_STEPS_COST
            self.log_message(f"Вы потратили {BOX_OPEN_STEPS_COST} шагов, чтобы открыть коробку.")

            reward_type = random.choice(["energy", "coins", "sneaker"])
            if reward_type == "energy":
                energy_gain = random.randint(30, 70)
                self.current_character.restore_energy(energy_gain)
                self.log_message(f"Из коробки выпало: {energy_gain} энергии!")
            elif reward_type == "coins":
                coins_gain = random.randint(50, 150)
                self.current_character.add_coins(coins_gain)
                self.log_message(f"Из коробки выпало: {coins_gain} монет!")
            elif reward_type == "sneaker":
                # Генерируем случайный кроссовок
                sneaker_name = random.choice(["Lucky Runner", "Durable Walker", "Mystic Kicks"])
                luck = random.randint(2, 6)
                durability = random.randint(90, 150)
                max_durability = durability
                level = random.randint(2, 4)
                new_sneaker_id = db.add_sneaker(
                    self.current_character.id,
                    sneaker_name,
                    luck,
                    durability,
                    max_durability,
                    level
                )
                if new_sneaker_id:
                    self.log_message(f"Из коробки выпали новые кроссовки: {sneaker_name} (Удача: {luck}, Прочность: {durability}, Уровень: {level})")
                else:
                    self.log_message("Из коробки выпало что-то, но не удалось добавить в инвентарь.")

            self.update_info_labels()
        else:
            messagebox.showwarning("Недостаточно шагов", f"Вам нужно {BOX_OPEN_STEPS_COST} шагов, чтобы открыть коробку.")

    def sell_sneaker_dialog(self):
        """Открывает диалоговое окно для продажи кроссовок."""
        if not self.current_character:

messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        owned_sneakers_data = db.get_sneakers_by_character(self.current_character.id)
        if not owned_sneakers_data:
            messagebox.showinfo("Информация", "У вас нет кроссовок для продажи.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Продать кроссовки")
        dialog.geometry("400x300")

        tk.Label(dialog, text="Выберите кроссовки для продажи:", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE)
        sneaker_objects = []
        for s_data in owned_sneakers_data:
            sneaker = Sneaker(s_data[0], s_data[2], s_data[3], s_data[4], s_data[5], s_data[6], s_data[1])
            sneaker_objects.append(sneaker)
            listbox.insert(tk.END, f"{str(sneaker)} (ID: {sneaker.id})")
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def on_sell():
            selected_index = listbox.curselection()
            if selected_index:
                sneaker_to_sell = sneaker_objects[selected_index[0]]
                # Стоимость продажи может быть частью стоимости покупки или фиксированной
                sell_price = int(sneaker_to_sell.level * 20 + sneaker_to_sell.luck * 5) # Пример расчета цены
                if messagebox.askyesno("Подтверждение продажи", f"Вы уверены, что хотите продать '{sneaker_to_sell.name}' за {sell_price} монет?"):
                    if self.current_character.spend_coins(0): # Просто проверка, что игрок "существует"
                        self.current_character.add_coins(sell_price)
                        db.delete_sneaker(sneaker_to_sell.id)
                        self.log_message(f"Вы продали кроссовки '{sneaker_to_sell.name}' за {sell_price} монет.")
                        self.update_info_labels()
                        dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Пожалуйста, выберите кроссовки для продажи.")

        tk.Button(dialog, text="Продать", command=on_sell).pack(pady=5)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).pack(pady=5)


    def manual_restore_energy(self):
        """Восстанавливает энергию вручную (если это разрешено)."""
        if not self.current_character:
            messagebox.showinfo("Информация", "Пожалуйста, создайте или загрузите персонажа.")
            return

        # Можно сделать это бесплатным или за монеты
        if self.current_character.energy < MAX_ENERGY:
            self.current_character.restore_energy(MAX_ENERGY - self.current_character.energy)
            self.log_message("Энергия восстановлена вручную.")
            self.update_info_labels()
        else:
            self.log_message("Энергия уже полная.")

    def save_game(self):
        """Сохраняет текущий прогресс игры."""
        if self.current_character:
            db.save_game_state(self.current_character.id,
                               self.current_character.coins,
                               self.current_character.energy,
                               self.current_character.steps_today)
            # Также сохраняем состояние кроссовок, если они были изменены (прочность, уровень и т.д.)
            if self.current_character.current_sneaker:
                db.update_sneaker(self.current_character.current_sneaker.id,
                                  luck=self.current_character.current_sneaker.luck,
                                  durability=self.current_character.current_sneaker.durability,
                                  level=self.current_character.current_sneaker.level)
            self.log_message(f"Прогресс персонажа '{self.current_character.name}' сохранен.")
        else:
            self.log_message("Нет активного персонажа для сохранения.")

    def on_closing(self):
        """Обработка закрытия окна игры."""
        if self.current_character:
            if

messagebox.askyesno("Сохранение", "Вы хотите сохранить прогресс перед выходом?"):
                self.save_game()
        self.root.destroy()

    def start_timers(self):
        """Запускает все игровые таймеры."""
        self.check_energy_restore_interval()
        self.start_shop_refresh_timer() # Уже вызывается в open_shop, но для надежности

    def check_energy_restore_interval(self):
        """Периодически проверяет восстановление энергии."""
        if self.current_character:
            if self.current_character.check_energy_restore():
                self.log_message("Энергия была автоматически восстановлена.")
                self.update_info_labels()
        self.root.after(60000, self.check_energy_restore_interval) # Проверяем каждую минуту

# --- Главная часть программы ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
