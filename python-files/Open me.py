import os
import time
import threading
import pygame

frames = [
    r"""
     (｡♥‿♥｡)
      ♥     ♥
    """,
    r"""
     (｡♥‿♥｡)
     ♥       ♥
    """,
    r"""
     (｡♥‿♥｡)
      ♥     ♥
    """,
    r"""
     (｡♥‿♥｡)
     ♥   ♥
    """,
    r"""
     (｡•‿•｡)
      ♥     ♥
    """,
    r"""
     (｡◕‿◕｡)
     ♥       ♥
    """,
    r"""
     (｡♥‿♥｡)
      ♥   ♥
    """,
    r"""
     (｡♥‿♥｡)
     ♥ ♥ ♥
    """,
    r"""
     (｡♥‿♥｡)
      ♥ ♥
    """,
    r"""
     (｡♥‿♥｡)
     ♥     ♥
    """
]

def clear(): 
    os.system('cls' if os.name == 'nt' else 'clear')

def play_ascii_movie(frames, delay=0.3, duration=12):
    start_time = time.time()
    while time.time() - start_time < duration:
        for frame in frames:
            clear()
            print(frame)
            time.sleep(delay)
            if time.time() - start_time >= duration:
                break

def play_midi(file_path):
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        time.sleep(1) 
    except Exception as e:
        print("Error playing music:", e)

if __name__ == '__main__':
    midi_file = "./song.mid" 
    threading.Thread(target=play_midi, args=(midi_file,), daemon=True).start()
    
    clear()
    print("Happy Birthday, my love! 🎉🎂")
    time.sleep(2)
    
    play_ascii_movie(frames, delay=0.3, duration=12)
    
    clear()
    print("I ❤️ you more than words can say.")
    time.sleep(3)
