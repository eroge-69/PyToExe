import pygame
import asyncio
import platform
import os

# Ініціалізація Pygame
pygame.init()

# Константи
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
CAMERA_WIDTH, CAMERA_HEIGHT = 400, 300  # Менший огляд камери
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -15
PLAYER_SPEED = 5
DIALOG_WIDTH, DIALOG_HEIGHT = 600, 250
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 60  # Більші та комфортніші кнопки

# Налаштування екрану
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Помойка 3")
clock = pygame.time.Clock()

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Створення фону неба (градієнт)
sky = pygame.Surface((WINDOW_WIDTH * 2, WINDOW_HEIGHT))
for y in range(WINDOW_HEIGHT):
    color = (
        int(135 + (70 - 135) * (y / WINDOW_HEIGHT)),
        int(206 + (130 - 206) * (y / WINDOW_HEIGHT)),
        int(235 + (180 - 235) * (y / WINDOW_HEIGHT))
    )
    pygame.draw.line(sky, color, (0, y), (WINDOW_WIDTH * 2, y))

# Завантаження фонового зображення для меню
try:
    background = pygame.image.load("https://5ka-cdn.x5static.net/_next/static/old_img/about/store.jpg")
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
except Exception as e:
    print(f"Помилка завантаження фонового зображення: {e}")
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background.fill((100, 100, 100))  # Запасний сірий фон

# Базовий шлях до папки Pomoyka3
BASE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "Pomoyka3", "Sprites")

# Спрайт гравця
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            sprite_path = os.path.join(BASE_PATH, "Hero1.png")
            print(f"Спроба завантаження Hero1.png з: {sprite_path}")
            self.image = pygame.image.load(sprite_path)
            self.image = pygame.transform.scale(self.image, (50, 50))
        except Exception as e:
            print(f"Помилка завантаження Hero1.png: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 0, 255))  # Синій квадрат як заглушка
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_y = 0
        self.jumping = False

    def update(self, keys, platforms):
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_w] and not self.jumping:
            self.velocity_y = JUMP_FORCE
            self.jumping = True
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH * 2:
            self.rect.right = WINDOW_WIDTH * 2
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity_y = 0
            self.jumping = False

# Спрайт платформи
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        try:
            sprite_path = os.path.join(BASE_PATH, "Ground.png")
            print(f"Спроба завантаження Ground.png з: {sprite_path}")
            self.image = pygame.image.load(sprite_path)
            self.image = pygame.transform.scale(self.image, (width, height))
        except Exception as e:
            print(f"Помилка завантаження Ground.png: {e}")
            self.image = pygame.Surface((width, height))
            self.image.fill((0, 255, 0))  # Зелений прямокутник як заглушка
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Декоративне дерево (без колізії)
class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            sprite_path = os.path.join(BASE_PATH, "Tree.png")
            print(f"Спроба завантаження Tree.png з: {sprite_path}")
            self.image = pygame.image.load(sprite_path)
            self.image = pygame.transform.scale(self.image, (50, 100))  # Розмір дерева
        except Exception as e:
            print(f"Помилка завантаження Tree.png: {e}")
            self.image = pygame.Surface((50, 100))
            self.image.fill((139, 69, 19))  # Коричневий прямокутник як заглушка
        self.rect = self.image.get_rect()
        self.rect.bottom = y  # Дерево врівень із платформою

# NPC (Man)
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            sprite_path = os.path.join(BASE_PATH, "Man.png")
            print(f"Спроба завантаження Man.png з: {sprite_path}")
            self.image = pygame.image.load(sprite_path)
            self.image = pygame.transform.scale(self.image, (50, 50))
        except Exception as e:
            print(f"Помилка завантаження Man.png: {e}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 0, 128))  # Темно-синій квадрат як заглушка
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Камера
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        if hasattr(entity, 'rect'):
            return entity.rect.move(-self.camera.x, -self.camera.y)
        return entity.move(-self.camera.x, -self.camera.y)

    def update(self, target):
        x = -target.rect.centerx + WINDOW_WIDTH // 2
        y = -target.rect.centery + WINDOW_HEIGHT // 2
        x = min(0, x)
        x = max(-(self.width - WINDOW_WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - WINDOW_HEIGHT), y)
        self.camera = pygame.Rect(-x, -y, WINDOW_WIDTH, WINDOW_HEIGHT)

# Стан гри
class Game:
    def __init__(self):
        self.state = "menu"
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.npc = None
        self.player = None
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 30)
        self.camera = Camera(WINDOW_WIDTH * 2, WINDOW_HEIGHT)
        self.dialog = None
        self.dialog_state = 0

    def draw_menu(self):
        screen.blit(background, (0, 0))
        title = self.font.render("Помойка 3", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        play_button = self.button_font.render("Играть", True, WHITE)
        exit_button = self.button_font.render("Уйти!", True, WHITE)
        play_rect = play_button.get_rect(center=(WINDOW_WIDTH // 2, 300))
        exit_rect = exit_button.get_rect(center=(WINDOW_WIDTH // 2, 400))
        pygame.draw.rect(screen, BLACK, play_rect.inflate(20, 20))
        pygame.draw.rect(screen, BLACK, exit_rect.inflate(20, 20))
        screen.blit(play_button, play_rect)
        screen.blit(exit_button, exit_rect)
        return play_rect, exit_rect

    def start_game(self):
        self.state = "game"
        self.player = Player(50, WINDOW_HEIGHT - 100)
        self.all_sprites.add(self.player)
        # Тільки одна платформа внизу
        platform = Platform(0, WINDOW_HEIGHT - 50, WINDOW_WIDTH * 2, 50)
        self.platforms.add(platform)
        self.all_sprites.add(platform)
        # Один дерево врівень із платформою
        tree = Tree(300, WINDOW_HEIGHT - 50)
        self.decorations.add(tree)
        self.all_sprites.add(tree)
        # NPC біля Shop
        self.npc = NPC(600, WINDOW_HEIGHT - 100)
        self.all_sprites.add(self.npc)

    def draw_dialog(self):
        dialog_box = pygame.Surface((DIALOG_WIDTH, DIALOG_HEIGHT))
        dialog_box.fill((200, 200, 200))
        pygame.draw.rect(dialog_box, BLACK, (0, 0, DIALOG_WIDTH, DIALOG_HEIGHT), 2)
        if self.dialog_state == 1:
            npc_text = self.font.render("Эй девка. Шо ты тут робиш?", True, BLACK)
            dialog_box.blit(npc_text, (10, 10))
            screen.blit(pygame.transform.scale(self.npc.image, (50, 50)), (10, DIALOG_HEIGHT + 10))
            # Кнопки відповідей
            button1 = pygame.Rect(DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 70, BUTTON_WIDTH, BUTTON_HEIGHT)
            button2 = pygame.Rect(DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 140, BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(dialog_box, (0, 128, 0), button1)
            pygame.draw.rect(dialog_box, (0, 128, 0), button2)
            dialog_box.blit(self.button_font.render("1. Гуляю", True, WHITE), (button1.x + 20, button1.y + 10))
            dialog_box.blit(self.button_font.render("2. Ты мне нравишься", True, WHITE), (button2.x + 20, button2.y + 10))
            screen.blit(pygame.transform.scale(self.player.image, (50, 50)), (DIALOG_WIDTH - 60, DIALOG_HEIGHT + 10))
        elif self.dialog_state == 2:
            npc_text = self.font.render("Так получай нааааааа!", True, BLACK)
            dialog_box.blit(npc_text, (10, 10))
            screen.blit(pygame.transform.scale(self.npc.image, (50, 50)), (10, DIALOG_HEIGHT + 10))
        elif self.dialog_state == 3:
            npc_text = self.font.render("Что правда?", True, BLACK)
            dialog_box.blit(npc_text, (10, 10))
            screen.blit(pygame.transform.scale(self.npc.image, (50, 50)), (10, DIALOG_HEIGHT + 10))
            # Кнопка відповіді
            button1 = pygame.Rect(DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 70, BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(dialog_box, (0, 128, 0), button1)
            dialog_box.blit(self.button_font.render("1. Да", True, WHITE), (button1.x + 20, button1.y + 10))
            screen.blit(pygame.transform.scale(self.player.image, (50, 50)), (DIALOG_WIDTH - 60, DIALOG_HEIGHT + 10))
        elif self.dialog_state == 4:
            npc_text = self.font.render("Ну пашли за мной!", True, BLACK)
            dialog_box.blit(npc_text, (10, 10))
            screen.blit(pygame.transform.scale(self.npc.image, (50, 50)), (10, DIALOG_HEIGHT + 10))

        screen.blit(dialog_box, ((WINDOW_WIDTH - DIALOG_WIDTH) // 2, 50))

    async def main(self):
        game = self
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and game.state == "menu":
                    pos = event.pos
                    play_rect, exit_rect = game.draw_menu()
                    if play_rect.collidepoint(pos):
                        game.start_game()
                    if exit_rect.collidepoint(pos):
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN and game.state == "game" and game.dialog is not None:
                    pos = event.pos
                    dialog_offset_x = (WINDOW_WIDTH - DIALOG_WIDTH) // 2
                    if game.dialog_state == 1:
                        button1 = pygame.Rect(dialog_offset_x + DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 70, BUTTON_WIDTH, BUTTON_HEIGHT)
                        button2 = pygame.Rect(dialog_offset_x + DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 140, BUTTON_WIDTH, BUTTON_HEIGHT)
                        if button1.collidepoint(pos):
                            game.dialog_state = 2  # Гуляю
                        elif button2.collidepoint(pos):
                            game.dialog_state = 3  # Ты мне нравишься
                    elif game.dialog_state == 3:
                        button1 = pygame.Rect(dialog_offset_x + DIALOG_WIDTH // 2 - BUTTON_WIDTH // 2, 70, BUTTON_WIDTH, BUTTON_HEIGHT)
                        if button1.collidepoint(pos):
                            game.dialog_state = 4  # Да

            keys = pygame.key.get_pressed()

            if game.state == "menu":
                screen.blit(background, (0, 0))
                game.draw_menu()
            elif game.state == "game":
                game.camera.update(game.player)
                screen.blit(sky, game.camera.apply(pygame.Rect(0, 0, WINDOW_WIDTH * 2, WINDOW_HEIGHT)))
                game.player.update(keys, game.platforms)
                for sprite in game.all_sprites:
                    screen.blit(sprite.image, game.camera.apply(sprite))

                # Перевірка діалогу
                if (not game.dialog and
                    game.player.rect.colliderect(game.npc.rect) and
                    abs(game.player.rect.centerx - game.npc.rect.centerx) < 50):
                    game.dialog = True
                    game.dialog_state = 1
                if game.dialog:
                    game.draw_dialog()
                    if game.dialog_state == 2:  # Перехід на другий рівень
                        game.state = "next_level"
                    elif game.dialog_state == 4:  # Перехід до секретної локації
                        game.state = "secret_location"

            pygame.display.flip()
            clock.tick(FPS)
            await asyncio.sleep(1.0 / FPS)

        pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(Game().main())
else:
    if __name__ == "__main__":
        asyncio.run(Game().main())