import pygame, sys, random, json, time, os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Noobengineer Studio - Dünyanın En Kolay Oyunu")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# --- Dosya işlemleri ---
SAVE_FILE = "scores.json"
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        settings = json.load(f)
else:
    settings = {
        "username": "",
        "language": None,
        "theme": "dark",
        "sensitivity": "normal",
        "achievements_enabled": True,
        "achievements_unlocked": [],
        "highscore": 0
    }

# Başarım mesajları
ACHIEVEMENTS = {
    "tr": {
        50: "İyi refleks!",
        100: "Harikasın!",
        500: "Reflekslerin çok iyi!",
        1000: "YOK ARTIK!!!",
        5000: "Sen insansın??",
        10000: "Seni hayatsız herif! En iyisisin!"
    },
    "en": {
        50: "Good reflex!",
        100: "Amazing!",
        500: "Great reflexes!",
        1000: "NO WAY!!!",
        5000: "Are you even human?",
        10000: "You no-lifer! You're the best!"
    }
}

# --- Yardımcı ---
def save_settings():
    with open(SAVE_FILE, "w") as f:
        json.dump(settings, f)

def draw_text(text, size, x, y, color):
    f = pygame.font.SysFont(None, size)
    img = f.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def draw_button(text, x, y, w, h, color, text_color):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    txt = font.render(text, True, text_color)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)
    return rect

# --- Dil Seçme ---
def language_screen():
    if settings["language"]:
        return settings["language"]
    while True:
        screen.fill((30,30,30))
        draw_text("Dil Seçiniz / Choose Language", 50, WIDTH//2, 150, (255,255,255))
        tr_btn = draw_button("Türkçe", WIDTH//2-100, 250, 200, 60, (0,200,0), (255,255,255))
        en_btn = draw_button("English", WIDTH//2-100, 350, 200, 60, (0,0,200), (255,255,255))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tr_btn.collidepoint(event.pos):
                    settings["language"] = "tr"
                    save_settings()
                    return "tr"
                if en_btn.collidepoint(event.pos):
                    settings["language"] = "en"
                    save_settings()
                    return "en"

# --- İsim Seçme ---
def name_screen(lang):
    if settings["username"]:
        return settings["username"]
    username = ""
    active = True
    while active:
        screen.fill((40,40,40))
        draw_text("İsminizi girin:" if lang=="tr" else "Enter your name:", 40, WIDTH//2, 150, (255,255,255))
        pygame.draw.rect(screen, (255,255,255), (WIDTH//2-150, 250, 300, 50), 2)
        txt_surface = font.render(username, True, (255,255,255))
        screen.blit(txt_surface, (WIDTH//2-140, 260))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN and username.strip()!="":
                    settings["username"] = username.strip()
                    save_settings()
                    return username.strip()
                elif event.key==pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username)<15:
                        username += event.unicode

# --- Ana Menü ---
def main_menu(lang):
    while True:
        theme_colors = ((50,50,50),(255,255,255)) if settings["theme"]=="dark" else ((200,200,200),(0,0,0))
        screen.fill(theme_colors[0])
        draw_text("Dünyanın En Kolay Oyunu" if lang=="tr" else "World's Easiest Game", 50, WIDTH//2, 100, theme_colors[1])
        start_btn = draw_button("Oyuna Başla" if lang=="tr" else "Start Game", WIDTH//2-120, 200, 240, 60, (100,100,250), (255,255,255))
        settings_btn = draw_button("Ayarlar" if lang=="tr" else "Settings", WIDTH//2-120, 280, 240, 60, (100,250,100), (255,255,255))
        quit_btn = draw_button("Çıkış" if lang=="tr" else "Quit", WIDTH//2-120, 360, 240, 60, (250,100,100), (255,255,255))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos): game_loop(lang)
                if settings_btn.collidepoint(event.pos): settings_screen(lang)
                if quit_btn.collidepoint(event.pos): confirm_quit(lang)

# --- Ayarlar ---
def settings_screen(lang):
    while True:
        screen.fill((40,40,70) if settings["theme"]=="dark" else (200,200,200))
        draw_text("Ayarlar" if lang=="tr" else "Settings", 50, WIDTH//2, 50, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        # Tema
        dark_btn = draw_button("Karanlık / Dark", 100, 120, 200, 50, (50,50,50), (255,255,255))
        light_btn = draw_button("Aydınlık / Light", 500, 120, 200, 50, (200,200,200), (0,0,0))
        # Hassasiyet
        normal_btn = draw_button("Normal", 100, 200, 200, 50, (100,100,100), (255,255,255))
        fast_btn = draw_button("Hızlı / Fast", 500, 200, 200, 50, (100,250,100), (0,0,0))
        # Başarımlar aç/kapa
        ach_on_btn = draw_button("Başarımlar Açık", 100, 280, 200, 50, (0,200,0), (255,255,255))
        ach_off_btn = draw_button("Başarımlar Kapalı", 500, 280, 200, 50, (200,0,0), (255,255,255))
        # Kazanılan başarımlar
        show_ach_btn = draw_button("Kazanılan Başarımlar", 100, 360, 600, 50, (255,255,0), (0,0,0))
        # Kontroller
        show_ctrl_btn = draw_button("Kontroller", 100, 440, 600, 50, (0,200,200), (0,0,0))
        # Geri
        back_btn = draw_button("Geri / Back", 300, 520, 200, 50, (200,200,0), (0,0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if dark_btn.collidepoint(event.pos):
                    settings["theme"]="dark"; save_settings()
                if light_btn.collidepoint(event.pos):
                    settings["theme"]="light"; save_settings()
                if normal_btn.collidepoint(event.pos):
                    settings["sensitivity"]="normal"; save_settings()
                if fast_btn.collidepoint(event.pos):
                    settings["sensitivity"]="fast"; save_settings()
                if ach_on_btn.collidepoint(event.pos):
                    settings["achievements_enabled"]=True; save_settings()
                if ach_off_btn.collidepoint(event.pos):
                    settings["achievements_enabled"]=False; save_settings()
                if show_ach_btn.collidepoint(event.pos):
                    show_achievements(lang)
                if show_ctrl_btn.collidepoint(event.pos):
                    show_controls(lang)
                if back_btn.collidepoint(event.pos):
                    return

def show_achievements(lang):
    viewing = True
    while viewing:
        screen.fill((30,30,30) if settings["theme"]=="dark" else (220,220,220))
        draw_text("Kazanılan Başarımlar" if lang=="tr" else "Achievements Unlocked", 50, WIDTH//2, 50, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        y_pos = 150
        if settings["achievements_unlocked"]:
            for s in sorted(settings["achievements_unlocked"]):
                draw_text(f"{s}: {ACHIEVEMENTS[lang][s]}", 35, WIDTH//2, y_pos, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
                y_pos += 50
        else:
            draw_text("Hiç kazanılmadı." if lang=="tr" else "None yet.", 35, WIDTH//2, y_pos, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        back_btn = draw_button("Geri / Back", 300, HEIGHT-70, 200, 50, (200,200,0), (0,0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos): viewing=False

def show_controls(lang):
    viewing = True
    while viewing:
        screen.fill((30,30,30) if settings["theme"]=="dark" else (220,220,220))
        draw_text("Kontroller / Controls", 50, WIDTH//2, 50, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        draw_text("Ok Tuşları veya Fare ile sepeti hareket ettirin." if lang=="tr" else "Move basket with arrow keys or mouse.", 35, WIDTH//2, 200, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        back_btn = draw_button("Geri / Back", 300, HEIGHT-70, 200, 50, (200,200,0), (0,0,0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos): viewing=False

# --- Çıkış ---
def confirm_quit(lang):
    while True:
        screen.fill((30,30,30))
        draw_text("Çıkmak istediğinize emin misiniz?" if lang=="tr" else "Are you sure to quit?", 40, WIDTH//2, 200, (255,255,255))
        yes_btn = draw_button("Evet" if lang=="tr" else "Yes", WIDTH//2-120, 300, 100, 60, (0,200,0), (255,255,255))
        no_btn = draw_button("Hayır" if lang=="tr" else "No", WIDTH//2+20, 300, 100, 60, (200,0,0), (255,255,255))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if yes_btn.collidepoint(event.pos): pygame.quit(); sys.exit()
                if no_btn.collidepoint(event.pos): return

# --- Kaybettiniz ---
def game_over_screen(lang, score):
    while True:
        screen.fill((60,0,0))
        draw_text("Kaybettiniz!" if lang=="tr" else "You Lost!", 60, WIDTH//2, 150, (255,255,255))
        draw_text(f"Puan: {score}" if lang=="tr" else f"Score: {score}", 40, WIDTH//2, 220, (255,255,0))
        retry_btn = draw_button("Tekrar Dene" if lang=="tr" else "Retry", WIDTH//2-120, 300, 240, 60, (100,200,250), (0,0,0))
        menu_btn = draw_button("Ana Menü" if lang=="tr" else "Main Menu", WIDTH//2-120, 380, 240, 60, (200,200,0), (0,0,0))
        quit_btn = draw_button("Çıkış" if lang=="tr" else "Quit", WIDTH//2-120, 460, 240, 60, (250,100,100), (255,255,255))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos): return "retry"
                if menu_btn.collidepoint(event.pos): return "menu"
                if quit_btn.collidepoint(event.pos): confirm_quit(lang)

# --- Oyun Döngüsü ---
def game_loop(lang):
    basket_x, basket_y = WIDTH//2, HEIGHT-50
    apple_x, apple_y = random.randint(20,WIDTH-20), 0
    apple_speed = 25
    score, lives = 0, 3
    mouse_held = False
    last_achievement = None
    achievement_time = 0

    while True:
        screen.fill((20,20,20) if settings["theme"]=="dark" else (220,220,220))
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1: mouse_held=True
            if event.type==pygame.MOUSEBUTTONUP and event.button==1: mouse_held=False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: basket_x -= 10
        if keys[pygame.K_RIGHT]: basket_x += 10
        if mouse_held:
            mx,_ = pygame.mouse.get_pos()
            sens = 0.2 if settings["sensitivity"]=="normal" else 0.5
            basket_x += (mx-basket_x)*sens

        # Elma düşüşü
        apple_y += apple_speed
        if basket_x-50<apple_x<basket_x+50 and basket_y-20<apple_y<basket_y+20:
            score+=1
            apple_x, apple_y = random.randint(20,WIDTH-20), 0

            if score in ACHIEVEMENTS[lang] and settings["achievements_enabled"]:
                last_achievement = ACHIEVEMENTS[lang][score]
                achievement_time = time.time()
                if score not in settings["achievements_unlocked"]:
                    settings["achievements_unlocked"].append(score)
                    save_settings()
            if score>settings["highscore"]:
                settings["highscore"]=score
                save_settings()

        if apple_y>HEIGHT:
            lives-=1
            apple_x, apple_y = random.randint(20,WIDTH-20), 0
            if lives==0:
                result = game_over_screen(lang, score)
                if result=="retry": return game_loop(lang)
                elif result=="menu": return

        pygame.draw.rect(screen, (200,200,200) if settings["theme"]=="dark" else (50,50,50), (basket_x-50,basket_y,100,20))
        pygame.draw.circle(screen, (255,0,0), (apple_x,apple_y), 15)
        draw_text(f"Puan: {score}" if lang=="tr" else f"Score: {score}", 30, WIDTH//2, 30, (255,255,255) if settings["theme"]=="dark" else (0,0,0))
        draw_text(f"Can: {lives}" if lang=="tr" else f"Lives: {lives}", 30, WIDTH//2, 60, (255,255,255) if settings["theme"]=="dark" else (0,0,0))

        if last_achievement and time.time() - achievement_time < 3:
            rect = pygame.Rect(WIDTH-310, 20, 290, 60)
            pygame.draw.rect(screen, (50,50,50), rect, border_radius=10)
            pygame.draw.rect(screen, (255,215,0), rect, 3, border_radius=10)
            txt = font.render(last_achievement, True, (255,255,255))
            screen.blit(txt, (rect.x+10, rect.y+15))

        pygame.display.flip()
        clock.tick(60)

# --- Çalıştır ---
lang = language_screen()
name_screen(lang)
main_menu(lang)


