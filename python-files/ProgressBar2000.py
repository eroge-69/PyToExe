# progressbar_rus_with_sounds.py
# Progressbar-like прототип с русским интерфейсом, звуками, улучшенным UI и балансом
# Требуется: pygame (numpy опционально для звуков)
# Запуск: python progressbar_rus_with_sounds.py

import pygame, sys, os, json, random, time, math
from datetime import datetime

# Попытка подключить numpy для генерации звуков
try:
    import numpy as np
    NUMPY = True
except Exception:
    NUMPY = False

# -------------------- Конфигурация / Сохранение --------------------
APP_NAME = "ProgressBar2000"
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", APP_NAME)
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")
ACHIV_FILE = os.path.join(SAVE_DIR, "achievements.txt")

WIDTH, HEIGHT = 1100, 700
FPS = 60
MAX_SEGMENTS = 17

DEFAULT_STATE = {
    "score": 0,
    "os": "Win95",
    "lives": 3,
    "last_life_time": time.time(),
    "upgrades": {"cpu": "486DX2", "ram_mb": 16, "hdd_gb": 1},
    "achievements": [],
    "level": 1,
    "firewall": 0,
    "pink_counter": 0,
    "recycle_praised": False,
    "components": {
        "cpu": 1,
        "ram": 1,
        "hdd": 1,
        "gpu": 1
    },
    "exp": 0,
    "minigames_unlocked": False,
    "console_unlocked": False
}

def ensure_save_dir():
    if not os.path.isdir(SAVE_DIR):
        os.makedirs(SAVE_DIR, exist_ok=True)

def load_state():
    ensure_save_dir()
    if not os.path.exists(SAVE_FILE):
        save_game(DEFAULT_STATE.copy())
        return DEFAULT_STATE.copy()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STATE.copy()

def save_game(state):
    ensure_save_dir()
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Ошибка сохранения:", e)

def export_achievements(state):
    ensure_save_dir()
    try:
        with open(ACHIV_FILE, "w", encoding="utf-8") as f:
            f.write("Экспорт достижений — " + datetime.now().isoformat() + "\n\n")
            for a in state.get("achievements", []):
                f.write("- " + a + "\n")
        return True
    except Exception:
        return False

# -------------------- Pygame init & fonts --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ProgressBar — Russian edition ( ALPHA 1.2.0 )")
clock = pygame.time.Clock()

# Шрифты (в разных размерах)
FONT = pygame.font.SysFont("MS Sans Serif", 16)
FONT_SMALL = pygame.font.SysFont("MS Sans Serif", 13)
FONT_TINY = pygame.font.SysFont("MS Sans Serif", 11)
FONT_BIG = pygame.font.SysFont("MS Sans Serif", 26, bold=True)
FONT_CONSOLE = pygame.font.SysFont("Courier New", 16)

# -------------------- Скины ОС --------------------
SKINS = [
    {"name":"Win95","bg":(192,192,192),"title":(0,0,128),"panel":(223,223,223),"accent":(0,120,215),"text":(0,0,0),"white":(255,255,255),"bsod":(35,83,160)},
    {"name":"Win98","bg":(200,200,210),"title":(0,16,128),"panel":(236,236,236),"accent":(0,102,204),"text":(0,0,0),"white":(255,255,255),"bsod":(18,56,126)},
    {"name":"WinXP","bg":(170,200,255),"title":(0,84,255),"panel":(245,245,255),"accent":(0,120,215),"text":(0,0,0),"white":(255,255,255),"bsod":(0,0,128)},
    {"name":"Vista","bg":(40,50,80),"title":(0,120,180),"panel":(220,230,240),"accent":(0,150,220),"text":(255,255,255),"white":(255,255,255),"bsod":(0,0,80)}
]

def current_skin(state):
    name = state.get("os","Win95")
    for s in SKINS:
        if s["name"] == name: return s
    return SKINS[0]

# -------------------- Звуки (генерация) --------------------
SOUNDS = {}
def gen_tone(freq, dur=0.12, vol=0.2, sr=22050):
    if not NUMPY: return None
    t = np.linspace(0, dur, int(sr*dur), False)
    wave = 0.5 * np.sin(2*np.pi*freq*t)
    # simple envelope
    env = np.linspace(1,0.2,wave.shape[0])
    wave = (wave * env * vol).astype(np.float32)
    arr = np.tile(wave.reshape(-1,1), (1,2))
    snd = np.int16(arr * 32767)
    try:
        return pygame.sndarray.make_sound(snd)
    except Exception:
        return None

if NUMPY:
    SOUNDS['pickup'] = gen_tone(900,0.07,0.15)
    SOUNDS['click'] = gen_tone(1200,0.05,0.12)
    SOUNDS['bsod'] = gen_tone(160,0.35,0.35)
    SOUNDS['levelup'] = gen_tone(600,0.12,0.16)
    SOUNDS['error'] = gen_tone(300,0.15,0.15)
    SOUNDS['success'] = gen_tone(800,0.2,0.2)
else:
    SOUNDS['pickup'] = None; SOUNDS['click'] = None; SOUNDS['bsod'] = None; SOUNDS['levelup'] = None
    SOUNDS['error'] = None; SOUNDS['success'] = None

def play_sound(name):
    s = SOUNDS.get(name)
    if s:
        try:
            s.play()
        except:
            pass

# -------------------- Глобальное состояние --------------------
state = load_state()
for k,v in DEFAULT_STATE.items():
    if k not in state:
        state[k]=v

# -------------------- Утилиты --------------------
def draw_text(surf, text, pos, color, font=FONT):
    surf.blit(font.render(str(text), True, color), pos)

def clamp(v,a,b): return max(a,min(b,v))

def retro_boot_effect(duration=1.2, text=None):
    start=time.time()
    while time.time()-start < duration:
        t = (time.time()-start)/duration
        screen.fill((0,0,0))
        flick = 20 + int(220*(1-t))
        for y in range(0, HEIGHT, 6):
            pygame.draw.line(screen, (flick,flick,flick), (0,y), (WIDTH,y))
        if text:
            draw_text(screen, text, (WIDTH//2-120, HEIGHT//2-10), (180,220,180), FONT_BIG)
        else:
            draw_text(screen, "Загрузка " + state.get("os","Win95") + "...", (WIDTH//2-120, HEIGHT//2-10), (180,220,180), FONT_BIG)
        pygame.display.flip()
        clock.tick(60)

# -------------------- UI: маленькие пиксельные иконки --------------------
def draw_icon_progress(surf, x,y):
    pygame.draw.rect(surf, (80,130,230), (x,y+6,36,10)); pygame.draw.rect(surf,(0,0,0),(x,y+6,36,10),1)
def draw_icon_recycle(surf,x,y):
    pygame.draw.polygon(surf,(200,200,200),[(x+6,y+2),(x+30,y+2),(x+36,y+22),(x+2,y+22)]); pygame.draw.rect(surf,(0,0,0),(x+2,y+2,34,22),1)
def draw_icon_ach(surf,x,y):
    pygame.draw.rect(surf,(240,230,160),(x+4,y+4,28,14)); pygame.draw.circle(surf,(255,200,0),(x+8,y+11),4)
def draw_icon_menu(surf,x,y):
    pygame.draw.rect(surf,(230,230,230),(x+6,y+6,28,20)); pygame.draw.rect(surf,(0,0,0),(x+6,y+6,28,20),1)
def draw_icon_console(surf,x,y):
    pygame.draw.rect(surf,(0,0,0),(x+6,y+6,28,20)); pygame.draw.rect(surf,(0,200,0),(x+10,y+10,20,12),1)
def draw_icon_minigames(surf,x,y):
    pygame.draw.rect(surf,(200,100,100),(x+6,y+6,28,20)); pygame.draw.rect(surf,(0,0,0),(x+6,y+6,28,20),1)
    pygame.draw.rect(surf,(255,150,150),(x+12,y+12,8,8))

# -------------------- Классы: Desktop --------------------
class Desktop:
    def __init__(self, app):
        self.app = app
        self.rect_progress = pygame.Rect(40, 80, 72, 72)
        self.rect_recycle = pygame.Rect(WIDTH-96, HEIGHT-140, 72, 72)  # корзина внизу справа
        self.rect_ach = pygame.Rect(40, 180, 72, 72)
        self.rect_menu = pygame.Rect(40, 280, 72, 72)
        self.rect_console = pygame.Rect(40, 380, 72, 72)
        self.rect_minigames = pygame.Rect(40, 480, 72, 72)
        self.show_ach = False
        self.show_components = False
        self.recent_interaction = None
    def draw(self):
        skin = current_skin(state)
        screen.fill(skin["bg"])
        pygame.draw.rect(screen, skin["title"], (0,0,WIDTH,28))
        draw_text(screen, f"Рабочий стол — {state.get('os')} (уровень {state.get('level',1)})", (8,2), skin["white"], FONT_BIG)
        # icons
        pygame.draw.rect(screen, skin["panel"], self.rect_progress); pygame.draw.rect(screen, (0,0,0), self.rect_progress,1)
        draw_icon_progress(screen, self.rect_progress.x+8, self.rect_progress.y+20)
        draw_text(screen, "Progress.exe", (self.rect_progress.x-6, self.rect_progress.y + self.rect_progress.h + 6), skin["text"], FONT_SMALL)
        
        pygame.draw.rect(screen, skin["panel"], self.rect_ach); pygame.draw.rect(screen, (0,0,0), self.rect_ach,1)
        draw_icon_ach(screen, self.rect_ach.x+6, self.rect_ach.y+10)
        draw_text(screen, "Достижения", (self.rect_ach.x-6, self.rect_ach.y + self.rect_ach.h + 6), skin["text"], FONT_SMALL)
        
        pygame.draw.rect(screen, skin["panel"], self.rect_menu); pygame.draw.rect(screen, (0,0,0), self.rect_menu,1)
        draw_icon_menu(screen, self.rect_menu.x+6, self.rect_menu.y+8)
        draw_text(screen, "Меню", (self.rect_menu.x-6, self.rect_menu.y + self.rect_menu.h + 6), skin["text"], FONT_SMALL)
        
        pygame.draw.rect(screen, skin["panel"], self.rect_recycle); pygame.draw.rect(screen, (0,0,0), self.rect_recycle,1)
        draw_icon_recycle(screen, self.rect_recycle.x+6, self.rect_recycle.y+8)
        draw_text(screen, "Корзина", (self.rect_recycle.x-6, self.rect_recycle.y + self.rect_recycle.h + 6), skin["text"], FONT_SMALL)
        
        if state.get("console_unlocked", False):
            pygame.draw.rect(screen, skin["panel"], self.rect_console); pygame.draw.rect(screen, (0,0,0), self.rect_console,1)
            draw_icon_console(screen, self.rect_console.x+6, self.rect_console.y+8)
            draw_text(screen, "Консоль", (self.rect_console.x-6, self.rect_console.y + self.rect_console.h + 6), skin["text"], FONT_SMALL)
        
        if state.get("minigames_unlocked", False):
            pygame.draw.rect(screen, skin["panel"], self.rect_minigames); pygame.draw.rect(screen, (0,0,0), self.rect_minigames,1)
            draw_icon_minigames(screen, self.rect_minigames.x+6, self.rect_minigames.y+8)
            draw_text(screen, "Мини-игры", (self.rect_minigames.x-6, self.rect_minigames.y + self.rect_minigames.h + 6), skin["text"], FONT_SMALL)
        
        # info panel
        info = pygame.Rect(WIDTH-320, 40, 300, 200)
        pygame.draw.rect(screen, skin["panel"], info); pygame.draw.rect(screen, (0,0,0), info,1)
        draw_text(screen, f"Очки: {state.get('score',0)}", (info.x+8, info.y+8), skin["text"])
        draw_text(screen, f"Опыт: {state.get('exp',0)}", (info.x+8, info.y+36), skin["text"])
        draw_text(screen, f"Жизней: {state.get('lives',0)}", (info.x+8, info.y+64), skin["text"])
        draw_text(screen, f"Розовые: {state.get('pink_counter',0)}", (info.x+8, info.y+92), skin["text"])
        draw_text(screen, f"Компоненты: CPU:{state['components']['cpu']} RAM:{state['components']['ram']}", (info.x+8, info.y+120), skin["text"])
        draw_text(screen, f"HDD:{state['components']['hdd']} GPU:{state['components']['gpu']}", (info.x+8, info.y+144), skin["text"])
        draw_text(screen, f"Готово к обновлению: {'Да' if state.get('exp',0) >= 1000 else 'Нет'}", (info.x+8, info.y+172), skin["text"])
        
        if self.recent_interaction:
            draw_text(screen, self.recent_interaction, (info.x+8, info.y+200), (120,0,120))
        
        # achievements window if toggled
        if self.show_ach:
            self.draw_achievements()
        
        # components window if toggled
        if self.show_components:
            self.draw_components()
    def draw_achievements(self):
        skin = current_skin(state)
        r = pygame.Rect(200, 80, 480, 420)
        pygame.draw.rect(screen, skin["panel"], r); pygame.draw.rect(screen, (0,0,0), r,1)
        draw_text(screen, "Достижения", (r.x+8, r.y+8), skin["text"], FONT_BIG)
        y = r.y + 48
        ach = state.get("achievements", [])
        if not ach:
            draw_text(screen, "Ачивок пока нет", (r.x+12, y), skin["text"])
        else:
            for a in ach:
                draw_text(screen, "- " + a, (r.x+12, y), skin["text"]); y += 22
        # export button
        btn = pygame.Rect(r.x+300, r.y+20, 150, 28)
        pygame.draw.rect(screen, skin["panel"], btn); pygame.draw.rect(screen, (0,0,0), btn,1)
        draw_text(screen, "Экспорт", (btn.x+24, btn.y+6), skin["text"], FONT_SMALL)
    def draw_components(self):
        skin = current_skin(state)
        r = pygame.Rect(200, 80, 480, 420)
        pygame.draw.rect(screen, skin["panel"], r); pygame.draw.rect(screen, (0,0,0), r,1)
        draw_text(screen, "Компоненты системы", (r.x+8, r.y+8), skin["text"], FONT_BIG)
        
        y = r.y + 48
        comp = state.get("components", {})
        draw_text(screen, f"Процессор (CPU): Уровень {comp.get('cpu',1)}", (r.x+12, y), skin["text"]); y += 30
        draw_text(screen, f"Оперативная память (RAM): Уровень {comp.get('ram',1)}", (r.x+12, y), skin["text"]); y += 30
        draw_text(screen, f"Жесткий диск (HDD): Уровень {comp.get('hdd',1)}", (r.x+12, y), skin["text"]); y += 30
        draw_text(screen, f"Видеокарта (GPU): Уровень {comp.get('gpu',1)}", (r.x+12, y), skin["text"]); y += 30
        
        draw_text(screen, "Эффекты:", (r.x+12, y), skin["text"]); y += 25
        draw_text(screen, "- CPU: увеличивает скорость курсора", (r.x+20, y), skin["text"]); y += 22
        draw_text(screen, "- RAM: уменьшает интервал спавна сегментов", (r.x+20, y), skin["text"]); y += 22
        draw_text(screen, "- HDD: увеличивает награды за сегменты", (r.x+20, y), skin["text"]); y += 22
        draw_text(screen, "- GPU: уменьшает штрафы за розовые сегменты", (r.x+20, y), skin["text"]); y += 22
        
        # upgrade button if enough exp
        if state.get("exp", 0) >= 1000:
            btn = pygame.Rect(r.x+300, r.y+380, 150, 28)
            pygame.draw.rect(screen, skin["panel"], btn); pygame.draw.rect(screen, (0,0,0), btn,1)
            draw_text(screen, "Улучшить (1000 опыта)", (btn.x+12, btn.y+6), skin["text"], FONT_SMALL)
    def handle_event(self, ev, app):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx,my = ev.pos
            if self.rect_progress.collidepoint((mx,my)):
                play_sound('click'); app.start_progress()
            elif self.rect_recycle.collidepoint((mx,my)):
                play_sound('click'); choice = self.recycle_dialog()
                if choice == "praise":
                    self.recent_interaction = "Вы похвалили корзину — она запомнит."
                    state["recycle_praised"] = True
                    save_game(state)
                elif choice == "tease":
                    stolen = min(100, state.get("score",0))
                    state["score"] = max(0, state.get("score",0) - stolen)
                    self.recent_interaction = f"Вы подразнили корзину — она украла {stolen} очков!"
                    save_game(state)
            elif self.rect_ach.collidepoint((mx,my)):
                play_sound('click'); self.show_ach = not self.show_ach; self.show_components = False
            elif self.rect_menu.collidepoint((mx,my)):
                play_sound('click'); self.show_components = not self.show_components; self.show_ach = False
            elif self.rect_console.collidepoint((mx,my)) and state.get("console_unlocked", False):
                play_sound('click'); app.start_console()
            elif self.rect_minigames.collidepoint((mx,my)) and state.get("minigames_unlocked", False):
                play_sound('click'); app.start_minigames()
            
            # Check for upgrade button click
            if self.show_components and state.get("exp", 0) >= 1000:
                btn = pygame.Rect(200+300, 80+380, 150, 28)
                if btn.collidepoint((mx,my)):
                    self.upgrade_component()
    def upgrade_component(self):
        skin = current_skin(state)
        dlg = pygame.Rect(WIDTH//2-180, HEIGHT//2-80, 360, 160)
        run=True; choice=None
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    save_game(state); pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
                    mx,my = e.pos
                    btn_cpu = pygame.Rect(dlg.x+24, dlg.y+60, 70, 40)
                    btn_ram = pygame.Rect(dlg.x+104, dlg.y+60, 70, 40)
                    btn_hdd = pygame.Rect(dlg.x+184, dlg.y+60, 70, 40)
                    btn_gpu = pygame.Rect(dlg.x+264, dlg.y+60, 70, 40)
                    
                    if btn_cpu.collidepoint((mx,my)):
                        choice="cpu"; run=False
                    if btn_ram.collidepoint((mx,my)):
                        choice="ram"; run=False
                    if btn_hdd.collidepoint((mx,my)):
                        choice="hdd"; run=False
                    if btn_gpu.collidepoint((mx,my)):
                        choice="gpu"; run=False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    run=False
            # draw dialog
            pygame.draw.rect(screen, (240,240,240), dlg); pygame.draw.rect(screen,(0,0,0),dlg,1)
            draw_text(screen, "Улучшение компонента", (dlg.x+12, dlg.y+8), (0,0,0), FONT_BIG)
            draw_text(screen, "Выберите компонент для улучшения:", (dlg.x+12, dlg.y+40), (0,0,0))
            
            btn_cpu = pygame.Rect(dlg.x+24, dlg.y+60, 70, 40)
            btn_ram = pygame.Rect(dlg.x+104, dlg.y+60, 70, 40)
            btn_hdd = pygame.Rect(dlg.x+184, dlg.y+60, 70, 40)
            btn_gpu = pygame.Rect(dlg.x+264, dlg.y+60, 70, 40)
            
            pygame.draw.rect(screen, (220,220,220), btn_cpu); pygame.draw.rect(screen,(0,0,0),btn_cpu,1)
            pygame.draw.rect(screen, (220,220,220), btn_ram); pygame.draw.rect(screen,(0,0,0),btn_ram,1)
            pygame.draw.rect(screen, (220,220,220), btn_hdd); pygame.draw.rect(screen,(0,0,0),btn_hdd,1)
            pygame.draw.rect(screen, (220,220,220), btn_gpu); pygame.draw.rect(screen,(0,0,0),btn_gpu,1)
            
            draw_text(screen, "CPU", (btn_cpu.x+20, btn_cpu.y+10), (0,0,0))
            draw_text(screen, "RAM", (btn_ram.x+20, btn_ram.y+10), (0,0,0))
            draw_text(screen, "HDD", (btn_hdd.x+20, btn_hdd.y+10), (0,0,0))
            draw_text(screen, "GPU", (btn_gpu.x+20, btn_gpu.y+10), (0,0,0))
            
            pygame.display.flip(); clock.tick(30)
        
        if choice:
            state["components"][choice] += 1
            state["exp"] -= 1000
            save_game(state)
            self.recent_interaction = f"Улучшен {choice.upper()} до уровня {state['components'][choice]}!"
            play_sound('levelup')
    def recycle_dialog(self):
        skin = current_skin(state)
        dlg = pygame.Rect(WIDTH//2-180, HEIGHT//2-80, 360, 160)
        run=True; choice=None
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    save_game(state); pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
                    mx,my = e.pos
                    btn_praise = pygame.Rect(dlg.x+24, dlg.y+90, 140, 40)
                    btn_tease = pygame.Rect(dlg.x+196, dlg.y+90, 140, 40)
                    if btn_praise.collidepoint((mx,my)):
                        play_sound('click'); choice="praise"; run=False
                    if btn_tease.collidepoint((mx,my)):
                        play_sound('click'); choice="tease"; run=False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    run=False
            # draw dialog
            pygame.draw.rect(screen, (240,240,240), dlg); pygame.draw.rect(screen,(0,0,0),dlg,1)
            draw_text(screen, "Корзина", (dlg.x+12, dlg.y+8), (0,0,0), FONT_BIG)
            draw_text(screen, "Похвалить — шанс на бонус после уровня.", (dlg.x+12, dlg.y+40), (0,0,0))
            draw_text(screen, "Подразнить — риск потерять очки.", (dlg.x+12, dlg.y+60), (0,0,0))
            btn_praise = pygame.Rect(dlg.x+24, dlg.y+90, 140, 40)
            btn_tease = pygame.Rect(dlg.x+196, dlg.y+90, 140, 40)
            pygame.draw.rect(screen, (220,220,220), btn_praise); pygame.draw.rect(screen,(0,0,0),btn_praise,1)
            pygame.draw.rect(screen, (220,220,220), btn_tease); pygame.draw.rect(screen,(0,0,0),btn_tease,1)
            draw_text(screen, "Похвалить", (btn_praise.x+22, btn_praise.y+10), (0,0,0))
            draw_text(screen, "Подразнить", (btn_tease.x+18, btn_tease.y+10), (0,0,0))
            pygame.display.flip(); clock.tick(30)
        return choice
    def apply_promocode(self, code):
        code = code.strip().upper()
        if code == "GIVEME1000":
            state["score"] = state.get("score",0) + 1000; save_game(state); play_sound('click')
            return "Промокод применён: +1000 очков"
        if code == "CLEANBIN":
            state["recycle_praised"] = True; save_game(state); play_sound('click')
            return "Корзина счастлива (похвала активирована)"
        if code == "ALLACH":
            sample = ["Профессионалист","Оранжевый красавчик","Тянь-Янь","Любитель боли","First BSOD"]
            got=0
            for a in sample:
                if a not in state.get("achievements",[]):
                    state.setdefault("achievements",[]).append(a); got+=1
            save_game(state); play_sound('levelup')
            return f"Открылось {got} достижений"
        if code == "CONSOLE":
            state["console_unlocked"] = True; save_game(state); play_sound('success')
            return "Консоль разблокирована!"
        if code == "MINIGAMES":
            state["minigames_unlocked"] = True; save_game(state); play_sound('success')
            return "Мини-игры разблокированы!"
        return "Неверный промокод"

# -------------------- Классы: сегменты и курсор --------------------
class Segment:
    # kind: 'blue','orange','pink','red','mine','x2','x3'
    def __init__(self, kind, x, speed):
        self.kind = kind
        self.x = x
        self.y = -random.randint(10,220)
        self.size = 16 if kind in ('blue','orange','x2','x3') else 20
        self.speed = speed
        self.blink = (kind=='red')
        self.bstate = True
        self.bt = random.uniform(0.12,0.45)
        self.alive = True
    def update(self, dt):
        self.y += self.speed * dt * 60
        if self.blink:
            self.bt -= dt
            if self.bt <= 0:
                self.bstate = not self.bstate
                self.bt = random.uniform(0.12,0.4)
        if self.y > HEIGHT + 60:
            self.alive = False
    def draw(self, surf):
        if self.kind=='red' and not self.bstate:
            return
        if self.kind=='blue': col=(60,120,255)
        elif self.kind=='orange': col=(255,140,0)
        elif self.kind=='pink': col=(255,105,180)
        elif self.kind=='red': col=(200,0,0)
        elif self.kind=='mine': col=(90,90,90)
        elif self.kind=='x2': col=(30,200,30)
        elif self.kind=='x3': col=(255,215,0)
        else: col=(120,120,120)
        pygame.draw.rect(surf, col, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(surf, (0,0,0), (self.x, self.y, self.size, self.size),1)
        if self.kind == 'mine':
            pygame.draw.circle(surf, (255,80,0), (self.x + self.size//2, int(self.y + self.size/2)), 4)
        if self.kind == 'x2':
            draw_text(surf, "x2", (self.x+2, self.y+1), (0,0,0), FONT_SMALL)
        if self.kind == 'x3':
            draw_text(surf, "x3", (self.x+1, self.y+1), (0,0,0), FONT_SMALL)

class ProgressCursor:
    def __init__(self):
        self.w = 220; self.h = 22
        self.x = WIDTH//2 - self.w//2
        self.y = HEIGHT - 120
        self.follow_mouse = True
        self.base_speed = 14.0
        self.sticky = True
        self.st_strength = 0.22
    def update(self, dt, game):
        # Apply CPU upgrade effect
        cpu_level = state.get("components", {}).get("cpu", 1)
        self.speed = self.base_speed * (1 + 0.1 * (cpu_level - 1))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= int(self.speed * dt * 60)
        if keys[pygame.K_RIGHT]:
            self.x += int(self.speed * dt * 60)
        if self.follow_mouse:
            mx,_ = pygame.mouse.get_pos()
            curcx = self.x + self.w//2
            self.x += int((mx - curcx) * 0.6)
        self.x = clamp(self.x, 8, WIDTH - self.w - 8)
        # sticky: притянуть к ближайшему сегменту
        if self.sticky and game.segments:
            nearest=None; nd=9999
            for s in game.segments:
                dx = abs((self.x+self.w//2) - (s.x + s.size/2))
                dy = s.y - self.y
                if dx < 180 and dy > -140:
                    if dx < nd:
                        nd=dx; nearest=s
            if nearest and nd < 120:
                tcx = nearest.x + nearest.size/2
                curcx = self.x + self.w//2
                self.x += int((tcx - curcx) * self.st_strength)
    def draw(self, surf, skin):
        pygame.draw.rect(surf, skin["panel"], (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surf, (0,0,0), (self.x, self.y, self.w, self.h), 1)

# -------------------- Прогресс-игра --------------------
class ProgressGame:
    def __init__(self, app):
        self.app = app
        self.cursor = ProgressCursor()
        self.segments = []
        self.progress = 0.0   # 0..100
        self.negative = 0     # negative pink counter display (for UI)
        self.level = state.get("level",1)
        self.spawn_timer = 0.0
        # spawn interval decreases as level increases, but limited
        self.base_spawn_interval = max(0.12, 0.45 - (self.level-1)*0.02)
        self.base_speed = min(5.0, 2.0 + (self.level-1)*0.12)
        self.last_save = time.time()
        self.bsod = False
        # bsod minigame
        self.bsod_minigame_active = False
        self.bsod_minigame_time = 0.0
        self.bsod_minigame_duration = 2.0
        # target scales with level (higher level = harder)
        self.bsod_minigame_target = max(10, 10 + (self.level//3))
        self.bsod_minigame_count = 0
        self.shake = False
        # stats for achievements
        self.col_blue = 0; self.col_orange = 0; self.col_pink = 0; self.col_x2=0; self.col_x3=0
    def spawn_segment(self):
        if len(self.segments) >= MAX_SEGMENTS: return
        # Apply RAM upgrade effect
        ram_level = state.get("components", {}).get("ram", 1)
        spawn_interval = self.base_spawn_interval * (1 - 0.05 * (ram_level - 1))
        
        # probabilities that slightly change with level
        lvl = self.level
        # base probabilities
        r = random.random()
        # red chance grows with level modestly
        red_chance = min(0.12, 0.04 + lvl*0.005)
        mine_chance = min(0.10, 0.03 + lvl*0.004)
        pink_chance = 0.20
        orange_chance = 0.20
        x2_chance = 0.12
        x3_chance = 0.06
        blue_chance = 1.0 - (red_chance + mine_chance + pink_chance + orange_chance + x2_chance + x3_chance)
        # choose
        cut = 0.0
        if r < red_chance: kind='red'
        elif r < red_chance + mine_chance: kind='mine'
        elif r < red_chance + mine_chance + pink_chance: kind='pink'
        elif r < red_chance + mine_chance + pink_chance + orange_chance: kind='orange'
        elif r < red_chance + mine_chance + pink_chance + orange_chance + x2_chance: kind='x2'
        elif r < red_chance + mine_chance + pink_chance + orange_chance + x2_chance + x3_chance: kind='x3'
        else: kind='blue'
        x=random.randint(80, WIDTH-120)
        s = self.base_speed + random.uniform(-0.2,0.8)
        self.segments.append(Segment(kind, x, s))
    def update(self, dt):
        # Apply RAM upgrade effect
        ram_level = state.get("components", {}).get("ram", 1)
        spawn_interval = self.base_spawn_interval * (1 - 0.05 * (ram_level - 1))
        
        # regen lives each 5 minutes
        now=time.time()
        if now - state.get("last_life_time", now) >= 300.0:
            if state.get("lives",0) < 5:
                state["lives"] += 1
            state["last_life_time"] = now
            save_game(state)
        if self.bsod:
            # handle minigame timing
            if self.bsod_minigame_active:
                self.bsod_minigame_time += dt
                if self.bsod_minigame_time >= self.bsod_minigame_duration:
                    self.bsod_minigame_active = False
                    self.shake = False
                    # evaluate success
                    if self.bsod_minigame_count >= self.bsod_minigame_target:
                        # success restore partial
                        self.bsod = False
                        self.progress = max(0.0, self.progress * 0.6)
                        state["score"] = state.get("score",0) + 50
                        play_sound('pickup')
                        save_game(state)
                    else:
                        # fail
                        self.bsod = False
                        self.progress = 0.0
                        state["score"] = max(0, state.get("score",0) - 100)
                        if state.get("lives",0) > 0:
                            state["lives"] -= 1
                        play_sound('bsod')
                        save_game(state)
            return
        # spawn
        self.spawn_timer += dt
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            self.spawn_segment()
        # update segments
        for s in list(self.segments):
            s.update(dt)
            if not s.alive:
                try: self.segments.remove(s)
                except: pass
                continue
            # collision with cursor
            if (self.cursor.y < s.y + s.size < self.cursor.y + self.cursor.h) and (self.cursor.x < s.x < self.cursor.x + self.cursor.w):
                # Apply HDD upgrade effect (score multiplier)
                hdd_level = state.get("components", {}).get("hdd", 1)
                score_multiplier = 1 + 0.1 * (hdd_level - 1)
                
                # Apply GPU upgrade effect (pink penalty reduction)
                gpu_level = state.get("components", {}).get("gpu", 1)
                pink_penalty_reduction = 0.1 * (gpu_level - 1)
                
                # apply effects
                if s.kind == 'blue':
                    self.progress = min(100.0, self.progress + 5.0)
                    state["score"] = state.get("score",0) + int(8 * score_multiplier)
                    self.col_blue += 1
                    play_sound('pickup')
                elif s.kind == 'orange':
                    self.progress = min(100.0, self.progress + 5.0)
                    state["score"] = state.get("score",0) + int(6 * score_multiplier)
                    self.col_orange += 1
                    play_sound('pickup')
                elif s.kind == 'pink':
                    if self.progress > 0:
                        self.progress = max(0.0, self.progress - max(1, 5 - pink_penalty_reduction))
                    else:
                        state["pink_counter"] = state.get("pink_counter",0) - 1
                        self.negative = -state["pink_counter"]
                    state["score"] = max(0, state.get("score",0) - int(6 * (1 - pink_penalty_reduction)))
                    self.col_pink += 1
                    play_sound('bsod')
                    if state.get("pink_counter",0) <= -100 and "Любитель боли" not in state.get("achievements",[]):
                        state.setdefault("achievements",[]).append("Любитель боли")
                elif s.kind == 'red':
                    play_sound('bsod'); self.trigger_bsod()
                elif s.kind == 'mine':
                    play_sound('bsod'); self.trigger_bsod()
                elif s.kind == 'x2':
                    self.progress = min(100.0, self.progress + 10.0)
                    state["score"] = state.get("score",0) + int(14 * score_multiplier)
                    self.col_x2 += 1
                    play_sound('pickup')
                elif s.kind == 'x3':
                    self.progress = min(100.0, self.progress + 15.0)
                    state["score"] = state.get("score",0) + int(18 * score_multiplier)
                    self.col_x3 += 1
                    play_sound('pickup')
                try: self.segments.remove(s)
                except: pass
        # update cursor
        self.cursor.update(dt, self)
        # level complete
        if self.progress >= 100.0:
            self.on_level_complete()
        # autosave
        if time.time() - self.last_save > 5.0:
            save_game(state); self.last_save = time.time()
    def draw(self):
        skin = current_skin(state)
        screen.fill(skin["bg"])
        draw_text(screen, f"C:\\WINDOWS\\SYSTEM32\\PROGRESS.EXE — уровень {self.level}", (8,6), skin["text"], FONT_BIG)
        pygame.draw.rect(screen, skin["panel"], (12,40,340,160)); pygame.draw.rect(screen, skin["panel"], (WIDTH-352,40,320,160))
        draw_text(screen, f"Уровень: {self.level}", (20,56), skin["text"])
        draw_text(screen, f"Очки: {state.get('score',0)}", (20,86), skin["text"])
        draw_text(screen, f"Опыт: {state.get('exp',0)}", (20,116), skin["text"])
        draw_text(screen, f"Жизни: {state.get('lives',0)}", (20,146), skin["text"])
        # draw segments
        for s in self.segments:
            s.draw(screen)
        # draw cursor
        self.cursor.draw(screen, skin)
        # draw bottom progress bar including negative part and orange indicators
        bx,by,bw,bh = 24, HEIGHT-116, WIDTH-48, 56
        pygame.draw.rect(screen, skin["white"], (bx,by,bw,bh)); pygame.draw.rect(screen,(0,0,0),(bx,by,bw,bh),1)
        # compute positive fill width
        pos_ratio = max(0.0, min(1.0, self.progress/100.0))
        pos_width = int((bw-8) * pos_ratio)
        pygame.draw.rect(screen, skin["accent"], (bx+4, by+4, pos_width, bh-8))
        # show orange collected markers above bar
        if self.col_orange > 0:
            for i in range(min(10, self.col_orange)):
                tx = bx + 12 + i*18
                pygame.draw.rect(screen, (255,140,0), (tx, by-8, 12, 6))
        # negative pink blocks to left
        neg = self.negative
        if neg > 0:
            max_neg_show = 20
            nshow = min(neg, max_neg_show)
            for i in range(nshow):
                nx = bx - (i+1)*10
                pygame.draw.rect(screen, (255,105,180), (nx, by+12, 8, 12))
        draw_text(screen, f"{int(self.progress)}%", (bx + bw//2 - 24, by + 8), (0,0,0), FONT_BIG)
        # lives icons
        for i in range(state.get("lives",0)):
            pygame.draw.rect(screen, (200,0,0), (24 + i*26, HEIGHT-72, 18, 18)); pygame.draw.rect(screen,(0,0,0),(24 + i*26, HEIGHT-72, 18, 18),1)
        # if bsod overlay
        if self.bsod:
            self.draw_bsod_overlay()
    def trigger_bsod(self):
        self.bsod = True
        self.bsod_minigame_active = False
        self.bsod_minigame_time = 0.0
        self.bsod_minigame_count = 0
        self.shake = False
        if "First BSOD" not in state.get("achievements",[]):
            state.setdefault("achievements",[]).append("First BSOD"); save_game(state)
    def draw_bsod_overlay(self):
        skin = current_skin(state)
        ov = pygame.Surface((WIDTH, HEIGHT)); ov.fill(skin["bsod"]); ov.set_alpha(230); screen.blit(ov,(0,0))
        for y in range(0, HEIGHT, 6):
            pygame.draw.line(screen, (0,0,0), (0, y + random.randint(-1,1)), (WIDTH, y + random.randint(-1,1)))
        draw_text(screen, "Произошла критическая системная ошибка.", (WIDTH//2-300, HEIGHT//2-100), skin["white"], FONT_BIG)
        if not self.bsod_minigame_active:
            draw_text(screen, "Нажмите R чтобы начать быструю попытку восстановления.", (WIDTH//2-330, HEIGHT//2 - 40), skin["white"])
            draw_text(screen, "Либо нажмите кнопку 'Восстановить' (снимает 1 жизнь).", (WIDTH//2-330, HEIGHT//2 - 12), skin["white"])
            btn = pygame.Rect(WIDTH//2 - 140, HEIGHT//2 + 8, 280, 44)
            pygame.draw.rect(screen, (220,220,220), btn); pygame.draw.rect(screen, (0,0,0), btn, 1)
            draw_text(screen, "Восстановить (снять 1 жизнь)", (btn.x+36, btn.y+10), (0,0,0))
        else:
            remaining = max(0.0, self.bsod_minigame_duration - self.bsod_minigame_time)
            draw_text(screen, f"МИНИИГРА: Нажимай ПРОБЕЛ! Время: {remaining:.2f}s", (WIDTH//2-300, HEIGHT//2 - 40), skin["white"])
            draw_text(screen, f"Нажато: {self.bsod_minigame_count} / {self.bsod_minigame_target}", (WIDTH//2-120, HEIGHT//2 - 8), skin["white"])
    def on_level_complete(self):
        total_collected = self.col_blue + self.col_orange + self.col_pink + self.col_x2 + self.col_x3
        earned = None
        if total_collected > 0:
            # precise checks:
            if self.col_orange == total_collected and total_collected>0:
                earned = "Оранжевый красавчик"
            elif self.col_blue == total_collected and total_collected>0:
                earned = "Профессионалист"
            else:
                # 50/50 approx -> Тянь-Янь
                if self.col_orange > 0 and self.col_blue > 0:
                    # require both >= 40% each
                    if (self.col_orange / total_collected) >= 0.4 and (self.col_blue / total_collected) >= 0.4:
                        # check closeness
                        if abs(self.col_orange - self.col_blue) <= max(1, int(total_collected*0.15)):
                            earned = "Тянь-Янь"
        # recycle praise bonus
        if state.get("recycle_praised", False):
            state["score"] = state.get("score",0) + 80
            if "Бонус от мусорки" not in state.get("achievements",[]):
                state.setdefault("achievements",[]).append("Бонус от мусорки")
            state["recycle_praised"] = False
            save_game(state)
        
        # Add experience points
        exp_gained = 100 + self.level * 20
        state["exp"] = state.get("exp", 0) + exp_gained
        
        # Check for component upgrades
        if state["exp"] >= 1000 and "Системный администратор" not in state.get("achievements",[]):
            state.setdefault("achievements",[]).append("Системный администратор")
        
        # Unlock console and minigames at certain levels
        if self.level >= 3 and not state.get("console_unlocked", False):
            state["console_unlocked"] = True
            if "Консольный мастер" not in state.get("achievements",[]):
                state.setdefault("achievements",[]).append("Консольный мастер")
        
        if self.level >= 5 and not state.get("minigames_unlocked", False):
            state["minigames_unlocked"] = True
            if "Игроман" not in state.get("achievements",[]):
                state.setdefault("achievements",[]).append("Игроман")
        
        # finalize: reward points and advance level
        state["score"] = state.get("score",0) + 200
        self.level += 1
        state["level"] = self.level
        save_game(state)
        # show only the earned achievement (or None)
        if earned:
            if earned not in state.get("achievements",[]):
                state.setdefault("achievements",[]).append(earned)
            play_sound('levelup')
            self.app.show_level_complete(earned, exp_gained)
        else:
            self.app.show_level_complete(None, exp_gained)

# -------------------- Консольная мини-игра --------------------
class ConsoleGame:
    def __init__(self, app):
        self.app = app
        self.history = []
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.commands = {
            "help": self.cmd_help,
            "scan": self.cmd_scan,
            "fix": self.cmd_fix,
            "hack": self.cmd_hack,
            "clear": self.cmd_clear,
            "exit": self.cmd_exit
        }
        self.entities = []
        self.generate_entities()
        self.completed = False
    def generate_entities(self):
        self.entities = []
        for i in range(5):
            x = random.randint(10, 90)
            y = random.randint(10, 90)
            self.entities.append({"type": "virus", "x": x, "y": y, "fixed": False})
        for i in range(3):
            x = random.randint(10, 90)
            y = random.randint(10, 90)
            self.entities.append({"type": "file", "x": x, "y": y, "fixed": False})
    def cmd_help(self, args):
        self.history.append("Доступные команды:")
        self.history.append("help - показать справку")
        self.history.append("scan - просканировать систему")
        self.history.append("fix X Y - исправить проблему в координатах X Y")
        self.history.append("hack - взломать систему (только после исправления всех проблем)")
        self.history.append("clear - очистить экран")
        self.history.append("exit - выйти из консоли")
    def cmd_scan(self, args):
        if not any(not e["fixed"] for e in self.entities if e["type"] == "virus"):
            self.history.append("Все вирусы устранены! Система чиста.")
            return
        
        self.history.append("Сканирование системы...")
        for e in self.entities:
            if not e["fixed"]:
                if e["type"] == "virus":
                    self.history.append(f"Обнаружен вирус в секторе ({e['x']}, {e['y']})")
                else:
                    self.history.append(f"Обнаружен поврежденный файл в секторе ({e['x']}, {e['y']})")
    def cmd_fix(self, args):
        if len(args) < 2:
            self.history.append("Ошибка: укажите координаты (fix X Y)")
            return
        
        try:
            x = int(args[0])
            y = int(args[1])
        except:
            self.history.append("Ошибка: координаты должны быть числами")
            return
        
        for e in self.entities:
            if not e["fixed"] and abs(e["x"] - x) <= 5 and abs(e["y"] - y) <= 5:
                e["fixed"] = True
                if e["type"] == "virus":
                    self.history.append(f"Вирус в секторе ({e['x']}, {e['y']}) устранен!")
                    state["score"] = state.get("score", 0) + 50
                else:
                    self.history.append(f"Файл в секторе ({e['x']}, {e['y']}) восстановлен!")
                    state["score"] = state.get("score", 0) + 30
                save_game(state)
                return
        
        self.history.append(f"В секторе ({x}, {y}) не обнаружено проблем")
    def cmd_hack(self, args):
        if any(not e["fixed"] for e in self.entities):
            self.history.append("Не все проблемы устранены! Используйте команду scan для поиска проблем.")
            return
        
        self.history.append("Взлом системы...")
        self.history.append("Успех! Получен доступ к системным файлам.")
        state["score"] = state.get("score", 0) + 200
        state["exp"] = state.get("exp", 0) + 100
        save_game(state)
        self.completed = True
    def cmd_clear(self, args):
        self.history = []
    def cmd_exit(self, args):
        self.app.stop_console()
    def handle_command(self):
        parts = self.input_text.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            self.history.append(f"> {self.input_text}")
            self.commands[cmd](args)
        else:
            self.history.append(f"> {self.input_text}")
            self.history.append(f"Неизвестная команда: {cmd}")
        
        self.input_text = ""
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    def draw(self):
        skin = current_skin(state)
        screen.fill((0, 20, 0))
        
        # Draw console header
        pygame.draw.rect(screen, (0, 40, 0), (0, 0, WIDTH, 30))
        draw_text(screen, "Системная консоль - Введите 'help' для справки", (10, 5), (0, 255, 0), FONT)
        
        # Draw command history
        y = 40
        for line in self.history[-20:]:
            draw_text(screen, line, (10, y), (180, 255, 180), FONT_CONSOLE)
            y += 20
        
        # Draw input line
        pygame.draw.rect(screen, (0, 30, 0), (0, HEIGHT-30, WIDTH, 30))
        input_display = "> " + self.input_text
        if self.cursor_visible:
            input_display += "_"
        draw_text(screen, input_display, (10, HEIGHT-25), (0, 255, 0), FONT_CONSOLE)
        
        # Draw status
        remaining = sum(1 for e in self.entities if not e["fixed"])
        draw_text(screen, f"Осталось проблем: {remaining}", (WIDTH-200, HEIGHT-25), (0, 255, 0), FONT_CONSOLE)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.handle_command()
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 50:
                    self.input_text += event.unicode

# -------------------- Мини-игры --------------------
class MinigameMenu:
    def __init__(self, app):
        self.app = app
        self.games = [
            {"name": "Змейка", "description": "Классическая змейка", "unlocked": True},
            {"name": "Тетрис", "description": "Классический тетрис", "unlocked": state.get("level", 1) >= 2},
            {"name": "Сапер", "description": "Найди все мины", "unlocked": state.get("level", 1) >= 4},
            {"name": "Арканоид", "description": "Разбей все блоки", "unlocked": state.get("level", 1) >= 6}
        ]
        self.selected = 0
    def draw(self):
        skin = current_skin(state)
        screen.fill(skin["bg"])
        
        # Draw title
        pygame.draw.rect(screen, skin["title"], (0, 0, WIDTH, 40))
        draw_text(screen, "Мини-игры", (WIDTH//2-60, 5), skin["white"], FONT_BIG)
        
        # Draw games list
        for i, game in enumerate(self.games):
            y = 60 + i * 80
            color = skin["accent"] if i == self.selected else skin["panel"]
            pygame.draw.rect(screen, color, (WIDTH//2-200, y, 400, 60))
            pygame.draw.rect(screen, (0,0,0), (WIDTH//2-200, y, 400, 60), 2)
            
            if game["unlocked"]:
                draw_text(screen, game["name"], (WIDTH//2-190, y+10), skin["text"], FONT_BIG)
                draw_text(screen, game["description"], (WIDTH//2-190, y+35), skin["text"], FONT_SMALL)
            else:
                draw_text(screen, "Заблокировано", (WIDTH//2-190, y+10), (100,100,100), FONT_BIG)
                draw_text(screen, f"Достигните уровня {i*2+2} для разблокировки", (WIDTH//2-190, y+35), (100,100,100), FONT_SMALL)
        
        # Draw back button
        pygame.draw.rect(screen, skin["panel"], (20, HEIGHT-60, 120, 40))
        pygame.draw.rect(screen, (0,0,0), (20, HEIGHT-60, 120, 40), 2)
        draw_text(screen, "Назад", (40, HEIGHT-50), skin["text"], FONT)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.games)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.games)
            elif event.key == pygame.K_RETURN:
                if self.games[self.selected]["unlocked"]:
                    self.app.start_minigame(self.selected)
            elif event.key == pygame.K_ESCAPE:
                self.app.stop_minigames()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Check back button
            if 20 <= x <= 140 and HEIGHT-60 <= y <= HEIGHT-20:
                self.app.stop_minigames()
            # Check game selection
            for i in range(len(self.games)):
                game_y = 60 + i * 80
                if WIDTH//2-200 <= x <= WIDTH//2+200 and game_y <= y <= game_y+60:
                    self.selected = i
                    if self.games[i]["unlocked"]:
                        self.app.start_minigame(i)

# -------------------- Менеджер приложения --------------------
class App:
    def __init__(self):
        self.desktop = Desktop(self)
        self.mode = "boot"  # boot, desktop, progress, level_complete, console, minigames, minigame
        self.game = None
        self.console = None
        self.minigame_menu = None
        self.minigame = None
        self.level_complete_ach = None
        self.level_complete_exp = 0
        pygame.mouse.set_visible(True)
        self.boot_shown = False
    def start(self):
        retro_boot_effect(1.2)
        self.mode = "desktop"
    def start_progress(self):
        # OS upgrade check: if enough очков, upgrade immediately and boot effect
        if state.get("exp",0) >= 1000 and state.get("score",0) >= 20000:
            names = [s["name"] for s in SKINS]
            cur = state.get("os","Win95")
            idx = names.index(cur) if cur in names else 0
            if idx < len(names) - 1:
                state["os"] = names[idx + 1]
                state["exp"] = 0  # Reset exp after OS upgrade
                save_game(state)
                retro_boot_effect(1.4, text=f"Обновление ОС: {state['os']}")
        pygame.mouse.set_visible(False)
        self.game = ProgressGame(self)
        self.mode = "progress"
    def stop_progress(self):
        pygame.mouse.set_visible(True)
        save_game(state)
        self.game = None
        self.mode = "desktop"
    def show_level_complete(self, earned_ach, exp_gained):
        self.level_complete_ach = earned_ach
        self.level_complete_exp = exp_gained
        self.mode = "level_complete"
        pygame.mouse.set_visible(True)
    def start_console(self):
        self.console = ConsoleGame(self)
        self.mode = "console"
    def stop_console(self):
        self.console = None
        self.mode = "desktop"
    def start_minigames(self):
        self.minigame_menu = MinigameMenu(self)
        self.mode = "minigames"
    def stop_minigames(self):
        self.minigame_menu = None
        self.mode = "desktop"
    def start_minigame(self, game_index):
        # Placeholder for actual minigame implementation
        print(f"Starting minigame {game_index}")
        # For now, just go back to menu
        self.mode = "minigames"
    def prompt_promocode(self):
        skin = current_skin(state)
        dlg = pygame.Rect(WIDTH//2-220, HEIGHT//2-60, 440, 120)
        input_text = ""
        active = True
        while active:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    save_game(state); pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        active=False; break
                    elif e.key == pygame.K_RETURN:
                        code = input_text.strip(); active=False; return code
                    elif e.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 30:
                            input_text += e.unicode
            pygame.draw.rect(screen, (240,240,240), dlg); pygame.draw.rect(screen,(0,0,0),dlg,1)
            draw_text(screen, "Введите промокод (ENTER для подтверждения, ESC выход):", (dlg.x+12, dlg.y+8), (0,0,0))
            ib = pygame.Rect(dlg.x+12, dlg.y+44, dlg.w-24, 36)
            pygame.draw.rect(screen, (255,255,255), ib); pygame.draw.rect(screen,(0,0,0),ib,1)
            draw_text(screen, input_text, (ib.x+6, ib.y+6), (0,0,0))
            pygame.display.flip(); clock.tick(60)
        return None
    def run(self):
        if not self.boot_shown:
            self.start(); self.boot_shown=True
        running = True
        while running:
            dt = clock.tick(FPS)/1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    save_game(state); running=False
                if self.mode == "desktop":
                    self.desktop.handle_event(ev, self)
                elif self.mode == "progress":
                    g = self.game
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            self.stop_progress()
                        if ev.key == pygame.K_TAB:
                            g.cursor.follow_mouse = not g.cursor.follow_mouse
                        if g.bsod:
                            if not g.bsod_minigame_active and ev.key == pygame.K_r:
                                g.bsod_minigame_active = True; g.bsod_minigame_time = 0.0; g.bsod_minigame_count = 0; g.shake = True
                                play_sound('click')
                            elif g.bsod_minigame_active and ev.key == pygame.K_SPACE:
                                g.bsod_minigame_count += 1
                                # small click sound occasionally
                                if g.bsod_minigame_count % 3 == 0: play_sound('click')
                            elif (not g.bsod_minigame_active) and ev.key == pygame.K_RETURN:
                                if state.get("lives",0) > 0:
                                    state["lives"] -= 1; g.bsod = False; g.progress = max(0.0, g.progress*0.5); save_game(state)
                                else:
                                    g.bsod = False; g.progress = 0.0; save_game(state); self.stop_progress()
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if g.bsod:
                            btn = pygame.Rect(WIDTH//2 - 140, HEIGHT//2 + 8, 280, 44)
                            if btn.collidepoint(ev.pos):
                                if state.get("lives",0) > 0:
                                    state["lives"] -= 1; g.bsod = False; g.progress = max(0.0, g.progress*0.5); save_game(state)
                                else:
                                    g.bsod = False; g.progress = 0.0; save_game(state); self.stop_progress()
                elif self.mode == "level_complete":
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        mx,my = ev.pos
                        bx = WIDTH//2 - 180; by = HEIGHT//2 + 100
                        btn_continue = pygame.Rect(bx, by, 150, 40)
                        btn_desktop = pygame.Rect(bx+170, by, 150, 40)
                        if btn_continue.collidepoint((mx,my)):
                            pygame.mouse.set_visible(False); self.game = ProgressGame(self); self.mode = "progress"; play_sound('click')
                        elif btn_desktop.collidepoint((mx,my)):
                            self.stop_progress(); play_sound('click')
                elif self.mode == "console":
                    self.console.handle_event(ev)
                elif self.mode == "minigames":
                    self.minigame_menu.handle_event(ev)
            
            # drawing & updates
            if self.mode == "desktop":
                self.desktop.draw(); mx,my = pygame.mouse.get_pos()
                pygame.draw.rect(screen, (230,230,230), (mx,my,10,10)); pygame.draw.rect(screen,(0,0,0),(mx,my,10,10),1)
            elif self.mode == "progress":
                g = self.game
                # if bsod + shake, render then blit with random offset
                if g.bsod and (g.bsod_minigame_active or g.shake):
                    g.update(dt); g.draw()
                    if g.shake:
                        sx = random.randint(-8,8); sy = random.randint(-8,8)
                        surf = screen.copy()
                        screen.fill((0,0,0)); screen.blit(surf, (sx, sy))
                else:
                    g.update(dt); g.draw()
            elif self.mode == "level_complete":
                skin = current_skin(state)
                screen.fill((36,36,36))
                draw_text(screen, "Поздравляем! Уровень завершен.", (WIDTH//2 - 260, HEIGHT//2 - 120), (255,255,255), FONT_BIG)
                draw_text(screen, f"Уровень: {state.get('level',1)}", (WIDTH//2 - 260, HEIGHT//2 - 60), (255,255,255))
                draw_text(screen, f"Очки: {state.get('score',0)}", (WIDTH//2 - 260, HEIGHT//2 - 30), (255,255,255))
                draw_text(screen, f"Опыт: +{self.level_complete_exp}", (WIDTH//2 - 260, HEIGHT//2 + 0), (255,255,255))
                if self.level_complete_ach:
                    draw_text(screen, f"Вы заработали ачивку: {self.level_complete_ach}", (WIDTH//2 - 260, HEIGHT//2 + 30), (180,220,120))
                else:
                    draw_text(screen, "Ачивки не заработаны.", (WIDTH//2 - 260, HEIGHT//2 + 30), (220,120,120))
                bx = WIDTH//2 - 180; by = HEIGHT//2 + 100
                btn_continue = pygame.Rect(bx, by, 150, 40)
                btn_desktop = pygame.Rect(bx+170, by, 150, 40)
                pygame.draw.rect(screen, skin["panel"], btn_continue); pygame.draw.rect(screen, (0,0,0), btn_continue,1)
                pygame.draw.rect(screen, skin["panel"], btn_desktop); pygame.draw.rect(screen, (0,0,0), btn_desktop,1)
                draw_text(screen, "Продолжить", (btn_continue.x+26, btn_continue.y+10), skin["text"])
                draw_text(screen, "На рабочий стол", (btn_desktop.x+10, btn_desktop.y+10), skin["text"])
            elif self.mode == "console":
                self.console.update(dt)
                self.console.draw()
            elif self.mode == "minigames":
                self.minigame_menu.draw()
            
            pygame.display.flip()
        pygame.quit(); sys.exit()

# -------------------- Запуск --------------------
if __name__ == "__main__":
    app = App()
    app.run()