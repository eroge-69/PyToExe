import os
import random
import pygame
import sys

# ---------------------------- CONSTANTS ----------------------------
WIDTH, HEIGHT     = 800, 600
FPS               = 60
APPLE_RADIUS      = 25           # bigger apples
BOX_W, BOX_H      = 120, 120
GAP_BTM           = 20
BOX_Y             = HEIGHT - BOX_H - GAP_BTM
BOX_XS            = [WIDTH // 6 * (i + 1) - BOX_W // 2 for i in range(5)]

APPLE_COL         = (220, 30, 30)
BOX_COL           = (180, 200, 40)
TEXT_COL          = (255, 255, 255)
BG_COL            = (180, 220, 180)   # lighter board

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Apple Picker")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 32, True)
big    = pygame.font.SysFont("Arial", 48, True)

sounds = {n: pygame.mixer.Sound(os.path.join("sounds", f"{n}.ogg"))
          for n in range(1, 6) if os.path.exists(os.path.join("sounds", f"{n}.ogg"))}

# ---------------------------- HELPERS ----------------------------
def make_apples():
    """Return 15 apples (1-5, 3 each) inside the visible top area without overlap."""
    numbers = list(range(1, 6)) * 3
    random.shuffle(numbers)

    apples = []
    margin = APPLE_RADIUS + 5
    top_bound    = margin
    bottom_bound = HEIGHT // 3
    left_bound   = margin
    right_bound  = WIDTH - margin

    placed = []
    for num in numbers:
        for _ in range(5000):
            x = random.randint(left_bound, right_bound)
            y = random.randint(top_bound, bottom_bound)
            ok = True
            for (px, py) in placed:
                if ((px - x) ** 2 + (py - y) ** 2) ** 0.5 < APPLE_RADIUS * 2 + 5:
                    ok = False
                    break
            if ok:
                placed.append((x, y))
                apples.append({
                    "num": num,
                    "x": x,
                    "y": y,
                    "orig": (x, y),
                    "dragging": False
                })
                break
    # ensure all 15 were placed (fallback if area too tight)
    while len(apples) < 15:
        x = random.randint(left_bound, right_bound)
        y = random.randint(top_bound, bottom_bound)
        apples.append({
            "num": numbers[len(apples)],
            "x": x,
            "y": y,
            "orig": (x, y),
            "dragging": False
        })
    return apples


def draw_die_dots(surf, rect, value):
    dot_r = 10
    positions = {
        1: [(0.5, 0.5)],
        2: [(0.25, 0.25), (0.75, 0.75)],
        3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
        4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
        5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    }[value]
    for px, py in positions:
        cx = int(rect.x + rect.w * px)
        cy = int(rect.y + rect.h * py)
        pygame.draw.circle(surf, TEXT_COL, (cx, cy), dot_r)


def draw_end_buttons(surf, mouse):
    """Draw bigger round Replay / Quit buttons so the words fit inside."""
    bw = bh = 120                     # increased size
    gap = 60
    left = (WIDTH - (bw * 2 + gap)) // 2
    top  = HEIGHT // 2 + 60

    replay_center = (left + bw // 2, top + bh // 2)
    quit_center   = (left + bw + gap + bw // 2, top + bh // 2)

    for center, col_base, txt in [(replay_center, (50, 220, 50), "Replay"),
                                  (quit_center,   (220, 50, 50), "Quit")]:
        col = tuple(min(255, c + 30) if ((mouse[0] - center[0]) ** 2 +
                                         (mouse[1] - center[1]) ** 2) ** 0.5 < bw // 2
                    else c for c in col_base)
        pygame.draw.circle(surf, col, center, bw // 2)
        pygame.draw.circle(surf, (0, 0, 0), center, bw // 2, 3)
        surf.blit(big.render(txt, True, TEXT_COL),
                  big.render(txt, True, TEXT_COL).get_rect(center=center))

    return (pygame.Rect(left, top, bw, bh),
            pygame.Rect(left + bw + gap, top, bw, bh))


# ---------------------------- GAME STATE ----------------------------
def reset():
    global apples, score, finished
    apples   = make_apples()
    score    = 0
    finished = False

reset()

# ---------------------------- MAIN LOOP ----------------------------
running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if finished:
                replay_rect, quit_rect = draw_end_buttons(screen, mouse_pos)
                if replay_rect.collidepoint(mouse_pos):
                    reset()
                elif quit_rect.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()
                continue

            for a in apples:
                dx, dy = mouse_pos[0] - a["x"], mouse_pos[1] - a["y"]
                if dx * dx + dy * dy < APPLE_RADIUS * APPLE_RADIUS:
                    a["dragging"] = True
                    sounds.get(a["num"], None) and sounds[a["num"]].play()

        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            for a in [a for a in apples if a["dragging"]]:
                a["dragging"] = False
                box_idx = a["num"] - 1
                box_rect = pygame.Rect(BOX_XS[box_idx], BOX_Y, BOX_W, BOX_H)
                if box_rect.collidepoint(mouse_pos):
                    apples.remove(a)
                    score += 1
                    if score == 15:
                        finished = True
                else:
                    a["x"], a["y"] = a["orig"]

        elif ev.type == pygame.MOUSEMOTION:
            for a in [a for a in apples if a["dragging"]]:
                a["x"], a["y"] = mouse_pos

    screen.fill(BG_COL)

    for i in range(5):
        box = pygame.Rect(BOX_XS[i], BOX_Y, BOX_W, BOX_H)
        pygame.draw.rect(screen, BOX_COL, box, border_radius=15)
        draw_die_dots(screen, box, i + 1)

    for a in apples:
        pygame.draw.circle(screen, APPLE_COL, (int(a["x"]), int(a["y"])), APPLE_RADIUS)
        label = font.render(str(a["num"]), True, TEXT_COL)
        screen.blit(label, label.get_rect(center=(a["x"], a["y"])))

    screen.blit(font.render(f"Score: {score}", True, TEXT_COL), (10, 10))

    if finished:
        draw_end_buttons(screen, mouse_pos)

    pygame.display.flip()

pygame.quit()