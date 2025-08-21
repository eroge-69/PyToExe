from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
import openpyxl
from openpyxl import Workbook
import os
from datetime import datetime
import sys

class BackgroundScreen(Screen):
    """Базовый класс для экранов с фоном"""
    background_source = ObjectProperty(None)
    
    def __init__(self, background_source=None, **kwargs):
        super().__init__(**kwargs)
        self.background_source = background_source
        self.setup_background()
    
    def setup_background(self):
        """Настраивает фон для экрана"""
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(source=self.background_source, 
                                   pos=(0, 0), 
                                   size=Window.size)
        
        self.bind(size=self.update_bg_rect)
    
    def update_bg_rect(self, *args):
        """Обновляет размер фона"""
        self.bg_rect.size = self.size

class MainScreen(BackgroundScreen):
    """Главный экран с выбором оценки"""
    pass

class ThankYouScreen(BackgroundScreen):
    """Экран благодарности с таймером"""
    pass

class SmoothScreenManager(ScreenManager):
    """Кастомный менеджер экранов с оптимизированными переходами"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = FadeTransition(duration=0.1)

class FeedbackApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_path = self.get_base_path()
        self.ratings_file = self.get_path('feedback_data.xlsx')
        self.font_file = self.get_path('NotoEmoji-Regular.ttf')
        self.background_image = self.get_path('background.png')
        
    def get_base_path(self):
        """Определяет базовый путь"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    def get_path(self, filename):
        """Возвращает полный путь к файлу"""
        return os.path.join(self.base_path, filename)
    
    def build(self):
        # Настройка полноэкранного режима
        Window.fullscreen = 'auto'
        
        # Предзагрузка фонового изображения
        if not os.path.exists(self.background_image):
            print("Фоновое изображение не найдено, используем градиент...")
            self.background_image = None
        
        # Инициализация файла
        self.initialize_excel_file()
        
        # Создаем кастомный менеджер экранов
        self.sm = SmoothScreenManager()
        
        # Создаем общий canvas для фона
        with self.sm.canvas.before:
            Color(1, 1, 1, 1)
            self.global_bg_rect = Rectangle(source=self.background_image, 
                                          pos=(0, 0), 
                                          size=Window.size)
        
        # Привязываем обновление глобального фона
        Window.bind(size=self.update_global_bg)
        
        # Главный экран
        main_screen = MainScreen(name='main', background_source=self.background_image)
        self.setup_main_screen(main_screen)
        
        # Экран благодарности
        thank_you_screen = ThankYouScreen(name='thank_you', background_source=self.background_image)
        self.setup_thank_you_screen(thank_you_screen)
        
        # Добавляем экраны в менеджер
        self.sm.add_widget(main_screen)
        self.sm.add_widget(thank_you_screen)
        
        self.update_stats()
        
        return self.sm
    
    def update_global_bg(self, instance, value):
        """Обновляет глобальный фон при изменении размера окна"""
        self.global_bg_rect.size = value
    
    def setup_main_screen(self, screen):
        """Настраивает главный экран"""
        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=30)
        
        # Полупрозрачный overlay
        with main_layout.canvas.before:
            Color(0, 0, 0, 0.3)
            self.overlay_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        main_layout.bind(pos=self.update_overlay, size=self.update_overlay)
        
        # Заголовок
        title_label = Label(text='Оцените качество обслуживания', 
                           font_size=36,
                           bold=True,
                           size_hint=(1, 0.2),
                           color=(1, 1, 1, 1))
        main_layout.add_widget(title_label)
        
        # Кнопки оценок
        buttons_layout = BoxLayout(orientation='horizontal', 
                                  spacing=30,
                                  size_hint=(1, 0.6))
        
        buttons_data = [
            ('\U0001F620', 1, 'Плохо'),
            ('\U0001F641', 2, 'Неудовлетворительно'),
            ('\U0001F610', 3, 'Удовлетворительно'),
            ('\U0001F642', 4, 'Хорошо'),
            ('\U0001F60A', 5, 'Отлично')
        ]
        
        self.buttons = []
        for emoji, rating, description in buttons_data:
            button = Button(text=emoji, 
                           font_size=60,
                           on_press=self.on_rating_select,
                           size_hint=(1, 1),
                           background_normal='',
                           background_color=(0.2, 0.5, 0.8, 0.1),
                           color=(1, 1, 1, 1),
                           bold=True)
            
            if os.path.exists(self.font_file):
                button.font_name = self.font_file
            
            button.rating = rating
            button.description = description
            
            buttons_layout.add_widget(button)
            self.buttons.append(button)
        
        main_layout.add_widget(buttons_layout)
        
        # Статистика
        stats_layout = BoxLayout(orientation='vertical', 
                                size_hint=(1, 0.2),
                                spacing=10)
        
        self.stats_label = Label(text='Всего оценок: 0\nСредний балл: 0.0',
                                font_size=24,
                                halign='center',
                                color=(1, 1, 1, 1))
        
        stats_layout.add_widget(self.stats_label)
        main_layout.add_widget(stats_layout)
        
        screen.add_widget(main_layout)
    
    def setup_thank_you_screen(self, screen):
        """Настраивает экран благодарности"""
        thank_you_layout = BoxLayout(orientation='vertical', 
                                    padding=50, 
                                    spacing=50)
        
        # Полупрозрачный overlay
        with thank_you_layout.canvas.before:
            Color(0, 0, 0, 0.4)
            self.ty_overlay_rect = Rectangle(pos=thank_you_layout.pos, size=thank_you_layout.size)
        
        thank_you_layout.bind(pos=self.update_ty_overlay, size=self.update_ty_overlay)
        
        # Сообщение благодарности
        self.thank_you_label = Label(text='', 
                                    font_size=42, 
                                    bold=True,
                                    halign='center',
                                    size_hint=(1, 0.6),
                                    color=(1, 1, 1, 1))
        
        # Таймер обратного отсчета
        self.timer_label = Label(text='', 
                                font_size=36,
                                color=(1, 0.8, 0.8, 1),
                                bold=True,
                                halign='center',
                                size_hint=(1, 0.4))
        
        thank_you_layout.add_widget(self.thank_you_label)
        thank_you_layout.add_widget(self.timer_label)
        screen.add_widget(thank_you_layout)
    
    def update_overlay(self, instance, value):
        """Обновляет позицию и размер overlay"""
        if hasattr(self, 'overlay_rect'):
            self.overlay_rect.pos = instance.pos
            self.overlay_rect.size = instance.size
    
    def update_ty_overlay(self, instance, value):
        """Обновляет позицию и размер overlay для экрана благодарности"""
        if hasattr(self, 'ty_overlay_rect'):
            self.ty_overlay_rect.pos = instance.pos
            self.ty_overlay_rect.size = instance.size
    
    def on_rating_select(self, instance):
        """Обработчик выбора оценки"""
        rating = instance.rating
        description = instance.description
        
        # Мгновенно сохраняем оценку
        self.save_rating_to_excel(rating, description)
        
        # Показываем экран благодарности
        self.show_thank_you_screen(rating, description)
        
        # Обновляем статистику
        self.update_stats()
    
    def show_thank_you_screen(self, rating, description):
        """Показывает экран благодарности с таймером"""
        self.thank_you_label.text = f'Спасибо за вашу оценку!\n\n{rating}/5 - {description}'
        self.timer_label.text = 'Возврат через: 10'
        
        # Запускаем таймер обратного отсчета
        self.timer_count = 10
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        
        # Плавный переход на экран благодарности
        self.sm.current = 'thank_you'
    
    def update_timer(self, dt):
        """Обновляет таймер обратного отсчета"""
        self.timer_count -= 1
        self.timer_label.text = f'Возврат через: {self.timer_count}'
        
        if self.timer_count <= 3:
            self.timer_label.color = (1, 0.6, 0.6, 1)
        
        if self.timer_count <= 0:
            self.timer_event.cancel()
            self.return_to_main_screen()
    
    def return_to_main_screen(self):
        """Возврат на главный экран"""
        self.sm.current = 'main'
    
    def initialize_excel_file(self):
        """Создает или загружает Excel файл"""
        if not os.path.exists(self.ratings_file):
            try:
                wb = Workbook()
                ws = wb.active
                ws.title = "Оценки"
                
                ws.column_dimensions['A'].width = 20
                ws.column_dimensions['B'].width = 10
                ws.column_dimensions['C'].width = 25
                
                ws['A1'] = 'Дата и время'
                ws['B1'] = 'Оценка'
                ws['C1'] = 'Описание'
                
                for cell in ['A1', 'B1', 'C1']:
                    ws[cell].font = openpyxl.styles.Font(bold=True)
                    ws[cell].fill = openpyxl.styles.PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
                
                wb.save(self.ratings_file)
                
            except Exception as e:
                print(f"Ошибка создания файла: {e}")
    
    def save_rating_to_excel(self, rating, description):
        """Сохраняет оценку в Excel файл"""
        try:
            wb = openpyxl.load_workbook(self.ratings_file)
            ws = wb.active
            
            next_row = ws.max_row + 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ws[f'A{next_row}'] = current_time
            ws[f'B{next_row}'] = rating
            ws[f'C{next_row}'] = description
            
            wb.save(self.ratings_file)
            
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
    
    def update_stats(self):
        """Обновляет статистику на главном экране"""
        try:
            if os.path.exists(self.ratings_file):
                wb = openpyxl.load_workbook(self.ratings_file)
                ws = wb.active
                
                ratings = []
                for row in range(2, ws.max_row + 1):
                    rating_val = ws[f'B{row}'].value
                    if rating_val is not None:
                        ratings.append(rating_val)
                
                total = len(ratings)
                if total > 0:
                    average = sum(ratings) / total
                    self.stats_label.text = f'Всего оценок: {total}\nСредний балл: {average:.1f}'
                else:
                    self.stats_label.text = 'Всего оценок: 0\nСредний балл: 0.0'
                    
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")

if __name__ == '__main__':
    FeedbackApp().run()