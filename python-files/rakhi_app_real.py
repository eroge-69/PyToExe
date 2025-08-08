

import tkinter as tk
from tkinter import messagebox
import random
import threading
import time
import webbrowser
import urllib.parse



# Messages
messages = {
    "Raksha Bandhan": [
        "This Rakhi is a thread of love, protection, and memories. 🤗",
        "No matter how far we are, you're always in my heart. 🧵",
        "You're my protector, guide, and best friend. ❤️"
    ],
    "Friendship Day": [
        "You're not just a friend, you're family. 🫂",
        "Through thick and thin, you've always been there.",
        "Friendship is the thread that ties us together. 💫"
    ]
}

# --- GUI START ---
root = tk.Tk()
root.title("Festival Greeting App 💝")
root.geometry("450x620")
root.configure(bg="#fff3e6")

# Canvas for animation
canvas = tk.Canvas(root, width=450, height=120, bg="#fff3e6", highlightthickness=0)
canvas.pack()

# Confetti particles
confetti_particles = []

def create_confetti():
    colors = ["#f06292", "#ffd54f", "#ba68c8", "#4dd0e1", "#81c784"]
    for _ in range(20):
        x = random.randint(0, 440)
        size = random.randint(5, 12)
        color = random.choice(colors)
        shape = canvas.create_oval(x, 0, x + size, size, fill=color, outline=color)
        confetti_particles.append((shape, random.uniform(1, 3)))

def animate_confetti():
    create_confetti()
    for _ in range(60):  # animate for ~1 second
        for shape, speed in confetti_particles:
            canvas.move(shape, 0, speed)
        canvas.update()
        time.sleep(0.02)
    for shape, _ in confetti_particles:
        canvas.delete(shape)
    confetti_particles.clear()

# Greeting generator
def generate_greeting():
    name = name_entry.get()
    festival = festival_var.get()
    custom_msg = custom_msg_entry.get("1.0", tk.END).strip()

    if not name:
        return None

    final_msg = custom_msg if custom_msg else random.choice(messages[festival])
    full_message = f"🎉 Happy {festival}, {name}!\n\n{final_msg}"
    return full_message

# Show greeting
def show_greeting():
    greeting = generate_greeting()
    if greeting:
        threading.Thread(target=animate_confetti).start()
        messagebox.showinfo("Your Greeting", greeting)
    else:
        messagebox.showwarning("Missing Info", "Please enter a name!")

# WhatsApp sharing
def send_whatsapp():
    greeting = generate_greeting()
    if greeting:
        encoded = urllib.parse.quote(greeting)
        link = f"https://wa.me/?text={encoded}"
        webbrowser.open(link)
    else:
        messagebox.showwarning("Missing Info", "Please enter a name!")

# Header
tk.Label(root, text="💖 Celebrate Special Bonds 💖", font=("Comic Sans MS", 14, "bold"),
         bg="#fff3e6", fg="#4a148c").pack()

# Festival
tk.Label(root, text="Select Occasion 🎉:", bg="#fff3e6", font=("Comic Sans MS", 12)).pack(pady=(10, 0))
festival_var = tk.StringVar(value="Raksha Bandhan")
festival_menu = tk.OptionMenu(root, festival_var, "Raksha Bandhan", "Friendship Day")
festival_menu.config(bg="#f9c5d1", fg="#4a148c", font=("Comic Sans MS", 11), width=20)
festival_menu.pack(pady=5)

# Name Entry
tk.Label(root, text="Enter Name 👤:", bg="#fff3e6", font=("Comic Sans MS", 12)).pack(pady=(10, 0))
name_entry = tk.Entry(root, width=30, font=("Comic Sans MS", 11), bg="#fde2e4")
name_entry.pack(pady=5)

# Custom Message
tk.Label(root, text="Your Message 💌 (Optional):", bg="#fff3e6", font=("Comic Sans MS", 12)).pack(pady=(10, 0))
custom_msg_entry = tk.Text(root, height=4, width=35, font=("Comic Sans MS", 11), bg="#fde2e4")
custom_msg_entry.pack(pady=5)

# Buttons Frame
btn_frame = tk.Frame(root, bg="#fff3e6")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text="🎊 Show Greeting", command=show_greeting,
          bg="#f06292", fg="white", font=("Comic Sans MS", 11, "bold")).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="📲 Send on WhatsApp", command=send_whatsapp,
          bg="#25D366", fg="white", font=("Comic Sans MS", 11, "bold")).grid(row=0, column=1, padx=10)

# Footer
tk.Label(root, text="Made with ❤️ by Atharva", bg="#fff3e6", font=("Arial", 9), fg="gray").pack(side="bottom", pady=10)

root.mainloop()
