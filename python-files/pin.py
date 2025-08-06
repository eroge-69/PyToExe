import pygame
import sys

pygame.init()

# Ekran boyutu ve başlık
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("OKSİB - Ping Pong")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("arial", 40)
clock = pygame.time.Clock()

# Küresel değişkenler
paddle_width, paddle_height = 20, 100
ball_radius = 15
speed = 6

# Paddle ve top sınıfı
class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, SCREEN_HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height)
        self.speed = speed

    def move(self, dy):
        if 0 <= self.rect.y + dy <= SCREEN_HEIGHT - paddle_height:
            self.rect.y += dy

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, ball_radius, ball_radius)
        self.dx = speed
        self.dy = speed

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy *= -1

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, self.rect)

# Buton çizimi
def draw_button(text, rect, color=(100, 100, 100)):
    pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, WHITE)
    screen.blit(label, (rect.x + 20, rect.y + 10))

# Menü
def main_menu():
    while True:
        screen.fill(BLACK)
        title = font.render("OKSİB", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - 80, 50))

        btn_single = pygame.Rect(300, 150, 200, 60)
        btn_two = pygame.Rect(300, 240, 200, 60)
        btn_quit = pygame.Rect(300, 330, 200, 60)

        draw_button("Tek Kişilik", btn_single)
        draw_button("İki Kişilik", btn_two)
        draw_button("Çıkış", btn_quit)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_single.collidepoint(event.pos):
                    play_game(single=True)
                elif btn_two.collidepoint(event.pos):
                    play_game(single=False)
                elif btn_quit.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)

# Oyun fonksiyonu
def play_game(single=True):
    paddle1 = Paddle(30)
    paddle2 = Paddle(SCREEN_WIDTH - 50)
    ball = Ball()

    score1 = 0
    score2 = 0

    touch_y = None

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            elif event.type == pygame.MOUSEMOTION:
                touch_y = event.pos[1]

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move(-paddle1.speed)
        if keys[pygame.K_s]:
            paddle1.move(paddle1.speed)

        # Dokunmatik destek (tek paddle için)
        if touch_y is not None:
            if touch_y < paddle1.rect.centery:
                paddle1.move(-paddle1.speed)
            elif touch_y > paddle1.rect.centery:
                paddle1.move(paddle1.speed)

        if not single:
            if keys[pygame.K_UP]:
                paddle2.move(-paddle2.speed)
            if keys[pygame.K_DOWN]:
                paddle2.move(paddle2.speed)
        else:
            if ball.rect.centery < paddle2.rect.centery:
                paddle2.move(-paddle2.speed)
            elif ball.rect.centery > paddle2.rect.centery:
                paddle2.move(paddle2.speed)

        ball.move()

        # Çarpma kontrolü
        if ball.rect.colliderect(paddle1.rect) or ball.rect.colliderect(paddle2.rect):
            ball.dx *= -1

        # Skor kontrol
        if ball.rect.left <= 0:
            score2 += 1
            ball = Ball()
        elif ball.rect.right >= SCREEN_WIDTH:
            score1 += 1
            ball = Ball()

        # Çizim
        paddle1.draw()
        paddle2.draw()
        ball.draw()

        score_text = font.render(f"{score1} : {score2}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 50, 20))

        pygame.display.flip()
        clock.tick(60)

# Başlat
main_menu()
