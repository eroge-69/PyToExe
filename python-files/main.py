import tkinter as tk
from tkinter import font
import threading, time
import pygame

# CONFIG
COUNTDOWN_SECONDS = 15
ALARM_FILE = "Son_important.mp3"  # ton MP3 dans le même dossier
FLASH_DURATION = 0.07
FLASH_REPEAT = 20

pygame.mixer.init()

def red_flash(canvas):
    for _ in range(FLASH_REPEAT):
        canvas.config(bg="red")
        canvas.update()
        time.sleep(FLASH_DURATION)
        canvas.config(bg="black")
        canvas.update()
        time.sleep(FLASH_DURATION)

def run_countdown(root, label, canvas):
    for t in range(COUNTDOWN_SECONDS, -1, -1):
        label.config(text=f"Temps restant : {t} s")
        label.update_idletasks()
        time.sleep(1)
        if t == 5:
            # Freeze visuel simulé + curseur caché
            root.config(cursor="none")
            # Lancer l'alarme
            try:
                pygame.mixer.music.load(ALARM_FILE)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print("Erreur audio :", e)
            # Clignotement rouge
            red_flash(canvas)
    root.config(cursor="")
    try:
        pygame.mixer.music.stop()
    except:
        pass
    label.config(text="Fin du compte à rebours (Simulation safe).")

root = tk.Tk()
root.title("Fake Ransomware Simulation")
root.attributes("-fullscreen", True)
root.configure(bg="black")

big_font = font.Font(family="Helvetica", size=48, weight="bold")
countdown_label = tk.Label(root, text="", fg="white", bg="black", font=big_font)
countdown_label.pack(pady=50)

canvas_frame = tk.Frame(root, bg="black")
canvas_frame.pack(expand=True, fill="both")

threading.Thread(target=run_countdown, args=(root, countdown_label, canvas_frame), daemon=True).start()

def on_key(event):
    if event.keysym == "Escape":
        try:
            pygame.mixer.music.stop()
        except:
            pass
        root.destroy()
root.bind("<Key>", on_key)

root.mainloop()