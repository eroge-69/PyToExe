import pygame
import random
import sys
import pyperclip  # pip install pyperclip

# ------------- SETTINGS -------------
WIN_WIDTH, WIN_HEIGHT = 1000, 700
BG_COLOR = (20, 20, 20)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 200, 100)   # Green
REMOVE_COLOR = (200, 50, 50)   # Red
COPY_COLOR = (160, 80, 200)    # Purple
FONT_NAME = "arial"
SCROLL_SPEED = 20
# -----------------------------------

pygame.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Random User Picker")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont(FONT_NAME, 64, bold=True)
font_medium = pygame.font.SysFont(FONT_NAME, 36)
font_small = pygame.font.SysFont(FONT_NAME, 28)

# ----- Input box centered at top-middle -----
input_box_width = 500
input_box_height = 40
input_box_y = 80
input_box = pygame.Rect(WIN_WIDTH // 2 - input_box_width // 2, input_box_y, input_box_width, input_box_height)

color_inactive = (100, 100, 100)
color_active = ACCENT_COLOR
color = color_inactive
active = False
text = ''

# Data + scrolling
names = []
scroll_offset = 0   # we’ll keep your original scroll behavior

# Buttons
pick_button = pygame.Rect(WIN_WIDTH - 320, WIN_HEIGHT - 100, 270, 70)
remove_button = pygame.Rect(WIN_WIDTH // 2 - 230, WIN_HEIGHT // 2 + 60, 220, 50)  # "Remove from List"
copy_button   = pygame.Rect(WIN_WIDTH // 2 + 10,  WIN_HEIGHT // 2 + 60, 220, 50)  # "Copy & Remove"

winner = None
animating = False
animation_ticks = 0

def draw_button(rect, text_str, bg_color, font=font_medium):
    pygame.draw.rect(screen, bg_color, rect, border_radius=10)
    label = font.render(text_str, True, TEXT_COLOR)
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2))

def main():
    global active, color, text, names, winner, animating, animation_ticks, scroll_offset

    while True:
        screen.fill(BG_COLOR)

        # Title
        title = font_large.render("Random User Picker", True, ACCENT_COLOR)
        screen.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Focus input
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

                # Pick button
                if pick_button.collidepoint(event.pos) and names and not animating:
                    animating = True
                    animation_ticks = 30
                    winner = random.choice(names)

                # Winner action buttons
                if winner:
                    if remove_button.collidepoint(event.pos):
                        if winner in names:
                            names.remove(winner)
                        winner = None
                    if copy_button.collidepoint(event.pos):
                        if winner in names:
                            pyperclip.copy(winner)
                            names.remove(winner)
                        winner = None

            # Scrolling (keep your original feel)
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * SCROLL_SPEED
                # Original-style clamp so it can overlap at the bottom if you scroll hard
                max_scroll = max(0, len(names) * 30 - (WIN_HEIGHT - 200))
                scroll_offset = max(min(scroll_offset, 0), -max_scroll)

            # Typing + paste
            if event.type == pygame.KEYDOWN and active:
                mods = pygame.key.get_mods()
                ctrl_or_cmd = (mods & pygame.KMOD_CTRL) or (mods & pygame.KMOD_META)
                shift = mods & pygame.KMOD_SHIFT

                # Paste (Ctrl+V / Cmd+V / Shift+Insert)
                if (event.key == pygame.K_v and ctrl_or_cmd) or (event.key == pygame.K_INSERT and shift):
                    paste_text = pyperclip.paste()
                    if paste_text:
                        # single-line sanitize; avoids weird characters/newlines becoming boxes
                        paste_text = paste_text.replace("\r", "").replace("\n", "")
                        text += paste_text

                elif event.key == pygame.K_RETURN:
                    if text.strip():
                        names.append(text.strip())
                        text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        text += event.unicode

        # ----- Draw input box (top center) -----
        pygame.draw.rect(screen, color, input_box, 2, border_radius=5)
        txt_surface = font_small.render(text, True, TEXT_COLOR)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 7))

        # ----- Names list: start as high as the text box is -----
        y_offset = input_box.y + scroll_offset
        for i, name in enumerate(names):
            name_text = font_small.render(f"{i+1}. {name}", True, TEXT_COLOR)
            screen.blit(name_text, (50, y_offset))
            y_offset += 30

        # Winner display / animation
        if animating:
            if animation_ticks > 0:
                temp_name = random.choice(names)
                label = font_medium.render(temp_name, True, TEXT_COLOR)
                screen.blit(label, (WIN_WIDTH // 2 - label.get_width() // 2, WIN_HEIGHT // 2))
                animation_ticks -= 1
            else:
                animating = False
        elif winner:
            label = font_large.render(winner, True, ACCENT_COLOR)
            screen.blit(label, (WIN_WIDTH // 2 - label.get_width() // 2, WIN_HEIGHT // 2 - 40))
            draw_button(remove_button, "Remove from List", REMOVE_COLOR, font_small)
            draw_button(copy_button,   "Copy & Remove",    COPY_COLOR,  font_small)

        # Main pick button
        draw_button(pick_button, "Random User",
                    ACCENT_COLOR if names and not animating else (100, 100, 100))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
