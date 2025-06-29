import pygame
import random
import math
import requests
import sys

# Yapay zeka cevabı alma fonksiyonu
def get_ai_response_local(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False}
        )
        return response.json()["response"].strip()
    except Exception as e:
        return f"Bağlantı hatası: {str(e)}"

# Ayarlar
WIDTH, HEIGHT = 900, 600
FPS = 30

ROBOT_COUNT = 3
ROBOT_RADIUS = 20
INTERACTION_DISTANCE = 80
QUESTIONS_PER_CONVO = 3
WALK_SPEED = 1.5

START_HOUR = 9
END_HOUR = 22
SECONDS_PER_MINUTE = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ROBOT_COLOR = (100, 200, 255)
BALLOON_COLOR = (255, 255, 224)
HOUSE_COLOR = (170, 120, 70)
STREET_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (135, 206, 235)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kasaba Robot Simülasyonu")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont(None, 20)
font_large = pygame.font.SysFont(None, 36)

house_positions = [
    (100, 100),
    (700, 100),
    (400, 450)
]

class Robot:
    def __init__(self, name, home_pos):
        self.name = name
        self.home_x, self.home_y = home_pos
        self.x = self.home_x
        self.y = self.home_y
        self.speed = WALK_SPEED
        self.direction = 0
        self.current_message = ""
        self.talking_with = None
        self.ready_to_respond = True
        self.question_count = 0
        self.in_conversation = False
        self.state = "at_home"  # at_home, walking_out, walking, walking_home

        self.choose_random_direction()

    def choose_random_direction(self):
        self.direction = random.uniform(0, 2 * math.pi)

    def move(self):
        if self.in_conversation:
            return  # Sohbet sırasında hareket etme

        if self.state == "walking_out":
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
            if math.hypot(self.x - self.home_x, self.y - self.home_y) > 100:
                self.state = "walking"

        elif self.state == "walking":
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
            if self.x < ROBOT_RADIUS or self.x > WIDTH - ROBOT_RADIUS:
                self.direction = math.pi - self.direction
            if self.y < ROBOT_RADIUS or self.y > HEIGHT - ROBOT_RADIUS:
                self.direction = -self.direction

        elif self.state == "walking_home":
            dx = self.home_x - self.x
            dy = self.home_y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.x, self.y = self.home_x, self.home_y
                self.state = "at_home"
            else:
                self.direction = math.atan2(dy, dx)
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, ROBOT_COLOR, (int(self.x), int(self.y)), ROBOT_RADIUS)
        name_text = font_small.render(self.name, True, BLACK)
        surface.blit(name_text, (self.x - ROBOT_RADIUS, self.y - ROBOT_RADIUS - 15))
        if self.current_message:
            self.draw_speech_bubble(surface, self.current_message)

    def draw_speech_bubble(self, surface, text):
        padding = 6
        max_width = 150
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            test_surface = font_small.render(test_line, True, BLACK)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        height = (font_small.get_height() + 2) * len(lines) + padding * 2
        width = max([font_small.render(line, True, BLACK).get_width() for line in lines]) + padding * 2

        bubble_x = self.x + 10
        bubble_y = self.y - height - 20

        pygame.draw.rect(surface, BALLOON_COLOR, (bubble_x, bubble_y, width, height), border_radius=5)
        pygame.draw.rect(surface, BLACK, (bubble_x, bubble_y, width, height), 1, border_radius=5)

        for i, line in enumerate(lines):
            text_surface = font_small.render(line, True, BLACK)
            surface.blit(text_surface, (bubble_x + padding, bubble_y + padding + i * (font_small.get_height() + 2)))

    def start_conversation(self, other):
        self.talking_with = other
        other.talking_with = self
        self.in_conversation = True
        other.in_conversation = True
        self.question_count = 0
        other.question_count = 0
        self.current_message = "Selam, nasılsın?"
        prompt = f"{self.name} diyor ki: Selam, nasılsın?"
        other.current_message = get_ai_response_local(prompt)
        other.ready_to_respond = True

    def continue_conversation(self):
        if self.talking_with and self.ready_to_respond and self.in_conversation:
            if self.question_count >= QUESTIONS_PER_CONVO:
                # Konuşma bitti, serbest bırak
                self.talking_with.talking_with = None
                self.talking_with.in_conversation = False
                self.talking_with.current_message = ""
                self.talking_with.ready_to_respond = True

                self.talking_with = None
                self.in_conversation = False
                self.current_message = ""
                self.ready_to_respond = True
            else:
                prompt = f"{self.talking_with.name} sana dedi ki: '{self.talking_with.current_message}'. Ne cevap verirsin?"
                self.current_message = get_ai_response_local(prompt)
                self.ready_to_respond = False
                self.talking_with.ready_to_respond = True
                self.question_count += 1

def draw_town():
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, STREET_COLOR, (0, HEIGHT//2 - 60, WIDTH, 120))
    for pos in house_positions:
        x, y = pos
        pygame.draw.rect(screen, HOUSE_COLOR, (x - 40, y - 40, 80, 80))
        pygame.draw.polygon(screen, (150, 75, 0), [(x - 50, y - 40), (x, y - 90), (x + 50, y - 40)])

class Clock:
    def __init__(self):
        self.hour = START_HOUR
        self.minute = 0
        self.seconds_accum = 0

    def update(self, dt):
        self.seconds_accum += dt
        while self.seconds_accum >= SECONDS_PER_MINUTE:
            self.seconds_accum -= SECONDS_PER_MINUTE
            self.minute += 1
            if self.minute >= 60:
                self.minute = 0
                self.hour += 1

    def get_time_str(self):
        return f"{self.hour:02d}:{self.minute:02d}"

clock_display = Clock()

robots = [Robot(f"R{i+1}", house_positions[i]) for i in range(ROBOT_COUNT)]

for r in robots:
    r.state = "walking_out"

running = True
while running:
    dt = clock.tick(FPS) / 1000

    clock_display.update(dt)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if clock_display.hour >= END_HOUR:
        for r in robots:
            if r.state != "at_home":
                r.state = "walking_home"
        if all(r.state == "at_home" for r in robots):
            running = False

    draw_town()

    # Robotlar hareket etsin ama sohbette duracaklar
    for r in robots:
        r.move()

    # Robotlar sohbetini devam ettirsin
    for r in robots:
        r.continue_conversation()

    # Mesafeyi kontrol edip sohbeti başlat
    for i in range(len(robots)):
        for j in range(i+1, len(robots)):
            r1 = robots[i]
            r2 = robots[j]
            if not r1.in_conversation and not r2.in_conversation:
                dist = math.hypot(r1.x - r2.x, r1.y - r2.y)
                if dist < INTERACTION_DISTANCE:
                    r1.start_conversation(r2)

    for r in robots:
        r.draw(screen)

    time_text = font_large.render("Saat: " + clock_display.get_time_str(), True, BLACK)
    screen.blit(time_text, (WIDTH - 180, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
