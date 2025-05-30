import pygame
import random

# Pygame başlatma
pygame.init()

# Ekran boyutları
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Pencere başlığını ayarlama
pygame.display.set_caption("Tagalın Tuğlaları")

# Renkler
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (153, 101, 21)
RED = (255, 0, 0)

# Saat
clock = pygame.time.Clock()

# Hedef sınıfı (Ördekler)
class Duck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(BROWN)  # Ördek rengi
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, screen_width - 100)
        self.rect.y = random.randint(-150, -50)  # Başlangıçta yukarıda
        self.speed = random.randint(3, 6)  # Hareket hızı

    def update(self):
        self.rect.y += self.speed  # Yukarıdan aşağıya doğru hareket
        if self.rect.y > screen_height:  # Ekranın dışına çıkarsa
            self.rect.y = random.randint(-150, -50)  # Yeniden yukarıdan başlar
            self.rect.x = random.randint(100, screen_width - 100)  # Yeni rastgele x konumu

# Kurşun sınıfı
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10  # Kurşun hızı

    def update(self):
        self.rect.y -= self.speed  # Aşağıdan yukarıya doğru hareket
        if self.rect.y < 0:  # Ekranın dışına çıkarsa
            self.kill()  # Kurşunu yok et

# Başlangıç menüsü
def start_menu():
    font = pygame.font.SysFont('Arial', 48)
    title_text = font.render('Tagalın Tuğlaları', True, (0, 0, 0))
    start_text = font.render('Press Enter to Start', True, (0, 0, 0))

    running = True
    while running:
        screen.fill(WHITE)
        screen.blit(title_text, (screen_width // 4, screen_height // 4))
        screen.blit(start_text, (screen_width // 3, screen_height // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False  # Başlama menüsünden çıkıp oyuna geç

# Çıkış menüsü
def game_over(score):
    font = pygame.font.SysFont('Arial', 48)
    game_over_text = font.render('Game Over', True, (0, 0, 0))
    score_text = font.render(f'Tebrikler, Skorunuz: {score}', True, (0, 0, 0))
    restart_text = font.render('Press R to Restart or Q to Quit', True, (0, 0, 0))

    running = True
    while running:
        screen.fill(WHITE)
        screen.blit(game_over_text, (screen_width // 4, screen_height // 4))
        screen.blit(score_text, (screen_width // 4, screen_height // 2))
        screen.blit(restart_text, (screen_width // 5, screen_height // 1.5))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Yeniden başlat
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

# Oyun döngüsü
def game():
    ducks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    # İlk 5 ördeği oluştur
    for i in range(5):
        duck = Duck()
        ducks.add(duck)
        all_sprites.add(duck)

    score = 0
    lives = 3
    start_ticks = pygame.time.get_ticks()  # Başlangıç zamanını al

    spawn_timer = 0  # Ördeklerin spawn edilme süresi
    spawn_interval = 1000  # Ördeklerin her saniye spawn olması için 1000 ms

    # Oyun döngüsü
    running = True
    game_started = False  # Başlangıçta oyun başlamamış

    while running:
        clock.tick(60)
        screen.fill(WHITE)  # Arka planı beyaz yapıyoruz

        # Başlangıçta oyun başlamadan önce, Enter'a basılmasını bekle
        if not game_started:
            font = pygame.font.SysFont('Arial', 32)
            start_message = font.render('Press Enter to Start', True, (0, 0, 0))
            screen.blit(start_message, (screen_width // 3, screen_height // 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_started = True  # Enter'a basıldığında oyun başlar

        if game_started:
            # Süreyi hesapla (50 saniye)
            elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
            if elapsed_time > 50:  # 50 saniye geçtiğinde oyun sona erer
                running = False

            # Yeni ördekleri spawn etme
            if pygame.time.get_ticks() - spawn_timer > spawn_interval:
                duck = Duck()  # Yeni ördek oluştur
                ducks.add(duck)
                all_sprites.add(duck)
                spawn_timer = pygame.time.get_ticks()  # Son spawn zamanını güncelle

            # Sprite'ların güncellenmesi
            all_sprites.update()

            # Kontroller
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Sol tıklama
                        mouse_pos = pygame.mouse.get_pos()
                        bullet = Bullet(mouse_pos[0], mouse_pos[1])
                        bullets.add(bullet)
                        all_sprites.add(bullet)

            # Çarpışma kontrolü
            for bullet in bullets:
                ducks_hit = pygame.sprite.spritecollide(bullet, ducks, True)  # Kurşun ördeği vurursa
                if ducks_hit:
                    score += 1
                    bullet.kill()  # Kurşun vurduğu ördeği yok eder

            # Ekrana yazılar
            font = pygame.font.SysFont('Arial', 24)
            score_text = font.render(f'Score: {score}', True, (0, 0, 0))
            screen.blit(score_text, (10, 10))

            time_left = 50 - int(elapsed_time)
            time_text = font.render(f'Time: {time_left}', True, (0, 0, 0))
            screen.blit(time_text, (screen_width - 120, 10))

            # Sprite'ları çizme
            all_sprites.draw(screen)
            pygame.display.update()

            # Eğer oyun biterse, Game Over menüsüne geç
            if elapsed_time > 50:
                running = False
                game_over(score)

    pygame.quit()

# Ana oyun döngüsü
start_menu()  # Başlangıç menüsünü göster
game()  # Oyunu başlat
