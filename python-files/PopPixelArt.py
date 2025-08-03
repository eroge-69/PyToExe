import requests
import pygame
import time
import json

# === Supabase Config ===
SUPABASE_URL = "https://jgblihefwknhzsxgjtkn.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpnYmxpaGVmd2tuaHpzeGdqdGtuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyNDg0ODAsImV4cCI6MjA2OTgyNDQ4MH0.2cwbXNvCoRmKCrCecNzjlQIj-YVr9BB6ATMDV8P2hrk"
SUPABASE_EMAIL = "gshreyaa16504@gmail.com"
SUPABASE_PASSWORD = "Bruh1Bruh2Bruh3"
# === Retry Settings ===
MAX_RETRIES = 10
RETRY_DELAY = 30  # seconds

# === Authenticate and get JWT ===
def login_and_get_jwt():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": SUPABASE_EMAIL,
        "password": SUPABASE_PASSWORD
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise Exception("Login failed: " + resp.text)
    return resp.json()["access_token"]

# === Fetch active animation for the logged-in user ===
def fetch_animation(jwt):
    url = f"{SUPABASE_URL}/rest/v1/animations?select=animation_json&active=eq.true"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception("Fetch failed: " + resp.text)
    data = resp.json()
    if not data:
        raise Exception("No active animation found.")
    return data[0]["animation_json"]

# === Retry logic ===
config = None
for attempt in range(MAX_RETRIES):
    try:
        jwt = login_and_get_jwt()
        config = fetch_animation(jwt)
        break  # Success
    except Exception as e:
        print(f"[Attempt {attempt+1}] Error: {e}")
        time.sleep(RETRY_DELAY)
else:
    print("Failed after retries. Exiting.")
    sys.exit(0)

# === Pygame Setup and Animation ===
grid_width = config["grid"]["width"]
grid_height = config["grid"]["height"]
cell_size = config["grid"]["cell_size"]

colors = config["colors"]
BG_COLOR = tuple(colors["bg"])
ALIVE_COLOR = tuple(colors["alive"])
TEXT_COLOR = tuple(colors["text"])

win_width = grid_width * cell_size
win_height = grid_height * cell_size + 60

pygame.init()
screen = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption(config["title"])
clock = pygame.time.Clock()

font = pygame.font.SysFont(config.get("font", "consolas"), config.get("font_size", 28))

parsed_frames = []
for frame in config["animation"]["frames"]:
    parsed = [[c == "1" for c in row] for row in frame["grid"]]
    parsed_frames.append({
        "duration": frame["duration"],
        "grid": parsed
    })

auto_close = config["animation"].get("auto_close", False)

def draw_frame(grid):
    screen.fill(BG_COLOR)
    for y, row in enumerate(grid):
        for x, alive in enumerate(row):
            color = ALIVE_COLOR if alive else BG_COLOR
            pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size - 1, cell_size - 1))
    text_surface = font.render(config["text"], True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(win_width // 2, win_height - 30))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

# === Run Animation Loop ===
running = True
frame_index = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frame = parsed_frames[frame_index]
    draw_frame(frame["grid"])
    pygame.time.wait(int(frame["duration"] * 1000))

    frame_index += 1
    if frame_index >= len(parsed_frames):
        if auto_close:
            running = False
        else:
            frame_index = 0

    clock.tick(60)

pygame.quit()