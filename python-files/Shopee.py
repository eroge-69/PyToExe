import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Will You Be My Date? 💖")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 30)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
PURPLE = (153, 50, 204)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Player setup
player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 50)
player_speed = 7

# Falling items
items = []
item_speed = 5
item_size = 30
item_spawn_timer = 0
acai_caught = 0

# States
STATE_GAME = "game"
STATE_QUIZ_MC = "quiz_mc"        # multiple choice quiz
STATE_QUIZ_TEXT = "quiz_text"    # text input question
STATE_QUIZ_SCALE = "quiz_scale"  # scale input question
STATE_ASK = "ask"                # final yes/no input
STATE_BEG = "beg"
STATE_FINAL = "final"

state = STATE_GAME

# Quiz multiple choice questions
quiz_mc = [
    {
        "q": "What’s her guilty pleasure snack?",
        "choices": ["Gummy", "Choco", "cookie", "Everything"],
        "answer": 3
    },
    {
        "q": "What  do you always call me when youre mad?",
        "choices": ["Endika", "Buba", "Baby", "All of the above"],
        "answer": 1
    },
    {
        "q": "What did we do on our first date back together as exes?",
        "choices": ["Arab Street", "Pizza", "McDonald's"],
        "answer": 1
    }
]

quiz_mc_index = 0

# Text question (no right/wrong)
quiz_text_question = "What is Shariel's goal in life , He wants to know iff u do know"
quiz_text_answer = ""

# Scale question
quiz_scale_question = "On a scale of 1 to 10, how much do you love me?"
quiz_scale_answer = ""

# Final yes/no question
final_answer = ""

# Love letter
love_paragraph = (
    "Thank you for playing... But more than that, thank you for being you.\n"
    "I love you so much. I still remember every little thing about us —\n"
    "the way we eat like there's no tomorrow, how our random acai runs\n"
    "somehow turn into perfect dates, and how you call me 'Buba' like\n"
    "it's the most natural thing in the world.\n\n"
    "I miss you — more than I know how to put into words. And if you say yes...\n"
    "I promise August 1st will be one of those spontaneous, unforgettable days\n"
    "that only we could pull off.\n\n"
    "Text me our first child name when youre done\n"
    "— Shariel 💌"
)

def draw_text(text, x, y, size=30, color=BLACK):
    lines = text.split("\n")
    f = pygame.font.SysFont("arial", size)
    for i, line in enumerate(lines):
        txt = f.render(line, True, color)
        screen.blit(txt, (x, y + i * (size + 5)))

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == STATE_GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x -= player_speed
                elif event.key == pygame.K_RIGHT:
                    player.x += player_speed

        elif state == STATE_QUIZ_MC:
            if event.type == pygame.KEYDOWN:
                if event.unicode in ['1', '2', '3', '4']:
                    selected = int(event.unicode) - 1
                    if selected == quiz_mc[quiz_mc_index]['answer']:
                        quiz_mc_index += 1
                        if quiz_mc_index >= len(quiz_mc):
                            state = STATE_QUIZ_TEXT
                    else:
                        # Show try again message (we'll just print here)
                        print("Oops! Try again <3")

        elif state == STATE_QUIZ_TEXT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    state = STATE_QUIZ_SCALE
                elif event.key == pygame.K_BACKSPACE:
                    quiz_text_answer = quiz_text_answer[:-1]
                else:
                    quiz_text_answer += event.unicode

        elif state == STATE_QUIZ_SCALE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Validate scale answer
                    try:
                        val = int(quiz_scale_answer)
                        if val >= 9 and val <= 10:
                            state = STATE_ASK
                        else:
                            # Not enough love - show message by drawing below
                            pass
                    except:
                        # invalid input
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    quiz_scale_answer = quiz_scale_answer[:-1]
                else:
                    if event.unicode.isdigit():
                        quiz_scale_answer += event.unicode

        elif state == STATE_ASK:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if final_answer.strip().lower() == "yes":
                        state = STATE_FINAL
                    else:
                        state = STATE_BEG
                elif event.key == pygame.K_BACKSPACE:
                    final_answer = final_answer[:-1]
                else:
                    final_answer += event.unicode

        elif state == STATE_BEG:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press R to restart
                    final_answer = ""
                    quiz_scale_answer = ""
                    quiz_text_answer = ""
                    quiz_mc_index = 0
                    acai_caught = 0
                    items.clear()
                    state = STATE_GAME

    keys = pygame.key.get_pressed()
    if state == STATE_GAME:
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player.x += player_speed

        player.x = max(0, min(WIDTH - player.width, player.x))

        item_spawn_timer += 1
        if item_spawn_timer > 20:
            item_spawn_timer = 0
            item_type = random.choice(["acai"] * 3 + ["pickle"])
            item = pygame.Rect(random.randint(0, WIDTH - item_size), 0, item_size, item_size)
            items.append((item, item_type))

        for item, kind in items[:]:
            item.y += item_speed
            if item.colliderect(player):
                items.remove((item, kind))
                if kind == "acai":
                    acai_caught += 1
                    if acai_caught >= 5:
                        state = STATE_QUIZ_MC
                elif kind == "pickle":
                    acai_caught = 0
            elif item.y > HEIGHT:
                items.remove((item, kind))

        pygame.draw.rect(screen, PINK, player)
        for item, kind in items:
            color = GREEN if kind == "acai" else RED
            pygame.draw.ellipse(screen, color, item)

        draw_text(f"Acai Caught: {acai_caught}/5", 10, 10)
        draw_text("Use ← and → to move. Catch acai! Avoid pickles!", 10, 50, 24, PURPLE)

    elif state == STATE_QUIZ_MC:
        q = quiz_mc[quiz_mc_index]
        draw_text(f"{q['q']}", 50, 100)
        for i, choice in enumerate(q['choices']):
            draw_text(f"{i + 1}. {choice}", 70, 160 + i * 40)

    elif state == STATE_QUIZ_TEXT:
        draw_text(quiz_text_question, 50, 100)
        draw_text("Type your answer and press Enter:", 50, 160)
        draw_text(quiz_text_answer, 50, 220, 28, PURPLE)

    elif state == STATE_QUIZ_SCALE:
        draw_text(quiz_scale_question, 50, 100)
        draw_text("Type a number 1-10 and press Enter:", 50, 160)
        draw_text(quiz_scale_answer, 50, 220, 28, PURPLE)
        # Show warning if invalid or below 9
        try:
            val = int(quiz_scale_answer)
            if val < 9:
                draw_text("You need to choose 9 or above to continue 💖", 50, 270, 24, RED)
        except:
            pass

    elif state == STATE_ASK:
        draw_text("Will you be my date on August 1st — National Girlfriend Day?", 50, 100)
        draw_text("Type your answer and press Enter:", 50, 160)
        draw_text(final_answer, 50, 220, 28, PURPLE)

    elif state == STATE_BEG:
        draw_text("Are you sure...?🥺\nThink about all your sivanianian at home.\n", 50, 100, 28, RED)
        draw_text("damn u dont want to\n", 50, 200, 24, PURPLE)
        draw_text("(Press R to restart the game and answer again ❤️)", 50, 300, 22, BLACK)

    elif state == STATE_FINAL:
        draw_text(love_paragraph, 50, 100, 24, BLACK)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
