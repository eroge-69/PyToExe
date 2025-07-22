import tkinter as tk
from tkinter import PhotoImage, Entry, Button
import random
import sys
import subprocess
import os

# --- Chatbot logic ---
def get_response(user_input):
    user_input = user_input.lower()

    greetings = ["hello", "hi", "hey"]
    how_are_you = ["how are you", "how's it going", "how do you do"]
    jokes = ["joke", "tell me a joke"]
    goodbyes = ["bye", "goodbye", "see you"]
    triggers = ["fuck you", "stock images are ugly"]

    if any(trigger in user_input for trigger in triggers):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            batch_path = os.path.join(script_dir, "secret.bat")
            subprocess.Popen([batch_path], shell=True)
            return "You are going to regret that..."
        except Exception as e:
            return f"Error running batch file: {e}"

    if any(greet in user_input for greet in greetings):
        return random.choice([
            "Hi there! How can I help you today?",
            "Hello! What's up?",
            "Hey! How's it going?"
        ])
    if any(phrase in user_input for phrase in how_are_you):
        return random.choice([
            "I'm doing great, thanks!",
            "All good here, how about you?",
            "Feeling fantastic, and you?"
        ])
    if any(phrase in user_input for phrase in jokes):
        return random.choice([
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why was the math book sad? Because it had too many problems."
        ])
    if any(bye in user_input for bye in goodbyes):
        return random.choice([
            "Goodbye! Have a great day!",
            "See you later!",
            "Take care!"
        ])
    return random.choice([
        "That's interesting! Tell me more.",
        "Hmm, I'm still learning. Can you explain that differently?",
        "I'd love to chat about something else! What do you like?",
        "Can you say that again in a different way?",
        "I enjoy hearing about new things!"
    ])

# --- Main window setup ---
root = tk.Tk()
root.title("Smart Buddy")
root.overrideredirect(True)
root.geometry("300x500")
root.config(bg='#eaeaea')  # Give the root window a solid background
root.wm_attributes("-topmost", True)

# --- Load character image ---
try:
    buddy_img = PhotoImage(file="buddy.png")
except Exception as e:
    print("Error loading buddy.png:", e)
    sys.exit(1)

# --- Solid UI frame ---
ui_frame = tk.Frame(root, bg="#ffffff", bd=0)
ui_frame.pack(fill='both', expand=True)

# --- Response label above the image ---
response_label = tk.Label(ui_frame, text="Hello! I'm Buddy!",
                          wraplength=260, font=("Segoe UI", 10),
                          bg="#ffffff", fg='black', justify='center')
response_label.pack(pady=(20, 10))

# --- Image label ---
image_label = tk.Label(ui_frame, image=buddy_img, bg='#ffffff')
image_label.pack()

# --- Make window draggable ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

image_label.bind("<ButtonPress-1>", start_move)
image_label.bind("<ButtonRelease-1>", stop_move)
image_label.bind("<B1-Motion>", do_move)

# --- Input area with visible background ---
input_frame = tk.Frame(ui_frame, bg="#f5f5f5", bd=1, relief="ridge")
input_frame.pack(pady=20, padx=20, fill='x')

entry = Entry(input_frame, width=22, font=("Segoe UI", 10), relief="flat", bg="white", fg="black")
entry.pack(side='left', padx=(10, 5), ipady=6)

def send_message(event=None):
    user_input = entry.get()
    if not user_input.strip():
        return

    response = get_response(user_input)
    response_label.config(text=response)
    entry.delete(0, tk.END)

    if any(b in user_input.lower() for b in ["bye", "goodbye", "see you"]):
        root.after(1500, root.destroy)

send_btn = Button(input_frame, text="Send", command=send_message,
                  font=("Segoe UI", 9), bg="#dddddd", relief="flat")
send_btn.pack(side='left', padx=5, ipadx=10)

entry.bind("<Return>", send_message)

root.mainloop()
