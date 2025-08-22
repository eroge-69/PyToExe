import pygame
import random
import time
import sys
from datetime import datetime

# Инициализация Pygame
pygame.init()

# Глобальные переменные для настроек
WIDTH, HEIGHT = 800, 600
SCREEN_SIZE_OPTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1920, 1080)
]
current_size_index = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyRMENAl alpha v3.0 - Massive Update") 
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
font = None
big_font = None

def init_fonts():
    global font, big_font
    base_size = min(WIDTH, HEIGHT) // 30
    font = pygame.font.SysFont("Courier New", base_size)
    big_font = pygame.font.SysFont("Courier New", int(base_size * 1.5))

init_fonts()

# ==================== ДИАЛОГИ ====================
class DialogueManager:
    def __init__(self):
        self.dialogue_queue = []
        self.current_dialogue = None
        self.characters = {
            "Алиса": {"color": (255, 100, 100), "side": "left"},
            "Рей": {"color": (100, 100, 255), "side": "right"},
            "Система": {"color": (100, 255, 100), "side": "center"}
        }
        self.active = False
        self.typing_index = 0
        self.last_char_time = 0
        self.current_options = []
        self.option_selected = None
        
    def add_dialogue(self, character, text, duration=5, options=None):
        self.dialogue_queue.append({
            "character": character,
            "text": text,
            "duration": duration,
            "options": options or [],
            "start_time": 0
        })
        
    def update(self):
        if not self.active and self.dialogue_queue:
            self.current_dialogue = self.dialogue_queue.pop(0)
            self.active = True
            self.typing_index = 0
            self.last_char_time = time.time()
            self.current_dialogue["start_time"] = time.time()
            self.current_options = self.current_dialogue["options"]
            self.option_selected = 0 if self.current_options else None
            
        if self.active:
            if (time.time() - self.last_char_time > 0.05 and 
                self.typing_index < len(self.current_dialogue["text"])):
                self.typing_index += 1
                self.last_char_time = time.time()
                
            if (time.time() - self.current_dialogue["start_time"] > 
                self.current_dialogue["duration"] and not self.current_options):
                self.active = False
                
    def draw(self, screen):
        if not self.active or not self.current_dialogue:
            return
            
        char_data = self.characters.get(self.current_dialogue["character"], 
                                      {"color": WHITE, "side": "center"})
        text = self.current_dialogue["text"][:self.typing_index]
        
        # Рендер текста
        lines = []
        words = text.split(' ')
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] < WIDTH - 100:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
            
        # Отрисовка фона
        if char_data["side"] != "center":
            box_width = min(WIDTH - 200, 600)
            box_height = 40 + len(lines) * 30
            box_x = 50 if char_data["side"] == "left" else WIDTH - box_width - 50
            box_y = HEIGHT - box_height - 50
            
            pygame.draw.rect(screen, (30, 30, 30), 
                           (box_x - 10, box_y - 10, box_width + 20, box_height + 20))
            pygame.draw.rect(screen, (60, 60, 60), 
                           (box_x, box_y, box_width, box_height))
            
            # Имя персонажа
            name_surface = font.render(
                self.current_dialogue["character"], 
                True, 
                char_data["color"]
            )
            screen.blit(name_surface, (box_x + 20, box_y + 10))
            
            # Текст
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, WHITE)
                screen.blit(text_surface, (box_x + 20, box_y + 50 + i * 30))
        
        # Отрисовка вариантов ответа
        if self.current_options:
            options_box_y = HEIGHT - 180 - len(self.current_options) * 40
            pygame.draw.rect(screen, (20, 20, 20), 
                           (WIDTH//2 - 200, options_box_y - 20, 400, 100 + len(self.current_options) * 40))
            
            for i, option in enumerate(self.current_options):
                color = YELLOW if i == self.option_selected else WHITE
                option_text = font.render(f"{i+1}. {option['text']}", True, color)
                screen.blit(option_text, (WIDTH//2 - 180, options_box_y + i * 40))
                
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and self.current_options:
            if pygame.K_1 <= event.key <= pygame.K_9:
                option_idx = event.key - pygame.K_1
                if option_idx < len(self.current_options):
                    return self.current_options[option_idx]["action"]
            elif event.key == pygame.K_UP:
                self.option_selected = max(0, self.option_selected - 1) if self.option_selected is not None else 0
            elif event.key == pygame.K_DOWN:
                if self.option_selected is None:
                    self.option_selected = 0
                else:
                    self.option_selected = min(len(self.current_options) - 1, self.option_selected + 1)
            elif event.key == pygame.K_RETURN and self.option_selected is not None:
                return self.current_options[self.option_selected]["action"]
        return None

# ==================== SQL ИНЪЕКЦИЯ ====================
class SQLInjectionGame:
    def __init__(self, query):
        self.original_query = query
        self.player_query = query
        self.cursor_pos = len(query)
        self.success = False
        self.vulnerable_points = [
            {"pos": len("SELECT * FROM users WHERE username='admin' AND password='"), "type": "string"},
            {"pos": len("SELECT * FROM users WHERE id="), "type": "numeric"}
        ]
        self.common_payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "' UNION SELECT 1,password,3 FROM users --",
            "'; DROP TABLE users --"
        ]
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (50, 100, WIDTH-100, 300))
        pygame.draw.rect(screen, DARK_GREEN, (55, 105, WIDTH-110, 290))
        
        # Отрисовка запроса
        x_pos = 60
        for i, char in enumerate(self.player_query):
            color = RED if any(v["pos"] == i for v in self.vulnerable_points) else GREEN
            char_surf = font.render(char, True, color)
            screen.blit(char_surf, (x_pos, 120))
            x_pos += char_surf.get_width()
            
        # Курсор
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = 60 + font.size(self.player_query[:self.cursor_pos])[0]
            pygame.draw.line(screen, WHITE, (cursor_x, 150), (cursor_x, 170), 2)
            
        # Подсказки
        help_text = font.render("Примеры SQL-инъекций:", True, YELLOW)
        screen.blit(help_text, (60, 200))
        
        for i, payload in enumerate(self.common_payloads):
            payload_text = font.render(f"{i+1}. {payload}", True, CYAN)
            screen.blit(payload_text, (60, 230 + i * 30))
            
        status_color = GREEN if self.success else RED
        status_text = font.render("УСПЕХ!" if self.success else "Неверный запрос", True, status_color)
        screen.blit(status_text, (WIDTH - 200, 120))
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.player_query), self.cursor_pos + 1)
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.player_query = self.player_query[:self.cursor_pos-1] + self.player_query[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RETURN:
                self.check_injection()
                return self.success
            elif event.key == pygame.K_1:
                self.insert_payload(0)
            elif event.key == pygame.K_2:
                self.insert_payload(1)
            elif event.key == pygame.K_3:
                self.insert_payload(2)
            elif event.key == pygame.K_4:
                self.insert_payload(3)
            elif event.unicode:
                self.player_query = self.player_query[:self.cursor_pos] + event.unicode + self.player_query[self.cursor_pos:]
                self.cursor_pos += len(event.unicode)
        return None
        
    def insert_payload(self, payload_idx):
        if payload_idx < len(self.common_payloads):
            payload = self.common_payloads[payload_idx]
            self.player_query = self.player_query[:self.cursor_pos] + payload + self.player_query[self.cursor_pos:]
            self.cursor_pos += len(payload)
        
    def check_injection(self):
        patterns = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "' UNION SELECT",
            "'; DROP TABLE"
        ]
        self.success = any(patt in self.player_query for patt in patterns)

# ==================== НАСТРОЙКИ ====================
class Settings:
    def __init__(self):
        self.difficulty = "medium"
        self.resolution_index = 0
        self.fullscreen = False

# ==================== СЮЖЕТ ====================
class StoryManager:
    def __init__(self):
        self.chapter = 1
        self.mission = 1
        self.story_flags = set()
        
        self.missions = {
            1: {
                1: {
                    "target": "mail.omnicorp.com",
                    "goal": "Взломать почту сотрудника",
                    "password_length": 4,
                    "difficulty": "easy",
                    "hint": "Попробуйте дату рождения (ддмм)",
                    "success_msg": "Письмо обнаружено: #ProjectPhoenix - биологическое оружие!",
                    "next_chapter": 1,
                    "next_mission": 2,
                    "cutscene": "Алиса: 'Мы должны это остановить...'",
                    "dialogues": [
                        {
                            "character": "Алиса",
                            "text": "Привет, новичок. Нам нужно проникнуть в почту сотрудника OmniCorp.",
                            "trigger": "start"
                        },
                        {
                            "character": "Алиса",
                            "text": "Какой метод взлома будем использовать?",
                            "trigger": "start",
                            "options": [
                                {
                                    "text": "Brute-force (просто, но долго)",
                                    "action": "set_hack_method('bruteforce')"
                                },
                                {
                                    "text": "SQL-инъекция (нужен инжектор)",
                                    "action": "set_hack_method('sql')",
                                    "condition": "has_item('sql_injector')"
                                },
                                {
                                    "text": "Фишинг (рискованно)",
                                    "action": "set_hack_method('phishing')"
                                }
                            ]
                        },
                        {
                            "character": "Рей",
                            "text": "Будь осторожен, их система защиты активна.",
                            "trigger": "after_3_attempts"
                        },
                        {
                            "character": "Алиса",
                            "text": "Отлично! Мы получили доступ к письмам.",
                            "trigger": "success"
                        }
                    ]
                },
                2: {
                    "target": "testlab.omnicorp.com",
                    "goal": "Найти видео испытаний",
                    "password_length": 6,
                    "difficulty": "medium",
                    "captcha_after": 3,
                    "success_msg": "Видео найдено! Вирус тестируют на людях...",
                    "next_chapter": 2,
                    "next_mission": 1,
                    "cutscene": "Лаборатория находится в Швейцарии. Нужно проникнуть в их систему безопасности."
                }
            },
            2: {
                1: {
                    "target": "secure.omnicorp.com",
                    "goal": "Взломать сервер безопасности",
                    "password_length": 6,
                    "difficulty": "medium",
                    "time_limit": 120,
                    "admin_scan": 20,
                    "success_msg": "Координаты лаборатории: 46.2044°N, 6.1432°E",
                    "next_chapter": 3,
                    "next_mission": 1,
                    "cutscene": "Теперь у нас есть доступ к основной системе. Время действовать!"
                }
            }
        }
    
    def get_current_mission(self):
        return self.missions[self.chapter][self.mission]
    
    def complete_mission(self):
        current = self.get_current_mission()
        return {
            "next_chapter": current["next_chapter"],
            "next_mission": current["next_mission"],
            "cutscene": current.get("cutscene", "")
        }

# ==================== ИГРОВЫЕ КЛАССЫ ====================
class BruteforceGame:
    def __init__(self, settings):
        self.settings = settings
        self.reset_game()
        self.chapter_transition = False
        self.hack_method = "bruteforce"
        self.inventory = []
        self.dialogue_manager = DialogueManager()  # Добавлено здесь
        self.reset_game()
        self.chapter_transition = False
    
    def reset_game(self):
        self.password = ""
        self.guess = ""
        self.attempts = 0
        self.feedback = []
        self.time_left = random.randint(35, 50)
        self.last_time = time.time()
        self.health = 100
        self.detection_risk = 0
        self.command_mode = False
        self.status_message = ""
        self.message_time = 0
        self.captcha_text = ""
        self.captcha_input = ""
        self.chapter_transition = False
        self.money = 1000
        self.shop = Shop()
        self.hint_interval = None
        self.hint_counter = 0
        self.auto_heal = False
        self.log_system = LogSystem()
        self.admin_ai = AdminAI()
        self.network_map = NetworkMap()
        self.darknet = DarkNet()
        self.show_map = False
        self.show_darknet = False
        self.crypto_game = None
        self.sql_game = None
        self.story = StoryManager()
        self.story_mode = True
        self.dialogue_manager = DialogueManager()  # И здесь
        self.hack_method = "bruteforce"
        self.inventory = []
        self.load_mission()
        self.init_story_dialogues()
    
    def init_story_dialogues(self):
        if not self.story_mode:
            return
            
        mission = self.story.get_current_mission()
        if "dialogues" in mission:
            for dialogue in mission["dialogues"]:
                if dialogue["trigger"] == "start":
                    options = []
                    for opt in dialogue.get("options", []):
                        if not opt.get("condition") or self.check_condition(opt["condition"]):
                            options.append(opt)
                    
                    self.dialogue_manager.add_dialogue(
                        dialogue["character"],
                        dialogue["text"],
                        dialogue.get("duration", 5),
                        options
                    )
    
    def check_condition(self, condition):
        if ">" in condition:
            var, val = condition.split(">")
            return getattr(self, var) > float(val)
        elif "has_item" in condition:
            item = condition.split("'")[1]
            return item in self.inventory
        return True
    
    def trigger_dialogue(self, trigger_name):
        if not self.story_mode:
            return
            
        mission = self.story.get_current_mission()
        if "dialogues" in mission:
            for dialogue in mission["dialogues"]:
                if dialogue["trigger"] == trigger_name:
                    options = []
                    for opt in dialogue.get("options", []):
                        if not opt.get("condition") or self.check_condition(opt["condition"]):
                            options.append(opt)
                    
                    self.dialogue_manager.add_dialogue(
                        dialogue["character"],
                        dialogue["text"],
                        dialogue.get("duration", 5),
                        options
                    )
    
    def add_health(self):
        current_health = self.health
        
        if current_health > 80:
            return 0
        elif 50 <= current_health <= 80:
            health_to_add = random.randint(10, 50)
        elif 1 <= current_health < 50:
            health_to_add = random.randint(50, 70)
        else:
            health_to_add = random.randint(50, 80)
        
        self.health = min(100, self.health + health_to_add)
        return health_to_add
    
    def load_mission(self):
        if not self.story_mode:
            self.current_target = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            self.generate_password()
            return
            
        mission = self.story.get_current_mission()
        self.current_target = mission["target"]
        self.generate_password(mission["password_length"])
        self.time_left = mission.get("time_limit", 60)
        
        if "admin_scan" in mission:
            self.admin_ai.base_scan_interval = mission["admin_scan"]
        
        self.status_message = ""
        self.message_time = 0
    
    def generate_password(self, length=None):
        if length is None:
            if self.settings.difficulty == "easy":
                length = random.randint(4, 5)
            elif self.settings.difficulty == "medium":
                length = random.randint(5, 7)
            else:
                length = random.randint(7, 9)
        
        if self.settings.difficulty == "easy" or (self.story_mode and self.story.get_current_mission()["difficulty"] == "easy"):
            chars = "abcdef1234"
        elif self.settings.difficulty == "medium" or (self.story_mode and self.story.get_current_mission()["difficulty"] == "medium"):
            chars = "abcdefABCDEF1234!@"
        else:
            chars = "abcdefABCDEF1234!@#$%^&*"
        self.password = "".join(random.choices(chars, k=length))
    
    def check_guess(self):
        self.attempts += 1
        self.hint_counter += 1
        self.feedback = []
        self.log_system.add_log(f"BRUTEFORCE ATTEMPT ({self.attempts})")
        
        if self.hint_interval and self.hint_counter >= self.hint_interval:
            self.hint_counter = 0
            self.show_hint()
        
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
            added_health = self.add_health()
            health_message = f" +{added_health}% здоровья" if added_health > 0 else ""
            
            reward_multiplier = {
                "bruteforce": 1.0,
                "sql": 1.5,
                "phishing": 1.8
            }
            base_reward = len(self.password) * 50
            reward = int(base_reward * reward_multiplier.get(self.hack_method, 1.0))
            self.money += reward
            reward_message = f" +${reward}"
            
            if self.story_mode:
                mission = self.story.get_current_mission()
                self.status_message = f"{mission['success_msg']}{health_message}{reward_message}"
                self.message_time = time.time()
                
                next_mission = self.story.complete_mission()
                self.chapter_transition = True
                self.time_left = 9999
                self.status_message = "Введите 'next_chapter' для перехода к следующей главе"
                self.message_time = time.time()
            else:
                self.status_message = f"Доступ разрешен!{health_message}{reward_message}"
            
            self.darknet.reputation += 10
            self.trigger_dialogue("success")
            return True
        
        if self.attempts == 3:
            self.trigger_dialogue("after_3_attempts")
            
        return False
    
    def start_next_chapter(self):
        current = self.story.get_current_mission()
        next_mission = self.story.complete_mission()
        self.story.chapter = next_mission["next_chapter"]
        self.story.mission = next_mission["next_mission"]
        self.chapter_transition = False
        self.load_mission()
        self.init_story_dialogues()
        
        mission = self.story.get_current_mission()
        self.time_left = mission.get("time_limit", 60)
        
        if "cutscene" in mission and mission["cutscene"]:
            self.status_message = mission["cutscene"]
            self.message_time = time.time()
    
    def show_hint(self):
        if not self.password:
            return
            
        hidden_positions = [i for i, char in enumerate(self.guess) 
                          if i < len(self.password) and char != self.password[i]]
        
        if hidden_positions:
            pos = random.choice(hidden_positions)
            hint_char = self.password[pos]
            self.status_message = f"Подсказка: символ {pos+1} - '{hint_char}'"
            self.message_time = time.time()
    
    def captcha_challenge(self):
        self.captcha_text = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        self.captcha_input = ""
        self.log_system.add_log(f"CAPTCHA TRIGGERED: {self.captcha_text}")
        return self.captcha_text
    
    def update_timer(self):
        if self.chapter_transition:
            return
            
        now = time.time()
        if now - self.last_time >= 1:
            self.time_left -= 1
            self.last_time = now
            
            if hasattr(self, 'auto_heal') and self.auto_heal:
                self.health = min(100, self.health + 1)
            
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
        
        if self.chapter_transition and command == "next_chapter":
            self.start_next_chapter()
            return
        
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
        
        elif command == "sql_inject":
            if "sql_injector" in self.inventory:
                self.sql_game = SQLInjectionGame("SELECT * FROM users WHERE username='admin' AND password=''")
                self.status_message = "Режим SQL-инъекции активирован"
            else:
                self.status_message = "Для этого нужен SQL-инжектор (купите в DarkNet)"
        
        elif command == "ddos":
            self.status_message = "Запуск DDoS атаки..."
            self.time_left = max(10, self.time_left - 15)
            self.detection_risk = min(100, self.detection_risk + 40)
        
        elif command == "help":
            help_text = [
                "Команды:",
                "show_logs - показать логи системы",
                "delete_logs - удалить следы взлома",
                "map - карта сети",
                "darknet - доступ к DarkNet",
                "encrypt - режим шифрования",
                "sql_inject - SQL-инъекция (требуется инжектор)",
                "ddos - DDoS атака (рискованно)",
                "clear - очистить сообщения"
            ]
            self.status_message = "\n".join(help_text)
        
        elif command == "clear":
            self.status_message = ""
        
        else:
            self.status_message = f"Неизвестная команда: {command}"
        
        self.message_time = time.time()
    
    def draw_game_interface(self, screen):
        # Отрисовка интерфейса
        timer_color = GREEN if self.time_left > 10 else YELLOW if self.time_left > 5 else RED
        screen.blit(font.render(f"Время: {self.time_left} сек", True, timer_color), (20, 20))
        screen.blit(font.render(f"Попыток: {self.attempts}", True, DARK_GREEN), (20, 50))
        screen.blit(font.render(f"Целостность: {self.health}%", True, 
                    GREEN if self.health > 50 else YELLOW if self.health > 20 else RED), (20, 80))
        screen.blit(font.render(f"Риск обнаружения: {self.detection_risk}%", True, 
                    BLUE if self.detection_risk < 50 else YELLOW if self.detection_risk < 80 else RED), (20, 110))
        
        screen.blit(font.render(f"Деньги: ${self.money}", True, YELLOW), (20, 140))
        screen.blit(font.render(f"Метод: {self.hack_method}", True, CYAN), (20, 170))
        
        if self.hint_interval:
            hint_text = font.render(f"Подсказка через: {self.hint_interval - self.hint_counter}", True, BLUE)
            screen.blit(hint_text, (WIDTH - hint_text.get_width() - 20, 140))
        
        if self.story_mode:
            mission = self.story.get_current_mission()
            mission_text = font.render(f"Миссия {self.story.chapter}.{self.story.mission}: {mission['goal']}", True, CYAN)
            screen.blit(mission_text, (WIDTH//2 - mission_text.get_width()//2, 10))
        
        if self.chapter_transition:
            transition_text = big_font.render("ГЛАВА ЗАВЕРШЕНА", True, CYAN)
            screen.blit(transition_text, (WIDTH//2 - transition_text.get_width()//2, HEIGHT//2 - 50))
            
            help_text = font.render("Введите 'next_chapter' для продолжения", True, YELLOW)
            screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT//2 + 20))
        elif self.sql_game:
            self.sql_game.draw(screen)
        elif self.crypto_game:
            self.crypto_game.draw(screen)
        elif self.show_map:
            self.network_map.draw(screen, font)
        elif self.show_darknet:
            self.darknet.draw(screen, font)
        else:
            if self.command_mode:
                input_label = font.render("> Введите команду:", True, CYAN)
            else:
                target = self.current_target if self.story_mode else "Random Server"
                input_label = font.render(f"> Введите пароль ({target}):", True, GREEN)
            
            screen.blit(input_label, (20, 200))
            
            x_pos = 20 + input_label.get_width()
            if not self.feedback:
                guess_surface = font.render(self.guess, True, WHITE)
                screen.blit(guess_surface, (x_pos, 200))
            else:
                for char, color in self.feedback:
                    char_surface = font.render(char, True, color)
                    screen.blit(char_surface, (x_pos, 200))
                    x_pos += char_surface.get_width()
            
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = x_pos
                cursor_color = CYAN if self.command_mode else GREEN
                screen.blit(font.render("_", True, cursor_color), (cursor_x, 200))
            
            self.log_system.draw(screen, font)
        
        if self.status_message and time.time() - self.message_time < 3:
            if "+" in self.status_message:
                parts = self.status_message.split("+")
                main_text = font.render(parts[0], True, YELLOW)
                health_text = font.render(f"+{parts[1]}", True, GREEN)
                screen.blit(main_text, (20, 240))
                screen.blit(health_text, (20 + main_text.get_width(), 240))
            else:
                screen.blit(font.render(self.status_message, True, YELLOW), (20, 240))
        
        self.dialogue_manager.draw(screen)
        
        help_text = "F1: Команды | F2: Магазин | ESC: Выход" if self.show_map or self.show_darknet else "F1: Команды | F2: Магазин"
        screen.blit(font.render(help_text, True, DARK_GREEN), (WIDTH - font.size(help_text)[0] - 20, HEIGHT - 30))

# ==================== ОСТАЛЬНЫЕ КЛАССЫ ====================
class AdminAI:
    def __init__(self):
        self.alert_level = 0
        self.last_action_time = time.time()
        self.actions = [
            (40, "Сканирование сети...", 15),
            (70, "Сброс паролей!", 40),
            (90, "Блокировка IP!", 70)
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
        pygame.draw.rect(screen, DARK_GREEN, (WIDTH//2-300, HEIGHT//2-200, 600, 400))
        pygame.draw.rect(screen, BLACK, (WIDTH//2-290, HEIGHT//2-190, 580, 380))
        
        title = font.render("=== КАРТА СЕТИ ===", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2-180))
        
        for i, (ip, data) in enumerate(self.nodes.items()):
            y_pos = HEIGHT//2-120 + i*60
            node_text = font.render(f"{ip} - {data['name']} (Защита: {data['security']}/5)", True, 
                                  GREEN if data['security'] < 3 else YELLOW)
            screen.blit(node_text, (WIDTH//2-250, y_pos))

class DarkNet:
    def __init__(self):
        self.reputation = 0
        self.contracts = [
            {"target": "10.0.0.2", "reward": 500, "risk": 20, "description": "Кража данных клиентов"},
            {"target": "10.0.0.3", "reward": 800, "risk": 40, "description": "Удаление резервных копий"},
            {"target": "192.168.1.1", "reward": 1200, "risk": 60, "description": "Полный контроль сети"}
        ]
        self.items = {
            "sql_injector": {
                "name": "SQL-инжектор v3.1",
                "price": 700,
                "description": "Позволяет использовать SQL-инъекции",
                "effect": "add_item('sql_injector')"
            },
            "vpn": {
                "name": "Премиум VPN",
                "price": 300,
                "description": "Снижает риск обнаружения на 20%",
                "effect": "detection_risk -= 20"
            },
            "exploit_kit": {
                "name": "Набор эксплойтов",
                "price": 1000,
                "description": "Увеличивает урон от brute-force на 30%",
                "effect": "health_damage *= 1.3"
            }
        }
    
    def draw(self, screen, font):
        pygame.draw.rect(screen, PURPLE, (WIDTH//2-350, HEIGHT//2-250, 700, 500))
        pygame.draw.rect(screen, BLACK, (WIDTH//2-340, HEIGHT//2-240, 680, 480))
        
        title = font.render("=== DARKNET MARKET ===", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2-220))
        
        rep_text = font.render(f"Ваша репутация: {self.reputation}", True, GREEN)
        screen.blit(rep_text, (WIDTH//2-300, HEIGHT//2-170))
        
        # Контракты
        contracts_title = font.render("=== КОНТРАКТЫ ===", True, CYAN)
        screen.blit(contracts_title, (WIDTH//2-300, HEIGHT//2-120))
        
        for i, contract in enumerate(self.contracts):
            y_pos = HEIGHT//2-80 + i*60
            texts = [
                f"Цель: {contract['target']}",
                f"Награда: ${contract['reward']}",
                f"Риск: {contract['risk']}%",
                f"Описание: {contract['description']}"
            ]
            for j, text in enumerate(texts):
                screen.blit(font.render(text, True, YELLOW if j == 3 else WHITE), 
                          (WIDTH//2-300, y_pos + j*30))
        
        # Предметы
        items_title = font.render("=== ХАКЕРСКИЕ ИНСТРУМЕНТЫ ===", True, CYAN)
        screen.blit(items_title, (WIDTH//2-300, HEIGHT//2+100))
        
        for i, (item_id, item) in enumerate(self.items.items()):
            y_pos = HEIGHT//2 + 140 + i*60
            color = GREEN if game.money >= item["price"] else RED
            text = font.render(f"{i+1}. {item['name']} - ${item['price']}", True, color)
            screen.blit(text, (WIDTH//2-300, y_pos))

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
            
        pygame.draw.rect(screen, DARK_GREEN, (20, HEIGHT//2-50, WIDTH-40, HEIGHT//2-20))
        pygame.draw.rect(screen, BLACK, (25, HEIGHT//2-45, WIDTH-50, HEIGHT//2-30))
        
        title = font.render("=== СИСТЕМНЫЕ ЛОГИ ===", True, CYAN)
        screen.blit(title, (30, HEIGHT//2-40))
        
        for i, log in enumerate(self.logs[-10:]):
            log_color = RED if log['is_player'] else GREEN
            log_text = f"{log['timestamp']} | {log['type']} | {log['ip']}"
            screen.blit(font.render(log_text, True, log_color), (30, HEIGHT//2 + i*30))

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

class Shop:
    def __init__(self):
        self.items = {
            "health_boost": {
                "name": "Улучшенный брандмауэр (+20% здоровья)",
                "price": 200,
                "effect": lambda game: setattr(game, 'health', min(200, game.health + 20))
            },
            "time_plus": {
                "name": "Ускоренный процессор (+30 сек)",
                "price": 300,
                "effect": lambda game: setattr(game, 'time_left', game.time_left + 30)
            },
            "password_hint": {
                "name": "Анализатор паролей (подсказка каждые 5 попыток)",
                "price": 500,
                "effect": lambda game: setattr(game, 'hint_interval', 5)
            },
            "stealth_module": {
                "name": "Стелс-модуль (-30% к обнаружению)",
                "price": 400,
                "effect": lambda game: setattr(game, 'detection_risk', max(0, game.detection_risk - 30))
            },
            "auto_heal": {
                "name": "Авто-ремонт (+1% здоровья/сек)",
                "price": 800,
                "effect": lambda game: setattr(game, 'auto_heal', True)
            }
        }
        self.available_items = list(self.items.keys())
    
    def draw(self, screen, font, money):
        pygame.draw.rect(screen, PURPLE, (WIDTH//2-350, HEIGHT//2-250, 700, 500))
        pygame.draw.rect(screen, BLACK, (WIDTH//2-340, HEIGHT//2-240, 680, 480))
        
        title = font.render("=== HACKER SHOP ===", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2-220))
        
        money_text = font.render(f"Ваши деньги: ${money}", True, GREEN)
        screen.blit(money_text, (WIDTH//2 - money_text.get_width()//2, HEIGHT//2-180))
        
        for i, item_id in enumerate(self.available_items):
            item = self.items[item_id]
            color = GREEN if money >= item["price"] else RED
            text = font.render(f"{i+1}. {item['name']} - ${item['price']}", True, color)
            screen.blit(text, (WIDTH//2-300, HEIGHT//2-120 + i*60))
        
        help_text = font.render("ESC - выйти | 1-5 - купить", True, DARK_GREEN)
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT//2+200))

class ResolutionMenu:
    def __init__(self):
        self.selected = 0
        self.options = SCREEN_SIZE_OPTIONS
        self.text_options = [f"{w}x{h}" for w, h in self.options]
        self.logo = [
            "  ____ __   ______  __  __ _ _   _ _  _   _ ",
            " |  _ \ \ / /  _ \|  \/  / | \ | | || | | |",
            " | |_) \ V /| |_) | |\/| | |  \| | || |_| |",
            "    |  __/ | | |  _ <| |  | | | |\  |__   _| |___",
            "      |_|    |_| |_| \_\_|  |_|_| \_|  |_| |_____| "
        ]
    
    def draw(self, screen):
        screen.fill(BLACK)
        for i, line in enumerate(self.logo):
            text = big_font.render(line, True, GREEN)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 100 + i*40))
        
        title = font.render("Выберите разрешение экрана:", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 300))
        
        for i, opt in enumerate(self.text_options):
            color = CYAN if i == self.selected else WHITE
            text = font.render(f"> {opt}", True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 350 + i*40))
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected]
        return None

class SettingsMenu:
    def __init__(self, settings):
        self.settings = settings
        self.selected = 0
        self.options = [
            ("Сложность", ["easy", "medium", "hard"]),
            ("Разрешение", [f"{w}x{h}" for w, h in SCREEN_SIZE_OPTIONS]),
            ("Полный экран", ["Нет", "Да"])
        ]
        self.current_values = [
            self.settings.difficulty,
            self.settings.resolution_index,
            self.settings.fullscreen
        ]
    
    def draw(self, screen):
        screen.fill(BLACK)
        title = font.render("=== НАСТРОЙКИ ===", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        for i, (option, values) in enumerate(self.options):
            color = CYAN if i == self.selected else WHITE
            option_text = font.render(f"{option}:", True, color)
            screen.blit(option_text, (WIDTH//2 - 200, 200 + i*60))
            
            if i == 1:
                value_text = font.render(values[self.current_values[i]], True, YELLOW)
            elif i == 2:
                value_text = font.render(values[int(self.current_values[i])], True, YELLOW)
            else:
                value_text = font.render(self.current_values[i], True, YELLOW)
            
            screen.blit(value_text, (WIDTH//2 + 50, 200 + i*60))
        
        help_text = font.render("Стрелки: выбор | Enter: изменить | ESC: назад", True, DARK_GREEN)
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, HEIGHT-100))
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                self.change_value(-1)
            elif event.key == pygame.K_RIGHT:
                self.change_value(1)
            elif event.key == pygame.K_RETURN:
                self.settings.difficulty = self.current_values[0]
                self.settings.resolution_index = self.current_values[1]
                self.settings.fullscreen = self.current_values[2]
                return "applied"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None
    
    def change_value(self, direction):
        if self.selected == 0:
            difficulties = ["easy", "medium", "hard"]
            current_index = difficulties.index(self.current_values[0])
            new_index = (current_index + direction) % len(difficulties)
            self.current_values[0] = difficulties[new_index]
        elif self.selected == 1:
            new_index = (self.current_values[1] + direction) % len(SCREEN_SIZE_OPTIONS)
            self.current_values[1] = new_index
        elif self.selected == 2:
            self.current_values[2] = not self.current_values[2]

class MainMenu:
    def __init__(self):
        self.options = ["Начать историю", "Свободная игра", "Настройки", "Выход"]
        self.selected = 0
        self.logo = [
            "  ____ __   ______  __  __ _ _   _ _  _   _ ",
            " |  _ \ \ / /  _ \|  \/  / | \ | | || | | |",
            " | |_) \ V /| |_) | |\/| | |  \| | || |_| |",
            "    |  __/ | | |  _ <| |  | | | |\  |__   _| |___",
            "      |_|    |_| |_| \_\_|  |_|_| \_|  |_| |_____| "
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

# ==================== ОСНОВНОЙ ЦИКЛ ====================
def main():
    global WIDTH, HEIGHT, screen, font, big_font, game
    
    # Выбор разрешения
    resolution_menu = ResolutionMenu()
    choosing_resolution = True
    running = True
    
    while choosing_resolution and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                choosing_resolution = False
            
            result = resolution_menu.handle_input(event)
            if result:
                WIDTH, HEIGHT = result
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                init_fonts()
                choosing_resolution = False
        
        resolution_menu.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    
    if not running:
        pygame.quit()
        return
    
    # Основные настройки
    settings = Settings()
    current_state = "menu"
    game = None
    menu = MainMenu()
    settings_menu = SettingsMenu(settings)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state == "menu":
                result = menu.handle_input(event)
                if result == "Начать историю":
                    current_state = "game"
                    game = BruteforceGame(settings)
                    game.story_mode = True
                    game.story = StoryManager()
                    game.init_story_dialogues()
                elif result == "Свободная игра":
                    current_state = "game"
                    game = BruteforceGame(settings)
                    game.story_mode = False
                    game.load_mission()
                elif result == "Настройки":
                    current_state = "settings"
                elif result == "Выход":
                    running = False
            
            elif current_state == "settings":
                result = settings_menu.handle_input(event)
                if result == "applied":
                    new_width, new_height = SCREEN_SIZE_OPTIONS[settings.resolution_index]
                    if new_width != WIDTH or new_height != HEIGHT:
                        WIDTH, HEIGHT = new_width, new_height
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if settings.fullscreen else 0)
                        init_fonts()
                        settings_menu = SettingsMenu(settings)
                    current_state = "menu"
                elif result == "back":
                    current_state = "menu"
            
            elif current_state == "game":
                # Обработка диалогов
                dialogue_action = game.dialogue_manager.handle_input(event)
                if dialogue_action:
                    if dialogue_action.startswith("set_hack_method"):
                        method = dialogue_action.split("'")[1]
                        game.hack_method = method
                        game.status_message = f"Выбран метод: {method}"
                    elif dialogue_action.startswith("add_item"):
                        item = dialogue_action.split("'")[1]
                        if item not in game.inventory:
                            game.inventory.append(item)
                
                if game.sql_game:
                    result = game.sql_game.handle_input(event)
                    if result == True:
                        game.status_message = "SQL-инъекция успешна! Доступ получен"
                        game.time_left += 20
                        game.sql_game = None
                        game.check_guess()  # Автоматический успех
                    elif result == False:
                        game.status_message = "SQL-инъекция не удалась"
                        game.detection_risk += 15
                        game.sql_game = None
                
                elif game.crypto_game:
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
                    
                    elif event.key == pygame.K_F2:
                        current_state = "shop"
                    
                    elif event.key == pygame.K_RETURN:
                        if game.command_mode:
                            game.process_command(game.guess)
                            game.guess = ""
                            game.command_mode = False
                        else:
                            if game.check_guess():
                                if not game.story_mode:
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
            
            elif current_state == "shop":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = "game"
                    elif pygame.K_1 <= event.key <= pygame.K_5:
                        item_index = event.key - pygame.K_1
                        if item_index < len(game.shop.available_items):
                            item_id = game.shop.available_items[item_index]
                            item = game.shop.items[item_id]
                            if game.money >= item["price"]:
                                game.money -= item["price"]
                                item["effect"](game)
                                game.status_message = f"Куплено: {item['name']}"
                                game.message_time = time.time()
            
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
        
        elif current_state == "settings":
            settings_menu.draw(screen)
        
        elif current_state == "game":
            if not game.chapter_transition:
                game.update_timer()
                if game.is_time_up() or game.health <= 0:
                    current_state = "failed"
                elif game.detection_risk >= 100:
                    current_state = "detected"
            
            game.draw_game_interface(screen)
        
        elif current_state == "shop":
            game.shop.draw(screen, font, game.money)
        
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