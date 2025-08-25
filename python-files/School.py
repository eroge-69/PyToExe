import tkinter as tk
from tkinter import ttk
import webbrowser
from PIL import Image, ImageTk
import os


class SchoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Школьное приложение - Управляющий совет")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        # Создаем notebook для переключения между страницами
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем страницы
        self.create_main_page()
        self.create_links_page()

    def create_main_page(self):
        """Создание главной страницы"""
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Главная")

        # Заголовок
        title_label = tk.Label(self.main_frame,
                               text="Управляющий совет школы",
                               font=("Arial", 20, "bold"),
                               fg="#2c3e50",
                               bg='#f0f0f0')
        title_label.pack(pady=20)

        # Логотип (заглушка)
        try:
            # Пытаемся загрузить изображение, если оно есть
            image = Image.open("school_logo.png")
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.main_frame, image=self.logo, bg='#f0f0f0')
            logo_label.pack(pady=10)
        except:
            # Если изображения нет, создаем текстовую заглушку
            logo_placeholder = tk.Label(self.main_frame,
                                        text="Логотип школы",
                                        font=("Arial", 12),
                                        fg="#7f8c8d",
                                        bg='#f0f0f0')
            logo_placeholder.pack(pady=50)

        # Кнопки
        button_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        button_frame.pack(pady=50)

        continue_btn = tk.Button(button_frame,
                                 text="Продолжить",
                                 font=("Arial", 14),
                                 bg="#3498db",
                                 fg="white",
                                 relief="flat",
                                 width=20,
                                 height=2,
                                 command=self.show_links_page)
        continue_btn.pack(pady=10)

        exit_btn = tk.Button(button_frame,
                             text="Выход из приложения",
                             font=("Arial", 14),
                             bg="#e74c3c",
                             fg="white",
                             relief="flat",
                             width=20,
                             height=2,
                             command=self.root.quit)
        exit_btn.pack(pady=10)

    def create_links_page(self):
        """Создание страницы с ссылками"""
        self.links_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.links_frame, text="Материалы")

        # Заголовок
        title_label = tk.Label(self.links_frame,
                               text="Материалы Управляющего совета",
                               font=("Arial", 18, "bold"),
                               fg="#2c3e50",
                               bg='#f0f0f0')
        title_label.pack(pady=20)

        # Кнопка назад
        back_btn = tk.Button(self.links_frame,
                             text="← Назад",
                             font=("Arial", 12),
                             bg="#95a5a6",
                             fg="white",
                             relief="flat",
                             command=self.show_main_page)
        back_btn.pack(anchor='nw', padx=20, pady=10)

        # Фрейм для кнопок с прокруткой
        canvas = tk.Canvas(self.links_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.links_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Словарь с названиями кнопок и URL
        buttons_data = {
            "Нормативные документы Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/normativnye-dokumenty-upravlyayuschego-soveta",
            "Состав Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/sostav-upravlyayuschego-soveta",
            "Структура Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/struktura-upravlyayuschego-soveta",
            "План работы Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/plan-raboty-upravlyayuschego-soveta",
            "Протоколы заседаний Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/protokoly-zasedaniy-upravlyayuschego-soveta",
            "Проекты Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/proekty-upravlyayuschego-soveta",
            "Награды и достижения Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/nagrady-i-dostizheniya-upravlyayuschego-soveta",
            "Трансляция опыта работы Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/translyatsiya-opyta-raboty-upravlyayuschego-soveta",
            "Публикации о деятельности Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/publikatsii-o-deyatelnosti-upravlyayuschego-soveta",
            "Новости Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/novosti-upravlyayuschego-soveta",
            "Результаты опросов, проведённых Управляющим советом": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/rezultaty-oprosov-provedennyh-upravlyayuschim-sovetom",
            "Отчёты о деятельности Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/otchety-o-deyatelnosti-upravlyayuschego-soveta",
            "Повышение квалификации": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/povyshenie-kvalifikatsii",
            "Архив материалов Управляющего совета": "https://shkola34staryjoskol-r31.gosweb.gosuslugi.ru/glavnoe/upravlyayuschiy-sovet/arhiv-materialov-upravlyayuschego-soveta"
        }

        # Создаем кнопки
        for text, url in buttons_data.items():
            btn = tk.Button(self.scrollable_frame,
                            text=text,
                            font=("Arial", 11),
                            bg="#2c3e50",
                            fg="white",
                            relief="flat",
                            wraplength=400,
                            justify="left",
                            width=50,
                            command=lambda u=url: self.open_url(u))
            btn.pack(pady=5, padx=20, fill='x')

        # Упаковываем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_main_page(self):
        """Показать главную страницу"""
        self.notebook.select(0)

    def show_links_page(self):
        """Показать страницу с ссылками"""
        self.notebook.select(1)

    def open_url(self, url):
        """Открыть URL в браузере"""
        webbrowser.open(url)


def main():
    root = tk.Tk()
    app = SchoolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()