Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> """
... Office Sneak — symulator zręczności (Pygame)
... - Sterowanie: Spacja (minimalizuj/odminimalizuj "przeglądarkę")
... - Przed rozpoczęciem wpisz login (max 8 znaków) — wynik będzie zapisany w ranking.txt
... - Celem: zdobywać punkty (oszukać kierownika). Gra kończy się, gdy:
...     * kierownik złapie Cię (przeglądarka widoczna przy kontroli) -> przegrana
...     * lub osiągniesz 11 punktów -> zwycięstwo
... - Przy zwykłym pracowniku: jeśli zminimalizujesz -> przegrana (pomyłka)
... - Ranking: zapisuje "LOGIN SCORE TIMESTAMP" w ranking.txt
... 
... Autor: wygenerowane przez ChatGPT — dostosuj grafiki/sounds wedle uznania.
... """
... import pygame, random, time, sys
... from pygame import gfxdraw
... from array import array
... import math
... from datetime import datetime
... 
... pygame.init()
... WIDTH, HEIGHT = 1000, 600
... screen = pygame.display.set_mode((WIDTH, HEIGHT))
... pygame.display.set_caption("Office Sneak")
... clock = pygame.time.Clock()
... FONT = pygame.font.SysFont("arial", 20)
... BIG = pygame.font.SysFont("arial", 36, bold=True)
... 
... # ---------- Settings / tuning ----------
... WIN_SCORE = 11
... RANKING_FILE = "ranking.txt"
... MAX_LOGIN = 8
... 
... # Base timings (seconds) — will shrink with score (difficulty increase)
... BASE_MIN_INTERVAL = 2.0   # minimal wait until next person
... BASE_MAX_INTERVAL = 6.0   # maximal wait
... BASE_ENTER_TIME = 1.6     # time it takes for person to walk to center and check
... MIN_ENTER_TIME = 0.6      # lower bound as difficulty increases
REACT_DECAY = 0.03        # how much enter_time reduces per point
# chance ratio: manager vs employee
MANAGER_PROB = 0.6  # 60% manager visits, 40% normal employee

# Colors
BG = (230, 230, 240)
DESK = (200, 170, 120)
LAPTOP = (30, 30, 40)
SCREEN_BG = (240, 250, 255)
DOOR = (120, 80, 50)
MAN_COLOR = (40, 40, 40)
EMP_COLOR = (70, 120, 180)
TEXT_COLOR = (20, 20, 20)
ALERT_COLOR = (200, 40, 40)

# Sounds: we'll try to generate short beep sounds (may not work on all systems)
def make_tone(freq=880, duration=0.12, volume=0.2, sample_rate=44100):
    # generate signed 16-bit little-endian waveform
    n_samples = int(sample_rate * duration)
    arr = array('h')
    amplitude = int(32767 * volume)
    for i in range(n_samples):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * freq * t))
        arr.append(sample)
    try:
        sound = pygame.mixer.Sound(buffer=arr.tobytes())
        return sound
    except Exception:
        return None

SND_SUCCESS = make_tone(1200, 0.09, 0.15)
SND_FAIL = make_tone(220, 0.15, 0.2)
SND_WARN = make_tone(800, 0.08, 0.12)

# ---------- Utility ----------
def clamp(x, a, b): return max(a, min(b, x))

def draw_text(surf, text, pos, font=FONT, color=TEXT_COLOR):
    surf.blit(font.render(text, True, color), pos)

def save_score(login, score):
    try:
        with open(RANKING_FILE, "a", encoding="utf-8") as f:
            f.write(f"{login} {score} {datetime.now().isoformat()}\n")
    except Exception as e:
        print("Błąd zapisu rankingu:", e)

def load_top(n=5):
    try:
        with open(RANKING_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return []
    entries = []
    for l in lines:
        parts = l.split()
        if len(parts) >= 3:
            login = parts[0]
            score = int(parts[1])
            ts = " ".join(parts[2:])
            entries.append((login, score, ts))
    entries.sort(key=lambda x: x[1], reverse=True)
    return entries[:n]

# ---------- Game objects & state ----------
class Person:
    def __init__(self, side, kind, enter_time):
        # side: "left" or "right"
        self.side = side
        self.kind = kind  # "manager" or "employee"
        # position: start off-screen near door, target is center in front of desk
        self.enter_time = enter_time
        self.timer = 0.0
        # compute walk path coords
        if self.side == "left":
            self.start_x = -80
            self.end_x = WIDTH * 0.22
        else:
            self.start_x = WIDTH + 80
            self.end_x = WIDTH * 0.78
        self.y = HEIGHT * 0.32
        self.x = self.start_x
        self.finished = False  # set True when they complete check and leave

    def update(self, dt):
        self.timer += dt
        t = clamp(self.timer / self.enter_time, 0.0, 1.0)
        # ease in-out
        t_ease = (math.cos((1 - t) * math.pi) + 1) / 2
        self.x = self.start_x + (self.end_x - self.start_x) * t_ease
        if self.timer >= self.enter_time:
            self.finished = True

    def draw(self, surf):
        # draw door shadow
        door_w, door_h = 100, 180
        if self.side == "left":
            dx = WIDTH * 0.08
        else:
            dx = WIDTH * 0.92 - door_w
        # person body
        body_w, body_h = 40, 60
        body_x = int(self.x - body_w / 2)
        body_y = int(self.y - body_h)
        if self.kind == "manager":
            # suit + mustache + stern face (prywaciaż)
            pygame.draw.rect(surf, MAN_COLOR, (body_x, body_y, body_w, body_h), border_radius=8)
            # head
            pygame.draw.circle(surf, (240, 200, 180), (int(self.x), body_y - 18), 16)
            # mustache
            pygame.draw.rect(surf, (40, 20, 20), (int(self.x)-10, body_y-15, 20, 6))
            # tie
            pygame.draw.polygon(surf, (180, 20, 20), [(int(self.x), body_y+10),(int(self.x)-7, body_y+30),(int(self.x)+7, body_y+30)])
        else:
            # casual employee: colored shirt, friendly face
            pygame.draw.rect(surf, EMP_COLOR, (body_x, body_y, body_w, body_h), border_radius=8)
            pygame.draw.circle(surf, (240, 200, 180), (int(self.x), body_y - 18), 14)
            # smile
            pygame.draw.arc(surf, (0,0,0), (int(self.x)-8, body_y-22, 16, 12), math.pi, 2*math.pi, 2)

# ---------- Screens: login, instructions ----------
def input_login_screen():
    login = ""
    active = True
    while active:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if len(login.strip())>0:
                        return login[:MAX_LOGIN]
                elif ev.key == pygame.K_BACKSPACE:
                    login = login[:-1]
                else:
                    ch = ev.unicode
                    if ch.isprintable() and len(login) < MAX_LOGIN:
                        login += ch
        screen.fill(BG)
        draw_text(screen, "Wpisz login (max 8 znaków) i naciśnij Enter:", (WIDTH*0.2, HEIGHT*0.35), BIG)
        pygame.draw.rect(screen, (255,255,255), (WIDTH*0.35, HEIGHT*0.45, WIDTH*0.3, 46), border_radius=6)
        draw_text(screen, login, (WIDTH*0.36, HEIGHT*0.46), BIG)
        draw_text(screen, "Sterowanie: Spacja — minimalizuj/odminimalizuj przeglądarkę", (WIDTH*0.2, HEIGHT*0.55))
        pygame.display.flip()
        clock.tick(30)

def show_end_screen(login, score, won):
    # save score already done by caller
    t = "WYGRAŁEŚ!" if won else "PRZYŁAPANY!"
    sub = f"Twój wynik: {score}  —  Zapisano do {RANKING_FILE}"
    wait = True
    while wait:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN or ev.key == pygame.K_ESCAPE:
                    return
        screen.fill(BG)
        draw_text(screen, t, (WIDTH*0.4, HEIGHT*0.3), BIG, ALERT_COLOR if not won else (40,160,40))
        draw_text(screen, sub, (WIDTH*0.26, HEIGHT*0.38), FONT)
        draw_text(screen, "Naciśnij Enter aby wrócić do menu.", (WIDTH*0.34, HEIGHT*0.5), FONT)
        # show top ranking
        draw_text(screen, "Top 5:", (WIDTH*0.1, HEIGHT*0.6), BIG)
        top = load_top(5)
        y = HEIGHT*0.65
        for i, e in enumerate(top):
            draw_text(screen, f"{i+1}. {e[0]} - {e[1]}", (WIDTH*0.1, y))
            y += 28
        pygame.display.flip()
        clock.tick(30)

# ---------- Main game ----------
def game_loop(login):
    # state
    score = 0
    browser_visible = True
    last_minimize_time = None
    # schedule first visit
    def schedule_next(score):
        # difficulty scales with score
        min_i = max(0.6, BASE_MIN_INTERVAL - score*0.03)
        max_i = max(1.2, BASE_MAX_INTERVAL - score*0.05)
        return random.uniform(min_i, max_i)
    time_to_next = schedule_next(0)
    person = None
    running = True
    paused = False
    # UI layout helpers
    desk_rect = pygame.Rect(WIDTH*0.2, HEIGHT*0.5, WIDTH*0.6, HEIGHT*0.35)
    laptop_rect = pygame.Rect(WIDTH*0.4, HEIGHT*0.55, WIDTH*0.2, HEIGHT*0.12)
    browser_rect = pygame.Rect(laptop_rect.x+12, laptop_rect.y+12, laptop_rect.w-24, laptop_rect.h-36)
    # Main timers
    total_time = 0.0
    last_time = time.time()
    # feedback flash
    flash = 0.0
    # scoring sound
    while running:
        now = time.time()
        dt = now - last_time
        dt = clamp(dt, 0, 0.05)
        last_time = now
        total_time += dt
        time_to_next -= dt
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.key == pygame.K_SPACE:
                    # Player pressed space -> minimize / restore
                    # If employee present (incoming or finished) -> lose
                    if person and person.kind == "employee":
                        # immediate fail
                        if SND_FAIL: SND_FAIL.play()
                        save_score(login, score)
                        show_end_screen(login, score, won=False)
                        return
                    # Toggle
                    browser_visible = not browser_visible
                    last_minimize_time = total_time
                    # If manager present and we minimize before check finishes -> success
                    if person and person.kind == "manager" and not person.finished:
                        # success: manager leaves and score increments
                        score += 1
                        flash = 0.5
                        if SND_SUCCESS: SND_SUCCESS.play()
                        # small animation: person jumps back out (we mark finished and set timer ahead)
                        person.timer = person.enter_time + 0.01
                        # schedule next
                        time_to_next = schedule_next(score)
                        # check win
                        if score >= WIN_SCORE:
                            save_score(login, score)
                            show_end_screen(login, score, won=True)
                            return

        # spawn person?
        if person is None and time_to_next <= 0:
            side = random.choice(["left", "right"])
            kind = "manager" if random.random() < MANAGER_PROB else "employee"
            # enter_time depends on difficulty (shrinks with score)
            enter_time = max(MIN_ENTER_TIME, BASE_ENTER_TIME - score * REACT_DECAY)
            person = Person(side, kind, enter_time)
        # update person
        if person:
            person.update(dt)
            # If person finished walking (i.e., at check moment), evaluate detection
            if person.finished:
                # manager checks: if browser visible => caught
                if person.kind == "manager":
                    if browser_visible:
                        # fail
                        if SND_FAIL: SND_FAIL.play()
                        save_score(login, score)
                        show_end_screen(login, score, won=False)
                        return
                    else:
                        # if browser hidden when check occurs, manager leaves silently, score already handled by minimize event.
                        # but if player was preemptively minimized (minimized before manager arrived), we should award +1 only if player minimized after manager started approaching?
                        # following chosen rule: minimize anytime during approach or before check counts if it happens after person spawned.
                        # However we already give point on pressing space while manager inbound.
                        pass
                else:
                    # employee leaves — nothing happens (but if player minimized while employee inbound we have already lost)
                    pass
                # schedule next
                person = None
                time_to_next = schedule_next(score)

        # draw background office
        screen.fill(BG)
        # walls
        pygame.draw.rect(screen, (215,215,225), (0,0,WIDTH, int(HEIGHT*0.45)))
        # floor
        pygame.draw.rect(screen, (200,200,190), (0, int(HEIGHT*0.45), WIDTH, int(HEIGHT*0.55)))
        # doors (left/right)
        door_w, door_h = 100, 190
        # left door
        lx = WIDTH*0.04
        ly = HEIGHT*0.45 - 10
        pygame.draw.rect(screen, DOOR, (lx, ly, door_w, door_h), border_radius=6)
        # right door
        rx = WIDTH*0.96 - door_w
        ry = ly
        pygame.draw.rect(screen, DOOR, (rx, ry, door_w, door_h), border_radius=6)
        # desk
        pygame.draw.rect(screen, DESK, desk_rect, border_radius=8)
        # coffee mug
        pygame.draw.circle(screen, (230,230,230), (int(desk_rect.x + 50), int(desk_rect.y + 30)), 14)
        pygame.draw.rect(screen, (120,80,40), (desk_rect.x + 60, desk_rect.y + 18, 6, 12))
        # laptop (closed base)
        pygame.draw.rect(screen, LAPTOP, laptop_rect, border_radius=6)
        # screen inner
        if browser_visible:
            pygame.draw.rect(screen, SCREEN_BG, browser_rect, border_radius=4)
            draw_text(screen, "Przeglądarka — WIDOCZNA (naciśnij Spację, żeby zminimalizować)", (browser_rect.x + 8, browser_rect.y + 6), FONT)
            # show some "tabs" decorative
            for i in range(3):
                pygame.draw.rect(screen, (200,220,230), (browser_rect.x + 8 + i*70, browser_rect.y + 36, 60, 12), border_radius=3)
        else:
            # show minimized bar
            mb = pygame.Rect(browser_rect.x, browser_rect.y + browser_rect.h - 16, browser_rect.w, 16)
            pygame.draw.rect(screen, (70,70,90), mb, border_radius=4)
            draw_text(screen, "[ZMINIMALIZOWANE] — odnowienie: Spacja", (mb.x+6, mb.y-2), FONT, (240,240,240))
        # draw person (if exists)
        if person:
            person.draw(screen)
            # show who it is when close (for debug/clarity small label)
            if person.timer > 0.05:
                lbl = "Kierownik" if person.kind=="manager" else "Pracownik"
                draw_text(screen, lbl, (person.x-30, person.y-95))
        # top UI: score, difficulty tier, time to next (hidden)
        draw_text(screen, f"Login: {login}", (20, 8))
        draw_text(screen, f"Punkty: {score}", (20, 34))
        # difficulty tier derived from score:
        if score <= 11:
            tier = "Łatwy"
        elif score <= 50:
            tier = "Średni"
        else:
            tier = "Trudny"
        draw_text(screen, f"Poziom: {tier}", (20, 60))
        # show small tip
        draw_text(screen, "Uwaga: jeśli zminimalizujesz przy pracowniku -> PRZEGRYWASZ", (WIDTH*0.25, 8))
        # flash on success
        if flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((40,200,40, int(120 * flash)))
            screen.blit(overlay, (0,0))
            flash -= dt
        # Show top ranking in corner
        top = load_top(3)
        draw_text(screen, "Ranking (top 3):", (WIDTH-240, 8))
        y = 34
        for i,e in enumerate(top):
            draw_text(screen, f"{i+1}. {e[0]} {e[1]}", (WIDTH-240, y))
            y += 22
        pygame.display.flip()
        clock.tick(60)

# ---------- Main flow ----------
def main():
    login = input_login_screen().strip()
    if not login:
        login = "ANON"
    # main menu
    while True:
        # menu
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BG)
        draw_text(screen, f"Witaj, {login}!", (WIDTH*0.06, HEIGHT*0.12), BIG)
        draw_text(screen, "Cel: minimalizuj przeglądarkę gdy wchodzi kierownik.", (WIDTH*0.06, HEIGHT*0.2))
        draw_text(screen, "Punkt zdobywasz jeśli zminimalizujesz zanim kierownik sprawdzi.", (WIDTH*0.06, HEIGHT*0.24))
        draw_text(screen, f"Gra kończy się przy przyłapaniu lub po zdobyciu {WIN_SCORE} pkt.", (WIDTH*0.06, HEIGHT*0.28))
        draw_text(screen, "Sterowanie: Spacja = minimalizuj, Esc = powrót/menu", (WIDTH*0.06, HEIGHT*0.32))
        draw_text(screen, "Naciśnij Enter, żeby zacząć, lub Esc żeby wyjść.", (WIDTH*0.06, HEIGHT*0.36))
        top = load_top(5)
        draw_text(screen, "Top 5:", (WIDTH*0.65, HEIGHT*0.12), BIG)
        y = HEIGHT*0.16
        for i,e in enumerate(top):
            draw_text(screen, f"{i+1}. {e[0]} - {e[1]}", (WIDTH*0.65, y))
            y += 28
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    game_loop(login)
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        clock.tick(30)

if __name__ == "__main__":
    main()
