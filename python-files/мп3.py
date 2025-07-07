import pygame
import tkinter as tk
from tkinter import filedialog

# Ініціалізація Pygame
pygame.mixer.init()

# Функції для керування музикою
def load_music():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file_path:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

def pause_music():
    pygame.mixer.music.pause()

def resume_music():
    pygame.mixer.music.unpause()

def stop_music():
    pygame.mixer.music.stop()

# Створення вікна Tkinter
root = tk.Tk()
root.title("Музичний плеєр")

# Кнопки керування
btn_load = tk.Button(root, text="Завантажити", command=load_music)
btn_pause = tk.Button(root, text="Пауза", command=pause_music)
btn_resume = tk.Button(root, text="Продовжити", command=resume_music)
btn_stop = tk.Button(root, text="Зупинити", command=stop_music)

# Розташування кнопок
btn_load.pack(pady=5)
btn_pause.pack(pady=5)
btn_resume.pack(pady=5)
btn_stop.pack(pady=5)

root.mainloop()