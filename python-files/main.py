import pygame
import sys
import tkinter as tk
from tkinter import filedialog
import datetime

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Happy Birthday Game")
clock = pygame.time.Clock()
font = pygame.font.Font("zpix.ttf", 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 192, 203)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (160, 32, 240)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

preview_image = None
state = "password_input"
password = ""

picture_boxes = [
    pygame.Rect(50, 100, 140, 140),
    pygame.Rect(610, 100, 140, 140),
    pygame.Rect(50, 400, 140, 140),
    pygame.Rect(610, 400, 140, 140)
]
pictures = [None] * 4

cake_img = pygame.image.load("BirthdayCake.png").convert_alpha()
cake_img = pygame.transform.scale(cake_img, (300, 300))
cake_img.set_alpha(240)

bg2_img = pygame.image.load("BirthdayBgMC2.jpg").convert()
bg2_img = pygame.transform.scale(bg2_img, (800, 600))
bg2_img.set_alpha(150)

pygame.mixer.init()
pygame.mixer.music.load("Taylor Swift - Love Story.mp3")
pygame.mixer.music.set_volume(0.5)

confession_text = ""
answer_lines = ["", "", "", ""]
selected_image = None
volume_slider_x = 560
voice_timeline_x = 470

mic_icon = pygame.image.load("mic.png").convert_alpha()
mic_icon = pygame.transform.scale(mic_icon, (50, 50))

birthday_icon = pygame.transform.scale(pygame.image.load("cake_small.png").convert_alpha(), (30, 30))

voice_playing = False
voice_paused = False
voice_start_time = 0
voice_pause_time = 0
voice_length = 1
voice_circle_pos = voice_timeline_x + 100
try:
    voice = pygame.mixer.Sound("voice_clip.mp3")
    voice_length = voice.get_length()
except Exception as e:
    print("语音文件加载失败：", e)
    voice = None

def draw_password_input():
    screen.fill(PINK)
    prompt = font.render("Type in your password:", True, BLACK)
    screen.blit(prompt, (200, 200))
    pygame.draw.rect(screen, WHITE, (200, 260, 400, 50))
    pygame.draw.rect(screen, BLACK, (200, 260, 400, 50), 2)
    pw_surface = font.render(password, True, BLACK)
    screen.blit(pw_surface, (210, 270))
    enter_btn = font.render("Enter", True, BLACK)
    screen.blit(enter_btn, (660, 550))

def check_password_and_enter():
    global state
    if password.strip() == "0307":
        state = "cake_screen"
        pygame.mixer.music.play(-1)
    else:
        print(f"Wrong password! You typed: '{password}'")

def draw_cake_screen():
    screen.blit(bg2_img, (0, 0))
    screen.blit(cake_img, (240, 20))
    label = font.render("Add your favorite pictures:", True, BLACK)
    screen.blit(label, (130, 300))
    for i, box in enumerate(picture_boxes):
        pygame.draw.rect(screen, BLACK, box, 2)
        if pictures[i]:
            img_rect = pictures[i].get_rect(center=box.center)
            screen.blit(pictures[i], img_rect.topleft)
    enter_btn = font.render("Enter", True, BLACK)
    screen.blit(enter_btn, (660, 550))

def draw_preview():
    screen.fill(BLACK)
    if preview_image:
        large_img = pygame.transform.smoothscale(preview_image, (600, 600))
        screen.blit(large_img, (100, 0))
    back_btn = font.render("Back", True, WHITE)
    screen.blit(back_btn, (650, 520))

def draw_voice_timeline():
    global voice_circle_pos
    pygame.draw.rect(screen, BLACK, (voice_timeline_x, 470, 200, 5))
    if voice_playing and not voice_paused:
        elapsed = pygame.time.get_ticks() / 1000 - voice_start_time
        percent = min(elapsed / voice_length, 1.0)
        voice_circle_pos = voice_timeline_x + int(200 * percent)
    pygame.draw.circle(screen, BLACK, (voice_circle_pos, 472), 8)

def draw_calendar():
    base_x, base_y = 451, 121
    cell_w, cell_h = 34.9, 37
    font_small = pygame.font.Font("zpix.ttf", 20)
    for i in range(1, 32):
        col = (i - 1) % 8
        row = (i - 1) // 8
        rect = pygame.Rect(base_x + col * cell_w, base_y + row * cell_h, cell_w, cell_h)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        num = font_small.render(str(i), True, BLACK)
        screen.blit(num, (rect.x + 10, rect.y + 8))
        if i == 3:
            screen.blit(birthday_icon, (rect.x + 6, rect.y + 4))

def draw_edit_page():
    global volume_slider_x
    screen.fill(PINK)
    title = font.render("纪念空间", True, BLACK)
    screen.blit(title, (310, 20))

    pygame.draw.rect(screen, WHITE, (50, 70, 300, 120))
    pygame.draw.rect(screen, BLACK, (50, 70, 300, 120), 2)
    confession = font.render("表白墙", True, RED)
    screen.blit(confession, (60, 75))

    pygame.draw.rect(screen, WHITE, (50, 220, 300, 200))
    pygame.draw.rect(screen, BLACK, (50, 220, 300, 200), 2)
    answer_label = font.render("回答时光", True, BLUE)
    screen.blit(answer_label, (60, 225))

    pygame.draw.rect(screen, WHITE, (450, 70, 280, 200))
    pygame.draw.rect(screen, BLACK, (450, 70, 280, 200), 2)
    calendar_label = font.render("生活日历", True, GREEN)
    screen.blit(calendar_label, (460, 75))
    draw_calendar()

    pygame.draw.rect(screen, WHITE, (450, 290, 280, 130))
    pygame.draw.rect(screen, BLACK, (450, 290, 280, 130), 2)
    love_label = font.render("甜蜜时光", True, ORANGE)
    screen.blit(love_label, (460, 295))

    together_day = datetime.date(2024, 12, 23)
    today = datetime.date.today()
    days = (today - together_day).days
    days_text = font.render(f"在一起第 {days} 天", True, PINK)
    screen.blit(days_text, (460, 340))

    draw_voice_timeline()
    screen.blit(mic_icon, (410, 450))
    music_label = font.render("语音", True, BLACK)
    screen.blit(music_label, (680, 452))

    enter_btn = font.render("Back", True, BLACK)
    screen.blit(enter_btn, (650, 520))

def choose_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    root.destroy()
    return file_path

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "password_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    check_password_and_enter()
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                elif len(password) < 4:
                    password += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(650, 520, 100, 50).collidepoint(event.pos):
                    check_password_and_enter()

        elif state == "cake_screen":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, box in enumerate(picture_boxes):
                    if box.collidepoint(event.pos):
                        if pictures[i]:
                            preview_image = pictures[i]
                            state = "preview"
                            break
                        else:
                            path = choose_image()
                            if path:
                                try:
                                    image = pygame.image.load(path).convert_alpha()
                                    img_w, img_h = image.get_size()
                                    scale = min(140 / img_w, 140 / img_h)
                                    new_size = (int(img_w * scale), int(img_h * scale))
                                    image = pygame.transform.smoothscale(image, new_size)
                                    image.set_alpha(230)
                                    pictures[i] = image
                                except:
                                    print("Failed to load image.")
                            break
                if pygame.Rect(650, 520, 100, 50).collidepoint(event.pos):
                    state = "edit_page"

        elif state == "preview":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(650, 520, 100, 50).collidepoint(event.pos):
                    state = "cake_screen"

        elif state == "edit_page":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(410, 450, 50, 50).collidepoint(event.pos):
                    if voice:
                        if not voice_playing:
                            pygame.mixer.music.pause()
                            voice.play()
                            voice_playing = True
                            voice_paused = False
                            voice_start_time = pygame.time.get_ticks() / 1000
                        elif not voice_paused:
                            voice.stop()
                            voice_paused = True
                            voice_playing = False
                            pygame.mixer.music.unpause()
                elif pygame.Rect(650, 520, 100, 50).collidepoint(event.pos):
                    state = "cake_screen"

    if voice_playing and not voice_paused and (pygame.time.get_ticks() / 1000 - voice_start_time >= voice_length):
        voice_playing = False
        pygame.mixer.music.unpause()

    if state == "password_input":
        draw_password_input()
    elif state == "cake_screen":
        draw_cake_screen()
    elif state == "preview":
        draw_preview()
    elif state == "edit_page":
        draw_edit_page()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
