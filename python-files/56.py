import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import os
import random
from datetime import datetime, timedelta

class RPGSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Виртуоз Жизни")
        self.root.geometry("1920x1080")
        self.root.resizable(True, True)
        
        # Устанавливаем черно-фиолетовую цветовую схему
        self.setup_theme()
        
        # Данные пользователя
        self.user_data = {
            "name": "", "surname": "", "password": "", "balance": 0,
            "weapon_license": False, "farm_license": False, "last_farm_click": None,
            "weapons": [], "current_job": None, "last_mission_time": None,
            "experience": 0, "level": 1, "click_count": 0, "house": None,
            "furniture": [], "food_items": [], "hunger": 100, "sleep": 100,
            "is_sick": False, "last_disease_check": None, "is_unconscious": False,
            "skills": {"strength": 1, "intelligence": 1, "charisma": 1},
            "reputation": 0, "achievements": [], "vehicles": [],
            "businesses": [], "investments": [], "pets": [],
            "clothing": [], "quests": [], "daily_rewards": [],
            "friends": [], "guild": None, "energy": 100,
            "last_login": None, "play_time": 0, "kill_count": 0,
            "crafting_level": 1, "mining_level": 1, "fishing_level": 1,
            "bank_deposit": 0, "loan": 0, "last_business_income": None
        }
        
        # Загрузка данных пользователя
        self.load_user_data()
        
        # Инициализация времени последнего входа
        if not self.user_data["last_login"]:
            self.user_data["last_login"] = datetime.now().isoformat()
        
        # Состояние фарма
        self.farming = False
        self.farm_thread = None
        self.mission_available = False
        
        # Создание вкладок
        self.create_notebook()
        
        # Создание всех интерфейсов
        self.create_all_tabs()
        
        # Обновление интерфейса
        self.update_balance()
        self.update_licenses_display()
        
        # Запуск систем
        self.root.after(1000, self.update_farm_timer)
        self.root.after(1000, self.check_missions)
        self.root.after(1000, self.update_needs)
        self.root.after(1000, self.check_disease)
        self.root.after(1000, self.update_play_time)
        self.root.after(60000, self.process_business_income)  # Каждую минуту проверяем доход от бизнеса
    
    def setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        self.bg_color = '#121212'
        self.fg_color = '#FFFFFF'
        self.accent_color = '#8A2BE2'
        self.secondary_color = '#4B0082'
        self.progress_color = '#9370DB'
        
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_color, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", self.fg_color)])
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton", background=self.accent_color, foreground=self.fg_color, focuscolor="none")
        style.map("TButton", background=[("active", self.secondary_color), ("pressed", self.secondary_color)])
        style.configure("Large.TButton", font=("Arial", 12), padding=10)
        style.configure("Danger.TButton", background="#FF4444", foreground=self.fg_color)
        
        self.root.configure(bg=self.bg_color)
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем фреймы для 30 вкладок
        self.tab_frames = {}
        tab_names = [
            "💰 Главная", "👤 Профиль", "📜 Лицензии", "⚡ Быстрый фарм",
            "🔫 Оружие", "🎒 Инвентарь", "💼 Работа", "⭐ Прокачка",
            "🏠 Недвижимость", "🛋️ Мебель", "🍕 Еда", "🏡 Дом",
            "🏥 Больница", "💪 Навыки", "🏆 Достижения", "🚗 Транспорт",
            "🏢 Бизнес", "📈 Инвестиции", "🐾 Питомцы", "👕 Одежда",
            "🎯 Задания", "🎁 Награды", "👥 Друзья", "⚔️ Гильдия",
            "⚒️ Крафт", "⛏️ Шахта", "🎣 Рыбалка", "🏛️ Банк",
            "🎰 Казино", "🌍 Карта"
        ]
        
        for name in tab_names:
            self.tab_frames[name] = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_frames[name], text=name)
    
    def create_all_tabs(self):
        # Создаем все вкладки
        self.create_main_tab()
        self.create_profile_tab()
        self.create_licenses_tab()
        self.create_quick_farm_tab()
        self.create_weapons_tab()
        self.create_inventory_tab()
        self.create_work_tab()
        self.create_skills_tab()
        self.create_real_estate_tab()
        self.create_furniture_tab()
        self.create_food_tab()
        self.create_house_tab()
        self.create_hospital_tab()
        self.create_attributes_tab()
        self.create_achievements_tab()
        self.create_vehicles_tab()
        self.create_business_tab()
        self.create_investments_tab()
        self.create_pets_tab()
        self.create_clothing_tab()
        self.create_quests_tab()
        self.create_rewards_tab()
        self.create_friends_tab()
        self.create_guild_tab()
        self.create_crafting_tab()
        self.create_mining_tab()
        self.create_fishing_tab()
        self.create_bank_tab()
        self.create_casino_tab()
        self.create_map_tab()
    
    def create_main_tab(self):
        frame = self.tab_frames["💰 Главная"]
        
        title = ttk.Label(frame, text="RPG x Симулятор", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Баланс
        self.balance_label = ttk.Label(frame, text="0 руб", font=("Arial", 28, "bold"), foreground=self.accent_color)
        self.balance_label.pack(pady=10)
        
        # Быстрые действия
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(pady=20)
        
        ttk.Button(actions_frame, text="💤 Поспать", command=self.sleep, width=15).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="🍕 Поесть", command=self.open_fridge, width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(actions_frame, text="💼 Работа", command=lambda: self.notebook.select(6), width=15).grid(row=0, column=2, padx=5, pady=5)
        
        # Статус
        self.status_label = ttk.Label(frame, text="", font=("Arial", 12), wraplength=400)
        self.status_label.pack(pady=10)
        
        # Благотворительность
        charity_frame = ttk.LabelFrame(frame, text="Благотворительность", padding=10)
        charity_frame.pack(pady=10)
        
        ttk.Button(charity_frame, text="Пожертвовать 1000 руб (+1 опыт)", command=self.donate_charity).pack(pady=5)
    
    def create_profile_tab(self):
        frame = self.tab_frames["👤 Профиль"]
        
        ttk.Label(frame, text="Профиль игрока", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Форма профиля
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, self.user_data["name"])
        
        ttk.Label(form_frame, text="Фамилия:").grid(row=1, column=0, sticky="w", pady=5)
        self.surname_entry = ttk.Entry(form_frame, width=20)
        self.surname_entry.grid(row=1, column=1, padx=5, pady=5)
        self.surname_entry.insert(0, self.user_data["surname"])
        
        ttk.Button(frame, text="Сохранить профиль", command=self.save_profile).pack(pady=10)
        ttk.Button(frame, text="Сбросить прогресс", command=self.reset_progress, style="Danger.TButton").pack(pady=5)
        
        # Информация о профиле
        self.profile_info = ttk.Label(frame, text="", font=("Arial", 12), wraplength=500)
        self.profile_info.pack(pady=20)
        
        self.update_profile_info()
    
    def create_licenses_tab(self):
        frame = self.tab_frames["📜 Лицензии"]
        ttk.Label(frame, text="Лицензии и разрешения", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Лицензия на оружие
        weapon_frame = ttk.LabelFrame(frame, text="Лицензия на оружие", padding=10)
        weapon_frame.pack(fill='x', pady=5, padx=20)
        
        ttk.Label(weapon_frame, text="Стоимость: 100,000 руб").pack(anchor='w')
        self.weapon_license_btn = ttk.Button(weapon_frame, text="Купить", command=lambda: self.buy_license("weapon", 100000))
        self.weapon_license_btn.pack(anchor='w', pady=5)
        
        self.update_licenses_display()
    
    def create_quick_farm_tab(self):
        frame = self.tab_frames["⚡ Быстрый фарм"]
        ttk.Label(frame, text="Быстрый заработок", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Button(frame, text="Получить 50,000 руб", command=self.farm_no_license, style="Large.TButton").pack(pady=10)
        self.farm_timer_label = ttk.Label(frame, text="Доступно")
        self.farm_timer_label.pack(pady=5)
    
    def create_weapons_tab(self):
        frame = self.tab_frames["🔫 Оружие"]
        ttk.Label(frame, text="Арсенал", font=("Arial", 20, "bold")).pack(pady=20)
        
        weapons = [
            ("Пистолет", 50000), ("Дробовик", 100000), 
            ("Снайперка", 150000), ("Автомат", 200000)
        ]
        
        for name, price in weapons:
            weapon_frame = ttk.LabelFrame(frame, text=name, padding=10)
            weapon_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(weapon_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(weapon_frame, text="Купить", command=lambda n=name, p=price: self.buy_weapon(n, p)).pack(anchor='w', pady=5)
    
    def create_inventory_tab(self):
        frame = self.tab_frames["🎒 Инвентарь"]
        ttk.Label(frame, text="Инвентарь", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Создаем Treeview для инвентаря
        columns = ("Предмет", "Количество", "Тип")
        self.inventory_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=150)
        
        self.inventory_tree.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.update_inventory_display()
    
    def create_work_tab(self):
        frame = self.tab_frames["💼 Работа"]
        ttk.Label(frame, text="Трудоустройство", font=("Arial", 20, "bold")).pack(pady=20)
        
        jobs = [
            ("👮 Полицейский", "police", "100,000 руб/задание", "Оружие + лицензия"),
            ("👨‍⚕️ Врач", "doctor", "50,000 руб/задание", "50 опыта"),
            ("👨‍🚒 Пожарный", "fireman", "125,000 руб/задание", "150 опыта")
        ]
        
        for name, job_type, salary, req in jobs:
            job_frame = ttk.LabelFrame(frame, text=name, padding=10)
            job_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(job_frame, text=f"Зарплата: {salary}").pack(anchor='w')
            ttk.Label(job_frame, text=f"Требования: {req}").pack(anchor='w')
            ttk.Button(job_frame, text="Устроиться", command=lambda t=job_type: self.get_job(t)).pack(anchor='w', pady=5)
        
        # Кнопка для выполнения задания
        ttk.Button(frame, text="Выполнить задание", command=self.do_job, style="Large.TButton").pack(pady=20)
        self.job_status_label = ttk.Label(frame, text="")
        self.job_status_label.pack(pady=5)
    
    def create_skills_tab(self):
        frame = self.tab_frames["⭐ Прокачка"]
        ttk.Label(frame, text="Прокачка персонажа", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Уровень и опыт
        exp_frame = ttk.LabelFrame(frame, text="Опыт", padding=10)
        exp_frame.pack(fill='x', pady=5, padx=20)
        
        self.exp_label = ttk.Label(exp_frame, text=f"Уровень: {self.user_data['level']} | Опыт: {self.user_data['experience']}")
        self.exp_label.pack(anchor='w')
        
        ttk.Button(exp_frame, text="Получить опыт (+10)", command=self.gain_experience).pack(anchor='w', pady=5)
    
    def create_real_estate_tab(self):
        frame = self.tab_frames["🏠 Недвижимость"]
        ttk.Label(frame, text="Недвижимость", font=("Arial", 20, "bold")).pack(pady=20)
        
        properties = [
            ("🏢 Квартира", 500000), ("🏠 Дом", 1000000), 
            ("🏰 Особняк", 5000000), ("🏢 Пентхаус", 10000000)
        ]
        
        for name, price in properties:
            prop_frame = ttk.LabelFrame(frame, text=name, padding=10)
            prop_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(prop_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(prop_frame, text="Купить", command=lambda n=name, p=price: self.buy_house(n, p)).pack(anchor='w', pady=5)
    
    def create_furniture_tab(self):
        frame = self.tab_frames["🛋️ Мебель"]
        ttk.Label(frame, text="Мебель и интерьер", font=("Arial", 20, "bold")).pack(pady=20)
        
        furniture = [
            ("🛋️ Диван", 50000), ("🪑 Стол", 30000),
            ("🛏️ Кровать", 75000), ("📺 Телевизор", 100000)
        ]
        
        for name, price in furniture:
            furn_frame = ttk.LabelFrame(frame, text=name, padding=10)
            furn_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(furn_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(furn_frame, text="Купить", command=lambda n=name, p=price: self.buy_furniture(n, p)).pack(anchor='w', pady=5)
    
    def create_food_tab(self):
        frame = self.tab_frames["🍕 Еда"]
        ttk.Label(frame, text="Продукты питания", font=("Arial", 20, "bold")).pack(pady=20)
        
        foods = [
            ("🥪 Бутерброд", 500, 20), ("🍕 Пицца", 1500, 50),
            ("🥩 Стейк", 3000, 80), ("🍣 Суши", 5000, 100)
        ]
        
        for name, price, hunger in foods:
            food_frame = ttk.LabelFrame(frame, text=name, padding=10)
            food_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(food_frame, text=f"Цена: {price:,} руб | +{hunger} голода").pack(anchor='w')
            ttk.Button(food_frame, text="Купить", command=lambda n=name, p=price, h=hunger: self.buy_food(n, p, h)).pack(anchor='w', pady=5)
    
    def create_house_tab(self):
        frame = self.tab_frames["🏡 Дом"]
        ttk.Label(frame, text="Ваш дом", font=("Arial", 20, "bold")).pack(pady=20)
        
        if not self.user_data["house"]:
            ttk.Label(frame, text="У вас нет дома! Купите недвижимость во вкладке 'Недвижимость'", 
                     foreground="orange").pack(pady=50)
            return
        
        # Отображаем информацию о доме
        house_info = ttk.LabelFrame(frame, text="Информация", padding=10)
        house_info.pack(fill='x', pady=5, padx=20)
        
        ttk.Label(house_info, text=f"Тип: {self.user_data['house']}").pack(anchor='w')
        ttk.Label(house_info, text=f"Мебель: {len(self.user_data['furniture'])} предметов").pack(anchor='w')
        
        # Действия в доме
        actions = ttk.LabelFrame(frame, text="Действия", padding=10)
        actions.pack(fill='x', pady=5, padx=20)
        
        ttk.Button(actions, text="💤 Поспать (+50 сна)", command=self.sleep, width=20).pack(pady=5)
        ttk.Button(actions, text="🧊 Открыть холодильник", command=self.open_fridge, width=20).pack(pady=5)
    
    def create_hospital_tab(self):
        frame = self.tab_frames["🏥 Больница"]
        ttk.Label(frame, text="Медицинский центр", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Button(frame, text="Лечение от голода - 25,000 руб", 
                  command=lambda: self.get_treatment("hunger", 25000)).pack(pady=5)
        ttk.Button(frame, text="Лечение от болезни - 100,000 руб", 
                  command=lambda: self.get_treatment("disease", 100000)).pack(pady=5)
    
    def create_attributes_tab(self):
        frame = self.tab_frames["💪 Навыки"]
        ttk.Label(frame, text="Характеристики", font=("Arial", 20, "bold")).pack(pady=20)
        
        skills = ttk.LabelFrame(frame, text="Навыки", padding=10)
        skills.pack(fill='x', pady=5, padx=20)
        
        for skill, level in self.user_data["skills"].items():
            skill_frame = ttk.Frame(skills)
            skill_frame.pack(fill='x', pady=2)
            ttk.Label(skill_frame, text=f"{skill.title()}: {level}").pack(side='left')
            ttk.Button(skill_frame, text="Прокачать", 
                      command=lambda s=skill: self.upgrade_skill(s)).pack(side='right')
    
    def create_achievements_tab(self):
        frame = self.tab_frames["🏆 Достижения"]
        ttk.Label(frame, text="Достижения", font=("Arial", 20, "bold")).pack(pady=20)
        
        achievements = [
            ("💰 Первые деньги", "Заработать 100,000 руб", lambda: self.user_data["balance"] >= 100000),
            ("🏠 Домовладелец", "Купить первый дом", lambda: self.user_data["house"] is not None),
            ("💼 Карьерист", "Устроиться на работу", lambda: self.user_data["current_job"] is not None),
            ("⚔️ Воин", "Купить первое оружие", lambda: len(self.user_data["weapons"]) > 0)
        ]
        
        for name, desc, condition in achievements:
            ach_frame = ttk.LabelFrame(frame, text=name, padding=10)
            ach_frame.pack(fill='x', pady=5, padx=20)
            ttk.Label(ach_frame, text=desc).pack(anchor='w')
            
            # Проверяем выполнено ли достижение
            if condition():
                ttk.Label(ach_frame, text="✅ Выполнено", foreground="green").pack(anchor='w')
            else:
                ttk.Label(ach_frame, text="❌ Не выполнено", foreground="red").pack(anchor='w')
    
    def create_vehicles_tab(self):
        frame = self.tab_frames["🚗 Транспорт"]
        ttk.Label(frame, text="Автопарк", font=("Arial", 20, "bold")).pack(pady=20)
        
        vehicles = [
            ("🚗 Седан", 500000), ("🚙 Внедорожник", 1000000),
            ("🏎️ Спорткар", 5000000), ("🚁 Вертолет", 20000000)
        ]
        
        for name, price in vehicles:
            vehicle_frame = ttk.LabelFrame(frame, text=name, padding=10)
            vehicle_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(vehicle_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(vehicle_frame, text="Купить", 
                      command=lambda n=name, p=price: self.buy_vehicle(n, p)).pack(anchor='w', pady=5)
    
    def create_business_tab(self):
        frame = self.tab_frames["🏢 Бизнес"]
        ttk.Label(frame, text="Бизнес", font=("Arial", 20, "bold")).pack(pady=20)
        
        businesses = [
            ("🏪 Магазин", 1000000, 50000), ("🏢 Офис", 5000000, 200000),
            ("🏭 Завод", 20000000, 1000000)
        ]
        
        for name, price, income in businesses:
            biz_frame = ttk.LabelFrame(frame, text=name, padding=10)
            biz_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(biz_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Label(biz_frame, text=f"Доход: {income:,} руб/день").pack(anchor='w')
            ttk.Button(biz_frame, text="Купить", 
                      command=lambda n=name, p=price, i=income: self.buy_business(n, p, i)).pack(anchor='w', pady=5)
    
    def create_investments_tab(self):
        frame = self.tab_frames["📈 Инвестиции"]
        ttk.Label(frame, text="Инвестиции", font=("Arial", 20, "bold")).pack(pady=20)
        
        investments = [
            ("📊 Акции", 50000, 1.1), ("🏦 Облигации", 100000, 1.05),
            ("💰 Криптовалюта", 50000, 1.2)
        ]
        
        for name, min_invest, multiplier in investments:
            inv_frame = ttk.LabelFrame(frame, text=name, padding=10)
            inv_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(inv_frame, text=f"Мин. инвестиция: {min_invest:,} руб").pack(anchor='w')
            ttk.Label(inv_frame, text=f"Множитель: x{multiplier}").pack(anchor='w')
            ttk.Button(inv_frame, text="Инвестировать", 
                      command=lambda n=name, m=min_invest, mult=multiplier: self.invest_money(n, m, mult)).pack(anchor='w', pady=5)
    
    def create_pets_tab(self):
        frame = self.tab_frames["🐾 Питомцы"]
        ttk.Label(frame, text="Питомцы", font=("Arial", 20, "bold")).pack(pady=20)
        
        pets = [
            ("🐶 Собака", 50000), ("🐱 Кот", 30000),
            ("🐴 Лошадь", 200000), ("🐉 Дракон", 5000000)
        ]
        
        for name, price in pets:
            pet_frame = ttk.LabelFrame(frame, text=name, padding=10)
            pet_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(pet_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(pet_frame, text="Купить", 
                      command=lambda n=name, p=price: self.buy_pet(n, p)).pack(anchor='w', pady=5)
    
    def create_clothing_tab(self):
        frame = self.tab_frames["👕 Одежда"]
        ttk.Label(frame, text="Гардероб", font=("Arial", 20, "bold")).pack(pady=20)
        
        clothes = [
            ("👕 Футболка", 5000), ("👔 Костюм", 50000),
            ("🥋 Броня", 100000), ("👑 Корона", 1000000)
        ]
        
        for name, price in clothes:
            cloth_frame = ttk.LabelFrame(frame, text=name, padding=10)
            cloth_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(cloth_frame, text=f"Цена: {price:,} руб").pack(anchor='w')
            ttk.Button(cloth_frame, text="Купить", 
                      command=lambda n=name, p=price: self.buy_clothing(n, p)).pack(anchor='w', pady=5)
    
    def create_quests_tab(self):
        frame = self.tab_frames["🎯 Задания"]
        ttk.Label(frame, text="Задания", font=("Arial", 20, "bold")).pack(pady=20)
        
        quests = [
            ("💰 Накопить 1,000,000 руб", 50000, lambda: self.user_data["balance"] >= 1000000),
            ("🏠 Купить дом", 25000, lambda: self.user_data["house"] is not None),
            ("💼 Устроиться на работу", 10000, lambda: self.user_data["current_job"] is not None)
        ]
        
        for desc, reward, condition in quests:
            quest_frame = ttk.LabelFrame(frame, text=f"Награда: {reward:,} руб", padding=10)
            quest_frame.pack(fill='x', pady=5, padx=20)
            ttk.Label(quest_frame, text=desc).pack(anchor='w')
            
            if condition():
                ttk.Label(quest_frame, text="✅ Выполнено", foreground="green").pack(anchor='w')
            else:
                ttk.Label(quest_frame, text="❌ Не выполнено", foreground="red").pack(anchor='w')
    
    def create_rewards_tab(self):
        frame = self.tab_frames["🎁 Награды"]
        ttk.Label(frame, text="Ежедневные награды", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Button(frame, text="Получить ежедневную награду", command=self.claim_daily_reward, 
                  style="Large.TButton").pack(pady=20)
        
        # Отображение статуса награды
        self.reward_status = ttk.Label(frame, text="")
        self.reward_status.pack(pady=10)
        self.update_reward_status()
    
    def create_friends_tab(self):
        frame = self.tab_frames["👥 Друзья"]
        ttk.Label(frame, text="Друзья", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Label(frame, text="Система друзей скоро будет добавлена!", foreground="orange").pack(pady=50)
    
    def create_guild_tab(self):
        frame = self.tab_frames["⚔️ Гильдия"]
        ttk.Label(frame, text="Гильдия", font=("Arial", 20, "bold")).pack(pady=20)
        
        if not self.user_data["guild"]:
            ttk.Button(frame, text="Создать гильдию", command=self.create_guild).pack(pady=10)
            ttk.Button(frame, text="Вступить в гильдию").pack(pady=10)
        else:
            ttk.Label(frame, text=f"Гильдия: {self.user_data['guild']}").pack(pady=10)
            ttk.Button(frame, text="Покинуть гильдию", command=self.leave_guild).pack(pady=10)
    
    def create_crafting_tab(self):
        frame = self.tab_frames["⚒️ Крафт"]
        ttk.Label(frame, text="Крафтинг", font=("Arial", 20, "bold")).pack(pady=20)
        
        recipes = [
            ("🛡️ Щит", "100 дерева, 50 железа"),
            ("⚔️ Меч", "50 железа, 25 золота"),
            ("💎 Украшение", "10 алмазов, 5 изумрудов")
        ]
        
        for name, materials in recipes:
            recipe_frame = ttk.LabelFrame(frame, text=name, padding=10)
            recipe_frame.pack(fill='x', pady=5, padx=20)
            
            ttk.Label(recipe_frame, text=f"Материалы: {materials}").pack(anchor='w')
            ttk.Button(recipe_frame, text="Создать", command=lambda n=name: self.craft_item(n)).pack(anchor='w', pady=5)
    
    def create_mining_tab(self):
        frame = self.tab_frames["⛏️ Шахта"]
        ttk.Label(frame, text="Шахта", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Button(frame, text="⛏️ Добыть ресурсы", command=self.mine_resources, 
                  style="Large.TButton").pack(pady=20)
        
        self.mining_status = ttk.Label(frame, text=f"Уровень добычи: {self.user_data['mining_level']:.1f}")
        self.mining_status.pack(pady=10)
    
    def create_fishing_tab(self):
        frame = self.tab_frames["🎣 Рыбалка"]
        ttk.Label(frame, text="Рыбалка", font=("Arial", 20, "bold")).pack(pady=20)
        
        ttk.Button(frame, text="🎣 Рыбачить", command=self.go_fishing, 
                  style="Large.TButton").pack(pady=20)
        
        self.fishing_status = ttk.Label(frame, text=f"Уровень рыбалки: {self.user_data['fishing_level']:.1f}")
        self.fishing_status.pack(pady=10)
    
    def create_bank_tab(self):
        frame = self.tab_frames["🏛️ Банк"]
        ttk.Label(frame, text="Банк", font=("Arial", 20, "bold")).pack(pady=20)
        
        bank_frame = ttk.LabelFrame(frame, text="Банковские операции", padding=10)
        bank_frame.pack(fill='x', pady=5, padx=20)
        
        ttk.Button(bank_frame, text="Вклад под 5%", command=self.make_deposit).pack(pady=5)
        ttk.Button(bank_frame, text="Взять кредит", command=self.take_loan).pack(pady=5)
        ttk.Button(bank_frame, text="Погасить кредит", command=self.repay_loan).pack(pady=5)
        
        # Информация о банковских операциях
        info_frame = ttk.LabelFrame(frame, text="Информация", padding=10)
        info_frame.pack(fill='x', pady=5, padx=20)
        
        self.bank_info = ttk.Label(info_frame, text="")
        self.bank_info.pack(anchor='w')
        self.update_bank_info()
    
    def create_casino_tab(self):
        frame = self.tab_frames["🎰 Казино"]
        ttk.Label(frame, text="Казино", font=("Arial", 20, "bold")).pack(pady=20)
        
        games_frame = ttk.LabelFrame(frame, text="Азартные игры", padding=10)
        games_frame.pack(fill='x', pady=5, padx=20)
        
        ttk.Button(games_frame, text="🎰 Игровой автомат", command=self.play_slot_machine).pack(pady=5)
        ttk.Button(games_frame, text="🎲 Кости", command=self.play_dice).pack(pady=5)
        ttk.Button(games_frame, text="🃏 Блэкджек", command=self.play_blackjack).pack(pady=5)
    
    def create_map_tab(self):
        frame = self.tab_frames["🌍 Карта"]
        ttk.Label(frame, text="Карта мира", font=("Arial", 20, "bold")).pack(pady=20)
        
        locations = [
            "🏙️ Город", "🌲 Лес", "🏔️ Горы", 
            "🏖️ Пляж", "🏰 Замок", "🕵️ Секретная зона"
        ]
        
        for location in locations:
            ttk.Button(frame, text=location, command=lambda l=location: self.travel_to(l), 
                      width=20).pack(pady=5)
    
    # Базовые методы игры
    def update_balance(self):
        self.balance_label.config(text=f"{self.user_data['balance']:,} руб")
        self.update_status()
    
    def update_status(self):
        status = f"Голод: {self.user_data['hunger']}/100 | Сон: {self.user_data['sleep']}/100"
        if self.user_data["is_sick"]:
            status += " | 🤒 Болен"
        if self.user_data["is_unconscious"]:
            status += " | 😵 Без сознания"
        self.status_label.config(text=status)
    
    def update_profile_info(self):
        info = f"Игрок: {self.user_data['name']} {self.user_data['surname']}\n"
        info += f"Уровень: {self.user_data['level']} | Опыт: {self.user_data['experience']}\n"
        info += f"Баланс: {self.user_data['balance']:,} руб\n"
        info += f"Дом: {self.user_data['house'] or 'Нет'}\n"
        info += f"Работа: {self.get_job_name(self.user_data['current_job'])}"
        self.profile_info.config(text=info)
    
    def update_inventory_display(self):
        # Очищаем Treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Добавляем оружие
        for weapon in self.user_data["weapons"]:
            self.inventory_tree.insert("", "end", values=(weapon, 1, "Оружие"))
        
        # Добавляем мебель
        for furniture in self.user_data["furniture"]:
            self.inventory_tree.insert("", "end", values=(furniture, 1, "Мебель"))
        
        # Добавляем еду
        food_count = {}
        for food in self.user_data["food_items"]:
            name = food["name"]
            food_count[name] = food_count.get(name, 0) + 1
        
        for name, count in food_count.items():
            self.inventory_tree.insert("", "end", values=(name, count, "Еда"))
    
    def update_licenses_display(self):
        if self.user_data["weapon_license"]:
            self.weapon_license_btn.config(text="Куплено", state="disabled")
        if self.user_data["farm_license"]:
            self.farm_license_btn.config(text="Куплено", state="disabled")
    
    def update_reward_status(self):
        today = datetime.now().date().isoformat()
        if today in self.user_data["daily_rewards"]:
            self.reward_status.config(text="Награда уже получена сегодня", foreground="orange")
        else:
            self.reward_status.config(text="Награда доступна", foreground="green")
    
    def get_job_name(self, job_type):
        job_names = {
            "police": "Полицейский", "doctor": "Врач", 
            "fireman": "Пожарный", None: "Безработный"
        }
        return job_names.get(job_type, "Безработный")
    
    # Основные игровые методы
    def buy_house(self, house_type, cost):
        if self.user_data["house"]:
            messagebox.showwarning("Ошибка", "У вас уже есть дом!")
            return
        if self.user_data["balance"] < cost:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        
        self.user_data["balance"] -= cost
        self.user_data["house"] = house_type
        self.update_balance()
        self.update_profile_info()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{house_type} куплен!")
    
    def sleep(self):
        if self.user_data["sleep"] >= 100:
            messagebox.showinfo("Инфо", "Вы не хотите спать!")
            return
        self.user_data["sleep"] = min(100, self.user_data["sleep"] + 50)
        self.update_status()
        self.save_user_data()
        messagebox.showinfo("Отдых", "Вы поспали и восстановили силы!")
    
    def open_fridge(self):
        if not self.user_data["food_items"]:
            messagebox.showinfo("Холодильник", "Холодильник пуст!")
            return
        
        fridge_window = tk.Toplevel(self.root)
        fridge_window.title("Холодильник")
        fridge_window.geometry("300x400")
        fridge_window.configure(bg=self.bg_color)
        
        for food in self.user_data["food_items"]:
            frame = ttk.Frame(fridge_window)
            frame.pack(fill='x', pady=2, padx=10)
            ttk.Label(frame, text=food["name"]).pack(side='left')
            ttk.Button(frame, text="Съесть", 
                      command=lambda f=food: self.eat_food(f, fridge_window)).pack(side='right')
    
    def eat_food(self, food, window):
        self.user_data["hunger"] = min(100, self.user_data["hunger"] + food["hunger_restore"])
        self.user_data["food_items"].remove(food)
        self.update_status()
        self.update_inventory_display()
        self.save_user_data()
        window.destroy()
        messagebox.showinfo("Поел", f"Вы съели {food['name']}!")
    
    def buy_food(self, name, price, hunger):
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["food_items"].append({"name": name, "hunger_restore": hunger})
        self.update_balance()
        self.update_inventory_display()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def buy_furniture(self, name, price):
        if not self.user_data["house"]:
            messagebox.showerror("Ошибка", "Сначала купите дом!")
            return
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["furniture"].append(name)
        self.update_balance()
        self.update_inventory_display()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def buy_weapon(self, name, price):
        if not self.user_data["weapon_license"]:
            messagebox.showerror("Ошибка", "Нужна лицензия на оружие!")
            return
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["weapons"].append(name)
        self.update_balance()
        self.update_inventory_display()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def buy_license(self, license_type, cost):
        if self.user_data["balance"] < cost:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= cost
        self.user_data[f"{license_type}_license"] = True
        self.update_balance()
        self.update_licenses_display()
        self.save_user_data()
        messagebox.showinfo("Успех", "Лицензия куплена!")
    
    def farm_no_license(self):
        if self.user_data["last_farm_click"]:
            last_click = datetime.fromisoformat(self.user_data["last_farm_click"])
            if (datetime.now() - last_click).total_seconds() < 60:
                messagebox.showwarning("Ошибка", "Подождите 1 минуту!")
                return
        
        self.user_data["balance"] += 50000
        self.user_data["last_farm_click"] = datetime.now().isoformat()
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", "50,000 руб получены!")
    
    def gain_experience(self):
        if self.user_data["level"] >= 25:
            messagebox.showinfo("Максимум", "Достигнут максимальный уровень!")
            return
        self.user_data["experience"] += 10
        self.user_data["click_count"] += 1
        
        # Проверяем повышение уровня (каждые 50 опыта)
        required_exp = self.user_data["level"] * 50
        if self.user_data["experience"] >= required_exp:
            self.user_data["level"] += 1
            self.user_data["experience"] -= required_exp
            messagebox.showinfo("Уровень UP!", f"Новый уровень: {self.user_data['level']}!")
        
        self.exp_label.config(text=f"Уровень: {self.user_data['level']} | Опыт: {self.user_data['experience']}")
        self.update_profile_info()
        self.save_user_data()
    
    def donate_charity(self):
        if self.user_data["balance"] < 1000:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= 1000
        self.user_data["experience"] += 1
        self.update_balance()
        self.update_profile_info()
        self.save_user_data()
        messagebox.showinfo("Спасибо!", "Пожертвование принято!")
    
    def get_job(self, job_type):
        if job_type == "police" and (not self.user_data["weapon_license"] or not self.user_data["weapons"]):
            messagebox.showerror("Ошибка", "Нужна лицензия и оружие!")
            return
        if job_type == "doctor" and self.user_data["experience"] < 50:
            messagebox.showerror("Ошибка", "Нужно 50 опыта!")
            return
        if job_type == "fireman" and self.user_data["experience"] < 150:
            messagebox.showerror("Ошибка", "Нужно 150 опыта!")
            return
        
        self.user_data["current_job"] = job_type
        self.update_profile_info()
        self.save_user_data()
        messagebox.showinfo("Успех", f"Вы устроились {self.get_job_name(job_type)}ом!")
    
    def do_job(self):
        if not self.user_data["current_job"]:
            messagebox.showerror("Ошибка", "Сначала устройтесь на работу!")
            return
        
        # Проверяем время последнего задания
        if self.user_data["last_mission_time"]:
            last_mission = datetime.fromisoformat(self.user_data["last_mission_time"])
            if (datetime.now() - last_mission).total_seconds() < 300:  # 5 минут
                messagebox.showwarning("Ошибка", "Подождите 5 минут перед следующим заданием!")
                return
        
        # Выплачиваем зарплату в зависимости от работы
        salary = 0
        if self.user_data["current_job"] == "police":
            salary = 100000
        elif self.user_data["current_job"] == "doctor":
            salary = 50000
        elif self.user_data["current_job"] == "fireman":
            salary = 125000
        
        self.user_data["balance"] += salary
        self.user_data["last_mission_time"] = datetime.now().isoformat()
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Задание выполнено", f"Вы получили {salary:,} руб!")
    
    def get_treatment(self, treatment_type, cost):
        if self.user_data["balance"] < cost:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= cost
        if treatment_type == "hunger":
            self.user_data["is_unconscious"] = False
            self.user_data["hunger"] = 50
        else:
            self.user_data["is_sick"] = False
        self.update_balance()
        self.update_status()
        self.save_user_data()
        messagebox.showinfo("Выздоровел", "Лечение прошло успешно!")
    
    def save_profile(self):
        self.user_data["name"] = self.name_entry.get()
        self.user_data["surname"] = self.surname_entry.get()
        self.update_profile_info()
        self.save_user_data()
        messagebox.showinfo("Успех", "Профиль сохранен!")
    
    def reset_progress(self):
        if messagebox.askyesno("Подтверждение", "Точно сбросить весь прогресс?"):
            self.user_data = {
                "name": "", "surname": "", "password": "", "balance": 0,
                "weapon_license": False, "farm_license": False, "last_farm_click": None,
                "weapons": [], "current_job": None, "last_mission_time": None,
                "experience": 0, "level": 1, "click_count": 0, "house": None,
                "furniture": [], "food_items": [], "hunger": 100, "sleep": 100,
                "is_sick": False, "last_disease_check": None, "is_unconscious": False,
                "skills": {"strength": 1, "intelligence": 1, "charisma": 1},
                "reputation": 0, "achievements": [], "vehicles": [],
                "businesses": [], "investments": [], "pets": [],
                "clothing": [], "quests": [], "daily_rewards": [],
                "friends": [], "guild": None, "energy": 100,
                "last_login": None, "play_time": 0, "kill_count": 0,
                "crafting_level": 1, "mining_level": 1, "fishing_level": 1,
                "bank_deposit": 0, "loan": 0, "last_business_income": None
            }
            self.name_entry.delete(0, tk.END)
            self.surname_entry.delete(0, tk.END)
            self.update_balance()
            self.update_profile_info()
            self.update_inventory_display()
            self.update_licenses_display()
            self.save_user_data()
            messagebox.showinfo("Успех", "Прогресс сброшен!")
    
    # Новые методы для дополнительных функций
    def buy_vehicle(self, name, price):
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["vehicles"].append(name)
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def buy_business(self, name, price, income):
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["businesses"].append({"name": name, "income": income})
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", f"Бизнес '{name}' куплен!")
    
    def process_business_income(self):
        # Обработка дохода от бизнеса каждый день
        if self.user_data["last_business_income"]:
            last_income = datetime.fromisoformat(self.user_data["last_business_income"])
            if (datetime.now() - last_income).total_seconds() >= 86400:  # 24 часа
                total_income = 0
                for business in self.user_data["businesses"]:
                    total_income += business["income"]
                
                if total_income > 0:
                    self.user_data["balance"] += total_income
                    self.user_data["last_business_income"] = datetime.now().isoformat()
                    self.update_balance()
                    self.save_user_data()
                    # messagebox.showinfo("Доход от бизнеса", f"Вы получили {total_income:,} руб от вашего бизнеса!")
        
        self.root.after(60000, self.process_business_income)  # Проверяем каждую минуту
    
    def buy_pet(self, name, price):
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["pets"].append(name)
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def buy_clothing(self, name, price):
        if self.user_data["balance"] < price:
            messagebox.showerror("Ошибка", "Недостаточно средств!")
            return
        self.user_data["balance"] -= price
        self.user_data["clothing"].append(name)
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", f"{name} куплен!")
    
    def upgrade_skill(self, skill):
        cost = self.user_data["skills"][skill] * 1000
        if self.user_data["balance"] < cost:
            messagebox.showerror("Ошибка", f"Нужно {cost} руб!")
            return
        self.user_data["balance"] -= cost
        self.user_data["skills"][skill] += 1
        self.update_balance()
        self.save_user_data()
        messagebox.showinfo("Успех", f"Навык {skill} улучшен!")
    
    def claim_daily_reward(self):
        today = datetime.now().date().isoformat()
        if today in self.user_data["daily_rewards"]:
            messagebox.showinfo("Ошибка", "Награда уже получена сегодня!")
            return
        
        reward = random.randint(5000, 50000)
        self.user_data["balance"] += reward
        self.user_data["daily_rewards"].append(today)
        self.update_balance()
        self.update_reward_status()
        self.save_user_data()
        messagebox.showinfo("Награда", f"Получено {reward} руб!")
    
    def create_guild(self):
        guild_name = simpledialog.askstring("Гильдия", "Введите название гильдии:")
        if guild_name:
            self.user_data["guild"] = guild_name
            self.save_user_data()
            messagebox.showinfo("Успех", f"Гильдия '{guild_name}' создана!")
    
    def leave_guild(self):
        if messagebox.askyesno("Подтверждение", "Точно покинуть гильдию?"):
            self.user_data["guild"] = None
            self.save_user_data()
            messagebox.showinfo("Успех", "Вы покинули гильдию!")
    
    def craft_item(self, item_name):
        messagebox.showinfo("Крафт", f"Создание {item_name} скоро будет доступно!")
    
    def mine_resources(self):
        resources = ["Железо", "Золото", "Алмазы", "Изумруды"]
        resource = random.choice(resources)
        amount = random.randint(1, 5) * self.user_data["mining_level"]
        
        # Добавляем ресурсы в инвентарь (упрощенно)
        self.user_data["mining_level"] += 0.1
        self.mining_status.config(text=f"Уровень добычи: {self.user_data['mining_level']:.1f}")
        self.save_user_data()
        messagebox.showinfo("Добыча", f"Вы добыли {amount} {resource}!")
    
    def go_fishing(self):
        fish_types = ["Карп", "Щука", "Лосось", "Акула"]
        fish = random.choice(fish_types)
        size = random.randint(1, 10) * self.user_data["fishing_level"]
        
        self.user_data["fishing_level"] += 0.1
        self.fishing_status.config(text=f"Уровень рыбалки: {self.user_data['fishing_level']:.1f}")
        self.save_user_data()
        messagebox.showinfo("Рыбалка", f"Вы поймали {fish} размером {size} см!")
    
    def make_deposit(self):
        amount = simpledialog.askinteger("Вклад", "Сумма вклада:", minvalue=1000, maxvalue=self.user_data["balance"])
        if amount:
            self.user_data["balance"] -= amount
            self.user_data["bank_deposit"] += amount
            self.update_balance()
            self.update_bank_info()
            self.save_user_data()
            messagebox.showinfo("Вклад", f"Вклад на {amount} руб оформлен!")
    
    def take_loan(self):
        amount = simpledialog.askinteger("Кредит", "Сумма кредита:", minvalue=1000, maxvalue=1000000)
        if amount:
            self.user_data["balance"] += amount
            self.user_data["loan"] += amount
            self.update_balance()
            self.update_bank_info()
            self.save_user_data()
            messagebox.showinfo("Кредит", f"Кредит на {amount} руб получен!")
    
    def repay_loan(self):
        if self.user_data["loan"] <= 0:
            messagebox.showinfo("Инфо", "У вас нет кредита!")
            return
        
        amount = simpledialog.askinteger("Погашение кредита", "Сумма погашения:", 
                                       minvalue=1000, maxvalue=min(self.user_data["balance"], self.user_data["loan"]))
        if amount:
            self.user_data["balance"] -= amount
            self.user_data["loan"] -= amount
            self.update_balance()
            self.update_bank_info()
            self.save_user_data()
            messagebox.showinfo("Погашение", f"Кредит погашен на {amount} руб!")
    
    def update_bank_info(self):
        info = f"Вклад: {self.user_data['bank_deposit']:,} руб\n"
        info += f"Кредит: {self.user_data['loan']:,} руб"
        self.bank_info.config(text=info)
    
    def invest_money(self, investment_type, min_amount, multiplier):
        amount = simpledialog.askinteger("Инвестиции", f"Сумма инвестиции в {investment_type}:", 
                                       minvalue=min_amount, maxvalue=self.user_data["balance"])
        if amount:
            self.user_data["balance"] -= amount
            profit = int(amount * (multiplier - 1))
            self.user_data["balance"] += amount + profit
            self.user_data["investments"].append({
                "type": investment_type,
                "amount": amount,
                "profit": profit
            })
            self.update_balance()
            self.save_user_data()
            messagebox.showinfo("Инвестиции", f"Инвестиция принесла {profit} руб прибыли!")
    
    def play_slot_machine(self):
        if self.user_data["balance"] < 1000:
            messagebox.showerror("Ошибка", "Нужно 1000 руб для игры!")
            return
        
        self.user_data["balance"] -= 1000
        symbols = ["🍒", "🍋", "🍉", "⭐", "7️⃣"]
        result = [random.choice(symbols) for _ in range(3)]
        
        if result[0] == result[1] == result[2]:
            win = 10000
            self.user_data["balance"] += win
            messagebox.showinfo("ДЖЕКПОТ!", f"{' '.join(result)}\nВыигрыш: {win} руб!")
        else:
            messagebox.showinfo("Автомат", f"{' '.join(result)}\nПовезет в следующий раз!")
        
        self.update_balance()
        self.save_user_data()
    
    def play_dice(self):
        if self.user_data["balance"] < 500:
            messagebox.showerror("Ошибка", "Нужно 500 руб для игры!")
            return
        
        self.user_data["balance"] -= 500
        player_roll = random.randint(1, 6)
        dealer_roll = random.randint(1, 6)
        
        if player_roll > dealer_roll:
            win = 1000
            self.user_data["balance"] += win
            messagebox.showinfo("Кости", f"Вы: {player_roll} | Дилер: {dealer_roll}\nПобеда! +{win} руб!")
        elif player_roll == dealer_roll:
            self.user_data["balance"] += 500
            messagebox.showinfo("Кости", f"Вы: {player_roll} | Дилер: {dealer_roll}\nНичья! Возврат ставки.")
        else:
            messagebox.showinfo("Кости", f"Вы: {player_roll} | Дилер: {dealer_roll}\nПроигрыш!")
        
        self.update_balance()
        self.save_user_data()
    
    def play_blackjack(self):
        messagebox.showinfo("Блэкджек", "Блэкджек скоро будет доступен!")
    
    def travel_to(self, location):
        messagebox.showinfo("Путешествие", f"Вы отправились в {location}!")
    
    # Системные методы
    def update_needs(self):
        if not self.user_data["is_unconscious"]:
            self.user_data["hunger"] = max(0, self.user_data["hunger"] - 1)
            self.user_data["sleep"] = max(0, self.user_data["sleep"] - 0.5)
            
            if self.user_data["hunger"] <= 0:
                self.user_data["is_unconscious"] = True
                messagebox.showerror("Голод", "Вы потеряли сознание от голода!")
        
        self.update_status()
        self.save_user_data()
        self.root.after(10000, self.update_needs)
    
    def check_disease(self):
        if not self.user_data["is_sick"] and random.random() < 0.01:  # 1% шанс каждую секунду
            self.user_data["is_sick"] = True
            messagebox.showwarning("Болезнь", "Вы заболели! Сходите в больницу.")
            self.update_status()
            self.save_user_data()
        
        self.root.after(1000, self.check_disease)
    
    def update_play_time(self):
        self.user_data["play_time"] += 1
        self.save_user_data()
        self.root.after(1000, self.update_play_time)
    
    def update_farm_timer(self):
        # Обновление таймера быстрого фарма
        if self.user_data["last_farm_click"]:
            last_click = datetime.fromisoformat(self.user_data["last_farm_click"])
            seconds_left = 60 - (datetime.now() - last_click).total_seconds()
            if seconds_left > 0:
                self.farm_timer_label.config(text=f"Доступно через: {int(seconds_left)}с")
            else:
                self.farm_timer_label.config(text="Доступно")
        else:
            self.farm_timer_label.config(text="Доступно")
        
        self.root.after(1000, self.update_farm_timer)
    
    def check_missions(self):
        # Упрощенная система миссий
        self.root.after(1000, self.check_missions)
    
    def save_user_data(self):
        try:
            with open("user_data.json", "w", encoding="utf-8") as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_user_data(self):
        try:
            if os.path.exists("user_data.json"):
                with open("user_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Обновляем только существующие ключи
                    for key, value in data.items():
                        if key in self.user_data:
                            self.user_data[key] = value
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGSimulator(root)
    root.mainloop()