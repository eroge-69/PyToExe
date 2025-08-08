import pyautogui
import cv2
import numpy as np
import time

# Define the game screen region (left, top, width, height)
GAME_REGION = (100, 200, 600, 600)

# Load template images (place in same folder)
TEMPLATE_UNOPENED = cv2.imread('unopened.png', 0)
TEMPLATE_GEM = cv2.imread('gem.png', 0)
TEMPLATE_BOMB = cv2.imread('bomb.png', 0)

TILE_SIZE = 50  # Adjust based on your game tile size

def grab_screen():
    screenshot = pyautogui.screenshot(region=GAME_REGION)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

def match_tile(tile_img, template):
    res = cv2.matchTemplate(tile_img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val

def analyze_board():
    board_image = grab_screen()
    rows = board_image.shape[0] // TILE_SIZE
    cols = board_image.shape[1] // TILE_SIZE

    board = []

    for r in range(rows):
        row = ""
        for c in range(cols):
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            tile = board_image[y:y+TILE_SIZE, x:x+TILE_SIZE]

            score_unopened = match_tile(tile, TEMPLATE_UNOPENED)
            score_gem = match_tile(tile, TEMPLATE_GEM)
            score_bomb = match_tile(tile, TEMPLATE_BOMB)

            best_score = max(score_unopened, score_gem, score_bomb)

            if best_score == score_unopened:
                row += "@"
            elif best_score == score_gem:
                row += "$"
            elif best_score == score_bomb:
                row += "!"
            else:
                row += "?"

        board.append(row)

    print("\nDetected Game Board:")
    for row in board:
        print(" ".join(row))

# Main loop
print("Starting MinesBot... Press Ctrl+C to stop.")
try:
    while True:
        analyze_board()
        time.sleep(1.5)
except KeyboardInterrupt:
    print("Stopped.")
