import tkinter as tk
import pygame
import threading  # so the sound doesn't freeze the GUI


pygame.mixer.init()


def play_sound():
    """
    the function plays the music
    :return: none
    """
    def run():
        """
        play the music
        :return: none
        """
        pygame.mixer.music.load("sound.mp3")
        pygame.mixer.music.play()
    threading.Thread(target=run, daemon=True).start()


def close_popup():
    """
    close the window
    :return: none
    """
    play_sound()
    window.destroy()


window = tk.Tk()
window.title("💖 Motivation!")  # set title of window
window.geometry("300x150")  # set size of window
window.configure(bg="#FFE6F0")  # set background to pink

play_sound()

label = tk.Label(window, text="You’re a star! 🌟", font=("Comic Sans MS", 14), bg="#FFE6F0", fg="#FF69B4")
# font style and color
label.pack(pady=20)  # adds 20 pixels of space above and below the label

button = tk.Button(window, text="Thanks 💕", command=close_popup, bg="#FFD1DC", fg="#000000")
# the button to exit program
button.pack(pady=10)
window.mainloop()
