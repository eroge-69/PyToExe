import pygame
from pygame import mixer
import random
import time
import os
import json
import math
import textwrap
import threading

# === 0. СИСТЕМА ОЗВУЧКИ (TTS) ===
try:
    import pyttsx3

    engine = pyttsx3.init()
    TTS_AVAILABLE = True
    print("✅ TTS engine loaded successfully.")
except Exception as e:
    TTS_AVAILABLE = False
    engine = None
    print(f"⚠️ Warning: TTS engine failed to load. Voice will be disabled. Error: {e}")


def speak_text(text):
    if TTS_AVAILABLE and game_settings.get('tts_enabled', True) and engine:
        try:
            engine.stop();
            engine.say(text);
            engine.runAndWait()
        except Exception:
            pass


def speak_in_thread(text):
    if TTS_AVAILABLE:
        threading.Thread(target=speak_text, args=(text,), daemon=True).start()


# === 1. ИНИЦИАЛИЗАЦИЯ И КОНСТАНТЫ ===
pygame.init();
mixer.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Проклятие Острова Судьбы")
clock = pygame.time.Clock()


def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("Verdana", size, bold=bold)
    except:
        return pygame.font.SysFont(None, size + 4, bold=bold)


FONT_BIG = get_font(70, True);
FONT_MEDIUM = get_font(36);
FONT_SMALL = get_font(24);
FONT_TINY = get_font(18)
SAVE_FILE, SETTINGS_FILE = "savegame.json", "settings.json"
C_WHITE, C_TEXT, C_BLACK = (255, 255, 255), (220, 220, 220), (0, 0, 0)
C_BLUE_UI, C_GOLD = (30, 30, 60), (255, 215, 0)
C_STORM_BG = (20, 30, 40)
MUSIC_DIR, SOUNDS_DIR = "music", "sounds"

# === 2. АУДИО И НАСТРОЙКИ ===
sound_cache = {}
game_settings = {'music_volume': 0.5, 'sfx_volume': 0.7, 'tts_enabled': True}


def save_settings():
    with open(SETTINGS_FILE, 'w') as f: json.dump(game_settings, f)


def load_settings():
    global game_settings
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            try:
                game_settings.update(json.load(f))
            except json.JSONDecodeError:
                pass
    mixer.music.set_volume(game_settings.get('music_volume', 0.5))


def play_sound(filename):
    if not filename: return
    path = os.path.join(SOUNDS_DIR, filename)
    if path not in sound_cache:
        try:
            sound_cache[path] = mixer.Sound(path)
        except Exception:
            sound_cache[path] = None
    if sound_cache[path]:
        sound_cache[path].set_volume(game_settings.get('sfx_volume', 0.7));
        sound_cache[path].play()


def play_music(filename, loops=-1):
    if not filename: return
    path = os.path.join(MUSIC_DIR, filename)
    try:
        mixer.music.load(path)
        mixer.music.set_volume(game_settings.get('music_volume', 0.5));
        mixer.music.play(loops)
    except Exception:
        pass


load_settings()


# === 3. КЛАССЫ И ДАННЫЕ ===
class Character:
    def __init__(self, name, pos, size, color):
        self.name, self.pos, self.size, self.color = name, list(pos), size, color
        self.base_y = pos[1];
        self.animation_tick = random.randint(0, 100);
        self.speech_bubble = None
        self.rect = pygame.Rect(pos[0] - size // 2, pos[1] - size, size, size)

    def draw(self, surface):
        self.animation_tick += 1
        self.pos[1] = self.base_y + math.sin(self.animation_tick * 0.05) * 3
        head_radius, body_h, body_w = self.size // 4, self.size // 2, self.size // 2
        body_rect = pygame.Rect(self.pos[0] - body_w // 2, self.pos[1] - body_h - head_radius * 1.5, body_w, body_h)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=4)
        pygame.draw.circle(surface, (230, 190, 140), (self.pos[0], self.pos[1] - body_h - head_radius * 2.5),
                           head_radius)
        if self.speech_bubble and self.speech_bubble.is_alive():
            self.speech_bubble.update_pos((self.pos[0], self.pos[1] - self.size - 20));
            self.speech_bubble.draw(surface)

    def set_speech(self, text, duration_frames=180):
        self.speech_bubble = SpeechBubble(text, (self.pos[0], self.pos[1] - self.size - 20), duration_frames)


class SpeechBubble:
    def __init__(self, text, pos, duration):
        self.life, self.font = duration, FONT_TINY;
        self.text_surface = self.font.render(text, True, C_BLACK)
        self.rect = self.text_surface.get_rect(center=pos).inflate(20, 20)

    def update_pos(self, new_pos): self.rect.center = new_pos

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(surface, C_WHITE, self.rect, border_radius=10);
            pygame.draw.rect(surface, C_BLACK, self.rect, 2, border_radius=10)
            tail_points = [self.rect.midbottom, (self.rect.midbottom[0] - 10, self.rect.midbottom[1] + 10),
                           (self.rect.midbottom[0] + 10, self.rect.midbottom[1] + 10)]
            pygame.draw.polygon(surface, C_WHITE, tail_points);
            pygame.draw.line(surface, C_BLACK, tail_points[0], tail_points[1], 2);
            pygame.draw.line(surface, C_BLACK, tail_points[0], tail_points[2], 2)
            surface.blit(self.text_surface, self.text_surface.get_rect(center=self.rect.center));
            self.life -= 1

    def is_alive(self): return self.life > 0


class Inventory:
    def __init__(self):
        self.items, self.is_visible = {}, False

    def add(self, item_id, count=1):
        self.items[item_id] = self.items.get(item_id, 0) + count
        player.set_speech(f"+{count} {ALL_ITEMS[item_id]['name']}", 120);
        play_sound("pickup.mp3")  # 👈 ИСПРАВЛЕНО

    def remove(self, item_id, count=1):
        self.items[item_id] = self.items.get(item_id, 0) - count
        if self.items[item_id] <= 0: del self.items[item_id]

    def count(self, item_id):
        return self.items.get(item_id, 0)

    def draw(self, surface):
        if not self.is_visible: return
        inv_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 250, 400, 500)
        pygame.draw.rect(surface, C_BLUE_UI, inv_rect, border_radius=10);
        pygame.draw.rect(surface, C_GOLD, inv_rect, 2, border_radius=10)
        title = FONT_MEDIUM.render("Инвентарь", True, C_GOLD);
        surface.blit(title, (inv_rect.centerx - title.get_width() // 2, inv_rect.top + 20))
        y_offset = 80
        for item_id, count in self.items.items():
            if count > 0:
                text = FONT_SMALL.render(f"{ALL_ITEMS[item_id]['name']} x{count}", True, C_TEXT)
                surface.blit(text, (inv_rect.left + 30, inv_rect.top + y_offset));
                y_offset += 40


# === 4. 📖 ИГРОВЫЕ ДАННЫЕ И СОСТОЯНИЕ ===
game_state, player, npcs = {}, None, {}
NPC_DATA = {"beach": {"name": "Капитан", "pos": (WIDTH - 250, HEIGHT - 110), "size": 90, "color": (180, 100, 80)},
            "jungle": {"name": "Отшельник", "pos": (WIDTH - 250, HEIGHT - 110), "size": 90, "color": (100, 180, 100)}}
ALL_ITEMS = {"wood": {"name": "Обломки"}, "golem_heart": {"name": "Сердце Голема"}, "relic": {"name": "Реликвия"}}
INTERACTIVE_OBJECTS = {
    "beach": [
        {"id": "wood_1", "pos": (400, HEIGHT - 80), "size": (60, 40), "item_id_to_give": "wood",
         "hint": "Подобрать обломки", "collected": False},
        {"id": "wood_2", "pos": (WIDTH - 450, HEIGHT - 60), "size": (60, 40), "item_id_to_give": "wood",
         "hint": "Подобрать обломки", "collected": False},
        {"id": "wood_3", "pos": (150, HEIGHT - 200), "size": (60, 40), "item_id_to_give": "wood",
         "hint": "Подобрать обломки", "collected": False},
    ]
}
for loc_items in INTERACTIVE_OBJECTS.values():
    for item in loc_items: item["rect"] = pygame.Rect(item["pos"], item["size"])
STORY_DIALOGUES = {"captain_intro": {"speaker": "Капитан",
                                     "text": "Эй, очнулся! Мы разбились. Но если найдем 3 обломка, я смогу залатать шлюпку. Поможешь?",
                                     "choices": [{"text": "Да.", "action": ("start_quest", "q1_wood")},
                                                 {"text": "Осмотрюсь.", "action": ("set_flag", "captain_ignored")}]},
                   "hermit_intro": {"speaker": "Отшельник",
                                    "text": "Этот остров не отпустит тебя. Его сердце — Голем в пещере. Принеси мне его кристалл, и я помогу тебе.",
                                    "choices": [{"text": "Я добуду.", "action": ("start_quest", "q2_golem")},
                                                {"text": "Опасно.", "action": ("set_flag", "hermit_ignored")}]}}


def reset_game_state():
    global game_state, player, npcs
    game_state = {"scene": "menu", "mode": "explore", "player_location": "beach", "active_quests": [],
                  "completed_quests": [], "flags": {},
                  "collected_objects": [], "current_chapter": 0}
    player = Character("Игрок", (200, HEIGHT - 100), 80, (100, 150, 200));
    player.inventory = Inventory()
    npcs = {loc: Character(data['name'], data['pos'], data['size'], data['color']) for loc, data in NPC_DATA.items()}
    for loc_items in INTERACTIVE_OBJECTS.values():
        for item in loc_items: item["collected"] = False


def save_game():
    state_to_save = game_state.copy()
    state_to_save["inventory_items"] = player.inventory.items
    state_to_save["collected_objects"] = [item["id"] for loc_items in INTERACTIVE_OBJECTS.values() for item in loc_items
                                          if item["collected"]]
    with open(SAVE_FILE, "w") as f: json.dump(state_to_save, f, indent=4)
    player.set_speech("Игра сохранена", 120);
    play_sound("save.mp3")  # 👈 ИСПРАВЛЕНО


def load_game():
    if not os.path.exists(SAVE_FILE): return False
    with open(SAVE_FILE, "r") as f:
        loaded_state = json.load(f)
    game_state.update(loaded_state)
    player.inventory.items = loaded_state.get("inventory_items", {})
    collected_ids = game_state.get("collected_objects", [])
    for loc_items in INTERACTIVE_OBJECTS.values():
        for item in loc_items:
            if item["id"] in collected_ids: item["collected"] = True
    return True


# === 5. ОТРИСОВКА ФОНОВ И ЭФФЕКТОВ ===
background_surfaces = {}


def generate_backgrounds():
    print("Generating backgrounds...")
    beach = pygame.Surface((WIDTH, HEIGHT))
    pygame.draw.rect(beach, (20, 30, 40), (0, 0, WIDTH, int(HEIGHT * 0.7)))
    pygame.draw.rect(beach, (194, 178, 128), (0, int(HEIGHT * 0.65), WIDTH, int(HEIGHT * 0.35)))
    for y in range(int(HEIGHT * 0.65), HEIGHT, 2): pygame.draw.line(beach, (204, 188, 138), (0, y), (WIDTH, y))
    for _ in range(30): pygame.draw.circle(beach, (80, 70, 50),
                                           (random.randint(0, WIDTH), random.randint(int(HEIGHT * 0.7), HEIGHT)),
                                           random.randint(1, 4))
    pygame.draw.rect(beach, (60, 80, 110), (0, int(HEIGHT * 0.6), WIDTH, int(HEIGHT * 0.1)))
    for i in range(10): pygame.draw.line(beach, (220, 220, 230), (0, int(HEIGHT * 0.68) - i * 2),
                                         (WIDTH, int(HEIGHT * 0.65) - i * 2), 3)
    background_surfaces["beach"] = beach
    jungle = pygame.Surface((WIDTH, HEIGHT));
    jungle.fill((10, 20, 15))
    for i in range(4):
        color = (20 - i * 4, 40 - i * 8, 30 - i * 6)
        for _ in range(10 + i * 5):
            x, w, h = random.randint(0, WIDTH), random.randint(10 - i * 2, 25 - i * 4), random.randint(100 - i * 15,
                                                                                                       400 - i * 50)
            pygame.draw.rect(jungle, color, (x, HEIGHT - h, w, h))
    pygame.draw.rect(jungle, (15, 10, 5), (0, HEIGHT - 50, WIDTH, 50))
    background_surfaces["jungle"] = jungle
    cave = pygame.Surface((WIDTH, HEIGHT));
    cave.fill((20, 15, 25))
    for x_tile in range(WIDTH // 50 + 1):
        for y_tile in range(HEIGHT // 50 + 1):
            c = random.randint(-5, 5);
            pygame.draw.rect(cave, (20 + c, 15 + c, 25 + c), (x_tile * 50, y_tile * 50, 50, 50))
    for _ in range(15):
        x, w, h = random.randint(0, WIDTH), random.randint(10, 40), random.randint(50, 200)
        points = [(x, 0), (x + w, 0), (x + w / 2, h)] if random.random() > 0.5 else [(x, HEIGHT), (x + w, HEIGHT),
                                                                                     (x + w / 2, HEIGHT - h)]
        pygame.draw.polygon(cave, (30, 25, 35), points)
    for _ in range(20):
        x, y, size = random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(8, 20)
        glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (100, 100, 255, 60), (size, size), size)
        pygame.draw.circle(glow_surf, (150, 150, 255, 80), (size, size), size * 0.7)
        pygame.draw.circle(glow_surf, (200, 200, 255), (size, size), size * 0.4)
        cave.blit(glow_surf, (x - size, y - size), special_flags=pygame.BLEND_RGBA_ADD)
    background_surfaces["cave"] = cave
    print("Backgrounds generated!")


def fade_effect(fade_out=True, duration=1500):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(C_BLACK)
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = int((elapsed / duration) * 255) if fade_out else int(255 - (elapsed / duration) * 255)
        alpha = max(0, min(255, alpha))
        fade_surface.set_alpha(alpha)
        # Нужно перерисовывать сцену под затуханием, чтобы она не "замерзала"
        # Для простоты, мы можем просто закрашивать фон, но в идеале нужно вызывать функцию отрисовки текущей сцены
        draw_animated_menu_bg()
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)


# === 6. ФУНКЦИИ ОТРИСОВКИ ===
def draw_interactive_objects(surface, loc):
    if loc in INTERACTIVE_OBJECTS:
        for item in INTERACTIVE_OBJECTS[loc]:
            if not item["collected"]:
                if item["item_id_to_give"] == "wood":
                    pygame.draw.rect(surface, (139, 69, 19), item["rect"])
                    pygame.draw.rect(surface, (160, 82, 45), item["rect"].inflate(-10, -10))


def draw_hint(surface, entity):
    hint_text, pos = "", (0, 0)
    if isinstance(entity, Character):
        hint_text = f"Поговорить с '{entity.name}'"
        pos = (entity.pos[0], entity.pos[1] - entity.size - 20)
    elif isinstance(entity, dict) and "hint" in entity:
        hint_text = entity["hint"]
        pos = entity["rect"].center
    if hint_text:
        text_surf = FONT_TINY.render(hint_text, True, C_GOLD)
        text_rect = text_surf.get_rect(center=(pos[0], pos[1] - 30))
        pygame.draw.rect(surface, (*C_BLACK, 180), text_rect.inflate(10, 5), border_radius=5)
        surface.blit(text_surf, text_rect)
        rect_to_highlight = entity.rect if hasattr(entity, 'rect') else entity.get("rect")
        if rect_to_highlight:
            pygame.draw.rect(surface, C_GOLD, rect_to_highlight, 2, border_radius=5)


def draw_animated_menu_bg():
    screen.fill(C_STORM_BG)
    for i in range(5):
        points = [(x, HEIGHT - 100 - i * 30 + math.sin(x * 0.005 + pygame.time.get_ticks() * 0.001 + i * 0.7) * 15) for
                  x in range(0, WIDTH + 1, 10)]
        points.append((WIDTH, HEIGHT));
        points.append((0, HEIGHT))
        pygame.draw.polygon(screen, (10 + i * 5, 20 + i * 5, 30 + i * 5, 100 + i * 20), points)


def draw_dialogue_box(speaker, text, choices):
    box_rect = pygame.Rect(100, HEIGHT - 250, WIDTH - 200, 220)
    pygame.draw.rect(screen, C_BLUE_UI, box_rect, border_radius=10);
    pygame.draw.rect(screen, C_GOLD, box_rect, 2, border_radius=10)
    speaker_text = FONT_MEDIUM.render(speaker, True, C_GOLD);
    screen.blit(speaker_text, (box_rect.left + 30, box_rect.top + 20))
    for i, line in enumerate(textwrap.wrap(text, width=60)): screen.blit(FONT_SMALL.render(line, True, C_TEXT),
                                                                         (box_rect.left + 30,
                                                                          box_rect.top + 70 + i * 30))
    for i, choice in enumerate(choices):
        choice["rect"] = pygame.Rect(box_rect.right - 320, box_rect.top + 80 + i * 60, 280, 50)
        hover = choice["rect"].collidepoint(pygame.mouse.get_pos());
        color = C_GOLD if hover else C_TEXT
        pygame.draw.rect(screen, color, choice["rect"], 2, border_radius=5)
        choice_text = FONT_SMALL.render(choice['text'], True, color);
        screen.blit(choice_text, (choice["rect"].centerx - choice_text.get_width() // 2,
                                  choice["rect"].centery - choice_text.get_height() // 2))


def draw_hint_bar():
    bar_surf = pygame.Surface((WIDTH, 30), pygame.SRCALPHA);
    bar_surf.fill((*C_BLACK, 180));
    screen.blit(bar_surf, (0, HEIGHT - 30))
    hint_text = FONT_TINY.render("[M] Карта | [I] Инвентарь | [ESC] Меню | [F5] Сохранить", True, C_TEXT)
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 25))


# === 7. СЦЕНЫ ИГРЫ ===
def main_menu_scene():
    play_music("menu.mp3")
    options = ["Новая игра", "Загрузить", "Настройки", "Выход"]
    # 👈 ИСПРАВЛЕНО: все .wav заменены на .mp3
    option_sounds = ["start_game.mp3", None, "settings.mp3", "exit.mp3"]
    last_selection = -1
    while True:
        mx, my = pygame.mouse.get_pos();
        draw_animated_menu_bg()
        title = FONT_BIG.render("Проклятие Острова Судьбы", True, C_GOLD);
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        current_selection = -1
        for i, opt in enumerate(options):
            rect = pygame.Rect(WIDTH // 2 - 150, 300 + i * 80, 300, 60)
            if rect.collidepoint(mx, my): current_selection = i
            color = C_GOLD if current_selection == i else C_TEXT
            pygame.draw.rect(screen, C_BLUE_UI, rect, border_radius=5);
            pygame.draw.rect(screen, color, rect, 2, border_radius=5)
            text = FONT_MEDIUM.render(opt, True, color);
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        if current_selection != -1 and current_selection != last_selection:
            play_sound("select.mp3")  # 👈 ИСПРАВЛЕНО
        last_selection = current_selection

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_selection != -1:
                play_sound(option_sounds[current_selection])
                if current_selection == 0:  # Новая игра
                    mixer.music.fadeout(1500)
                    fade_effect(fade_out=True, duration=1500)
                    reset_game_state()
                    player.set_speech("Где я?...", 240)
                    play_music("main_theme.mp3")
                    return "game"
                elif current_selection == 1:  # Загрузить
                    if load_game():
                        play_sound("click.mp3")  # 👈 ИСПРАВЛЕНО
                        play_music("main_theme.mp3")
                        return "game"
                elif current_selection == 2:  # Настройки
                    return "settings"
                elif current_selection == 3:  # Выход
                    time.sleep(0.5)  # Даем звуку немного времени проиграться
                    return "quit"
        pygame.display.flip();
        clock.tick(60)


def game_scene():
    current_dialogue = None
    while True:
        mx, my = pygame.mouse.get_pos()
        loc = game_state["player_location"]
        hovered_entity = None

        if game_state.get("mode") == "explore":
            if loc in npcs and npcs[loc].rect.collidepoint(mx, my):
                hovered_entity = npcs[loc]
            elif loc in INTERACTIVE_OBJECTS:
                for item in INTERACTIVE_OBJECTS[loc]:
                    if not item["collected"] and item["rect"].collidepoint(mx, my):
                        hovered_entity = item
                        break

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if game_state.get("mode") == "dialogue":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_dialogue:
                    for choice in current_dialogue.get("choices", []):
                        if choice.get("rect") and choice["rect"].collidepoint(mx, my):
                            play_sound("click.mp3");
                            action_type, action_value = choice["action"]  # 👈 ИСПРАВЛЕНО
                            if action_type == "start_quest":
                                game_state["active_quests"].append(action_value)
                            elif action_type == "set_flag":
                                game_state["flags"][action_value] = True
                            current_dialogue = None;
                            game_state["mode"] = "explore";
                            break
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: play_music("menu.mp3"); return "menu"
                if event.key == pygame.K_i: player.inventory.is_visible = not player.inventory.is_visible; play_sound(
                    "inventory.mp3")  # 👈 ИСПРАВЛЕНО
                if event.key == pygame.K_m: play_sound("map.mp3"); map_scene()  # 👈 ИСПРАВЛЕНО
                if event.key == pygame.K_F5: save_game()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovered_entity:
                play_sound("click.mp3")  # 👈 ИСПРАВЛЕНО
                if isinstance(hovered_entity, Character):
                    npc = hovered_entity
                    if npc.name == "Капитан":
                        if game_state["current_chapter"] == 0 and player.inventory.count("wood") >= 3:
                            game_state["current_chapter"] = 1
                            player.inventory.remove("wood", 3)
                            new_text = "Я починил шлюпку... Но что это?! Шторм! Остров нас не отпускает! Говорят, в лесу живет Отшельник, он знает тайны этого места. Найди его!"
                            npc.set_speech(new_text, 360)
                            speak_in_thread(new_text)
                            player.set_speech("Новая цель: Найти Отшельника в лесу", 300)
                        elif game_state["current_chapter"] >= 1:
                            npc.set_speech("Нужно найти Отшельника в лесу!", 180)
                        elif "q1_wood" in game_state["active_quests"]:
                            npc.set_speech(f"Нужно еще обломков. Есть {player.inventory.count('wood')}/3.", 180)
                        else:
                            current_dialogue = STORY_DIALOGUES["captain_intro"];
                            speak_in_thread(current_dialogue["text"])
                            game_state["mode"] = "dialogue"
                    elif npc.name == "Отшельник":
                        if game_state["current_chapter"] >= 1:
                            current_dialogue = STORY_DIALOGUES["hermit_intro"]
                            speak_in_thread(current_dialogue["text"])
                            game_state["mode"] = "dialogue"
                        else:
                            npc.set_speech("Уходи... ты еще не готов говорить со мной.", 180)
                elif isinstance(hovered_entity, dict):
                    item = hovered_entity
                    player.inventory.add(item["item_id_to_give"])
                    item["collected"] = True
                    hovered_entity = None

                    # --- ОТРИСОВКА ---
        screen.blit(background_surfaces[loc], (0, 0))
        draw_interactive_objects(screen, loc)
        player.draw(screen)
        if loc in npcs: npcs[loc].draw(screen)
        if hovered_entity: draw_hint(screen, hovered_entity)
        if current_dialogue: draw_dialogue_box(**current_dialogue)
        player.inventory.draw(screen);
        draw_hint_bar();
        pygame.display.flip();
        clock.tick(60)


def settings_scene():
    sliders = {
        'music': {'rect': pygame.Rect(WIDTH // 2 - 150, 200, 300, 20), 'label': 'Музыка',
                  'value': game_settings.get('music_volume', 0.5)},
        'sfx': {'rect': pygame.Rect(WIDTH // 2 - 150, 300, 300, 20), 'label': 'Звуки',
                'value': game_settings.get('sfx_volume', 0.7)}
    }
    dragging = None;
    back_button = pygame.Rect(WIDTH // 2 - 100, 500, 200, 60)
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: play_sound(
                "click.mp3"); save_settings(); return "menu"  # 👈 ИСПРАВЛЕНО
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(mx, my): play_sound(
                    "click.mp3"); save_settings(); return "menu"  # 👈 ИСПРАВЛЕНО
                for key, s in sliders.items():
                    if s['rect'].collidepoint(mx, my): dragging = key
            if event.type == pygame.MOUSEBUTTONUP: dragging = None
            if event.type == pygame.MOUSEMOTION and dragging:
                rel = event.pos[0] - sliders[dragging]['rect'].x
                sliders[dragging]['value'] = max(0, min(1, rel / sliders[dragging]['rect'].width))
                if dragging == 'music':
                    game_settings['music_volume'] = sliders[dragging]['value']; mixer.music.set_volume(
                        game_settings['music_volume'])
                else:
                    game_settings['sfx_volume'] = sliders[dragging]['value']
        screen.fill(C_STORM_BG);
        title = FONT_BIG.render("Настройки", True, C_GOLD);
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        for key, s in sliders.items():
            pygame.draw.rect(screen, (50, 50, 50), s['rect']);
            pygame.draw.rect(screen, C_GOLD, (s['rect'].x, s['rect'].y, s['rect'].width * s['value'], s['rect'].height))
            label = FONT_MEDIUM.render(s['label'], True, C_TEXT);
            screen.blit(label, (s['rect'].centerx - label.get_width() // 2, s['rect'].y - 50))
        hover = back_button.collidepoint(mx, my);
        color = C_GOLD if hover else C_TEXT;
        pygame.draw.rect(screen, C_BLUE_UI, back_button, border_radius=5);
        pygame.draw.rect(screen, color, back_button, 2, border_radius=5)
        text = FONT_MEDIUM.render("Назад", True, color);
        screen.blit(text, (back_button.centerx - text.get_width() // 2, back_button.centery - text.get_height() // 2))
        pygame.display.flip();
        clock.tick(60)


def map_scene():
    map_locations = {"beach": (WIDTH * 0.2, HEIGHT * 0.7), "jungle": (WIDTH * 0.5, HEIGHT * 0.5),
                     "cave": (WIDTH * 0.8, HEIGHT * 0.3)}
    LOCATION_NAMES = {"beach": "Штормовой берег", "jungle": "Темный лес", "cave": "Глубокая пещера"}
    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_m or event.key == pygame.K_ESCAPE): return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for loc, pos in map_locations.items():
                    if pygame.Rect(pos[0] - 80, pos[1] - 25, 160, 50).collidepoint(mx, my):
                        game_state["player_location"] = loc;
                        return
        screen.fill(C_STORM_BG);
        title = FONT_BIG.render("Карта Острова", True, C_GOLD);
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        pygame.draw.line(screen, C_TEXT, map_locations["beach"], map_locations["jungle"], 3);
        pygame.draw.line(screen, C_TEXT, map_locations["jungle"], map_locations["cave"], 3)
        for loc, pos in map_locations.items():
            rect = pygame.Rect(pos[0] - 80, pos[1] - 25, 160, 50)
            color = C_GOLD if rect.collidepoint(mx, my) or game_state["player_location"] == loc else C_TEXT
            pygame.draw.rect(screen, C_BLUE_UI, rect, border_radius=5);
            pygame.draw.rect(screen, color, rect, 2, border_radius=5)
            text = FONT_SMALL.render(LOCATION_NAMES[loc], True, color);
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
        pygame.display.flip();
        clock.tick(60)


def ending_scene(music_file, title_text, body_text):
    play_music(music_file)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: return "menu"
        screen.fill(C_BLACK);
        title = FONT_BIG.render(title_text, True, C_GOLD);
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        for i, line in enumerate(textwrap.wrap(body_text, width=50)):
            line_text = FONT_MEDIUM.render(line, True, C_TEXT);
            screen.blit(line_text, (WIDTH // 2 - line_text.get_width() // 2, HEIGHT // 2 + i * 40))
        pygame.display.flip();
        clock.tick(60)


# === 8. ГЛАВНЫЙ ЦИКЛ ===
def main():
    reset_game_state();
    generate_backgrounds()
    scene_functions = {"menu": main_menu_scene, "settings": settings_scene, "game": game_scene}
    current_scene_name = "menu"
    while current_scene_name != "quit":
        if current_scene_name in scene_functions:
            current_scene_name = scene_functions[current_scene_name]()
        elif isinstance(current_scene_name, tuple) and current_scene_name[0] == 'ending':
            _, music, title, body = current_scene_name
            current_scene_name = ending_scene(music, title, body)
        else:
            current_scene_name = "quit"
    pygame.quit()


if __name__ == "__main__":
    main()