import pygame
import sys
import os
import importlib.util
import json
import random
from typing import Dict, List, Any, Optional, Callable, Tuple

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.5
WORLD_WIDTH = 2400  # Для бесконечного режима

# Цвета
BACKGROUND = (30, 30, 40)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 220)
CYAN = (70, 200, 220)
LAVA_COLOR = (255, 100, 0)
ACID_COLOR = (100, 255, 50)
BLOOD_COLOR = (150, 0, 0)
WATER_COLOR = (0, 100, 255, 100)
DARK_RED = (120, 0, 0)
MENU_BG = (40, 40, 50, 200)
BUTTON_COLOR = (70, 70, 90)
BUTTON_HOVER = (90, 90, 110)

class Settings:
    def __init__(self):
        self.default_bindings = {
            "spawn_npc_left": pygame.K_q,
            "spawn_npc_right": pygame.K_e,
            "spawn_circle": pygame.K_1,
            "spawn_rectangle": pygame.K_2,
            "spawn_heavy": pygame.K_3,
            "pause": pygame.K_SPACE,
            "clear": pygame.K_c,
            "delete": pygame.K_d,
            "toggle_map": pygame.K_m,
            "menu": pygame.K_ESCAPE
        }
        self.current_bindings = self.default_bindings.copy()
        self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r') as f:
                    data = json.load(f)
                    for key, value in data.get("bindings", {}).items():
                        if key in self.current_bindings:
                            self.current_bindings[key] = value
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        try:
            with open("settings.json", 'w') as f:
                json.dump({"bindings": self.current_bindings}, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get_key_name(self, key_value):
        return pygame.key.name(key_value)

class BloodParticle:
    def __init__(self, position: 'Vector2', velocity: 'Vector2'):
        self.position = position
        self.velocity = velocity
        self.lifetime = 1.0
        self.max_lifetime = 1.0
        self.size = random.randint(2, 6)
        self.color = BLOOD_COLOR
    
    def update(self):
        self.position += self.velocity
        self.velocity.y += 0.2
        self.velocity.x *= 0.98
        self.lifetime -= 0.02
        self.size = max(1, self.size - 0.1)
    
    def draw(self, screen, camera_offset):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)
        pos = (int(self.position.x - camera_offset.x), int(self.position.y - camera_offset.y))
        pygame.draw.circle(screen, color, pos, int(self.size))

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2(0, 0)

class LiquidZone:
    def __init__(self, rect: pygame.Rect, liquid_type: str, damage: float = 0):
        self.rect = rect
        self.liquid_type = liquid_type  # "water", "lava", "acid"
        self.damage = damage
        self.color = {
            "water": WATER_COLOR,
            "lava": LAVA_COLOR,
            "acid": ACID_COLOR
        }.get(liquid_type, WATER_COLOR)
        
    def draw(self, screen, camera_offset):
        adjusted_rect = pygame.Rect(
            self.rect.x - camera_offset.x,
            self.rect.y - camera_offset.y,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, self.color, adjusted_rect)
        
        # Добавляем эффект волн для воды
        if self.liquid_type == "water":
            for i in range(0, self.rect.width, 20):
                wave_y = adjusted_rect.top + 5 * math.sin(pygame.time.get_ticks() * 0.001 + i * 0.1)
                pygame.draw.line(screen, (100, 150, 255), 
                               (adjusted_rect.left + i, wave_y),
                               (adjusted_rect.left + i + 10, wave_y), 2)

class NPC:
    def __init__(self, position: 'Vector2', facing_right: bool = True):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.obj_type = "npc"
        self.properties = {
            "color": PURPLE,
            "size": 25,
            "mass": 2.0,
            "elasticity": 0.3,
            "friction": 0.2,
            "health": 200,
            "facing_right": facing_right,
            "limb_colors": [(200, 150, 200), (180, 130, 180)]
        }
        self.selected = False
        self.color = self.properties['color']
        self.size = self.properties['size']
        self.mass = self.properties['mass']
        self.elasticity = self.properties['elasticity']
        self.friction = self.properties['friction']
        self.health = self.properties['health']
        self.max_health = self.health
        
        self.walk_speed = 2.0
        self.jump_force = 8.0
        self.is_walking = False
        self.walk_direction = 1 if facing_right else -1
        self.last_damage_time = 0
        
    def update(self, liquid_zones, current_time):
        # NPC автоматически ходит в своем направлении
        if self.is_walking:
            self.velocity.x = self.walk_direction * self.walk_speed
        
        # Применяем гравитацию
        self.velocity.y += GRAVITY
        
        # Обновляем позицию
        self.position += self.velocity
        
        # Ограничиваем скорость
        max_speed = 20
        if self.velocity.magnitude() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
        
        # Проверяем жидкие зоны
        for zone in liquid_zones:
            npc_rect = pygame.Rect(self.position.x - self.size, self.position.y - self.size, 
                                 self.size * 2, self.size * 2)
            if zone.rect.colliderect(npc_rect):
                self.handle_liquid_contact(zone, current_time)
        
        # Проверяем границы мира (для бесконечного режима)
        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x *= -self.elasticity
        elif self.position.x > WORLD_WIDTH:
            self.position.x = WORLD_WIDTH
            self.velocity.x *= -self.elasticity
            
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y *= -self.elasticity
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT
            self.velocity.y *= -self.elasticity
            self.velocity.x *= (1 - self.friction)
    
    def handle_liquid_contact(self, zone, current_time):
        if current_time - self.last_damage_time > 500:  # Урон каждые 500 мс
            if zone.liquid_type == "lava":
                self.take_damage(20)
                self.velocity.y -= 2  # Всплытие в лаве
            elif zone.liquid_type == "acid":
                self.take_damage(15)
            elif zone.liquid_type == "water":
                self.velocity.y *= 0.8  # Сопротивление воды
                self.velocity.x *= 0.9
            self.last_damage_time = current_time
    
    def draw(self, screen, camera_offset):
        adjusted_pos = (int(self.position.x - camera_offset.x), int(self.position.y - camera_offset.y))
        
        # Рисуем тело NPC
        pygame.draw.circle(screen, self.color, adjusted_pos, self.size)
        
        # Рисуем голову
        head_pos = (adjusted_pos[0], adjusted_pos[1] - self.size - 10)
        pygame.draw.circle(screen, (240, 200, 240), head_pos, 12)
        
        # Рисуем конечности
        leg_offset = 8
        arm_offset = 15
        direction = 1 if self.properties.get("facing_right", True) else -1
        
        # Ноги
        pygame.draw.rect(screen, self.properties["limb_colors"][0], 
                        (adjusted_pos[0] - leg_offset, adjusted_pos[1] + self.size - 5, 
                         6, 20))
        pygame.draw.rect(screen, self.properties["limb_colors"][0], 
                        (adjusted_pos[0] + leg_offset - 6, adjusted_pos[1] + self.size - 5, 
                         6, 20))
        
        # Руки
        pygame.draw.rect(screen, self.properties["limb_colors"][1], 
                        (adjusted_pos[0] - arm_offset * direction, adjusted_pos[1] - 5, 
                         6, 15))
        
        # Выделение если выбрано
        if self.selected:
            pygame.draw.circle(screen, YELLOW, adjusted_pos, self.size + 2, 2)
            
        # Здоровье
        if self.health < self.max_health:
            health_width = (self.health / self.max_health) * (self.size * 2)
            health_rect = pygame.Rect(adjusted_pos[0] - self.size, adjusted_pos[1] - self.size - 25, 
                                     int(health_width), 5)
            pygame.draw.rect(screen, GREEN, health_rect)
    
    def apply_force(self, force: 'Vector2'):
        self.velocity += force / self.mass
    
    def is_point_inside(self, point: 'Vector2') -> bool:
        return (point - self.position).magnitude() <= self.size
    
    def take_damage(self, damage: float) -> List['BloodParticle']:
        self.health -= damage
        blood_particles = []
        
        # Создаем частицы крови
        for _ in range(random.randint(5, 15)):
            blood_vel = Vector2(random.uniform(-3, 3), random.uniform(-5, -2))
            blood_particles.append(BloodParticle(self.position + Vector2(random.uniform(-10, 10), 0), blood_vel))
        
        # Меняем цвет при получении урона
        self.color = (min(255, self.color[0] + 20), max(0, self.color[1] - 20), max(0, self.color[2] - 20))
        
        return blood_particles

class GameObject:
    def __init__(self, position: 'Vector2', obj_type: str, properties: Dict[str, Any] = None):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.obj_type = obj_type
        self.properties = properties or {}
        self.selected = False
        self.color = self.properties.get('color', WHITE)
        self.size = self.properties.get('size', 20)
        self.mass = self.properties.get('mass', 1.0)
        self.elasticity = self.properties.get('elasticity', 0.5)
        self.friction = self.properties.get('friction', 0.1)
        self.health = self.properties.get('health', 100)
        self.max_health = self.health
        
    def update(self, liquid_zones, current_time):
        # Применяем гравитацию
        self.velocity.y += GRAVITY
        
        # Обновляем позицию
        self.position += self.velocity
        
        # Ограничиваем скорость
        max_speed = 20
        if self.velocity.magnitude() > max_speed:
            self.velocity = self.velocity.normalize() * max_speed
        
        # Проверяем границы мира
        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x *= -self.elasticity
        elif self.position.x > WORLD_WIDTH:
            self.position.x = WORLD_WIDTH
            self.velocity.x *= -self.elasticity
            
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y *= -self.elasticity
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT
            self.velocity.y *= -self.elasticity
            self.velocity.x *= (1 - self.friction)
    
    def draw(self, screen, camera_offset):
        adjusted_pos = (int(self.position.x - camera_offset.x), int(self.position.y - camera_offset.y))
        
        # Рисуем объект
        if self.obj_type == "circle":
            pygame.draw.circle(screen, self.color, adjusted_pos, self.size)
        elif self.obj_type == "rectangle":
            rect = pygame.Rect(adjusted_pos[0] - self.size, adjusted_pos[1] - self.size/2, 
                              self.size*2, self.size)
            pygame.draw.rect(screen, self.color, rect)
        
        # Если объект выбран, рисуем контур
        if self.selected:
            if self.obj_type == "circle":
                pygame.draw.circle(screen, YELLOW, adjusted_pos, self.size + 2, 2)
            elif self.obj_type == "rectangle":
                rect = pygame.Rect(adjusted_pos[0] - self.size - 2, adjusted_pos[1] - self.size/2 - 2, 
                                  self.size*2 + 4, self.size + 4)
                pygame.draw.rect(screen, YELLOW, rect, 2)
        
        # Рисуем здоровье, если оно меньше максимального
        if self.health < self.max_health:
            health_width = (self.health / self.max_health) * (self.size * 2)
            health_rect = pygame.Rect(adjusted_pos[0] - self.size, adjusted_pos[1] - self.size - 10, 
                                     int(health_width), 5)
            pygame.draw.rect(screen, GREEN, health_rect)
    
    def apply_force(self, force: 'Vector2'):
        self.velocity += force / self.mass
    
    def is_point_inside(self, point: 'Vector2') -> bool:
        if self.obj_type == "circle":
            return (point - self.position).magnitude() <= self.size
        elif self.obj_type == "rectangle":
            return (abs(point.x - self.position.x) <= self.size and 
                    abs(point.y - self.position.y) <= self.size/2)
        return False
    
    def take_damage(self, damage: float) -> List['BloodParticle']:
        self.health -= damage
        blood_particles = []
        
        # Создаем частицы крови только для живых объектов
        if hasattr(self, 'obj_type') and self.obj_type == "npc":
            for _ in range(random.randint(3, 8)):
                blood_vel = Vector2(random.uniform(-2, 2), random.uniform(-3, -1))
                blood_particles.append(BloodParticle(self.position + Vector2(random.uniform(-5, 5), 0), blood_vel))
        
        return blood_particles

class ModManager:
    def __init__(self):
        self.mods = {}
        self.loaded_mods = []
    
    def load_mods(self, mods_directory="mods"):
        if not os.path.exists(mods_directory):
            os.makedirs(mods_directory)
            print("Создана папка mods для загрузки модов")
            return
        
        for mod_name in os.listdir(mods_directory):
            mod_path = os.path.join(mods_directory, mod_name)
            if os.path.isdir(mod_path):
                self.load_mod(mod_path)
    
    def load_mod(self, mod_path):
        try:
            # Загружаем информацию о моде
            info_path = os.path.join(mod_path, "mod.json")
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    mod_info = json.load(f)
                
                mod_name = mod_info.get("name", os.path.basename(mod_path))
                mod_version = mod_info.get("version", "1.0")
                mod_author = mod_info.get("author", "Unknown")
                
                # Загружаем основной скрипт мода
                script_path = os.path.join(mod_path, "mod.py")
                if os.path.exists(script_path):
                    spec = importlib.util.spec_from_file_location(mod_name, script_path)
                    mod_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod_module)
                    
                    self.mods[mod_name] = {
                        "module": mod_module,
                        "info": mod_info,
                        "path": mod_path
                    }
                    self.loaded_mods.append(mod_name)
                    print(f"✅ Мод '{mod_name}' v{mod_version} от {mod_author} успешно загружен")
                else:
                    print(f"⚠️ Мод '{mod_name}' не имеет файла mod.py")
            else:
                print(f"❌ Мод в {mod_path} не имеет файла mod.json")
        except Exception as e:
            print(f"❌ Ошибка загрузки мода из {mod_path}: {e}")
    
    def get_mod_objects(self) -> Dict[str, Dict[str, Any]]:
        objects = {}
        for mod_name, mod_data in self.mods.items():
            if hasattr(mod_data["module"], "get_objects"):
                try:
                    mod_objects = mod_data["module"].get_objects()
                    if isinstance(mod_objects, dict):
                        objects.update(mod_objects)
                        print(f"📦 Мод '{mod_name}' добавил {len(mod_objects)} объектов")
                except Exception as e:
                    print(f"❌ Ошибка получения объектов из мода '{mod_name}': {e}")
        return objects
    
    def call_mod_hooks(self, hook_name: str, *args, **kwargs):
        for mod_name, mod_data in self.mods.items():
            if hasattr(mod_data["module"], hook_name):
                try:
                    getattr(mod_data["module"], hook_name)(*args, **kwargs)
                except Exception as e:
                    print(f"❌ Ошибка в моде '{mod_name}' при вызове хука '{hook_name}': {e}")

class MapManager:
    def __init__(self):
        self.maps = {
            "normal": {
                "name": "Обычная",
                "liquid_zones": [],
                "background": BACKGROUND,
                "description": "Стандартная карта без особенностей"
            },
            "water": {
                "name": "Море",
                "liquid_zones": [
                    LiquidZone(pygame.Rect(0, SCREEN_HEIGHT - 200, WORLD_WIDTH, 200), "water")
                ],
                "background": (20, 40, 80),
                "description": "Глубокое море с сопротивлением воды"
            },
            "lava": {
                "name": "Лава",
                "liquid_zones": [
                    LiquidZone(pygame.Rect(0, SCREEN_HEIGHT - 150, WORLD_WIDTH, 150), "lava", 20)
                ],
                "background": (60, 20, 10),
                "description": "Раскаленная лава наносит урон"
            },
            "acid": {
                "name": "Кислота", 
                "liquid_zones": [
                    LiquidZone(pygame.Rect(0, SCREEN_HEIGHT - 180, WORLD_WIDTH, 180), "acid", 15)
                ],
                "background": (20, 60, 10),
                "description": "Едкая кислота растворяет объекты"
            },
            "infinite": {
                "name": "Бесконечная",
                "liquid_zones": [],
                "background": (40, 30, 50),
                "infinite": True,
                "description": "Бесконечный мир с камерой, следящей за объектами"
            }
        }
        self.current_map = "normal"
    
    def get_current_map(self):
        return self.maps[self.current_map]
    
    def set_map(self, map_name):
        if map_name in self.maps:
            self.current_map = map_name
            return True
        return False
    
    def get_map_list(self):
        return list(self.maps.keys())

class Menu:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.current_tab = "main"  # main, maps, settings, mods
        self.rebinding_key = None
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Полупрозрачный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(MENU_BG)
        screen.blit(overlay, (0, 0))
        
        # Основное окно меню
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, 
                              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        pygame.draw.rect(screen, (50, 50, 60), menu_rect)
        pygame.draw.rect(screen, WHITE, menu_rect, 2)
        
        # Заголовок
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("PeopleSandbox - Меню", True, WHITE)
        screen.blit(title, (menu_rect.centerx - title.get_width() // 2, menu_rect.y + 20))
        
        # Вкладки
        self.draw_tabs(screen, menu_rect)
        
        # Содержимое вкладки
        if self.current_tab == "main":
            self.draw_main_tab(screen, menu_rect)
        elif self.current_tab == "maps":
            self.draw_maps_tab(screen, menu_rect)
        elif self.current_tab == "settings":
            self.draw_settings_tab(screen, menu_rect)
        elif self.current_tab == "mods":
            self.draw_mods_tab(screen, menu_rect)
        
        # Кнопка закрытия
        close_rect = pygame.Rect(menu_rect.centerx - 50, menu_rect.bottom - 50, 100, 40)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = close_rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(screen, BUTTON_HOVER if is_hovered else BUTTON_COLOR, close_rect)
        close_text = self.game.font.render("Продолжить", True, WHITE)
        screen.blit(close_text, (close_rect.centerx - close_text.get_width() // 2, 
                               close_rect.centery - close_text.get_height() // 2))
    
    def draw_tabs(self, screen, menu_rect):
        tabs = ["main", "maps", "settings", "mods"]
        tab_names = {"main": "Главная", "maps": "Карты", "settings": "Настройки", "mods": "Моды"}
        
        tab_width = menu_rect.width // len(tabs)
        for i, tab in enumerate(tabs):
            tab_rect = pygame.Rect(menu_rect.x + i * tab_width, menu_rect.y + 80, tab_width, 40)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = tab_rect.collidepoint(mouse_pos)
            is_active = self.current_tab == tab
            
            color = BUTTON_HOVER if is_hovered or is_active else BUTTON_COLOR
            pygame.draw.rect(screen, color, tab_rect)
            
            tab_text = self.game.font.render(tab_names[tab], True, WHITE)
            screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width() // 2, 
                                 tab_rect.centery - tab_text.get_height() // 2))
    
    def draw_main_tab(self, screen, menu_rect):
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        # Статистика
        stats = [
            f"Объектов на сцене: {len(self.game.objects)}",
            f"Частиц крови: {len(self.game.blood_particles)}",
            f"Текущая карта: {self.game.map_manager.get_current_map()['name']",
            f"Загружено модов: {len(self.game.mod_manager.loaded_mods)}",
            f"Состояние: {'Пауза' if self.game.paused else 'Игра'}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.game.font.render(stat, True, WHITE)
            screen.blit(stat_text, (content_rect.x, content_rect.y + i * 30))
        
        # Быстрые действия
        actions_y = content_rect.y + 200
        actions = [
            ("Очистить сцену", self.game.clear_objects),
            ("Удалить выделенные", self.game.delete_selected_objects),
            ("Пауза/Продолжить", self.toggle_pause)
        ]
        
        for i, (action_name, action_func) in enumerate(actions):
            btn_rect = pygame.Rect(content_rect.x, actions_y + i * 50, 200, 40)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = btn_rect.collidepoint(mouse_pos)
            
            pygame.draw.rect(screen, BUTTON_HOVER if is_hovered else BUTTON_COLOR, btn_rect)
            btn_text = self.game.small_font.render(action_name, True, WHITE)
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, 
                                 btn_rect.centery - btn_text.get_height() // 2))
    
    def draw_maps_tab(self, screen, menu_rect):
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        maps = self.game.map_manager.get_map_list()
        current_map = self.game.map_manager.current_map
        
        for i, map_key in enumerate(maps):
            map_data = self.game.map_manager.maps[map_key]
            btn_rect = pygame.Rect(content_rect.x, content_rect.y + i * 80, content_rect.width, 70)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = btn_rect.collidepoint(mouse_pos)
            is_current = map_key == current_map
            
            # Цвет фона кнопки
            if is_current:
                color = (80, 120, 80)  # Зеленый для текущей карты
            elif is_hovered:
                color = BUTTON_HOVER
            else:
                color = BUTTON_COLOR
                
            pygame.draw.rect(screen, color, btn_rect)
            
            # Название карты
            name_text = self.game.font.render(map_data["name"], True, WHITE)
            screen.blit(name_text, (btn_rect.x + 10, btn_rect.y + 10))
            
            # Описание
            desc_text = self.game.small_font.render(map_data["description"], True, WHITE)
            screen.blit(desc_text, (btn_rect.x + 10, btn_rect.y + 35))
    
    def draw_settings_tab(self, screen, menu_rect):
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        y_offset = content_rect.y
        for action, key in self.game.settings.current_bindings.items():
            action_text = {
                "spawn_npc_left": "Спавн NPC влево",
                "spawn_npc_right": "Спавн NPC вправо", 
                "spawn_circle": "Спавн круга",
                "spawn_rectangle": "Спавн квадрата",
                "spawn_heavy": "Спавн тяжелого шара",
                "pause": "Пауза",
                "clear": "Очистить сцену",
                "delete": "Удалить выделенные",
                "toggle_map": "Сменить карту",
                "menu": "Открыть меню"
            }.get(action, action)
            
            key_name = self.game.settings.get_key_name(key)
            if self.rebinding_key == action:
                key_text = "Нажмите клавишу..."
            else:
                key_text = f"[{key_name}]"
            
            # Текст действия
            text = f"{action_text}: {key_text}"
            text_surface = self.game.small_font.render(text, True, WHITE)
            screen.blit(text_surface, (content_rect.x, y_offset))
            
            # Кнопка для переназначения
            button_rect = pygame.Rect(content_rect.right - 120, y_offset, 100, 25)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            pygame.draw.rect(screen, BUTTON_HOVER if is_hovered else BUTTON_COLOR, button_rect)
            button_text = self.game.small_font.render("Изменить", True, WHITE)
            screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, 
                                    button_rect.centery - button_text.get_height() // 2))
            
            y_offset += 35
    
    def draw_mods_tab(self, screen, menu_rect):
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        if not self.game.mod_manager.loaded_mods:
            no_mods_text = self.game.font.render("Моды не загружены", True, WHITE)
            screen.blit(no_mods_text, (content_rect.centerx - no_mods_text.get_width() // 2, 
                                     content_rect.centery))
        else:
            y_offset = content_rect.y
            for mod_name in self.game.mod_manager.loaded_mods:
                mod_data = self.game.mod_manager.mods[mod_name]
                mod_info = mod_data["info"]
                
                # Фон мода
                mod_rect = pygame.Rect(content_rect.x, y_offset, content_rect.width, 60)
                pygame.draw.rect(screen, BUTTON_COLOR, mod_rect)
                
                # Информация о моде
                name_text = self.game.font.render(f"{mod_info.get('name', mod_name)} v{mod_info.get('version', '1.0')}", True, WHITE)
                screen.blit(name_text, (mod_rect.x + 10, mod_rect.y + 5))
                
                author_text = self.game.small_font.render(f"Автор: {mod_info.get('author', 'Unknown')}", True, WHITE)
                screen.blit(author_text, (mod_rect.x + 10, mod_rect.y + 30))
                
                desc_text = self.game.small_font.render(mod_info.get('description', 'Без описания'), True, WHITE)
                screen.blit(desc_text, (mod_rect.x + 200, mod_rect.y + 30))
                
                y_offset += 70
    
    def handle_click(self, pos):
        if not self.active:
            return
            
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, 
                              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        
        # Проверка вкладок
        tabs = ["main", "maps", "settings", "mods"]
        tab_width = menu_rect.width // len(tabs)
        for i, tab in enumerate(tabs):
            tab_rect = pygame.Rect(menu_rect.x + i * tab_width, menu_rect.y + 80, tab_width, 40)
            if tab_rect.collidepoint(pos):
                self.current_tab = tab
                return
        
        # Обработка содержимого вкладок
        if self.current_tab == "main":
            self.handle_main_tab_click(pos)
        elif self.current_tab == "maps":
            self.handle_maps_tab_click(pos)
        elif self.current_tab == "settings":
            self.handle_settings_tab_click(pos)
        
        # Кнопка закрытия
        close_rect = pygame.Rect(menu_rect.centerx - 50, menu_rect.bottom - 50, 100, 40)
        if close_rect.collidepoint(pos):
            self.active = False
    
    def handle_main_tab_click(self, pos):
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, 
                              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        actions_y = content_rect.y + 200
        actions = [
            ("Очистить сцену", self.game.clear_objects),
            ("Удалить выделенные", self.game.delete_selected_objects),
            ("Пауза/Продолжить", self.toggle_pause)
        ]
        
        for i, (action_name, action_func) in enumerate(actions):
            btn_rect = pygame.Rect(content_rect.x, actions_y + i * 50, 200, 40)
            if btn_rect.collidepoint(pos):
                action_func()
                return
    
    def handle_maps_tab_click(self, pos):
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, 
                              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        maps = self.game.map_manager.get_map_list()
        
        for i, map_key in enumerate(maps):
            btn_rect = pygame.Rect(content_rect.x, content_rect.y + i * 80, content_rect.width, 70)
            if btn_rect.collidepoint(pos):
                self.game.map_manager.set_map(map_key)
                return
    
    def handle_settings_tab_click(self, pos):
        menu_rect = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6, 
                              SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)
        content_rect = pygame.Rect(menu_rect.x + 20, menu_rect.y + 140, 
                                 menu_rect.width - 40, menu_rect.height - 200)
        
        y_offset = content_rect.y
        for action in self.game.settings.current_bindings.keys():
            button_rect = pygame.Rect(content_rect.right - 120, y_offset, 100, 25)
            if button_rect.collidepoint(pos):
                self.rebinding_key = action
                return
            y_offset += 35
    
    def handle_keydown(self, event):
        if self.rebinding_key:
            self.game.settings.current_bindings[self.rebinding_key] = event.key
            self.game.settings.save_settings()
            self.rebinding_key = None
            return True
        return False
    
    def toggle_pause(self):
        self.game.paused = not self.game.paused

class PeopleSandbox:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PeopleSandbox")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Системы
        self.settings = Settings()
        self.mod_manager = ModManager()
        self.map_manager = MapManager()
        self.menu = Menu(self)
        
        # Игровые объекты
        self.objects = []
        self.selected_objects = []
        self.blood_particles = []
        
        # Состояние игры
        self.dragging = False
        self.drag_start = Vector2(0, 0)
        self.drag_end = Vector2(0, 0)
        self.paused = False
        self.camera_offset = Vector2(0, 0)
        
        # Загрузка модов
        self.mod_manager.load_mods()
        
        # Доступные объекты
        self.available_objects = {
            "circle": {"type": "circle", "properties": {"color": RED, "size": 20, "mass": 1.0}},
            "rectangle": {"type": "rectangle", "properties": {"color": BLUE, "size": 25, "mass": 2.0}},
            "heavy_circle": {"type": "circle", "properties": {"color": GREEN, "size": 30, "mass": 5.0}},
            "npc_left": {"type": "npc", "properties": {"facing_right": False}},
            "npc_right": {"type": "npc", "properties": {"facing_right": True}}
        }
        
        # Добавляем объекты из модов
        mod_objects = self.mod_manager.get_mod_objects()
        self.available_objects.update(mod_objects)
        
        self.current_object_type = "circle"
        
        # Создаем несколько начальных объектов
        for i in range(3):
            obj = GameObject(
                Vector2(200 + i * 100, 100),
                "circle",
                {"color": RED, "size": 15 + i * 5, "mass": 1.0 + i * 0.5}
            )
            self.objects.append(obj)
    
    def spawn_npc(self, facing_right=True):
        mouse_pos = Vector2(*pygame.mouse.get_pos()) + self.camera_offset
        npc = NPC(mouse_pos, facing_right)
        npc.is_walking = True
        self.objects.append(npc)
        self.mod_manager.call_mod_hooks("on_object_created", npc)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.menu.active:
                    if self.menu.handle_keydown(event):
                        continue
                
                if event.key == self.settings.current_bindings["menu"]:
                    self.menu.active = not self.menu.active
                elif not self.menu.active:
                    if event.key == self.settings.current_bindings["pause"]:
                        self.paused = not self.paused
                    elif event.key == self.settings.current_bindings["clear"]:
                        self.clear_objects()
                    elif event.key == self.settings.current_bindings["delete"]:
                        self.delete_selected_objects()
                    elif event.key == self.settings.current_bindings["spawn_npc_left"]:
                        self.spawn_npc(False)
                    elif event.key == self.settings.current_bindings["spawn_npc_right"]:
                        self.spawn_npc(True)
                    elif event.key == self.settings.current_bindings["toggle_map"]:
                        self.map_manager.next_map()
                    elif event.key == pygame.K_1:
                        self.current_object_type = "circle"
                    elif event.key == pygame.K_2:
                        self.current_object_type = "rectangle"
                    elif event.key == pygame.K_3:
                        self.current_object_type = "heavy_circle"
                    elif event.key == pygame.K_4:
                        self.current_object_type = "npc_left"
                    elif event.key == pygame.K_5:
                        self.current_object_type = "npc_right"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu.active:
                    self.menu.handle_click(pygame.mouse.get_pos())
                    continue
                    
                mouse_pos = Vector2(*pygame.mouse.get_pos()) + self.camera_offset
                
                if event.button == 1:  # Левая кнопка мыши
                    clicked_object = None
                    for obj in reversed(self.objects):
                        if obj.is_point_inside(mouse_pos):
                            clicked_object = obj
                            break
                    
                    if clicked_object:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            clicked_object.selected = not clicked_object.selected
                            if clicked_object.selected and clicked_object not in self.selected_objects:
                                self.selected_objects.append(clicked_object)
                            elif not clicked_object.selected and clicked_object in self.selected_objects:
                                self.selected_objects.remove(clicked_object)
                        else:
                            for obj in self.selected_objects:
                                obj.selected = False
                            self.selected_objects = [clicked_object]
                            clicked_object.selected = True
                        
                        self.dragging = True
                        self.drag_start = mouse_pos
                    else:
                        if self.current_object_type in ["npc_left", "npc_right"]:
                            facing_right = self.current_object_type == "npc_right"
                            self.spawn_npc(facing_right)
                        else:
                            new_obj = GameObject(
                                mouse_pos,
                                self.available_objects[self.current_object_type]["type"],
                                self.available_objects[self.current_object_type]["properties"].copy()
                            )
                            self.objects.append(new_obj)
                            self.mod_manager.call_mod_hooks("on_object_created", new_obj)
                
                elif event.button == 3:  # Правая кнопка мыши
                    for obj in self.objects:
                        if obj.is_point_inside(mouse_pos):
                            direction = (obj.position - mouse_pos).normalize()
                            obj.apply_force(direction * 50)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self.dragging = False
                    mouse_pos = Vector2(*pygame.mouse.get_pos()) + self.camera_offset
                    drag_vector = mouse_pos - self.drag_start
                    for obj in self.selected_objects:
                        obj.apply_force(drag_vector * 0.1)
        
        return True
    
    def update(self):
        if self.paused or self.menu.active:
            return
        
        current_time = pygame.time.get_ticks()
        current_map = self.map_manager.get_current_map()
        
        # Обновляем объекты
        for obj in self.objects:
            if isinstance(obj, NPC):
                obj.update(current_map["liquid_zones"], current_time)
            else:
                obj.update(current_map["liquid_zones"], current_time)
        
        # Обновляем частицы крови
        for particle in self.blood_particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.blood_particles.remove(particle)
        
        # Проверяем столкновения
        for i, obj1 in enumerate(self.objects):
            for obj2 in self.objects[i+1:]:
                blood_particles = self.check_collision(obj1, obj2)
                self.blood_particles.extend(blood_particles)
        
        # Удаляем уничтоженные объекты
        destroyed_objects = [obj for obj in self.objects if obj.health <= 0]
        for obj in destroyed_objects:
            if obj in self.selected_objects:
                self.selected_objects.remove(obj)
            # Создаем много крови при смерти
            for _ in range(20):
                blood_vel = Vector2(random.uniform(-5, 5), random.uniform(-8, -3))
                self.blood_particles.append(BloodParticle(obj.position, blood_vel))
        
        self.objects = [obj for obj in self.objects if obj.health > 0]
        
        # Обновляем камеру (следим за выделенными объектами)
        if self.selected_objects and current_map.get("infinite", False):
            avg_pos = Vector2(0, 0)
            for obj in self.selected_objects:
                avg_pos += obj.position
            avg_pos = avg_pos / len(self.selected_objects)
            self.camera_offset.x = avg_pos.x - SCREEN_WIDTH / 2
            self.camera_offset.x = max(0, min(self.camera_offset.x, WORLD_WIDTH - SCREEN_WIDTH))
        
        self.mod_manager.call_mod_hooks("on_update", self.objects)
    
    def check_collision(self, obj1, obj2) -> List[BloodParticle]:
        blood_particles = []
        
        if obj1.obj_type == "circle" and obj2.obj_type == "circle":
            distance = (obj1.position - obj2.position).magnitude()
            min_distance = obj1.size + obj2.size
            
            if distance < min_distance:
                normal = (obj2.position - obj1.position).normalize()
                overlap = min_distance - distance
                obj1.position -= normal * (overlap / 2)
                obj2.position += normal * (overlap / 2)
                
                relative_velocity = obj2.velocity - obj1.velocity
                velocity_along_normal = relative_velocity.x * normal.x + relative_velocity.y * normal.y
                
                if velocity_along_normal > 0:
                    return blood_particles
                
                e = min(obj1.elasticity, obj2.elasticity)
                j = -(1 + e) * velocity_along_normal
                j /= (1 / obj1.mass + 1 / obj2.mass)
                
                impulse = normal * j
                obj1.velocity -= impulse / obj1.mass
                obj2.velocity += impulse / obj2.mass
                
                damage = abs(velocity_along_normal) * 0.5
                blood_particles.extend(obj1.take_damage(damage))
                blood_particles.extend(obj2.take_damage(damage))
                
                self.mod_manager.call_mod_hooks("on_collision", obj1, obj2, damage)
        
        return blood_particles
    
    def draw(self):
        current_map = self.map_manager.get_current_map()
        self.screen.fill(current_map["background"])
        
        # Рисуем жидкие зоны
        for zone in current_map["liquid_zones"]:
            zone.draw(self.screen, self.camera_offset)
        
        # Рисуем объекты
        for obj in self.objects:
            obj.draw(self.screen, self.camera_offset)
        
        # Рисуем частицы крови
        for particle in self.blood_particles:
            particle.draw(self.screen, self.camera_offset)
        
        # Рисуем линию перетаскивания
        if self.dragging and not self.menu.active:
            mouse_pos = pygame.mouse.get_pos()
            drag_start_screen = (int(self.drag_start.x - self.camera_offset.x), 
                               int(self.drag_start.y - self.camera_offset.y))
            pygame.draw.line(self.screen, YELLOW, drag_start_screen, mouse_pos, 2)
        
        # Рисуем UI
        if not self.menu.active:
            self.draw_ui()
        
        # Рисуем меню
        self.menu.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Информация о текущем объекте
        obj_info = self.available_objects[self.current_object_type]
        obj_text = f"Текущий объект: {self.current_object_type}"
        text_surface = self.font.render(obj_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Количество объектов
        count_text = f"Объектов: {len(self.objects)} | Крови: {len(self.blood_particles)}"
        count_surface = self.font.render(count_text, True, WHITE)
        self.screen.blit(count_surface, (10, 40))
        
        # Текущая карта
        current_map = self.map_manager.get_current_map()
        map_text = f"Карта: {current_map['name']}"
        map_surface = self.font.render(map_text, True, WHITE)
        self.screen.blit(map_surface, (10, 70))
        
        # Состояние паузы
        if self.paused:
            pause_text = "ПАУЗА"
            pause_surface = self.font.render(pause_text, True, RED)
            self.screen.blit(pause_surface, (SCREEN_WIDTH - 100, 10))
        
        # Список загруженных модов
        if self.mod_manager.loaded_mods:
            mods_text = f"Моды: {len(self.mod_manager.loaded_mods)} загружено"
            mods_surface = self.small_font.render(mods_text, True, WHITE)
            self.screen.blit(mods_surface, (10, SCREEN_HEIGHT - 30))
        
        # Подсказки управления
        controls = [
            "ЛКМ: Создать/Выделить объект",
            "ПКМ: Применить силу", 
            "Shift+ЛКМ: Множественное выделение",
            f"{self.settings.get_key_name(self.settings.current_bindings['pause'])}: Пауза",
            f"{self.settings.get_key_name(self.settings.current_bindings['clear'])}: Очистить сцену",
            f"{self.settings.get_key_name(self.settings.current_bindings['delete'])}: Удалить выделенные",
            f"{self.settings.get_key_name(self.settings.current_bindings['spawn_npc_left'])}: NPC влево",
            f"{self.settings.get_key_name(self.settings.current_bindings['spawn_npc_right'])}: NPC вправо",
            f"{self.settings.get_key_name(self.settings.current_bindings['toggle_map'])}: Сменить карту",
            f"{self.settings.get_key_name(self.settings.current_bindings['menu'])}: Меню",
            "1-5: Выбор типа объекта"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_surface, (SCREEN_WIDTH - 350, 40 + i * 22))
    
    def clear_objects(self):
        self.objects.clear()
        self.selected_objects.clear()
        self.blood_particles.clear()
    
    def delete_selected_objects(self):
        for obj in self.selected_objects:
            if obj in self.objects:
                self.objects.remove(obj)
        self.selected_objects.clear()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    import math  # Добавляем для волн на воде
    game = PeopleSandbox()
    game.run()
    root.mainloop()
