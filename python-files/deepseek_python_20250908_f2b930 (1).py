import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

class CocosCompanyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cocos Company - Official Application")
        self.root.geometry("1000x700")
        self.root.configure(bg='#000000')
        
        # Цветовая схема
        self.bg_color = '#000000'
        self.primary_color = '#FFD700'
        self.secondary_color = '#333333'
        self.text_color = '#FFFFFF'
        
        self.setup_ui()
        
    def setup_ui(self):
        # Создаем notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем фреймы для каждой вкладки
        self.create_company_tab()
        self.create_gaming_tab()
        self.create_community_tab()
        self.create_support_tab()
        self.create_downloads_tab()
        self.create_speedruns_tab()
        self.create_reviews_tab()
        self.create_info_tab()
        self.create_auth_tab()
        
    def create_styled_frame(self, parent):
        frame = tk.Frame(parent, bg=self.bg_color, bd=2, relief='raised')
        return frame
        
    def create_title_label(self, parent, text):
        label = tk.Label(parent, text=text, font=('Arial', 16, 'bold'),
                        bg=self.bg_color, fg=self.primary_color)
        return label
        
    def create_text_widget(self, parent, height=10):
        text_widget = tk.Text(parent, wrap='word', font=('Arial', 10),
                            bg=self.secondary_color, fg=self.text_color,
                            relief='flat', borderwidth=2, height=height)
        return text_widget
        
    def create_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command,
                          bg=self.primary_color, fg='#000000',
                          font=('Arial', 10, 'bold'),
                          relief='raised', borderwidth=2,
                          padx=15, pady=5)
        return button

    def create_company_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="О компании Cocos")
        
        content = """COCOS COMPANY - ИННОВАЦИОННАЯ КОМПАНИЯ

Мы молодая и амбициозная компания, специализирующаяся на:
• Разработке игр и программного обеспечения
• Создании инновационных IT-решений  
• Поддержке игрового сообщества
• Развитии киберспортивной инфраструктуры

Наша миссия: Создавать качественный контент и объединять людей через игры!

Основана в 2024 году энтузиастами игровой индустрии."""
        
        title = self.create_title_label(frame, "COCOS COMPANY")
        title.pack(pady=20)
        
        text_widget = self.create_text_widget(frame, height=15)
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        text_widget.pack(pady=20, padx=20, fill='both', expand=True)

    def create_gaming_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Cocos Gaming")
        
        title = self.create_title_label(frame, "COCOS GAMING - НАШИ ПРОДУКТЫ")
        title.pack(pady=20)
        
        # TIMUTKA GAME DEMO
        game_frame = tk.Frame(frame, bg=self.secondary_color, bd=2, relief='sunken')
        game_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(game_frame, text="TIMUTKA GAME DEMO", 
                font=('Arial', 14, 'bold'), bg=self.secondary_color, fg=self.primary_color).pack(pady=10)
        
        tk.Label(game_frame, text="Скоро состоится релиз полной версии игры!", 
                font=('Arial', 12), bg=self.secondary_color, fg=self.text_color).pack(pady=5)
        
        download_btn = self.create_button(game_frame, "СКАЧАТЬ ДЕМО", 
                                        lambda: webbrowser.open("https://disk.yandex.ru/d/93F7Iq67yK-Mww"))
        download_btn.pack(pady=10)

    def create_community_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Сообщество Cocos")
        
        title = self.create_title_label(frame, "СООБЩЕСТВО COCOS")
        title.pack(pady=20)
        
        content = """Присоединяйтесь к нашему растущему сообществу!

• Discord сервер: скоро будет запущен
• Группа VK: в разработке  
• Telegram канал: готовится к открытию

Участвуйте в обсуждениях, предлагайте идеи и будьте в курсе всех новостей!"""
        
        text_widget = self.create_text_widget(frame, height=10)
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        text_widget.pack(pady=20, padx=20, fill='both', expand=True)

    def create_support_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Поддержка автора")
        
        title = self.create_title_label(frame, "ПОДДЕРЖИТЕ АВТОРА")
        title.pack(pady=20)
        
        support_info = """Ваша поддержка помогает развивать проекты!

Контакты для связи:
📞 Телефон: +7 920 651 1848

Финансовая поддержка:
• ЮMoney: 4100119004401216
• Банковская карта: 2200 1513 2450 0599

Средства пойдут на развитие проектов и кейсы в CS!"""
        
        text_widget = self.create_text_widget(frame, height=12)
        text_widget.insert('1.0', support_info)
        text_widget.config(state='disabled')
        text_widget.pack(pady=20, padx=20, fill='both', expand=True)

    def create_downloads_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Загрузки")
        
        title = self.create_title_label(frame, "МОДЫ ДЛЯ РАСТЕНИЙ ПРОТИВ ЗОМБИ")
        title.pack(pady=20)
        
        # Мод 1
        mod1_frame = tk.Frame(frame, bg=self.secondary_color, bd=2, relief='sunken')
        mod1_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(mod1_frame, text="Мод для PvZ версии 1.2", 
                font=('Arial', 12, 'bold'), bg=self.secondary_color, fg=self.primary_color).pack(pady=10)
        
        btn1 = self.create_button(mod1_frame, "СКАЧАТЬ МОД 1", 
                                lambda: webbrowser.open("https://drive.google.com/file/d/1QZUwwnt2Ex964UQmOFlXXDNFZiK3vJM4/view?usp=sharing"))
        btn1.pack(pady=10)
        
        # Мод 2
        mod2_frame = tk.Frame(frame, bg=self.secondary_color, bd=2, relief='sunken')
        mod2_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(mod2_frame, text="Самый невозможный мод в мире PvZ", 
                font=('Arial', 12, 'bold'), bg=self.secondary_color, fg=self.primary_color).pack(pady=10)
        
        btn2 = self.create_button(mod2_frame, "СКАЧАТЬ МОД 2", 
                                lambda: webbrowser.open("https://drive.google.com/file/d/1ioUCuC85ilM_vS-rLBuPDW1A0rCUVri9/view?usp=sharing"))
        btn2.pack(pady=10)

    def create_speedruns_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Спидраны")
        
        title = self.create_title_label(frame, "ЛУЧШИЕ СПИДРАНЫ")
        title.pack(pady=20)
        
        tk.Label(frame, text="Рекордный спидран по TIMUTKA GAME DEMO:", 
                font=('Arial', 12), bg=self.bg_color, fg=self.text_color).pack(pady=10)
        
        watch_btn = self.create_button(frame, "СМОТРЕТЬ ВИДЕО", 
                                     lambda: webbrowser.open("https://youtu.be/rbQOM6ZzbPQ?si=32eojkq_96N8dF2M"))
        watch_btn.pack(pady=20)

    def create_reviews_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Отзывы")
        
        title = self.create_title_label(frame, "ОТЗЫВЫ ИГРОКОВ")
        title.pack(pady=20)
        
        review = """ИГРА ТИМУТКА ГЕЙМ ДЕМО САМАЯ ЛУТШАЯЯ ТАМ В ГЛАВНОЙ РОЛИ 
МОЙ ПОКЛОННИК И ПОД ПОЛКОВНИК АЦЕНИВАЮ НА 5 ЗВЕЗД.

Отзыв от: Анонимный игрок
Рейтинг: ★★★★★"""
        
        text_widget = self.create_text_widget(frame, height=8)
        text_widget.insert('1.0', review)
        text_widget.config(state='disabled')
        text_widget.pack(pady=20, padx=20, fill='both', expand=True)

    def create_info_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Информация об игре")
        
        title = self.create_title_label(frame, "TIMUTKA GAME DEMO - ИНФОРМАЦИЯ")
        title.pack(pady=20)
        
        info_text = """Движок: Clickteam Fusion Developer 2.5

TIMUTKA GAME DEMO: Обзор и руководство

Название: TIMUTKA GAME DEMO
Жанр: Приключенческая игра, симулятор школьной жизни, инди-игра.
Сеттинг: Современная российская (или условно-славянская) школа.
Главный герой: Тимутка — обычный, но немного неуклюжий и впечатлительный школьник.

Сюжет и концепция:
В "TIMUTKA GAME DEMO" вы принимаете роль ученика по имени Тимутка. 
Игра представляет собой срез его школьной жизни, охватывающий два 
непростых, но полных событий дня.

Основные задачи:
• Собраться в школу
• Добраться до школы
• Посещать уроки
• Общаться с персонажами

Ключевые персонажи:
• Тимутка - главный герой
• Полина - одноклассница-отличница
• Семён - школьный охраник

Особенности игры:
• Простая стилизованная 2D-графика
• Юмористические диалоги и ситуации
• Демо-версия на 30-60 секунд геймплея"""
        
        text_widget = self.create_text_widget(frame, height=25)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')
        text_widget.pack(pady=20, padx=20, fill='both', expand=True)

    def create_auth_tab(self):
        frame = self.create_styled_frame(self.notebook)
        self.notebook.add(frame, text="Регистрация")
        
        title = self.create_title_label(frame, "РЕГИСТРАЦИЯ ЧЕРЕЗ GOOGLE")
        title.pack(pady=20)
        
        tk.Label(frame, text="Вход через Google аккаунт:", 
                font=('Arial', 12), bg=self.bg_color, fg=self.text_color).pack(pady=10)
        
        google_btn = self.create_button(frame, "ВОЙТИ ЧЕРЕЗ GOOGLE", 
                                      lambda: messagebox.showinfo("Вход", "Функция входа через Google будет реализована в будущем"))
        google_btn.pack(pady=20)
        
        tk.Label(frame, text="Регистрация через Google:", 
                font=('Arial', 12), bg=self.bg_color, fg=self.text_color).pack(pady=10)
        
        register_btn = self.create_button(frame, "ЗАРЕГИСТРИРОВАТЬСЯ", 
                                        lambda: messagebox.showinfo("Регистрация", "Функция регистрации будет реализована в будущем"))
        register_btn.pack(pady=20)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CocosCompanyApp(root)
    root.mainloop()