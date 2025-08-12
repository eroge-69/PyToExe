import tkinter as tk
import webbrowser
import time
import threading

# Liste de vidéos à ouvrir en cas "d'échec"
VIDEOS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=ZZ5LpwO-An4",
    "https://www.youtube.com/watch?v=U1UtRnGn5hc"
]

def start_countdown():
    countdown_time = 10  # secondes
    def countdown():
        nonlocal countdown_time
        while countdown_time > 0:
            timer_label.config(text=f"Temps restant : {countdown_time} sec")
            time.sleep(1)
            countdown_time -= 1
        explosion()

    threading.Thread(target=countdown, daemon=True).start()

def desamorcer():
    timer_label.config(text="💣 Bombe désamorcée ! 💣", fg="green")
    btn_desamorcer.config(state="disabled")

def explosion():
    # Ouvrir les vidéos
    for url in VIDEOS:
        webbrowser.open(url)
    # Changer la fenêtre en rouge
    root.config(bg="red")
    timer_label.config(text="💥 BOOM !!! 💥", fg="white", bg="red")
    btn_desamorcer.destroy()

# Création de la fenêtre
root = tk.Tk()
root.title("💣 Bombe à désamorcer 💣")
root.geometry("300x150")
root.resizable(False, False)

timer_label = tk.Label(root, text="Temps restant : ...", font=("Arial", 14))
timer_label.pack(pady=20)

btn_desamorcer = tk.Button(root, text="Désamorcer", font=("Arial", 12), command=desamorcer)
btn_desamorcer.pack()

start_countdown()

root.mainloop()
