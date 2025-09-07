import pygame
import pygame.gfxdraw
import math
from pygame.locals import *

# Инициализация pygame
pygame.init()
pygame.font.init()

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
FPS = 60
PRIMARY_COLOR = (41, 128, 185)
SECONDARY_COLOR = (52, 152, 219)
ACCENT_COLOR = (241, 196, 15)
BACKGROUND_COLOR = (240, 240, 245)
PANEL_COLOR = (250, 250, 255)
TEXT_COLOR = (45, 45, 55)
HIGHLIGHT_COLOR = (46, 204, 113)

# Настройки шрифтов
font_large = pygame.font.SysFont("Arial", 32, bold=True)
font_medium = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)
font_tiny = pygame.font.SysFont("Arial", 14)

class Button:
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, 
                 text_color=(255, 255, 255), rounded=True, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.rounded = rounded
        self.icon = icon
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        
        if self.rounded:
            # Рисуем скругленный прямоугольник
            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            
            # Добавляем тень
            shadow_rect = self.rect.copy()
            shadow_rect.y += 3
            pygame.draw.rect(surface, (0, 0, 0, 30), shadow_rect, border_radius=12)
        else:
            pygame.draw.rect(surface, color, self.rect)
        
        # Рисуем текст
        text_surface = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        if self.icon:
            # Если есть иконка, смещаем текст вправо
            icon_rect = self.icon.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
            surface.blit(self.icon, icon_rect)
            text_rect.x += 15
            surface.blit(text_surface, text_rect)
        else:
            surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class ToggleButton(Button):
    def __init__(self, x, y, width, height, text, color=PRIMARY_COLOR, active_color=HIGHLIGHT_COLOR, 
                 text_color=(255, 255, 255), rounded=True):
        super().__init__(x, y, width, height, text, color, color, text_color, rounded)
        self.active_color = active_color
        self.active = False
        
    def draw(self, surface):
        if self.active:
            self.color = self.active_color
        else:
            self.color = self.original_color
        super().draw(surface)
        
    def toggle(self):
        self.active = not self.active
        return self.active

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        
    def draw(self, surface):
        # Рисуем фон слайдера
        pygame.draw.rect(surface, (200, 200, 210), self.rect, border_radius=6)
        
        # Рисуем заполненную часть
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, PRIMARY_COLOR, fill_rect, border_radius=6)
        
        # Рисуем ползунок
        slider_x = self.rect.x + fill_width
        slider_rect = pygame.Rect(slider_x - 8, self.rect.y - 6, 16, self.rect.height + 12)
        pygame.draw.rect(surface, (255, 255, 255), slider_rect, border_radius=8)
        pygame.draw.rect(surface, PRIMARY_COLOR, slider_rect, 2, border_radius=8)
        
        # Рисуем текст
        label_text = font_small.render(f"{self.label}: {self.value}%", True, TEXT_COLOR)
        surface.blit(label_text, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event, pos):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.rect.x - 10, self.rect.y - 10, self.rect.width + 20, self.rect.height + 20).collidepoint(pos):
                self.dragging = True
                self.update_value(pos)
                
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == MOUSEMOTION and self.dragging:
            self.update_value(pos)
    
    def update_value(self, pos):
        rel_x = max(0, min(pos[0] - self.rect.x, self.rect.width))
        self.value = int(self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val))

class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.active = False
        self.color = (200, 200, 210)
        self.active_color = PRIMARY_COLOR
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.active_color if self.active else (200, 200, 210)
            
        if event.type == KEYDOWN and self.active:
            if event.key == K_RETURN:
                self.active = False
                self.color = (200, 200, 210)
            elif event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                
    def draw(self, surface):
        # Рисуем фон
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=8)
        
        # Рисуем текст или плейсхолдер
        if self.text:
            text_surface = font_small.render(self.text, True, TEXT_COLOR)
        else:
            text_surface = font_small.render(self.placeholder, True, (150, 150, 160))
            
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Салтийская Республика - Стратегия управления")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Данные игры
        self.country_name = "Салтийская Республика"
        self.short_name = "Салтия"
        self.capital = "Салтийск"
        self.president = "Роман Салтийский Кимович"
        
        self.budget = {
            "USD": 650000000000,  # 650 млрд долларов
            "ADD": 19000000000000,  # 19 трлн адден
            "EUR": 187000000000,  # 187 млрд евро
            "RUB": 65000000000  # 65 млрд рублей
        }
        
        self.taxes_enabled = False
        self.states = [
            {"name": "Салтийский", "capital": "Салтийск", "type": "штат"},
            {"name": "Алмайский", "capital": "Алма", "type": "штат"},
            {"name": "Нобраский", "capital": "Нобраск", "type": "штат"},
            {"name": "Сое", "capital": "Главный город", "type": "штат"},
            {"name": "Ерне", "capital": "Главный город", "type": "штат"},
            {"name": "Армасе", "capital": "Главный город", "type": "штат"},
            {"name": "Сибере", "capital": "Главный город", "type": "штат"},
            {"name": "Шоере", "capital": "Главный город", "type": "штат"},
            {"name": "Йорке", "capital": "Главный город", "type": "штат"},
            {"name": "Восточный", "capital": "Главный город", "type": "штат"},
            {"name": "Западный", "capital": "Главный город", "type": "штат"},
            {"name": "Северный", "capital": "Главный город", "type": "штат"}
        ]
        
        self.ministries = [
            {"name": "Министерство финансов", "budget": 5000000000, "allocation": 5},
            {"name": "Министерство обороны", "budget": 8000000000, "allocation": 8},
            {"name": "Министерство образования", "budget": 4000000000, "allocation": 4},
            {"name": "Министерство здравоохранения", "budget": 6000000000, "allocation": 6},
            {"name": "Министерство транспорта", "budget": 3000000000, "allocation": 3},
            {"name": "Министерство культуры", "budget": 2000000000, "allocation": 2}
        ]
        
        # Создаем UI элементы
        self.create_ui_elements()
        
        # Текущая страница
        self.current_page = "main"
        
    def create_ui_elements(self):
        # Основные кнопки навигации
        self.nav_buttons = [
            Button(20, 20, 200, 50, "Главная", icon=None),
            Button(20, 80, 200, 50, "Бюджет", icon=None),
            Button(20, 140, 200, 50, "Штаты", icon=None),
            Button(20, 200, 200, 50, "Министерства", icon=None),
            Button(20, 260, 200, 50, "Налоги", icon=None),
            Button(20, 320, 200, 50, "Настройки", icon=None)
        ]
        
        # Кнопка переключения налогов
        self.tax_toggle = ToggleButton(500, 400, 200, 50, "Налоги выключены", 
                                      active_color=HIGHLIGHT_COLOR)
        self.tax_toggle.text = "Налоги включены" if self.taxes_enabled else "Налоги выключены"
        self.tax_toggle.active = self.taxes_enabled
        
        # Поля ввода для редактирования
        self.edit_boxes = {
            "country_name": InputBox(500, 150, 300, 40, self.country_name, "Название страны"),
            "short_name": InputBox(500, 210, 300, 40, self.short_name, "Короткое название"),
            "capital": InputBox(500, 270, 300, 40, self.capital, "Столица"),
            "president": InputBox(500, 330, 300, 40, self.president, "Президент")
        }
        
        # Слайдеры для министерств
        self.ministry_sliders = []
        for i, ministry in enumerate(self.ministries):
            self.ministry_sliders.append(
                Slider(500, 200 + i*70, 300, 20, 0, 20, ministry["allocation"], ministry["name"])
            )
            
        # Кнопка сохранения
        self.save_button = Button(500, 600, 200, 50, "Сохранить изменения", ACCENT_COLOR)
        
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Проверяем наведение на кнопки
            for button in self.nav_buttons:
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    if button.text == "Главная":
                        self.current_page = "main"
                    elif button.text == "Бюджет":
                        self.current_page = "budget"
                    elif button.text == "Штаты":
                        self.current_page = "states"
                    elif button.text == "Министерства":
                        self.current_page = "ministries"
                    elif button.text == "Налоги":
                        self.current_page = "taxes"
                    elif button.text == "Настройки":
                        self.current_page = "settings"
            
            # Обработка переключения налогов
            self.tax_toggle.check_hover(mouse_pos)
            if self.tax_toggle.is_clicked(mouse_pos, event):
                self.taxes_enabled = self.tax_toggle.toggle()
                self.tax_toggle.text = "Налоги включены" if self.taxes_enabled else "Налоги выключены"
                
            # Обработка полей ввода
            for box in self.edit_boxes.values():
                box.handle_event(event)
                
            # Обработка слайдеров
            for slider in self.ministry_sliders:
                slider.handle_event(event, mouse_pos)
                
            # Обработка кнопки сохранения
            self.save_button.check_hover(mouse_pos)
            if self.save_button.is_clicked(mouse_pos, event):
                self.save_data()
                
    def save_data(self):
        # Сохранение данных из полей ввода
        self.country_name = self.edit_boxes["country_name"].text
        self.short_name = self.edit_boxes["short_name"].text
        self.capital = self.edit_boxes["capital"].text
        self.president = self.edit_boxes["president"].text
        
        # Сохранение данных слайдеров министерств
        for i, slider in enumerate(self.ministry_sliders):
            self.ministries[i]["allocation"] = slider.value
            
        print("Данные сохранены!")
        
    def draw_main_page(self):
        # Заголовок
        title = font_large.render(f"Добро пожаловать в {self.country_name}!", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Информация о стране
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 200), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 200), 2, border_radius=15)
        
        capital_text = font_medium.render(f"Столица: {self.capital}", True, TEXT_COLOR)
        self.screen.blit(capital_text, (320, 140))
        
        president_text = font_medium.render(f"Президент: {self.president}", True, TEXT_COLOR)
        self.screen.blit(president_text, (320, 180))
        
        budget_text = font_medium.render(f"Бюджет: {self.budget['USD']:,} млрд USD | {self.budget['ADD']:,} трлн ADD", True, TEXT_COLOR)
        self.screen.blit(budget_text, (320, 220))
        
        # Статистика
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 350, 600, 200), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 350, 600, 200), 2, border_radius=15)
        
        stats_title = font_medium.render("Статистика страны:", True, TEXT_COLOR)
        self.screen.blit(stats_title, (320, 370))
        
        states_text = font_small.render(f"Количество штатов: {len(self.states)}", True, TEXT_COLOR)
        self.screen.blit(states_text, (320, 410))
        
        taxes_text = font_small.render(f"Налоговая система: {'Включена' if self.taxes_enabled else 'Выключена'}", True, TEXT_COLOR)
        self.screen.blit(taxes_text, (320, 440))
        
        # Кнопка быстрого перехода к налогам
        tax_button = Button(500, 500, 200, 50, "Управление налогами", ACCENT_COLOR)
        tax_button.check_hover(pygame.mouse.get_pos())
        tax_button.draw(self.screen)
        
    def draw_budget_page(self):
        title = font_large.render("Бюджет страны", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Панель бюджета
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 400), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 400), 2, border_radius=15)
        
        # Отображение бюджета в разных валютах
        usd_text = font_medium.render(f"Доллары: ${self.budget['USD']:,.0f}", True, TEXT_COLOR)
        self.screen.blit(usd_text, (320, 140))
        
        add_text = font_medium.render(f"Аддены: {self.budget['ADD']:,.0f} ADD", True, TEXT_COLOR)
        self.screen.blit(add_text, (320, 180))
        
        eur_text = font_medium.render(f"Евро: €{self.budget['EUR']:,.0f}", True, TEXT_COLOR)
        self.screen.blit(eur_text, (320, 220))
        
        rub_text = font_medium.render(f"Рубли: {self.budget['RUB']:,.0f} RUB", True, TEXT_COLOR)
        self.screen.blit(rub_text, (320, 260))
        
        # График распределения бюджета (упрощенный)
        pygame.draw.rect(self.screen, (230, 230, 240), (320, 320, 560, 80), border_radius=10)
        
        # Упрощенная визуализация распределения бюджета
        total_allocation = sum(m["allocation"] for m in self.ministries)
        if total_allocation > 0:
            x = 320
            colors = [(41, 128, 185), (52, 152, 219), (26, 188, 156), (46, 204, 113), (241, 196, 15), (230, 126, 34)]
            for i, ministry in enumerate(self.ministries):
                width = (ministry["allocation"] / total_allocation) * 560
                pygame.draw.rect(self.screen, colors[i % len(colors)], (x, 320, width, 80), border_radius=10)
                x += width
                
        # Легенда
        legend_y = 420
        for i, ministry in enumerate(self.ministries):
            color = colors[i % len(colors)]
            pygame.draw.rect(self.screen, color, (320, legend_y, 20, 20), border_radius=5)
            ministry_text = font_tiny.render(f"{ministry['name']} ({ministry['allocation']}%)", True, TEXT_COLOR)
            self.screen.blit(ministry_text, (350, legend_y))
            legend_y += 25
            
    def draw_states_page(self):
        title = font_large.render("Управление штатами", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Список штатов с возможностью редактирования
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 500), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 500), 2, border_radius=15)
        
        for i, state in enumerate(self.states[:6]):  # Первые 6 штатов
            y_pos = 140 + i * 80
            pygame.draw.rect(self.screen, (230, 230, 240), (320, y_pos, 560, 60), border_radius=10)
            
            state_text = font_medium.render(f"{state['name']} ({state['type']})", True, TEXT_COLOR)
            self.screen.blit(state_text, (340, y_pos + 10))
            
            capital_text = font_small.render(f"Столица: {state['capital']}", True, TEXT_COLOR)
            self.screen.blit(capital_text, (340, y_pos + 35))
            
            edit_button = Button(750, y_pos + 15, 120, 30, "Изменить", font=font_tiny)
            edit_button.check_hover(pygame.mouse.get_pos())
            edit_button.draw(self.screen)
            
        # Прокрутка для остальных штатов
        if len(self.states) > 6:
            scroll_text = font_small.render("И еще {} штатов...".format(len(self.states) - 6), True, TEXT_COLOR)
            self.screen.blit(scroll_text, (500, 620))
            
    def draw_ministries_page(self):
        title = font_large.render("Финансирование министерств", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Панель управления бюджетом министерств
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 500), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 500), 2, border_radius=15)
        
        # Инструкция
        instruction = font_small.render("Используйте слайдеры для распределения бюджета между министерствами", True, TEXT_COLOR)
        self.screen.blit(instruction, (320, 140))
        
        # Слайдеры для каждого министерства
        for i, slider in enumerate(self.ministry_sliders):
            slider.draw(self.screen)
            
        # Общая сумма распределения
        total = sum(slider.value for slider in self.ministry_sliders)
        total_text = font_medium.render(f"Общее распределение: {total}%", True, 
                                      HIGHLIGHT_COLOR if total == 100 else (192, 57, 43))
        self.screen.blit(total_text, (500, 550))
        
        # Кнопка сохранения
        self.save_button.draw(self.screen)
        
    def draw_taxes_page(self):
        title = font_large.render("Налоговая система", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Панель управления налогами
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 300), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 300), 2, border_radius=15)
        
        # Описание налоговой системы
        tax_desc = font_small.render("Налоговая система Салтии основана на налогах для компаний и богатых граждан.", True, TEXT_COLOR)
        self.screen.blit(tax_desc, (320, 140))
        
        tax_status = font_medium.render(f"Статус: {'Налоги включены' if self.taxes_enabled else 'Налоги выключены'}", 
                                      True, HIGHLIGHT_COLOR if self.taxes_enabled else (192, 57, 43))
        self.screen.blit(tax_status, (320, 180))
        
        # Переключатель налогов
        self.tax_toggle.draw(self.screen)
        
        # Дополнительная информация
        if self.taxes_enabled:
            revenue_text = font_small.render("При включенных налогах бюджет пополняется на 5-10% ежемесячно.", True, TEXT_COLOR)
            self.screen.blit(revenue_text, (320, 250))
        else:
            revenue_text = font_small.render("При выключенных налогах бюджет пополняется только за счет других источников.", True, TEXT_COLOR)
            self.screen.blit(revenue_text, (320, 250))
            
    def draw_settings_page(self):
        title = font_large.render("Настройки страны", True, TEXT_COLOR)
        self.screen.blit(title, (300, 50))
        
        # Панель редактирования
        pygame.draw.rect(self.screen, PANEL_COLOR, (300, 120, 600, 400), border_radius=15)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (300, 120, 600, 400), 2, border_radius=15)
        
        # Поля для редактирования
        labels = [
            ("Название страны:", 130),
            ("Короткое название:", 190),
            ("Столица:", 250),
            ("Президент:", 310)
        ]
        
        for label, y in labels:
            label_text = font_medium.render(label, True, TEXT_COLOR)
            self.screen.blit(label_text, (320, y))
            
        # Поля ввода
        for box in self.edit_boxes.values():
            box.draw(self.screen)
            
        # Кнопка сохранения
        self.save_button.draw(self.screen)
        
    def draw_ui(self):
        # Фон
        self.screen.fill(BACKGROUND_COLOR)
        
        # Левая панель навигации
        pygame.draw.rect(self.screen, PANEL_COLOR, (0, 0, 250, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (250, 0, 2, SCREEN_HEIGHT))
        
        # Логотип
        pygame.draw.rect(self.screen, PRIMARY_COLOR, (20, 550, 210, 100), border_radius=15)
        logo_text = font_large.render(self.short_name, True, (255, 255, 255))
        self.screen.blit(logo_text, (30, 580))
        
        # Кнопки навигации
        for button in self.nav_buttons:
            button.draw(self.screen)
            
        # Отрисовка текущей страницы
        if self.current_page == "main":
            self.draw_main_page()
        elif self.current_page == "budget":
            self.draw_budget_page()
        elif self.current_page == "states":
            self.draw_states_page()
        elif self.current_page == "ministries":
            self.draw_ministries_page()
        elif self.current_page == "taxes":
            self.draw_taxes_page()
        elif self.current_page == "settings":
            self.draw_settings_page()
            
    def run(self):
        while self.running:
            self.handle_events()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()