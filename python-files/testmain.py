import pygame
import random
import time
import sys
from datetime import datetime

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyRMENAl alpha v1.1 - Fixed Captcha bug")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)

# Шрифты
font = pygame.font.SysFont("Courier New", 24)
big_font = pygame.font.SysFont("Courier New", 36)

class BruteforceGame:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.password = ""
        self.guess = ""
        self.attempts = 0
        self.feedback = []
        self.time_left = 35
        self.last_time = time.time()
        self.difficulty = "easy"
        self.health = 100
        self.detection_risk = 0
        self.command_mode = False
        self.status_message = ""
        self.message_time = 0
        self.generate_password(4)
        self.captcha_text = ""
        self.captcha_input = ""
        
        # Инициализация новых систем
        self.log_system = LogSystem()
        self.admin_ai = AdminAI()
        self.network_map = NetworkMap()
        self.darknet = DarkNet()
        self.show_map = False
        self.show_darknet = False
        self.crypto_game = None
        self.current_target = "10.0.0.2"

    def generate_password(self, length):
        if self.difficulty == "easy":
            chars = "abcdef1234"
        elif self.difficulty == "medium":
            chars = "abcdefABCDEF1234!@"
        else:  # hard
            chars = "abcdefABCDEF1234!@#$%^&*"
        self.password = "".join(random.choices(chars, k=length))
    
    def check_guess(self):
        self.attempts += 1
        self.feedback = []
        self.log_system.add_log(f"BRUTEFORCE ATTEMPT ({self.attempts})")
        
        # 10% шанс обнаружения
        if random.random() < 0.1:
            self.detection_risk += 25
            self.log_system.add_log("SECURITY ALERT", False)
        
        for i in range(len(self.guess)):
            if i < len(self.password) and self.guess[i] == self.password[i]:
                self.feedback.append((self.guess[i], GREEN))
            else:
                self.feedback.append((self.guess[i], RED))
                self.health -= random.randint(2, 5)
        
        if self.guess == self.password:
            self.darknet.reputation += 10
            return True
        return False
    
    def captcha_challenge(self):
        self.captcha_text = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        self.captcha_input = ""
        self.log_system.add_log(f"CAPTCHA TRIGGERED: {self.captcha_text}")
        return self.captcha_text
    
    def update_timer(self):
        now = time.time()
        if now - self.last_time >= 1:
            self.time_left -= 1
            self.last_time = now
            
            # Проверяем действия администратора
            admin_action, penalty = self.admin_ai.update(self.detection_risk)
            if admin_action:
                self.status_message = f"СИСТЕМА: {admin_action}"
                self.message_time = time.time()
                if "Сброс паролей" in admin_action:
                    self.generate_password(len(self.password))
                elif "Блокировка IP" in admin_action:
                    self.detection_risk = min(100, self.detection_risk + penalty)
    
    def is_time_up(self):
        return self.time_left <= 0
    
    def process_command(self, command):
        command = command.lower().strip()
        
        if command == "delete_logs":
            success, message = self.log_system.delete_logs()
            if success:
                self.detection_risk = max(0, self.detection_risk - 30)
            else:
                self.detection_risk = min(100, self.detection_risk + 10)
            self.status_message = message
        
        elif command == "show_logs":
            self.log_system.show_logs = not self.log_system.show_logs
            self.show_map = False
            self.show_darknet = False
            self.status_message = "Логи отображены" if self.log_system.show_logs else "Логи скрыты"
        
        elif command == "map":
            self.show_map = not self.show_map
            self.log_system.show_logs = False
            self.show_darknet = False
            self.status_message = "Карта сети открыта" if self.show_map else ""
        
        elif command == "darknet":
            self.show_darknet = not self.show_darknet
            self.log_system.show_logs = False
            self.show_map = False
            self.status_message = "DarkNet доступен" if self.show_darknet else ""
        
        elif command == "encrypt":
            self.crypto_game = CryptoGame()
            self.status_message = "Режим шифрования активирован"
        
        elif command == "ddos":
            self.status_message = "Запуск DDoS атаки..."
            self.time_left = max(10, self.time_left - 15)
            self.detection_risk = min(100, self.detection_risk + 40)
        
        elif command == "help":
            self.status_message = "Команды: show_logs, delete_logs, map, darknet, encrypt, ddos, clear"
        
        elif command == "clear":
            self.status_message = ""
        
        else:
            self.status_message = f"Неизвестная команда: {command}"
        
        self.message_time = time.time()

class AdminAI:
    def __init__(self):
        self.alert_level = 0
        self.last_action_time = time.time()
        self.actions = [
            (30, "Сканирование сети...", 10),
            (60, "Сброс паролей!", 30),
            (90, "Блокировка IP!", 50)
        ]
    
    def update(self, detection_risk):
        self.alert_level = min(100, self.alert_level + detection_risk * 0.05)
        
        now = time.time()
        if now - self.last_action_time > 5:
            self.last_action_time = now
            for threshold, message, penalty in self.actions:
                if self.alert_level >= threshold and random.random() < 0.3:
                    return message, penalty
        return None, 0

class NetworkMap:
    def __init__(self):
        self.nodes = {
            "192.168.1.1": {"name": "Маршрутизатор", "security": 2},
            "10.0.0.2": {"name": "Сервер БД", "security": 4},
            "10.0.0.3": {"name": "Файловый сервер", "security": 3}
        }
    
    def draw(self, screen, font):
        pygame.draw.rect(screen, DARK_GREEN, (100, 100, 600, 400))
        pygame.draw.rect(screen, BLACK, (110, 110, 580, 380))
        
        title = font.render("=== КАРТА СЕТИ ===", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        for i, (ip, data) in enumerate(self.nodes.items()):
            y_pos = 180 + i*60
            node_text = font.render(f"{ip} - {data['name']} (Защита: {data['security']}/5)", True, 
                                  GREEN if data['security'] < 3 else YELLOW)
            screen.blit(node_text, (150, y_pos))

class DarkNet:
    def __init__(self):
        self.reputation = 0
        self.contracts = [
            {"target": "10.0.0.2", "reward": 500, "risk": 20, "description": "Кража данных клиентов"},
            {"target": "10.0.0.3", "reward": 800, "risk": 40, "description": "Удаление резервных копий"},
            {"target": "192.168.1.1", "reward": 1200, "risk": 60, "description": "Полный контроль сети"}
        ]
    
    def draw(self, screen, font):
        pygame.draw.rect(screen, PURPLE, (50, 50, 700, 500))
        pygame.draw.rect(screen, BLACK, (60, 60, 680, 480))
        
        title = font.render("=== DARKNET MARKET ===", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        rep_text = font.render(f"Ваша репутация: {self.reputation}", True, GREEN)
        screen.blit(rep_text, (100, 130))
        
        for i, contract in enumerate(self.contracts):
            y_pos = 180 + i*120
            texts = [
                f"Цель: {contract['target']}",
                f"Награда: ${contract['reward']}",
                f"Риск: {contract['risk']}%",
                f"Описание: {contract['description']}"
            ]
            for j, text in enumerate(texts):
                screen.blit(font.render(text, True, YELLOW if j == 3 else WHITE), 
                          (100, y_pos + j*30))

class LogSystem:
    def __init__(self):
        self.logs = []
        self.generate_initial_logs()
        self.show_logs = False
        
    def generate_initial_logs(self):
        log_types = ["SYSTEM BOOT", "SERVICE START", "USER LOGIN", "NETWORK CONNECT"]
        for _ in range(random.randint(3, 6)):
            log = {
                'type': random.choice(log_types),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ip': f"192.168.1.{random.randint(1, 255)}",
                'is_player': False
            }
            self.logs.append(log)
    
    def add_log(self, action_type, is_player_action=True):
        log = {
            'type': action_type,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ip': "YOUR_IP",
            'is_player': is_player_action
        }
        self.logs.append(log)
        if len(self.logs) > 20:
            self.logs.pop(0)
    
    def delete_logs(self):
        success = random.random() < 0.7
        if success:
            self.logs = [log for log in self.logs if not log['is_player']]
            return True, "Логи успешно удалены!"
        return False, "Ошибка удаления: доступ запрещен!"
    
    def draw(self, screen, font):
        if not self.show_logs:
            return
            
        pygame.draw.rect(screen, DARK_GREEN, (20, 250, 760, 300))
        pygame.draw.rect(screen, BLACK, (25, 255, 750, 290))
        
        title = font.render("=== СИСТЕМНЫЕ ЛОГИ ===", True, CYAN)
        screen.blit(title, (30, 260))
        
        for i, log in enumerate(self.logs[-10:]):
            log_color = RED if log['is_player'] else GREEN
            log_text = f"{log['timestamp']} | {log['type']} | {log['ip']}"
            screen.blit(font.render(log_text, True, log_color), (30, 300 + i*30))

class CryptoGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.plaintext = "SECRET"
        self.key = random.randint(1, 255)
        self.ciphertext = "".join(chr(ord(c) ^ self.key) for c in self.plaintext)
        self.player_key = 0
    
    def draw(self, screen):
        screen.fill(BLACK)
        texts = [
            f"Зашифрованное сообщение: {self.ciphertext}",
            f"Текущий ключ: {bin(self.player_key)[2:]:>08}",
            "Используйте ← → для подбора ключа",
            "Enter - проверить, ESC - отмена"
        ]
        for i, text in enumerate(texts):
            screen.blit(font.render(text, True, GREEN), (50, 100 + i*40))
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.player_key = max(0, self.player_key - 1)
            elif event.key == pygame.K_RIGHT:
                self.player_key = min(255, self.player_key + 1)
            elif event.key == pygame.K_RETURN:
                return self.player_key == self.key
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
        return None

class MainMenu:
    def __init__(self):
        self.options = ["Новая игра", "Загрузить", "Настройки", "Выход"]
        self.selected = 0
        self.logo = [
            "  ___  _____  ___  _  _  ___  _   _  ___  ",
            " | _ \|_   _|/ __|| \| || __|| | | || _ \ ",
            " |  _/  | | | (__ | .` || _| | |_| ||  _/ ",
            " |_|    |_|  \___||_|\_||___| \___/ |_|  "
        ]
    
    def draw(self, screen):
        screen.fill(BLACK)
        for i, line in enumerate(self.logo):
            text = big_font.render(line, True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 100 + i*40))
        
        for i, opt in enumerate(self.options):
            color = CYAN if i == self.selected else WHITE
            text = font.render(f"> {opt}", True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 300 + i*40))
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]
        return None

def main():
    current_state = "menu"
    game = None
    menu = MainMenu()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state == "menu":
                result = menu.handle_input(event)
                if result == "Новая игра":
                    current_state = "game"
                    game = BruteforceGame()
                elif result == "Выход":
                    running = False
            
            elif current_state == "game":
                if game.crypto_game:
                    result = game.crypto_game.handle_input(event)
                    if result == True:
                        game.status_message = "Шифрование взломано! +15 секунд"
                        game.time_left += 15
                        game.crypto_game = None
                    elif result == "cancel":
                        game.status_message = "Шифрование отменено"
                        game.crypto_game = None
                
                elif event.type == pygame.KEYDOWN:
                    if game.show_map or game.show_darknet:
                        if event.key == pygame.K_ESCAPE:
                            game.show_map = False
                            game.show_darknet = False
                    
                    elif event.key == pygame.K_RETURN:
                        if game.command_mode:
                            game.process_command(game.guess)
                            game.guess = ""
                            game.command_mode = False
                        else:
                            if game.check_guess():
                                current_state = "success"
                            else:
                                if game.attempts >= 5:
                                    game.captcha_challenge()
                                    current_state = "captcha"
                                game.guess = ""
                    
                    elif event.key == pygame.K_F1:
                        game.command_mode = not game.command_mode
                        game.guess = ""
                    
                    elif event.key == pygame.K_BACKSPACE:
                        game.guess = game.guess[:-1]
                        game.feedback = []
                    
                    elif len(game.guess) < (50 if game.command_mode else len(game.password)):
                        game.guess += event.unicode
                        game.feedback = []
            
            elif current_state == "captcha":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if game.captcha_input == game.captcha_text:
                            current_state = "game"
                        else:
                            game.detection_risk += 30
                            current_state = "detected" if game.detection_risk >= 100 else "game"
                        game.captcha_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        game.captcha_input = game.captcha_input[:-1]
                    else:
                        game.captcha_input += event.unicode
            
            elif current_state in ["success", "failed", "detected"]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    current_state = "menu"
        
        # Отрисовка
        screen.fill(BLACK)
        
        if current_state == "menu":
            menu.draw(screen)
        
        elif current_state == "game":
            game.update_timer()
            if game.is_time_up() or game.health <= 0:
                current_state = "failed"
            elif game.detection_risk >= 100:
                current_state = "detected"
            
            # Отрисовка интерфейса
            timer_color = GREEN if game.time_left > 10 else YELLOW if game.time_left > 5 else RED
            screen.blit(font.render(f"Время: {game.time_left} сек", True, timer_color), (20, 20))
            screen.blit(font.render(f"Попыток: {game.attempts}", True, DARK_GREEN), (20, 50))
            screen.blit(font.render(f"Целостность: {game.health}%", True, 
                                  GREEN if game.health > 50 else YELLOW if game.health > 20 else RED), (20, 80))
            screen.blit(font.render(f"Риск обнаружения: {game.detection_risk}%", True, 
                                  BLUE if game.detection_risk < 50 else YELLOW if game.detection_risk < 80 else RED), (20, 110))
            
            if game.crypto_game:
                game.crypto_game.draw(screen)
            elif game.show_map:
                game.network_map.draw(screen, font)
            elif game.show_darknet:
                game.darknet.draw(screen, font)
            else:
                if game.command_mode:
                    input_label = font.render("> Введите команду:", True, CYAN)
                else:
                    input_label = font.render(f"> Введите пароль ({game.current_target}):", True, GREEN)
                
                screen.blit(input_label, (20, 160))
                
                x_pos = 20 + input_label.get_width()
                if not game.feedback:
                    guess_surface = font.render(game.guess, True, WHITE)
                    screen.blit(guess_surface, (x_pos, 160))
                else:
                    for char, color in game.feedback:
                        char_surface = font.render(char, True, color)
                        screen.blit(char_surface, (x_pos, 160))
                        x_pos += char_surface.get_width()
                
                if pygame.time.get_ticks() % 1000 < 500:
                    cursor_x = x_pos
                    cursor_color = CYAN if game.command_mode else GREEN
                    screen.blit(font.render("_", True, cursor_color), (cursor_x, 160))
                
                game.log_system.draw(screen, font)
            
            if game.status_message and time.time() - game.message_time < 3:
                screen.blit(font.render(game.status_message, True, YELLOW), (20, 200))
            
            if game.command_mode or (time.time() - game.last_time < 5 and game.attempts == 0):
                help_text = "F1: Команды | ESC: Выход" if game.show_map or game.show_darknet else "F1: Команды"
                screen.blit(font.render(help_text, True, DARK_GREEN), (WIDTH - font.size(help_text)[0] - 20, HEIGHT - 30))
        
        elif current_state == "captcha":
            input_label = font.render(f"> Введите капчу [{game.captcha_text}]:", True, YELLOW)
            screen.blit(input_label, (20, 160))
            screen.blit(font.render(game.captcha_input, True, WHITE), (20 + input_label.get_width(), 160))
            
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = 20 + input_label.get_width() + font.size(game.captcha_input)[0]
                screen.blit(font.render("_", True, YELLOW), (cursor_x, 160))
        
        elif current_state == "success":
            result_text = big_font.render("ДОСТУП РАЗРЕШЕН!", True, GREEN)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
            screen.blit(font.render("Нажмите SPACE для выхода в меню", True, WHITE), 
                       (WIDTH//2 - font.size("Нажмите SPACE для выхода в меню")[0]//2, HEIGHT//2 + 50))
        
        elif current_state == "failed":
            result_text = big_font.render("ВЗЛОМ ПРОВАЛЕН!", True, RED)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
            screen.blit(font.render("Нажмите SPACE для выхода в меню", True, WHITE), 
                       (WIDTH//2 - font.size("Нажмите SPACE для выхода в меню")[0]//2, HEIGHT//2 + 50))
        
        elif current_state == "detected":
            result_text = big_font.render("ВАС ОБНАРУЖИЛИ!", True, RED)
            screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
            screen.blit(font.render("Нажмите SPACE для выхода в меню", True, WHITE), 
                       (WIDTH//2 - font.size("Нажмите SPACE для выхода в меню")[0]//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()