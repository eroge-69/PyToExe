import pygame
import sys
import math
import random
import time
pygame.init()
WIDTH,HEIGHT=1400,800
CELL_SIZE=25
LINE_COLOR=(200,200,200)
BG_COLOR=(240,240,240)
X_COLOR=(255,0,0)
O_COLOR=(0,0,255)
BLACK=(0,0,0)
GRID_WIDTH=200
GRID_HEIGHT=100
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Caro by chivy")
font=pygame.font.SysFont(None,24)
board={}  
overlay_board={}  
offset_x=0
offset_y=0
dragging=False
last_mouse_pos=(0,0)
player=1
winner=0
vs_ai=False
win_time=None
countdown=None
def get_board_pos(mx,my):
    bx=math.floor((mx - offset_x) / CELL_SIZE)
    by=math.floor((my - offset_y) / CELL_SIZE)
    return bx,by

def draw_grid():
    for i in range(GRID_WIDTH + 1):
        x=offset_x + i * CELL_SIZE
        if 0 <= x <= WIDTH:
            pygame.draw.line(screen,LINE_COLOR,(x,0),(x,HEIGHT))
    for j in range(GRID_HEIGHT + 1):
        y=offset_y + j * CELL_SIZE
        if 0 <= y <= HEIGHT:
            pygame.draw.line(screen,LINE_COLOR,(0,y),(WIDTH,y))

def draw_marks():
    for (x,y),value in overlay_board.items():
        draw_mark(x,y,value,faded=True)
    for (x,y),value in board.items():
        draw_mark(x,y,value,faded=False)

def draw_mark(x,y,value,faded=False):
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        return
    px=x * CELL_SIZE + offset_x
    py=y * CELL_SIZE + offset_y
    if not (0 <= px + CELL_SIZE and px <= WIDTH and 0 <= py + CELL_SIZE and py <= HEIGHT):
        return
    center=(px + CELL_SIZE // 2,py + CELL_SIZE // 2)
    d=CELL_SIZE // 3
    color=X_COLOR if value == 1 else O_COLOR
    alpha=100 if faded else 255
    s=pygame.Surface((CELL_SIZE,CELL_SIZE),pygame.SRCALPHA)
    if value == 1:
        pygame.draw.line(s,color + (alpha,),(d,d),(CELL_SIZE - d,CELL_SIZE - d),5)
        pygame.draw.line(s,color + (alpha,),(d,CELL_SIZE - d),(CELL_SIZE - d,d),5)
    elif value == 2:
        pygame.draw.circle(s,color + (alpha,),(CELL_SIZE // 2,CELL_SIZE // 2),d,5)
    screen.blit(s,(px,py))

def draw_hover():
    mx,my=pygame.mouse.get_pos()
    bx,by=get_board_pos(mx,my)
    text=font.render(f'({bx},{by})',True,BLACK)
    screen.blit(text,(10,10))

def draw_timer():
    if countdown is not None:
        seconds_left=max(0,10 - int(time.time() - countdown))
        text=font.render(f'Reset sau: {seconds_left}s',True,(255,0,0))
        screen.blit(text,(WIDTH - 150,10))

def check_winner(last_move,pl,length=5):
    if last_move is None:
        return False
    x,y=last_move
    directions=[(1,0),(0,1),(1,1),(1,-1)]
    for dx,dy in directions:
        count=1
        for step in range(1,length):
            if board.get((x + dx * step,y + dy * step)) == pl:
                count += 1
            else:
                break
        for step in range(1,length):
            if board.get((x - dx * step,y - dy * step)) == pl:
                count += 1
            else:
                break
        if count >= length:
            return True
    return False

def get_empty_neighbors(dist=1):
    s=set()
    for (x,y) in board:
        for dx in range(-dist,dist + 1):
            for dy in range(-dist,dist + 1):
                if dx == 0 and dy == 0:
                    continue
                pos=(x + dx,y + dy)
                if 0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT:
                    if pos not in board:
                        s.add(pos)
    return list(s)

def ai_move():
    for move in get_empty_neighbors():
        board[move]=2
        if check_winner(move,2):
            del board[move]
            return move
        del board[move]
    for move in get_empty_neighbors():
        board[move]=1
        if check_winner(move,1):
            del board[move]
            return move
        del board[move]
    return random.choice(get_empty_neighbors()) if get_empty_neighbors() else None

def menu():
    global vs_ai
    screen.fill((255,255,255))
    t1=font.render("1. Chơi với người",True,BLACK)
    t2=font.render("2. Chơi với AI",True,BLACK)
    screen.blit(t1,(WIDTH//2 - 50,HEIGHT//2 - 30))
    screen.blit(t2,(WIDTH//2 - 50,HEIGHT//2))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    vs_ai=False
                    return
                elif event.key == pygame.K_2:
                    vs_ai=True
                    return

def reset_game():
    global board,overlay_board,offset_x,offset_y,dragging,last_mouse_pos,player,winner,last_move,win_time,countdown
    overlay_board={}  # Xóa hết overlay
    board={}  # Xóa hết dấu cũ
    offset_x=offset_y=0
    dragging=False
    last_mouse_pos=(0,0)
    player=1
    winner=0
    last_move=None
    win_time=None
    countdown=None

# ========== MAIN GAME ==========
menu()
running=True
last_move=None
while running:
    screen.fill(BG_COLOR)
    draw_grid()
    draw_marks()
    draw_hover()
    draw_timer()
    if winner:
        msg=font.render(f"Người {'X' if winner==1 else 'O'} thắng!",True,(0,128,0))
        screen.blit(msg,(WIDTH//2 - 60,10))
        if win_time is None:
            win_time=time.time()
            countdown=win_time
        elif time.time() - win_time > 5:
            reset_game()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

        elif event.type == pygame.MOUSEBUTTONDOWN and winner == 0:
            if event.button == 1:
                mx,my=pygame.mouse.get_pos()
                bx,by=get_board_pos(mx,my)
                if 0 <= bx < GRID_WIDTH and 0 <= by < GRID_HEIGHT and (bx,by) not in board:
                    board[(bx,by)]=player
                    last_move=(bx,by)
                    if check_winner(last_move,player):
                        winner=player
                    else:
                        player=2 if player == 1 else 1
                        if vs_ai and player == 2:
                            ai_pos=ai_move()
                            if ai_pos:
                                board[ai_pos]=2
                                if check_winner(ai_pos,2):
                                    winner=2
                                else:
                                    player=1

            elif event.button == 2:
                dragging=True
                last_mouse_pos=pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                dragging=False

        elif event.type == pygame.MOUSEMOTION and dragging:
            mx,my=pygame.mouse.get_pos()
            dx=mx - last_mouse_pos[0]
            dy=my - last_mouse_pos[1]
            offset_x += dx
            offset_y += dy
            last_mouse_pos=(mx,my)

pygame.quit()
