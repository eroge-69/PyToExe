import pygame
from zipfile import ZipFile, ZIP_DEFLATED
from tkinter import filedialog
from tkinter import *
import time
import threading
import tkinter as tk
from tkinter import messagebox
import shutil



# Open Explorer File Select
filepath = filedialog.askopenfilename(
        title="Select a .zip file",
        filetypes=[("Beatmap Files", "*.zip")]

)



# Extract Files At The Beatmap Folder
beatmap_name = filepath.split("/")[-1].replace(".zip", "")
filepath_forbeatmapextract = "./Beatmaps/" + beatmap_name
print(filepath_forbeatmapextract)

with ZipFile(filepath,'r') as zip:
    zip.extractall(filepath_forbeatmapextract)

filepath = filepath.replace(".zip", ".txt")

with open("./Beatmaps/" + beatmap_name + "/" + beatmap_name + ".txt" , 'r') as file:
    contents = file.read()
    print(contents)





# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load and play music
def delayed_music_play():
    time.sleep(0.9)  # Delay music for 2 seconds
    pygame.mixer.music.play()

pygame.mixer.music.load("./Beatmaps/" + beatmap_name + "/" + beatmap_name + ".mp3")
threading.Thread(target=delayed_music_play).start()


# Variables For The Technical Side
BASE_WIDTH, BASE_HEIGHT = 800, 450
screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
note_y_location = 10
clock = pygame.time.Clock()
D_key = False
F_key = False
J_key = False
K_key = False
score = 0
pygame.display.set_caption("Rythm Game - " + beatmap_name)
icon = pygame.image.load("./Beatmaps/" + beatmap_name + "/" + "icon.png").convert_alpha()
pygame.display.set_icon(icon)

# Sprites In Memory
note = pygame.image.load("./Assets/Note.png").convert_alpha()
background = pygame.image.load("./Beatmaps/" + beatmap_name + "/" + beatmap_name + ".png").convert()
hit = pygame.image.load("./Assets/Hit.png").convert_alpha()
hit_pressed = pygame.image.load("./Assets/HitPressed.png").convert_alpha()

# Sounds In Memory
click_sound = pygame.mixer.Sound("./Assets/Click.mp3")  # or .wav

# Parse beatmap contents into a list of (spawn_time, lane)
notes_data = []
for line in contents.strip().splitlines():
    parts = line.split(",")
    if len(parts) >= 2:
        spawn_time = float(parts[0])
        lane = int(parts[1])
        notes_data.append((spawn_time, lane))

note_spawned = [False] * len(notes_data)
notes = []  # Each note will be (x, y)

LANE_X = [290, 370, 450, 530]  # Example: 80px apart

# Initialize font for score display
font = pygame.font.Font("./Beatmaps/" + beatmap_name + "/" + "ScoreFont.ttf", 36)

running = True
start_ticks = pygame.time.get_ticks() / 1000  # Start time in seconds

fullscreen = False
end_timer_started = False
end_timer_start = 0
end_delay = 3  # seconds to wait before closing

# --- Add previous key state tracking ---
prev_D_key = False
prev_F_key = False
prev_J_key = False
prev_K_key = False

while running:
    current_time = pygame.time.get_ticks() / 1000 - start_ticks

    # Spawn notes at the right time
    for i, (spawn_time, lane) in enumerate(notes_data):
        if not note_spawned[i] and current_time >= spawn_time:
            if 0 <= lane < len(LANE_X):  # Check lane is valid
                x_pos = LANE_X[lane]
                notes.append([x_pos, 0])  # Start at y=0
                note_spawned[i] = True
            else:
                print(f"Invalid lane value: {lane}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Fullscreen toggle on maximize
        if event.type == pygame.VIDEORESIZE:
            display_info = pygame.display.Info()
            if event.w == display_info.current_w and event.h == display_info.current_h and not fullscreen:
                screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
                fullscreen = True
            elif fullscreen and (event.w != display_info.current_w or event.h != display_info.current_h):
                screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
                fullscreen = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                D_key = True
            if event.key == pygame.K_f:
                F_key = True
            if event.key == pygame.K_j:
                J_key = True
            if event.key == pygame.K_k:
                K_key = True
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                D_key = False
            if event.key == pygame.K_f:
                F_key = False
            if event.key == pygame.K_j:
                J_key = False
            if event.key == pygame.K_k:
                K_key = False

    # --- Draw everything to game_surface ---
    game_surface.blit(background, (0, 0))
    dark_overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    dark_overlay.set_alpha(225)
    dark_overlay.fill((0, 0, 0))
    game_surface.blit(dark_overlay, (0, 0))

    # Draw hit indicators
    if D_key:
     game_surface.blit(hit_pressed, (290, 350))
    else:
        game_surface.blit(hit, (290, 350))
    if F_key:
        game_surface.blit(hit_pressed, (370, 350))
    else:
        game_surface.blit(hit, (370, 350))
    if J_key:
     game_surface.blit(hit_pressed, (450, 350))
    else:
        game_surface.blit(hit, (450, 350))
    if K_key:
        game_surface.blit(hit_pressed, (530, 350))
    else:
        game_surface.blit(hit, (530, 350))

    # --- Collision detection and note removal for all lanes ---
    hit_rects = [
        hit.get_rect(topleft=(290, 350)),  # D lane
        hit.get_rect(topleft=(370, 350)),  # F lane
        hit.get_rect(topleft=(450, 350)),  # J lane
        hit.get_rect(topleft=(530, 350)),  # K lane

    ]
    
    lane_keys = [D_key, F_key, J_key, K_key]
    prev_lane_keys = [prev_D_key, prev_F_key, prev_J_key, prev_K_key]

    notes_to_remove = []
    for note_pos in notes:
        note_rect = note.get_rect(topleft=(note_pos[0], note_pos[1]))
        for lane_index, hit_rect in enumerate(hit_rects):
            # Only allow hit if key was just pressed (not held)
            if (
                note_rect.colliderect(hit_rect)
                and lane_keys[lane_index]
                and not prev_lane_keys[lane_index]  # Just pressed!
            ):
                notes_to_remove.append(note_pos)
                score += 100
                break  # No need to check other lanes for this note

    for note_pos in notes_to_remove:
        notes.remove(note_pos)

    # Draw and move notes
    for note_pos in notes:
        game_surface.blit(note, (note_pos[0], note_pos[1]))
        note_pos[1] += 6  # Move note down

    # Draw score in top-right
    score_text = font.render(f"X{score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(topright=(BASE_WIDTH - 10, 10))
    game_surface.blit(score_text, score_rect)


    # --- Auto-close when all notes are gone and all have spawned ---
    if all(note_spawned) and len(notes) == 0:
        if not end_timer_started:
            end_timer_start = pygame.time.get_ticks() / 1000
            end_timer_started = True
        elif pygame.time.get_ticks() / 1000 - end_timer_start >= end_delay:
            running = False

    # --- Scale game_surface to fit the window ---
    window_size = screen.get_size()
    scaled_surface = pygame.transform.smoothscale(game_surface, window_size)
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

    # --- Update previous key states at the end of the loop ---
    prev_D_key = D_key
    prev_F_key = F_key
    prev_J_key = J_key
    prev_K_key = K_key