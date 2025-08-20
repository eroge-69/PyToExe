import pygame
import random
import sys
import librosa # type: ignore
import sys
import os

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

song_file = resource_path("Soundloaders.app - ビバハピ - Mitchie M")
# Use song_file in your code instead of "song.mp3"



# --- CONFIG ---
SONG_FILE = r"C:\\Users\\levip\\Downloads\\Soundloaders.app - ビバハピ - Mitchie M.mp3"  # replace with your actual path
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Difficulty settings (lyric onset skipping)
DIFFICULTIES = {
    "normal": 3,   # every 3rd syllable
    "hard": 2,     # every 2nd syllable
    "expert": 1    # every syllable/onset
}

# --- CLASSES ---
class Note:
    def __init__(self, key, x, time, speed=5):
        self.key = key
        self.x = x
        self.y = 0
        self.speed = speed
        self.time = time  # time in seconds when note should be hit
        self.hit = False

    def update(self):
        self.y += self.speed

    def draw(self, screen, font):
        text = font.render(str(self.key), True, (255, 255, 255))
        screen.blit(text, (self.x, self.y))

# --- MAIN GAME ---
def rhythm_game(difficulty="normal"):
    # --- Onset (lyric syllable) detection with librosa ---
    print("Analyzing song for lyric onsets... this may take a little while...")
    y, sr = librosa.load(SONG_FILE)

    # Detect syllable onsets (sung parts)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    skip = DIFFICULTIES[difficulty]
    onset_times = onset_times[::skip]  # filter onsets by difficulty

    # Create notes mapped to lyric onsets
    key_positions = {
        1: 150,
        2: 300,
        3: 450,
        4: 600
    }
    notes = []
    for t in onset_times:
        key_choice = random.choice(list(key_positions.keys()))
        notes.append(Note(key_choice, key_positions[key_choice], t, speed=5))

    # --- Init pygame ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rhythm Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)

    # load music
    pygame.mixer.init()
    pygame.mixer.music.load(SONG_FILE)
    pygame.mixer.music.play()

    score = 0
    running = True
    start_ticks = pygame.time.get_ticks()

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit():
                    key_pressed = int(event.unicode)
                    current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
                    for note in notes:
                        if note.key == key_pressed and not note.hit and abs(note.time - current_time) < 0.2:
                            note.hit = True
                            score += 100
                            break

        # update and draw notes
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        for note in notes:
            if not note.hit and current_time >= note.time - 1.5:  # spawn a bit before hit time
                note.update()
                note.draw(screen, font)

        # draw hit zone
        pygame.draw.line(screen, (0, 255, 0), (0, SCREEN_HEIGHT-100), (SCREEN_WIDTH, SCREEN_HEIGHT-100), 5)

        # draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        # stop when music ends
        if not pygame.mixer.music.get_busy():
            running = False

    print("Final Score:", score)

if __name__ == "__main__":
    print("Choose difficulty: normal, hard, expert")
    diff = input("> ").strip().lower()
    if diff not in DIFFICULTIES:
        diff = "normal"

    print("Before running, install dependencies with:")
    print("pip install pygame librosa soundfile")

    rhythm_game(diff)

