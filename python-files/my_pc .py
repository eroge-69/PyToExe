import pygame
import sys
import webbrowser
import os
import time
from datetime import datetime

pygame.init()
pygame.font.init()

# تنظیمات صفحه
WIDTH, HEIGHT = 960, 600
FPS = 30

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARKGRAY = (50, 50, 50)
BLUE = (50, 120, 220)
GREEN = (50, 200, 50)
RED = (200, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python OS Simulator")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("arial", 28)
font_mid = pygame.font.SysFont("arial", 22)
font_small = pygame.font.SysFont("arial", 16)

# رمز ورود
PASSWORD = "1234"
lang = "EN"

# بارگذاری تصاویر
def load_image(name):
    path = os.path.join("my_pc", name)
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return None

# پس‌زمینه
background_img = load_image("images (4).jfif")
if background_img:
    background = pygame.transform.smoothscale(background_img, (WIDTH, HEIGHT))
else:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(DARKGRAY)

# آیکون‌ها با مسیر صحیح فایل‌ها
icons_info = [
    {"name": "Calculator", "file": "calculator (رسانیکا).png", "pos": (50, 50)},
    {"name": "My Computer", "file": "toppng.com-computer-png-1280x853.png", "pos": (160, 50)},
    {"name": "Browser", "file": "browsers-png-21678.png", "pos": (270, 50)},
    {"name": "Games", "file": "87q74gcsg3fnj9ogmnauhsckf8-c64db44a6269a5943cd009135d557640.png", "pos": (380, 50)},
]

for icon in icons_info:
    icon["image"] = load_image(icon["file"])
    if icon["image"]:
        icon["image"] = pygame.transform.smoothscale(icon["image"], (64, 64))
    icon["rect"] = pygame.Rect(icon["pos"][0], icon["pos"][1], 64, 64)

open_windows = []

# کلاس پایه پنجره
class Window:
    def __init__(self, title, size):
        self.title = title
        self.width, self.height = size
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGHT - self.height) // 2
        self.drag = False
        self.drag_offset = (0, 0)
        self.closed = False
        self.title_bar_height = 30

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.title_bar_height:
                self.drag = True
                self.drag_offset = (mx - self.x, my - self.y)
            close_rect = pygame.Rect(self.x + self.width - 30, self.y, 30, self.title_bar_height)
            if close_rect.collidepoint(mx, my):
                self.closed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.drag = False

        elif event.type == pygame.MOUSEMOTION:
            if self.drag:
                mx, my = event.pos
                self.x = mx - self.drag_offset[0]
                self.y = my - self.drag_offset[1]
                self.x = max(0, min(self.x, WIDTH - self.width))
                self.y = max(0, min(self.y, HEIGHT - self.height))

    def draw(self, surf):
        pygame.draw.rect(surf, DARKGRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surf, BLUE, (self.x, self.y, self.width, self.title_bar_height))
        title = font_mid.render(self.title, True, WHITE)
        surf.blit(title, (self.x + 5, self.y + 5))
        close_rect = pygame.Rect(self.x + self.width - 30, self.y, 30, self.title_bar_height)
        pygame.draw.rect(surf, RED, close_rect)
        x_txt = font_mid.render("X", True, WHITE)
        surf.blit(x_txt, (close_rect.x + 10, close_rect.y + 5))

# ماشین حساب پیشرفته با حذف، پاکسازی، دکمه‌های فشاری
class Calculator(Window):
    def __init__(self):
        super().__init__("Calculator", (320, 420))
        self.input_str = ""
        self.result = ""
        self.buttons = [
            ("7", 10, 100), ("8", 80, 100), ("9", 150, 100), ("/", 220, 100),
            ("4", 10, 160), ("5", 80, 160), ("6", 150, 160), ("*", 220, 160),
            ("1", 10, 220), ("2", 80, 220), ("3", 150, 220), ("-", 220, 220),
            ("0", 10, 280), (".", 80, 280), ("=", 150, 280), ("+", 220, 280),
            ("C", 10, 340), ("DEL", 150, 340),
        ]
        self.pressed = None

    def draw(self, surf):
        super().draw(surf)
        pygame.draw.rect(surf, BLACK, (self.x + 10, self.y + 40, self.width - 20, 50))
        size = 32 if len(self.input_str) < 12 else 24
        font_dynamic = pygame.font.SysFont("arial", size)
        inp = font_dynamic.render(self.input_str if self.input_str else "0", True, WHITE)
        inp_rect = inp.get_rect(right=self.x + self.width - 15, centery=self.y + 65)
        surf.blit(inp, inp_rect)
        res = font_small.render(self.result, True, GREEN if self.result != "Error" else RED)
        surf.blit(res, (self.x + 15, self.y + 95))
        self.rects = []
        for txt, bx, by in self.buttons:
            rect = pygame.Rect(self.x + bx, self.y + by, 60, 40)
            color = BLUE if txt == self.pressed else GRAY
            pygame.draw.rect(surf, color, rect)
            t = font_mid.render(txt, True, BLACK)
            surf.blit(t, t.get_rect(center=rect.center))
            self.rects.append((rect, txt))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, txt in self.rects:
                if rect.collidepoint(event.pos):
                    self.pressed = txt
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self._on_click(self.pressed)
                self.pressed = None

    def _on_click(self, txt):
        if txt == "C":
            self.input_str = ""
            self.result = ""
        elif txt == "DEL":
            self.input_str = self.input_str[:-1]
        elif txt == "=":
            try:
                expr = self.input_str.replace("^", "**")
                self.result = str(eval(expr, {"__builtins__": None}, {}))
            except:
                self.result = "Error"
        else:
            if txt in "+-*/.":
                if not self.input_str and txt != "-":
                    return
                if self.input_str and self.input_str[-1] in "+-*/.":
                    self.input_str = self.input_str[:-1]
            self.input_str += txt

# ترمینال ساده
class Terminal(Window):
    def __init__(self):
        super().__init__("Terminal", (500, 400))
        self.lines = []
        self.input_line = ""
        self.history = []
        self.hist_idx = -1

    def draw(self, surf):
        super().draw(surf)
        t_rect = pygame.Rect(self.x+5, self.y+self.title_bar_height+5, self.width-10, self.height-self.title_bar_height-10)
        pygame.draw.rect(surf, BLACK, t_rect)
        y = self.y + self.title_bar_height + 10
        for line in self.lines[-15:]:
            surf.blit(font_small.render(line, True, GREEN), (self.x+10, y))
            y += 18
        surf.blit(font_mid.render("> " + self.input_line + "_", True, WHITE), (self.x+10, self.y + self.height - 30))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_line = self.input_line[:-1]
            elif event.key == pygame.K_RETURN:
                cmd = self.input_line.strip()
                self.lines.append("> " + cmd)
                self._execute(cmd)
                self.history.append(cmd)
                self.hist_idx = -1
                self.input_line = ""
            elif event.key == pygame.K_UP and self.history:
                self.hist_idx = min(self.hist_idx + 1, len(self.history)-1)
                self.input_line = self.history[-1 - self.hist_idx]
            elif event.key == pygame.K_DOWN:
                if self.hist_idx > 0:
                    self.hist_idx -= 1
                    self.input_line = self.history[-1 - self.hist_idx]
                else:
                    self.input_line = ""
                    self.hist_idx = -1
            elif event.unicode.isprintable():
                self.input_line += event.unicode

    def _execute(self, cmd):
        cmd = cmd.lower()
        if cmd == "help":
            self.lines.append("Commands: help, clear, exit")
        elif cmd == "clear":
            self.lines.clear()
        elif cmd == "exit":
            self.closed = True
        else:
            self.lines.append(f"Unknown command: {cmd}")

# بازی مار
class SnakeGame(Window):
    def __init__(self):
        super().__init__("Snake Game", (400, 400))
        self.cell = 20
        self.cols = self.width // self.cell
        self.rows = (self.height - self.title_bar_height) // self.cell
        self.reset()

    def reset(self):
        self.snake = [(self.cols//2, self.rows//2)]
        self.direction = (0, -1)
        self._spawn_food()
        self.over = False
        self.score = 0
        self.last_move = pygame.time.get_ticks()
        self.delay = 150

    def _spawn_food(self):
        import random
        while True:
            self.food = (random.randint(0, self.cols-1), random.randint(0, self.rows-1))
            if self.food not in self.snake:
                break

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and not self.over:
            if event.key == pygame.K_UP and self.direction != (0, 1):
                self.direction = (0, -1)
            elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                self.direction = (0, 1)
            elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                self.direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                self.direction = (1, 0)
            elif event.key == pygame.K_r and self.over:
                self.reset()

    def update(self):
        if self.over: return
        now = pygame.time.get_ticks()
        if now - self.last_move > self.delay:
            self.last_move = now
            head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
            if (head[0]<0 or head[0]>=self.cols or head[1]<0 or head[1]>=self.rows or head in self.snake):
                self.over = True
                return
            self.snake.insert(0, head)
            if head == self.food:
                self.score += 1
                self._spawn_food()
            else:
                self.snake.pop()

    def draw(self, surf):
        super().draw(surf)
        gr = pygame.Rect(self.x+5, self.y+self.title_bar_height+5, self.width-10, self.height-self.title_bar_height-10)
        pygame.draw.rect(surf, BLACK, gr)
        for seg in self.snake:
            rect = pygame.Rect(gr.x + seg[0]*self.cell, gr.y + seg[1]*self.cell, self.cell, self.cell)
            pygame.draw.rect(surf, GREEN, rect)
        fr = pygame.Rect(gr.x + self.food[0]*self.cell, gr.y + self.food[1]*self.cell, self.cell, self.cell)
        pygame.draw.rect(surf, RED, fr)
        surf.blit(font_mid.render(f"Score: {self.score}", True, WHITE), (self.x + 10, self.y + 35))
        if self.over:
            ov = font_big.render("Game Over! Press R", True, RED)
            surf.blit(ov, (self.x + 50, self.y + self.height//2 - 20))

# My Computer window
class ThisPC(Window):
    def __init__(self):
        super().__init__("My Computer", (500, 400))
        self.items = ["Documents", "Downloads", "Pictures", "file1.txt", "file2.doc"]
        self.sel = None
        self.row_h = 30

    def draw(self, surf):
        super().draw(surf)
        cm = pygame.Rect(self.x+5, self.y+self.title_bar_height+5, self.width-10, self.height-self.title_bar_height-10)
        pygame.draw.rect(surf, BLACK, cm)
        y = self.y + self.title_bar_height + 10
        for i, it in enumerate(self.items):
            rect = pygame.Rect(self.x+10, y, self.width-20, self.row_h)
            color = WHITE if i != self.sel else BLUE
            surf.blit(font_mid.render(it, True, color), (self.x+15, y+5))
            y += self.row_h

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            y = self.y + self.title_bar_height + 10
            for i in range(len(self.items)):
                rect = pygame.Rect(self.x+10, y, self.width-20, self.row_h)
                if rect.collidepoint(mx, my):
                    self.sel = i
                y += self.row_h

# Start menu
class StartMenu:
    def __init__(self):
        self.width = 200
        self.height = 270
        self.x = 0
        self.y = HEIGHT - self.height - 40
        self.visible = False
        self.options = ["Calculator", "Browser", "Snake Game", "Terminal", "My Computer", "Logout"]

    def draw(self, surf):
        if not self.visible: return
        pygame.draw.rect(surf, DARKGRAY, (self.x, self.y, self.width, self.height))
        for i, opt in enumerate(self.options):
            rect = pygame.Rect(self.x+10, self.y+10+i*40, self.width-20, 35)
            pygame.draw.rect(surf, GRAY, rect)
            surf.blit(font_mid.render(opt, True, BLACK), (rect.x+10, rect.y+5))

    def handle_event(self, event):
        if not self.visible or event.type != pygame.MOUSEBUTTONDOWN:
            return
        mx, my = event.pos
        if self.x <= mx <= self.x+self.width and self.y <= my <= self.y+self.height:
            idx = (my - self.y - 10) // 40
            if 0 <= idx < len(self.options):
                self.select(self.options[idx])

    def select(self, opt):
        global running
        if opt == "Calculator":
            open_windows.append(Calculator())
        elif opt == "Browser":
            webbrowser.open("https://www.google.com")
        elif opt == "Snake Game":
            open_windows.append(SnakeGame())
        elif opt == "Terminal":
            open_windows.append(Terminal())
        elif opt == "My Computer":
            open_windows.append(ThisPC())
        elif opt == "Logout":
            running = False
        self.visible = False

start_menu = StartMenu()

def draw_taskbar():
    pygame.draw.rect(screen, DARKGRAY, (0, HEIGHT-40, WIDTH, 40))
    start_rect = pygame.Rect(0, HEIGHT-40, 80, 40)
    pygame.draw.rect(screen, BLUE if start_menu.visible else GRAY, start_rect)
    screen.blit(font_mid.render("Start", True, WHITE), (10, HEIGHT-30))
    now = datetime.now().strftime("%H:%M:%S")
    screen.blit(font_mid.render(now, True, WHITE), (WIDTH-100, HEIGHT-30))
    wifi = pygame.Rect(WIDTH-140, HEIGHT-35, 30, 30)
    pygame.draw.rect(screen, GREEN, wifi)
    screen.blit(font_small.render("WiFi", True, BLACK), (WIDTH-138, HEIGHT-25))
    screen.blit(font_mid.render(f"Lang: {lang}", True, WHITE), (WIDTH-220, HEIGHT-30))

def login_screen():
    inp = ""
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    inp = inp[:-1]
                elif e.key == pygame.K_RETURN:
                    if inp == PASSWORD:
                        return
                    inp = ""
                elif e.unicode.isprintable():
                    inp += e.unicode

        screen.blit(background, (0, 0))
        prompt = font_big.render("Enter Password:", True, WHITE)
        screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2 - 60))
        stars = "*" * len(inp)
        ps = font_big.render(stars, True, WHITE)
        screen.blit(ps, ((WIDTH-ps.get_width())//2, HEIGHT//2))
        pygame.display.flip()
        clock.tick(FPS)

def main():
    global running, lang
    running = True
    login_screen()

    while running:
        screen.blit(background, (0, 0))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            if e.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if (mods & pygame.KMOD_SHIFT) and (mods & pygame.KMOD_ALT):
                    lang = "EN" if lang == "FA" else "FA"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                for icon in icons_info:
                    if icon["rect"].collidepoint(mx, my):
                        name = icon["name"]
                        if name == "Calculator": open_windows.append(Calculator())
                        elif name == "My Computer": open_windows.append(ThisPC())
                        elif name == "Browser": webbrowser.open("https://www.google.com")
                        elif name == "Games": open_windows.append(SnakeGame())
                if 0 <= mx <= 80 and HEIGHT-40 <= my <= HEIGHT:
                    start_menu.visible = not start_menu.visible
                else:
                    if start_menu.visible:
                        start_menu.visible = False

            for win in open_windows: win.handle_event(e)
            start_menu.handle_event(e)

        open_windows[:] = [w for w in open_windows if not w.closed]

        for icon in icons_info:
            if icon["image"]: screen.blit(icon["image"], icon["pos"])
            txt = font_small.render(icon["name"], True, WHITE)
            screen.blit(txt, (icon["pos"][0], icon["pos"][1] + 66))

        for w in open_windows:
            w.draw(screen)
            if hasattr(w, "update"): w.update()

        draw_taskbar()
        start_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
