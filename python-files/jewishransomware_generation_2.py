import tkinter as tk
from tkinter import simpledialog, messagebox
import random

# Fake password
PASSWORD = "unlockmoney"

# ===== GUI SETUP =====
root = tk.Tk()
root.title("Money Hack Simulation")
root.attributes('-fullscreen', True)
root.configure(bg="black")

canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ===== MONEY ANIMATION =====
money_texts = []
colors = ["#00FF00", "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500"]

for _ in range(50):
    x = random.randint(0, root.winfo_screenwidth())
    y = random.randint(0, root.winfo_screenheight())
    t = canvas.create_text(x, y, text="$", fill=random.choice(colors), font=("Arial", random.randint(20, 50)))
    money_texts.append((t, random.randint(1, 5)))

def animate_money():
    for t, speed in money_texts:
        canvas.move(t, 0, speed)
        coords = canvas.coords(t)
        if coords[1] > root.winfo_screenheight():
            canvas.coords(t, random.randint(0, root.winfo_screenwidth()), 0)
    root.after(50, animate_money)

# ===== PASSWORD CHECK =====
def check_password():
    user_input = simpledialog.askstring("Secret Key", "Enter the secret key to unlock your money:")
    if user_input == PASSWORD:
        messagebox.showinfo("Unlocked", "Access Granted! Your fake money simulation ends here.")
        root.destroy()
    else:
        messagebox.showerror("Locked", "Wrong key! Your money is still 'locked'.")
        root.after(100, check_password)

# ===== START SIMULATION =====
label = tk.Label(root, text="!!! HACKING BANK SYSTEM !!!", font=("Arial", 36, "bold"), fg="red", bg="black")
label.place(relx=0.5, rely=0.1, anchor="center")

animate_money()
root.after(100, check_password)

root.mainloop()


