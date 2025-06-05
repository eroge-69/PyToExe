import pygame
import random

# تهيئة pygame
pygame.init()

# أبعاد الشاشة
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("لعبة الفضاء")

# الألوان
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# سرعة الكويكبات
asteroid_speed = 5

# الكائنات (المركبة الفضائية والكويكبات)
ship_width = 50
ship_height = 50
ship_x = screen_width // 2 - ship_width // 2
ship_y = screen_height - ship_height - 10

# تحديد خصائص المركبة الفضائية
ship = pygame.Rect(ship_x, ship_y, ship_width, ship_height)

# الكويكبات
asteroids = []

# إعدادات اللعبة
clock = pygame.time.Clock()
score = 0

# خط اللعبة
font = pygame.font.SysFont(None, 36)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def generate_asteroid():
    asteroid_width = 50
    asteroid_height = 50
    x_pos = random.randint(0, screen_width - asteroid_width)
    y_pos = -asteroid_height
    return pygame.Rect(x_pos, y_pos, asteroid_width, asteroid_height)

def game_over():
    draw_text("Game Over", font, RED, screen, screen_width // 2, screen_height // 2)
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()

# الحلقة الرئيسية للعبة
running = True
while running:
    screen.fill(WHITE)
    
    # معالجة الأحداث
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # تحريك المركبة الفضائية
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and ship.x > 0:
        ship.x -= 5
    if keys[pygame.K_RIGHT] and ship.x < screen_width - ship_width:
        ship.x += 5

    # إضافة كويكبات جديدة
    if random.randint(1, 100) <= 2:  # نسبة ظهور الكويكب
        asteroids.append(generate_asteroid())

    # تحريك الكويكبات
    for asteroid in asteroids[:]:
        asteroid.y += asteroid_speed
        if asteroid.y > screen_height:
            asteroids.remove(asteroid)
            score += 1
        
        # التحقق من التصادم
        if ship.colliderect(asteroid):
            game_over()
            running = False
    
    # رسم المركبة الفضائية والكويكبات
    pygame.draw.rect(screen, BLACK, ship)
    for asteroid in asteroids:
        pygame.draw.rect(screen, RED, asteroid)
    
    # عرض النقاط
    draw_text(f"Score: {score}", font, BLACK, screen, 70, 30)

    # تحديث الشاشة
    pygame.display.update()
    clock.tick(60)

pygame.quit()




