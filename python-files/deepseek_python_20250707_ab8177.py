import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import webbrowser

# Настройка темы
ctk.set_appearance_mode("System")  # Режим системы (темный/светлый)
ctk.set_default_color_theme("blue")  # Цветовая тема

class FashionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройка главного окна
        self.title("Модное приложение")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Создание сетки
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Создание боковой панели
        self.create_sidebar()
        
        # Создание основной области
        self.create_main_area()
        
        # Создание статус бара
        self.create_status_bar()
    
    def create_sidebar(self):
        # Фрейм для боковой панели
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Логотип
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Модное Приложение", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Кнопки боковой панели
        buttons = [
            ("Главная", self.show_home),
            ("Настройки", self.show_settings),
            ("О программе", self.show_about),
            ("Выход", self.quit_app)
        ]
        
        for i, (text, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                command=command,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                anchor="w"
            )
            btn.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
    
    def create_main_area(self):
        # Основной фрейм
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Домашняя страница (по умолчанию)
        self.home_page = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Заголовок
        title = ctk.CTkLabel(
            self.home_page,
            text="Добро пожаловать в модное приложение!",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=40)
        
        # Описание
        desc = ctk.CTkLabel(
            self.home_page,
            text="Это пример современного интерфейса на Python с использованием библиотеки customtkinter.",
            wraplength=400,
            justify="left"
        )
        desc.pack(pady=10, padx=20)
        
        # Кнопка действия
        action_btn = ctk.CTkButton(
            self.home_page,
            text="Сделать что-то крутое",
            command=self.do_something_cool,
            hover_color="green"
        )
        action_btn.pack(pady=30)
        
        # Ссылка
        link = ctk.CTkLabel(
            self.home_page,
            text="Узнать больше на GitHub",
            text_color="lightblue",
            cursor="hand2"
        )
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com"))
        
        self.home_page.grid(row=0, column=0, sticky="nsew")
    
    def create_status_bar(self):
        # Статус бар
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Готово", 
            anchor="w",
            fg_color=("gray85", "gray20"),
            corner_radius=0
        )
        self.status_bar.grid(row=3, column=1, sticky="ew")
    
    def show_home(self):
        self.clear_main_frame()
        self.home_page.grid(row=0, column=0, sticky="nsew")
        self.status_bar.configure(text="Показана домашняя страница")
    
    def show_settings(self):
        self.clear_main_frame()
        
        settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        title = ctk.CTkLabel(
            settings_frame,
            text="Настройки",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Переключатель темы
        theme_label = ctk.CTkLabel(settings_frame, text="Тема интерфейса:")
        theme_label.pack(pady=(10, 0))
        
        theme_option = ctk.CTkOptionMenu(
            settings_frame,
            values=["System", "Dark", "Light"],
            command=self.change_theme
        )
        theme_option.pack(pady=5)
        
        # Переключатель цвета
        color_label = ctk.CTkLabel(settings_frame, text="Цветовая схема:")
        color_label.pack(pady=(10, 0))
        
        color_option = ctk.CTkOptionMenu(
            settings_frame,
            values=["blue", "green", "dark-blue"],
            command=self.change_color
        )
        color_option.pack(pady=5)
        
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.status_bar.configure(text="Показаны настройки")
    
    def show_about(self):
        self.clear_main_frame()
     