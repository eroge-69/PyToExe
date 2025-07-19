import pygame
import sys
import random
import math
from enum import Enum
from pygame.locals import *

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
GREEN = (50, 200, 50)
RED = (255, 80, 80)
BLUE = (70, 130, 255)
YELLOW = (255, 215, 70)
PURPLE = (180, 70, 255)
CYAN = (0, 200, 200)
ORANGE = (255, 150, 50)
BACKGROUND = (15, 25, 35)
PANEL_COLOR = (30, 45, 60)
BUTTON_COLOR = (50, 120, 180)
BUTTON_HOVER = (70, 150, 220)

# Настройки игры
START_MONEY = 15000
DAY_DURATION = 30  # секунд
SERVER_STORAGE_COST = 800
SERVER_WORKER_COST = 1200
UPGRADE_COSTS = {
    "cpu": 300,
    "ram": 80,
    "gpu": 400,
    "storage": 5  # за GB
}

class ServerType(Enum):
    STORAGE = "Хранилище"
    WORKER = "Рабочий"

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.current_color = color
        self.font = pygame.font.SysFont(None, 28)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=5)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Server:
    def __init__(self, server_type, name):
        self.type = server_type
        self.name = name
        self.cpu = 1
        self.ram = 4  # GB
        self.gpu = 0
        self.storage = 100 if server_type == ServerType.STORAGE else 10  # GB
        self.price = SERVER_STORAGE_COST if server_type == ServerType.STORAGE else SERVER_WORKER_COST
        self.running = True
        self.current_order = None
        self.days_left = 0
        self.id = random.randint(1000, 9999)
        self.progress = 0
        
    def upgrade(self, component, amount):
        cost = UPGRADE_COSTS[component] * amount
        if component == "cpu":
            self.cpu += amount
        elif component == "ram":
            self.ram += amount
        elif component == "gpu":
            self.gpu += amount
        elif component == "storage":
            self.storage += amount
        return cost
    
    def assign_order(self, order):
        if self.current_order is None and self.meets_requirements(order):
            self.current_order = order
            self.days_left = order.duration
            return True
        return False
    
    def meets_requirements(self, order):
        if self.type != order.type:
            return False
        return (self.cpu >= order.requirements["cpu"] and
                self.ram >= order.requirements["ram"] and
                self.gpu >= order.requirements["gpu"] and
                self.storage >= order.requirements["storage"])
    
    def process_day(self):
        if self.current_order:
            self.days_left -= 1
            self.progress = 100 - (self.days_left / self.current_order.duration * 100)
            if self.days_left <= 0:
                payment = self.current_order.payment
                self.current_order = None
                self.days_left = 0
                self.progress = 0
                return payment
        return 0
    
    def get_info(self):
        info = [
            f"Сервер: {self.name}",
            f"Тип: {self.type.value}",
            f"CPU: {self.cpu} ядер",
            f"RAM: {self.ram} GB",
            f"GPU: {self.gpu} GB",
            f"Хранилище: {self.storage} GB"
        ]
        if self.current_order:
            info.append(f"Заказ: #{self.current_order.id}")
            info.append(f"Осталось дней: {self.days_left}")
            info.append(f"Оплата: ${self.current_order.payment}")
        return info

class Order:
    def __init__(self):
        self.type = random.choice(list(ServerType))
        self.payment = random.randint(300, 2500)
        self.duration = random.randint(2, 15)
        self.requirements = {
            "cpu": random.randint(1, 12),
            "ram": random.randint(1, 48),
            "gpu": random.randint(0, 16),
            "storage": random.randint(20, 2000)
        }
        self.id = random.randint(100, 999)
        
    def get_info(self):
        info = [
            f"Заказ #{self.id}",
            f"Тип: {self.type.value}",
            f"Оплата: ${self.payment}",
            f"Дней: {self.duration}",
            f"Требования:",
            f"  CPU: {self.requirements['cpu']} ядер",
            f"  RAM: {self.requirements['ram']} GB",
            f"  GPU: {self.requirements['gpu']} GB",
            f"  Хранилище: {self.requirements['storage']} GB"
        ]
        return info

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Серверный Магнат")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont(None, 60)
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 24)
        self.money = START_MONEY
        self.day = 1
        self.time_left = DAY_DURATION
        self.servers = []
        self.orders = []
        self.selected_server = None
        self.selected_order = None
        self.game_speed = 1
        self.paused = False
        self.message = ""
        self.message_timer = 0
        
        # Создание кнопок
        self.buttons = {
            "buy_storage": Button(20, 150, 200, 50, "Купить Хранилище ($800)"),
            "buy_worker": Button(20, 220, 200, 50, "Купить Рабочий ($1200)"),
            "skip_day": Button(20, 290, 200, 50, "Пропустить день"),
            "upgrade_cpu": Button(20, 450, 200, 40, "Улучшить CPU ($300)"),
            "upgrade_ram": Button(20, 500, 200, 40, "Улучшить RAM ($80)"),
            "upgrade_gpu": Button(20, 550, 200, 40, "Улучшить GPU ($400)"),
            "upgrade_storage": Button(20, 600, 200, 40, "Улучшить Хранилище ($5/GB)")
        }
        
        # Стартовые серверы
        self.add_server(ServerType.STORAGE, "Хранилище #1")
        self.add_server(ServerType.WORKER, "Рабочий #1")
    
    def add_server(self, server_type, name):
        server = Server(server_type, name)
        self.servers.append(server)
        return server
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 180  # 3 секунды при 60 FPS
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_RIGHT:
                    self.next_day()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_click = True
                    
                    # Выбор сервера
                    for i, server in enumerate(self.servers):
                        server_rect = pygame.Rect(250, 150 + i * 120, 700, 100)
                        if server_rect.collidepoint(mouse_pos):
                            self.selected_server = server
                            break
                    
                    # Выбор заказа
                    for i, order in enumerate(self.orders):
                        order_rect = pygame.Rect(1000, 150 + i * 130, 180, 120)
                        if order_rect.collidepoint(mouse_pos):
                            self.selected_order = order
                            break
        
        # Обновление кнопок
        for button in self.buttons.values():
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_click):
                if button == self.buttons["buy_storage"]:
                    if self.money >= SERVER_STORAGE_COST:
                        self.money -= SERVER_STORAGE_COST
                        server = self.add_server(ServerType.STORAGE, f"Хранилище #{len(self.servers)+1}")
                        self.selected_server = server
                        self.show_message("Куплено хранилище!")
                    else:
                        self.show_message("Недостаточно денег!")
                
                elif button == self.buttons["buy_worker"]:
                    if self.money >= SERVER_WORKER_COST:
                        self.money -= SERVER_WORKER_COST
                        server = self.add_server(ServerType.WORKER, f"Рабочий #{len(self.servers)+1}")
                        self.selected_server = server
                        self.show_message("Куплен рабочий сервер!")
                    else:
                        self.show_message("Недостаточно денег!")
                
                elif button == self.buttons["skip_day"]:
                    self.next_day()
                
                elif button == self.buttons["upgrade_cpu"] and self.selected_server:
                    cost = UPGRADE_COSTS["cpu"]
                    if self.money >= cost:
                        self.money -= cost
                        self.selected_server.upgrade("cpu", 1)
                        self.show_message(f"Улучшен CPU сервера {self.selected_server.name}")
                    else:
                        self.show_message("Недостаточно денег!")
                
                elif button == self.buttons["upgrade_ram"] and self.selected_server:
                    cost = UPGRADE_COSTS["ram"]
                    if self.money >= cost:
                        self.money -= cost
                        self.selected_server.upgrade("ram", 4)
                        self.show_message(f"Улучшена RAM сервера {self.selected_server.name}")
                    else:
                        self.show_message("Недостаточно денег!")
                
                elif button == self.buttons["upgrade_gpu"] and self.selected_server:
                    cost = UPGRADE_COSTS["gpu"]
                    if self.money >= cost:
                        self.money -= cost
                        self.selected_server.upgrade("gpu", 2)
                        self.show_message(f"Улучшен GPU сервера {self.selected_server.name}")
                    else:
                        self.show_message("Недостаточно денег!")
                
                elif button == self.buttons["upgrade_storage"] and self.selected_server:
                    amount = 100
                    cost = UPGRADE_COSTS["storage"] * amount
                    if self.money >= cost:
                        self.money -= cost
                        self.selected_server.upgrade("storage", amount)
                        self.show_message(f"Улучшено хранилище сервера {self.selected_server.name}")
                    else:
                        self.show_message("Недостаточно денег!")
        
        # Назначение заказа на сервер
        if mouse_click and self.selected_order and self.selected_server:
            if self.selected_server.assign_order(self.selected_order):
                self.orders.remove(self.selected_order)
                self.selected_order = None
                self.show_message(f"Заказ назначен на {self.selected_server.name}")
            else:
                self.show_message("Ошибка назначения заказа!")
        
        return True
    
    def update(self):
        if self.paused:
            return
        
        # Обновление времени
        self.time_left -= self.clock.get_time() / 1000 * self.game_speed
        if self.time_left <= 0:
            self.next_day()
            self.time_left = DAY_DURATION
        
        # Обновление сообщения
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def next_day(self):
        self.day += 1
        
        # Генерация новых заказов
        if random.random() < 0.5 and len(self.orders) < 5:
            self.orders.append(Order())
        
        # Обработка серверов
        for server in self.servers:
            income = server.process_day()
            if income > 0:
                self.money += income
                self.show_message(f"Заказ выполнен! +${income}")
    
    def draw_panel(self, x, y, width, height, title=None):
        pygame.draw.rect(self.screen, PANEL_COLOR, (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, width, height), 2, border_radius=10)
        if title:
            title_surf = self.font.render(title, True, YELLOW)
            self.screen.blit(title_surf, (x + 10, y + 10))
    
    def render(self):
        self.screen.fill(BACKGROUND)
        
        # Заголовок
        title_surf = self.title_font.render("Серверный Магнат", True, CYAN)
        self.screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 20))
        
        # Панель информации
        self.draw_panel(10, 80, 1180, 70)
        money_text = self.font.render(f"Деньги: ${self.money}", True, GREEN)
        day_text = self.font.render(f"День: {self.day}", True, WHITE)
        time_text = self.font.render(f"Время до конца дня: {int(self.time_left)}с", True, ORANGE)
        
        self.screen.blit(money_text, (30, 100))
        self.screen.blit(day_text, (250, 100))
        self.screen.blit(time_text, (450, 100))
        
        # Кнопки
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Панель серверов
        self.draw_panel(240, 130, 720, 640, "Ваши серверы")
        for i, server in enumerate(self.servers):
            server_color = GREEN if server.running else RED
            server_rect = pygame.Rect(250, 150 + i * 120, 700, 100)
            
            # Выделение выбранного сервера
            if server == self.selected_server:
                pygame.draw.rect(self.screen, (80, 100, 140), server_rect, border_radius=8)
            
            pygame.draw.rect(self.screen, PANEL_COLOR, server_rect, border_radius=8)
            pygame.draw.rect(self.screen, DARK_GRAY, server_rect, 2, border_radius=8)
            
            # Информация о сервере
            name_text = self.font.render(f"{server.name} (ID: {server.id})", True, server_color)
            self.screen.blit(name_text, (260, 160 + i * 120))
            
            specs_text = self.small_font.render(
                f"CPU: {server.cpu} | RAM: {server.ram}GB | GPU: {server.gpu}GB | Хранилище: {server.storage}GB", 
                True, LIGHT_GRAY
            )
            self.screen.blit(specs_text, (260, 190 + i * 120))
            
            # Прогресс выполнения заказа
            if server.current_order:
                pygame.draw.rect(self.screen, DARK_GRAY, (260, 215 + i * 120, 670, 20), border_radius=3)
                pygame.draw.rect(self.screen, BLUE, (262, 217 + i * 120, int(666 * server.progress/100), 16), border_radius=3)
                progress_text = self.small_font.render(
                    f"Заказ #{server.current_order.id}: {server.days_left} дней осталось", 
                    True, YELLOW
                )
                self.screen.blit(progress_text, (260, 240 + i * 120))
        
        # Панель заказов
        self.draw_panel(980, 130, 210, 640, "Доступные заказы")
        for i, order in enumerate(self.orders):
            order_rect = pygame.Rect(1000, 150 + i * 130, 180, 120)
            order_color = PURPLE if order.type == ServerType.STORAGE else ORANGE
            
            # Выделение выбранного заказа
            if order == self.selected_order:
                pygame.draw.rect(self.screen, (80, 100, 140), order_rect, border_radius=8)
            
            pygame.draw.rect(self.screen, PANEL_COLOR, order_rect, border_radius=8)
            pygame.draw.rect(self.screen, order_color, order_rect, 2, border_radius=8)
            
            order_id_text = self.small_font.render(f"Заказ #{order.id}", True, order_color)
            payment_text = self.small_font.render(f"${order.payment}", True, GREEN)
            days_text = self.small_font.render(f"{order.duration} дней", True, YELLOW)
            
            self.screen.blit(order_id_text, (1010, 160 + i * 130))
            self.screen.blit(payment_text, (1010, 185 + i * 130))
            self.screen.blit(days_text, (1010, 210 + i * 130))
            
            # Иконка типа сервера
            server_type = "Хранилище" if order.type == ServerType.STORAGE else "Рабочий"
            type_text = self.small_font.render(server_type, True, CYAN)
            self.screen.blit(type_text, (1010, 235 + i * 130))
        
        # Панель деталей
        self.draw_panel(10, 680, 1180, 110, "Детали")
        if self.selected_server:
            info = self.selected_server.get_info()
            for i, text in enumerate(info[:4]):
                text_surf = self.small_font.render(text, True, LIGHT_GRAY)
                self.screen.blit(text_surf, (20, 700 + i * 20))
        elif self.selected_order:
            info = self.selected_order.get_info()
            for i, text in enumerate(info[:5]):
                text_surf = self.small_font.render(text, True, LIGHT_GRAY)
                self.screen.blit(text_surf, (20, 700 + i * 20))
        else:
            help_text = [
                "Выберите сервер или заказ для просмотра деталей",
                "Кликайте на заказ, затем на сервер для назначения",
                "Пробел: Пауза, Стрелка вправо: Пропустить день"
            ]
            for i, text in enumerate(help_text):
                text_surf = self.small_font.render(text, True, LIGHT_GRAY)
                self.screen.blit(text_surf, (20, 700 + i * 20))
        
        # Сообщения
        if self.message and self.message_timer > 0:
            msg_surf = self.font.render(self.message, True, YELLOW)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, 650))
            pygame.draw.rect(self.screen, (30, 30, 70), 
                           (msg_rect.x - 10, msg_rect.y - 5, msg_rect.width + 20, msg_rect.height + 10),
                           border_radius=5)
            self.screen.blit(msg_surf, msg_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()