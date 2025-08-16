
import time
import os
from datetime import datetime
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox

# Δημιουργία GUI παραθύρου
root = tk.Tk()
root.title("Screenshot Tool")
root.geometry("400x100")
label = tk.Label(
    root,
    text="📸 Το πρόγραμμα τρέχει και αποθηκεύει screenshot κάθε 1 λεπτό.",
    wraplength=380,
    justify="center"
)
label.pack(pady=20)

# Φάκελος αποθήκευσης: Desktop/Screenshots
save_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Screenshots")
os.makedirs(save_folder, exist_ok=True)

# Συνάρτηση για περιοδικό screenshot
def take_screenshots():
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(save_folder, f"screenshot_{timestamp}.png")
        img = ImageGrab.grab()
        img.save(file_path)
        time.sleep(60)

# Εκκίνηση του screenshot loop σε ξεχωριστό νήμα
import threading
threading.Thread(target=take_screenshots, daemon=True).start()

# Εκκίνηση του GUI
root.mainloop()
