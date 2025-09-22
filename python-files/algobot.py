import pygame
import sys
import random
from collections import deque

pygame.init()

# Başlangıç ekran boyutu
WIDTH, HEIGHT = 600, 400
INFO_WIDTH = 300
win = pygame.display.set_mode((WIDTH+INFO_WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("10 Seviyeli Kodlama Oyunu")

# Renkler
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (150,150,150)
BLUE = (0,0,255)
RED = (255,0,0)
LIGHT_GRAY = (200,200,200)
GREEN = (0,255,0)
DARK_GRAY = (100,100,100)
YELLOW = (255,255,0)
CYAN = (0,200,255)

grid_size = 20
step_height = 20
steps_per_column = 15
column_spacing = 15
column_width = 80

# 10 Seviyeli yapı
levels = []
for i in range(10):
    robot_pos = (random.randint(0,19), random.randint(0,19))
    hedef_pos = (random.randint(0,19), random.randint(0,19))
    obstacles = [(random.randint(0,19), random.randint(0,19)) for _ in range(5+i*3)]
    obstacles = [o for o in obstacles if o != robot_pos and o != hedef_pos]
    levels.append((robot_pos, hedef_pos, obstacles))

current_level = 0
robot_pos = list(levels[current_level][0])
hedef_pos = list(levels[current_level][1])
obstacles = levels[current_level][2]

font = pygame.font.SysFont(None, 20)
user_moves = []

# Buton dikdörtgenleri
up_rect = pygame.Rect(WIDTH+20,50,60,40)
down_rect = pygame.Rect(WIDTH+20,150,60,40)
left_rect = pygame.Rect(WIDTH+10,100,60,40)  # Sol
right_rect = pygame.Rect(WIDTH+10+60+15,100,60,40)  # Sağ
reset_rect = pygame.Rect(WIDTH+20,300,80,40)
popup_button1 = pygame.Rect(0,0,100,40)
popup_button2 = pygame.Rect(0,0,100,40)

moves_area_y = 50
show_popup = False
popup_message = ""
popup_mode = ""  # "retry_next" veya "completed"
warning_msg = ""  # Oyun alanı dışı uyarısı
warning_timer = 0

# Minimum adım hesaplama (BFS)
def min_steps(start, end, obs):
    visited = set()
    q = deque()
    q.append((start, 0))
    visited.add(start)
    while q:
        (x,y), steps = q.popleft()
        if (x,y)==end:
            return steps
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<20 and 0<=ny<20 and (nx,ny) not in obs and (nx,ny) not in visited:
                visited.add((nx,ny))
                q.append(((nx,ny), steps+1))
    return float('inf')

optimal_steps = min_steps(tuple(robot_pos), tuple(hedef_pos), obstacles)

# Çizim fonksiyonları
def draw_grid():
    for x in range(0, WIDTH, grid_size):
        for y in range(0, HEIGHT, grid_size):
            rect = pygame.Rect(x,y,grid_size,grid_size)
            pygame.draw.rect(win, BLACK, rect,1)
    for obs in obstacles:
        pygame.draw.rect(win, GRAY, (obs[0]*grid_size, obs[1]*grid_size, grid_size, grid_size))

def draw_robot(color=BLUE):
    pygame.draw.rect(win, color, (robot_pos[0]*grid_size, robot_pos[1]*grid_size, grid_size, grid_size))

def draw_hedef():
    pygame.draw.rect(win, RED, (hedef_pos[0]*grid_size, hedef_pos[1]*grid_size, grid_size, grid_size))

def draw_button(rect, text, base_color=WHITE, text_color=BLACK):
    pygame.draw.rect(win, DARK_GRAY, rect)
    inner_rect = rect.inflate(-4,-4)
    pygame.draw.rect(win, base_color, inner_rect)
    text_surf = font.render(text, True, text_color)
    win.blit(text_surf, (inner_rect.x + (inner_rect.width-text_surf.get_width())//2,
                         inner_rect.y + (inner_rect.height-text_surf.get_height())//2))

def draw_text_lines(text, font, color, rect, surface):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < rect.width - 20:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    y = rect.y + 20
    for line in lines:
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (rect.x + 10, y))
        y += font.get_height() + 5

# --- Güncellenmiş draw_panel() ---
def draw_panel():
    global INFO_WIDTH
    pygame.draw.rect(win, LIGHT_GRAY, (WIDTH,0,INFO_WIDTH,HEIGHT))
    draw_button(up_rect, "Yukarı", YELLOW)
    draw_button(down_rect, "Aşağı", YELLOW)
    draw_button(left_rect, "Sol", YELLOW)
    draw_button(right_rect, "Sağ", YELLOW)
    draw_button(reset_rect, "Sıfırla", RED)

    # Adım listesi sağ butonun sağından başlıyor
    step_x_offset = right_rect.right
    for idx, move in enumerate(user_moves):
        col = idx // steps_per_column
        row = idx % steps_per_column
        x = step_x_offset + col*(column_width+column_spacing)
        y = moves_area_y + row*step_height
        win.blit(font.render(f"{idx+1}. {move}", True, BLACK), (x,y))

    # Ekran genişlemesini sadece yeni kolon oluştuğunda ve gerektiği kadar yap
    if user_moves:
        last_col = (len(user_moves)-1) // steps_per_column
        needed_width = step_x_offset + (last_col+1)*(column_width+column_spacing) + 20
        if needed_width > WIDTH + INFO_WIDTH:
            INFO_WIDTH = needed_width - WIDTH
            pygame.display.set_mode((WIDTH+INFO_WIDTH, HEIGHT), pygame.RESIZABLE)

    if warning_msg:
        warn_surf = font.render(warning_msg, True, RED)
        win.blit(warn_surf, (WIDTH+20, HEIGHT-50))

# --- Popup ve hareket fonksiyonları (orijinal haliyle) ---
def show_popup_message(msg, mode):
    global popup_button1, popup_button2
    popup_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 75, 300,150)
    pygame.draw.rect(win, WHITE, popup_rect)
    pygame.draw.rect(win, BLACK, popup_rect,3)
    draw_text_lines(msg, font, RED, popup_rect, win)
    if mode=="retry_next":
        popup_button1 = pygame.Rect(popup_rect.x + 30, popup_rect.bottom - 60,100,40)
        popup_button2 = pygame.Rect(popup_rect.x + 170, popup_rect.bottom - 60,100,40)
        draw_button(popup_button1, "Yeniden Dene", CYAN)
        draw_button(popup_button2, "Sonraki Seviye", GREEN)
    else:
        popup_button1 = pygame.Rect(popup_rect.centerx - 50, popup_rect.bottom - 60,100,40)
        draw_button(popup_button1, "Tamam", GREEN)

def move_robot(direction):
    global robot_pos, user_moves, show_popup, popup_message, popup_mode
    global current_level, hedef_pos, obstacles, optimal_steps
    global warning_msg, warning_timer

    new_pos = list(robot_pos)
    out_of_bounds = False

    if direction=="Yukarı":
        if new_pos[1]>0: new_pos[1]-=1
        else: out_of_bounds=True
    elif direction=="Aşağı":
        if new_pos[1]<(HEIGHT//grid_size)-1: new_pos[1]+=1
        else: out_of_bounds=True
    elif direction=="Sol":
        if new_pos[0]>0: new_pos[0]-=1
        else: out_of_bounds=True
    elif direction=="Sağ":
        if new_pos[0]<(WIDTH//grid_size)-1: new_pos[0]+=1
        else: out_of_bounds=True

    if out_of_bounds:
        warning_msg = "Oyun alanı dışına çıkıyorsun!"
        warning_timer = 30
        return

    if tuple(new_pos) in obstacles:
        color = CYAN
    else:
        color = BLUE
        robot_pos[:] = new_pos
        user_moves.append(direction)

    win.fill(WHITE)
    draw_grid()
    draw_robot(color)
    draw_hedef()
    draw_panel()
    pygame.display.update()
    pygame.time.delay(200)

    if robot_pos==hedef_pos:
        if len(user_moves)>optimal_steps:
            show_popup = True
            popup_mode = "retry_next"
            popup_message = f"Tebrikler! Seviye tamamlandı ama bunu {optimal_steps} adımda bitirebilirdiniz. Yeniden denemek ister misiniz?"
        else:
            current_level +=1
            if current_level<10:
                robot_pos[:] = list(levels[current_level][0])
                hedef_pos[:] = list(levels[current_level][1])
                obstacles[:] = levels[current_level][2]
                optimal_steps = min_steps(tuple(robot_pos), tuple(hedef_pos), obstacles)
                user_moves.clear()
            else:
                show_popup = True
                popup_mode = "completed"
                popup_message = "Tüm seviyeler tamamlandı!"

# --- Main loop ---
running = True
while running:
    win.fill(WHITE)
    draw_grid()
    draw_robot()
    draw_hedef()
    draw_panel()
    if show_popup:
        show_popup_message(popup_message, popup_mode)
    pygame.display.update()

    if warning_timer>0:
        warning_timer -= 1
        if warning_timer==0:
            warning_msg = ""

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.MOUSEBUTTONDOWN:
            mx,my = event.pos
            if show_popup:
                if popup_mode=="retry_next":
                    if popup_button1.collidepoint(mx,my):
                        robot_pos[:] = list(levels[current_level][0])
                        user_moves.clear()
                        show_popup=False
                    elif popup_button2.collidepoint(mx,my):
                        current_level +=1
                        if current_level<10:
                            robot_pos[:] = list(levels[current_level][0])
                            hedef_pos[:] = list(levels[current_level][1])
                            obstacles[:] = levels[current_level][2]
                            optimal_steps = min_steps(tuple(robot_pos), tuple(hedef_pos), obstacles)
                            user_moves.clear()
                            show_popup=False
                elif popup_mode=="completed":
                    if popup_button1.collidepoint(mx,my):
                        show_popup=False
            else:
                if up_rect.collidepoint(mx,my):
                    move_robot("Yukarı")
                elif down_rect.collidepoint(mx,my):
                    move_robot("Aşağı")
                elif left_rect.collidepoint(mx,my):
                    move_robot("Sol")
                elif right_rect.collidepoint(mx,my):
                    move_robot("Sağ")
                elif reset_rect.collidepoint(mx,my):
                    user_moves.clear()
                    robot_pos[:] = list(levels[current_level][0])
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                running=False

pygame.quit()
sys.exit()
