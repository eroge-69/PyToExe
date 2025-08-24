import pygame
import pygame.gfxdraw
import sys
import json
import os
import hashlib
import uuid

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BG_COLOR = (54, 57, 63)
TEXT_COLOR = (220, 221, 222)
ACCENT_COLOR = (88, 101, 242)
INPUT_BG_COLOR = (64, 68, 75)
BUTTON_HOVER_COLOR = (71, 82, 196)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Discord-подобное приложение")
clock = pygame.time.Clock()

# Шрифты
font_large = pygame.font.SysFont("Arial", 32)
font_medium = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)

# Данные пользователей
users_file = "users.json"
channels_file = "channels.json"

def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Загрузка данных
users = load_data(users_file)
channels = load_data(channels_file)

# Хеширование пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Генерация уникального ID
def generate_id():
    return str(uuid.uuid4())[:8]

# Класс для кнопок
class Button:
    def __init__(self, x, y, width, height, text, color=ACCENT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = BUTTON_HOVER_COLOR
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        text_surface = font_medium.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Класс для текстовых полей
class InputBox:
    def __init__(self, x, y, width, height, placeholder="", is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.is_password = is_password
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_TAB:  # Игнорируем таб
                self.text += event.unicode
        return False
        
    def draw(self, surface):
        # Рисуем фон
        pygame.draw.rect(surface, INPUT_BG_COLOR, self.rect, border_radius=5)
        
        # Рисуем текст или плейсхолдер
        if self.text:
            display_text = "*" * len(self.text) if self.is_password else self.text
            text_surface = font_medium.render(display_text, True, TEXT_COLOR)
        else:
            text_surface = font_medium.render(self.placeholder, True, (150, 152, 157))
            
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))
        
        # Рисуем обводку если активно
        if self.active:
            pygame.draw.rect(surface, ACCENT_COLOR, self.rect, 2, border_radius=5)

# Экран авторизации
def auth_screen():
    login_box = InputBox(SCREEN_WIDTH//2 - 150, 250, 300, 40, "Логин")
    password_box = InputBox(SCREEN_WIDTH//2 - 150, 320, 300, 40, "Пароль", is_password=True)
    login_button = Button(SCREEN_WIDTH//2 - 150, 400, 300, 40, "Войти")
    register_button = Button(SCREEN_WIDTH//2 - 150, 460, 300, 40, "Зарегистрироваться")
    
    error_message = ""
    success_message = ""
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            login_box.handle_event(event)
            password_box.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_button.rect.collidepoint(mouse_pos):
                    # Попытка входа
                    if login_box.text in users and users[login_box.text]["password"] == hash_password(password_box.text):
                        return login_box.text  # Возвращаем имя пользователя
                    else:
                        error_message = "Неверный логин или пароль"
                        success_message = ""
                        
                elif register_button.rect.collidepoint(mouse_pos):
                    # Попытка регистрации
                    if not login_box.text:
                        error_message = "Логин не может быть пустым"
                        success_message = ""
                    elif login_box.text in users:
                        error_message = "Пользователь уже существует"
                        success_message = ""
                    elif not password_box.text:
                        error_message = "Пароль не может быть пустым"
                        success_message = ""
                    else:
                        user_id = generate_id()
                        users[login_box.text] = {
                            "password": hash_password(password_box.text),
                            "id": user_id,
                            "channels": []
                        }
                        save_data(users_file, users)
                        error_message = ""
                        success_message = f"Регистрация успешна! Ваш ID: {user_id}"
        
        # Обновление состояния кнопок
        login_button.check_hover(mouse_pos)
        register_button.check_hover(mouse_pos)
        
        # Отрисовка
        screen.fill(BG_COLOR)
        
        # Заголовок
        title = font_large.render("Discord-подобное приложение", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Поля ввода и кнопки
        login_box.draw(screen)
        password_box.draw(screen)
        login_button.draw(screen)
        register_button.draw(screen)
        
        # Сообщение об ошибке
        if error_message:
            error_text = font_small.render(error_message, True, (240, 71, 71))
            screen.blit(error_text, (SCREEN_WIDTH//2 - error_text.get_width()//2, 520))
        
        # Сообщение об успехе
        if success_message:
            success_text = font_small.render(success_message, True, (59, 165, 93))
            screen.blit(success_text, (SCREEN_WIDTH//2 - success_text.get_width()//2, 520))
        
        pygame.display.flip()
        clock.tick(30)

# Главное меню
def main_menu(username):
    user_id = users[username]["id"]
    user_channels = users[username]["channels"]
    
    # Создаем элементы интерфейса
    create_channel_button = Button(50, 50, 200, 40, "Создать канал")
    search_box = InputBox(300, 50, 300, 40, "Поиск по ID")
    search_button = Button(620, 50, 100, 40, "Найти")
    logout_button = Button(SCREEN_WIDTH - 150, 50, 100, 40, "Выйти")
    
    # Список каналов
    channel_buttons = []
    for i, channel_id in enumerate(user_channels):
        if channel_id in channels:
            channel_name = channels[channel_id]["name"]
            channel_buttons.append(Button(50, 120 + i*60, 250, 50, channel_name))
    
    current_view = "channels"
    found_user = None
    message = ""
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            search_box.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_channel_button.rect.collidepoint(mouse_pos):
                    channel_id = generate_id()
                    channel_name = f"Канал {channel_id[:5]}"
                    channels[channel_id] = {
                        "name": channel_name,
                        "members": [username]
                    }
                    users[username]["channels"].append(channel_id)
                    save_data(users_file, users)
                    save_data(channels_file, channels)
                    # Обновляем список каналов
                    channel_buttons.append(Button(50, 120 + len(channel_buttons)*60, 250, 50, channel_name))
                    message = f"Создан канал: {channel_name}"
                
                elif search_button.rect.collidepoint(mouse_pos) and search_box.text:
                    # Поиск пользователя по ID
                    found_user = None
                    for user in users:
                        if users[user]["id"] == search_box.text:
                            found_user = user
                            break
                    current_view = "user_info"
                    message = f"Найден пользователь: {found_user}" if found_user else "Пользователь не найден"
                
                elif logout_button.rect.collidepoint(mouse_pos):
                    return  # Возвращаемся к экрану авторизации
                
                # Проверяем клики по каналам
                for i, button in enumerate(channel_buttons):
                    if button.rect.collidepoint(mouse_pos):
                        channel_id = user_channels[i]
                        message = f"Выбран канал: {channels[channel_id]['name']}"
        
        # Обновление состояния кнопок
        create_channel_button.check_hover(mouse_pos)
        search_button.check_hover(mouse_pos)
        logout_button.check_hover(mouse_pos)
        for button in channel_buttons:
            button.check_hover(mouse_pos)
        
        # Отрисовка
        screen.fill(BG_COLOR)
        
        # Панель сверху
        pygame.draw.rect(screen, (47, 49, 54), (0, 0, SCREEN_WIDTH, 100))
        
        # Кнопки и поиск
        create_channel_button.draw(screen)
        search_box.draw(screen)
        search_button.draw(screen)
        logout_button.draw(screen)
        
        # Отображение ID пользователя
        id_text = font_small.render(f"Ваш ID: {user_id}", True, TEXT_COLOR)
        screen.blit(id_text, (SCREEN_WIDTH - id_text.get_width() - 20, 20))
        
        # Сообщение
        if message:
            msg_text = font_small.render(message, True, TEXT_COLOR)
            screen.blit(msg_text, (300, 100))
        
        if current_view == "channels":
            # Заголовок каналов
            channels_text = font_medium.render("Ваши каналы:", True, TEXT_COLOR)
            screen.blit(channels_text, (50, 90))
            
            # Список каналов
            for button in channel_buttons:
                button.draw(screen)
                
        elif current_view == "user_info":
            # Информация о найденном пользователе
            info_y = 150
            if found_user:
                user_info_text = font_medium.render(f"Найден пользователь: {found_user}", True, TEXT_COLOR)
                user_id_text = font_medium.render(f"ID: {users[found_user]['id']}", True, TEXT_COLOR)
                screen.blit(user_info_text, (300, info_y))
                screen.blit(user_id_text, (300, info_y + 40))
            else:
                not_found_text = font_medium.render("Пользователь не найден", True, TEXT_COLOR)
                screen.blit(not_found_text, (300, info_y))
        
        pygame.display.flip()
        clock.tick(30)

# Основной цикл приложения
def main():
    while True:
        username = auth_screen()
        if username:
            main_menu(username)

if __name__ == "__main__":
    main()