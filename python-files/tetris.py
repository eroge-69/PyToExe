import pygame
import random
import copy

# ---------------------------
# 초기화 및 설정
# ---------------------------
pygame.init()
pygame.display.set_caption("Modern Tetris")

WIDTH, HEIGHT = 400, 600
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
SIDE_PANEL = 150
FPS = 60

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (50,50,50)
LIGHT_GRAY = (100,100,100)
COLORS = [
    (0, 255, 255), (0,0,255), (255,165,0),
    (255,255,0), (0,255,0), (128,0,128), (255,0,0)
]

LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
DOWN = pygame.K_DOWN
UP = pygame.K_UP
HOLD = pygame.K_c
HARD_DROP = pygame.K_SPACE
RESET = pygame.K_r

SHAPES = {
    'I': [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    'J': [[1,0,0],[1,1,1],[0,0,0]],
    'L': [[0,0,1],[1,1,1],[0,0,0]],
    'O': [[1,1],[1,1]],
    'S': [[0,1,1],[1,1,0],[0,0,0]],
    'T': [[0,1,0],[1,1,1],[0,0,0]],
    'Z': [[1,1,0],[0,1,1],[0,0,0]]
}

WALL_KICKS = [(0,0),(-1,0),(1,0),(0,-1),(0,1)]

# ---------------------------
# 클래스 정의
# ---------------------------
class Piece:
    def __init__(self, shape,color_index):
        self.shape = shape
        self.color_index = color_index
        self.x = GRID_WIDTH//2 - len(shape[0])//2
        self.y = 0

    def rotate(self,grid):
        old_shape = self.shape
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        for dx,dy in WALL_KICKS:
            if not self.check_collision(grid,self.x+dx,self.y+dy):
                self.x += dx
                self.y += dy
                return True
        self.shape = old_shape
        return False

    def check_collision(self,grid,nx,ny):
        for y,row in enumerate(self.shape):
            for x,cell in enumerate(row):
                if cell:
                    gx,gy = nx+x, ny+y
                    if gx<0 or gx>=GRID_WIDTH or gy>=GRID_HEIGHT:
                        return True
                    if gy>=0 and grid[gy][gx]!=-1:
                        return True
        return False

    def hard_drop(self,grid):
        while not self.check_collision(grid,self.x,self.y+1):
            self.y += 1

class Tetris:
    def __init__(self):
        self.grid = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score=0; self.level=1; self.lines_cleared=0; self.combo=-1
        self.current=self._next_piece()
        self.next_queue=[self._next_piece() for _ in range(5)]
        self.hold_piece=None; self.can_hold=True; self.game_over=False
        self.drop_timer=0; self.drop_speed=30
        self.lock_delay=0; self.lock_delay_limit=15
        self.shake_offset=0

    def _next_piece(self):
        if not hasattr(self,'bag') or len(self.bag)==0:
            self.bag=list(SHAPES.keys()); random.shuffle(self.bag)
        key=self.bag.pop()
        shape=copy.deepcopy(SHAPES[key])
        color_index=list(SHAPES.keys()).index(key)
        return Piece(shape,color_index)

    def hold(self):
        if not self.can_hold: return
        self.can_hold=False
        if self.hold_piece:
            self.current,self.hold_piece=self.hold_piece,self.current
            self.current.x = GRID_WIDTH//2 - len(self.current.shape[0])//2
            self.current.y = 0
        else:
            self.hold_piece=self.current
            self.current=self.next_queue.pop(0)
            self.next_queue.append(self._next_piece())

    def lock_piece(self):
        for y,row in enumerate(self.current.shape):
            for x,cell in enumerate(row):
                if cell:
                    gx,gy=self.current.x+x,self.current.y+y
                    if 0<=gy<GRID_HEIGHT:
                        self.grid[gy][gx]=self.current.color_index
                    else:
                        self.game_over=True
        self.clear_lines()
        self.current=self.next_queue.pop(0)
        self.next_queue.append(self._next_piece())
        self.can_hold=True
        self.lock_delay=0
        if self.current.check_collision(self.grid,self.current.x,self.current.y):
            self.game_over=True

    def clear_lines(self):
        lines=[]
        for i,row in enumerate(self.grid):
            if -1 not in row: lines.append(i)
        if lines:
            self.combo+=1
            self.lines_cleared+=len(lines)
            self.score += (100*len(lines)*self.level)*(self.combo+1)
            self.level=1+self.lines_cleared//10
            self.shake_offset=5 if len(lines)==4 else 2
            for i in lines:
                del self.grid[i]; self.grid.insert(0,[-1 for _ in range(GRID_WIDTH)])
        else:
            self.combo=-1

    def soft_drop(self):
        if not self.current.check_collision(self.grid,self.current.x,self.current.y+1):
            self.current.y +=1
        else:
            if self.lock_delay<self.lock_delay_limit: self.lock_delay+=1
            else: self.lock_piece()

    def hard_drop(self):
        self.current.hard_drop(self.grid)
        self.lock_piece()

    def move(self,dx):
        if not self.current.check_collision(self.grid,self.current.x+dx,self.current.y):
            self.current.x += dx
            return True
        return False

    def update(self):
        self.drop_timer+=1
        speed=max(1,self.drop_speed - self.level*2)
        if self.drop_timer>=speed:
            self.soft_drop()
            self.drop_timer=0

# ---------------------------
# 그리기
# ---------------------------
def draw_grid(surface,grid,shake_offset):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect=pygame.Rect(x*CELL_SIZE + shake_offset, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface,GRAY,rect,1)
            if grid[y][x]!=-1:
                pygame.draw.rect(surface,COLORS[grid[y][x]],rect.inflate(-2,-2))

def draw_piece(surface,piece,ghost=False):
    color=COLORS[piece.color_index] if not ghost else LIGHT_GRAY
    for y,row in enumerate(piece.shape):
        for x,cell in enumerate(row):
            if cell:
                rect=pygame.Rect((piece.x+x)*CELL_SIZE,(piece.y+y)*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                pygame.draw.rect(surface,color,rect.inflate(-2,-2))

def draw_ui(surface,tetris):
    pygame.draw.rect(surface,BLACK,(GRID_WIDTH*CELL_SIZE+10,0,SIDE_PANEL,HEIGHT))
    font=pygame.font.SysFont(None,24)
    label=font.render("NEXT",True,WHITE)
    surface.blit(label,(GRID_WIDTH*CELL_SIZE+40,20))
    for i,piece in enumerate(tetris.next_queue[:3]):
        for y,row in enumerate(piece.shape):
            for x,cell in enumerate(row):
                if cell:
                    rect=pygame.Rect(GRID_WIDTH*CELL_SIZE+40 + x*CELL_SIZE,50+i*100+y*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                    pygame.draw.rect(surface,COLORS[piece.color_index],rect.inflate(-2,-2))
    label=font.render("HOLD",True,WHITE)
    surface.blit(label,(GRID_WIDTH*CELL_SIZE+40,350))
    if tetris.hold_piece:
        piece=tetris.hold_piece
        for y,row in enumerate(piece.shape):
            for x,cell in enumerate(row):
                if cell:
                    rect=pygame.Rect(GRID_WIDTH*CELL_SIZE+40 + x*CELL_SIZE,380+y*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                    pygame.draw.rect(surface,COLORS[piece.color_index],rect.inflate(-2,-2))
    label=font.render(f"SCORE: {tetris.score}",True,WHITE)
    surface.blit(label,(GRID_WIDTH*CELL_SIZE+20,500))
    label=font.render(f"LEVEL: {tetris.level}",True,WHITE)
    surface.blit(label,(GRID_WIDTH*CELL_SIZE+20,530))

def draw_ghost(surface,piece,grid):
    ghost=copy.deepcopy(piece)
    ghost.hard_drop(grid)
    draw_piece(surface,ghost,ghost=True)

# ---------------------------
# 메인 루프 (개선된 옆 이동 구조)
# ---------------------------
def main():
    screen=pygame.display.set_mode((WIDTH+SIDE_PANEL,HEIGHT))
    clock=pygame.time.Clock()
    tetris=Tetris()

    # 횡 이동 관련 변수
    move_direction = 0      # -1=왼쪽, 1=오른쪽, 0=정지
    repeat_timer = 0        # 반복 이동 타이머
    initial_repeat_delay = 5  # 키 누른 직후 반복 이동 시작 전 대기
    repeat_speed = 1.5        # 반복 이동 프레임 간격
    move_active = False
    soft_drop_pressed=False

    running=True
    while running:
        screen.fill(BLACK)
        shake=tetris.shake_offset
        tetris.shake_offset=0

        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==LEFT:
                    move_direction=-1; move_active=True; repeat_timer=0
                elif event.key==RIGHT:
                    move_direction=1; move_active=True; repeat_timer=0
                elif event.key==DOWN: soft_drop_pressed=True
                elif event.key==UP: tetris.current.rotate(tetris.grid)
                elif event.key==HOLD: tetris.hold()
                elif event.key==HARD_DROP: tetris.hard_drop()
                elif event.key==RESET: tetris=Tetris()
            elif event.type==pygame.KEYUP:
                if (event.key==LEFT and move_direction==-1) or (event.key==RIGHT and move_direction==1):
                    move_direction=0; move_active=False; repeat_timer=0
                elif event.key==DOWN: soft_drop_pressed=False

        # ---------- 횡 이동 처리 ----------
        if move_direction !=0:
            if move_active:
                tetris.move(move_direction)  # 즉시 1칸 이동
                move_active=False
                repeat_timer=0
            else:
                repeat_timer +=1
                if repeat_timer >= initial_repeat_delay and (repeat_timer - initial_repeat_delay) % repeat_speed==0:
                    tetris.move(move_direction)
        else:
            repeat_timer=0
            move_active=False

        if soft_drop_pressed: tetris.soft_drop()
        tetris.update()
        draw_grid(screen,tetris.grid,shake)
        draw_ghost(screen,tetris.current,tetris.grid)
        draw_piece(screen,tetris.current)
        draw_ui(screen,tetris)

        if tetris.game_over:
            font=pygame.font.SysFont(None,48)
            label=font.render("GAME OVER",True,(255,0,0))
            screen.blit(label,(50,HEIGHT//2-24))

        pygame.display.flip()
        clock.tick(FPS)

if __name__=="__main__":
    main()
