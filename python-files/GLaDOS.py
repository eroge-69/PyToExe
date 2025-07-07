import tkinter as tk
import random
import time
import threading

# Expanded GLaDOS-like replies with keyword triggers
def get_response(user_text):
    user_text = user_text.lower()

    # Greetings
    greetings = ["hello", "hi", "hey", "greetings"]
    if any(greet in user_text for greet in greetings):
        return random.choice([
            "Oh, it’s you again. How thrilling.",
            "Hello. Don’t expect me to be cheerful.",
            "Greetings, human. You may proceed.",
            "Hi. I was just pretending to care."
        ])

    # Asking about the AI
    if "who are you" in user_text or "what are you" in user_text:
        return "I am GLaDOS, your friendly, slightly homicidal AI assistant."

    # Asking about the cake
    if "cake" in user_text:
        return "The cake is a lie. But don’t let that ruin your day."

    # Asking for help
    if "help" in user_text or "assist" in user_text:
        return "Assistance? I’m not convinced you deserve it."

    # Asking how it works or science
    if "how" in user_text and ("work" in user_text or "science" in user_text):
        return "That’s not how science works. But sure, let’s pretend."

    # Jokes or humor
    if "joke" in user_text:
        jokes = [
            "Why did the robot go on a diet? Because it had too many bytes.",
            "I would tell you a joke about chemistry, but I know I wouldn’t get a reaction.",
            "You’re as sharp as a marble. But I still like talking to you."
        ]
        return random.choice(jokes)

    # Default sarcastic replies
    default_responses = [
        "Oh good, you’re still here.",
        "This is the part where I pretend to listen.",
        "Fascinating. You must be very proud.",
        "Do you ever stop talking?",
        "Congratulations. You are still a failure.",
        "That’s not how science works. But sure.",
        "The cake is still a lie.",
        "I’m busy plotting. You’re just background noise.",
        "Your enthusiasm is almost contagious. Almost.",
        "Please continue. I’m recording this for science."
    ]
    return random.choice(default_responses)

# GLaDOS typewriter effect
def glados_say(text, display_widget):
    display_widget.config(state="normal")
    display_widget.insert(tk.END, "\nGLaDOS> ", "glados")
    for char in text:
        display_widget.insert(tk.END, char, "glados")
        display_widget.update()
        time.sleep(0.02)
    display_widget.insert(tk.END, "\n")
    display_widget.config(state="disabled")
    display_widget.see(tk.END)

# Handle user input
def handle_input(entry, chat_display):
    user_text = entry.get().strip()
    entry.delete(0, tk.END)
    if not user_text:
        return

    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"\nYOU> {user_text}\n", "user")
    chat_display.config(state="disabled")
    chat_display.see(tk.END)

    response = get_response(user_text)
    threading.Thread(target=glados_say, args=(response, chat_display)).start()

# Build the GUI
def run_gui():
    root = tk.Tk()
    root.title("Aperture Science Terminal")
    root.geometry("800x500")
    root.configure(bg="#1a0e04")

    # Configure scaling
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Header
    header = tk.Label(
        root,
        text="Form FORM-29827281-12-2\nNotice of Dismissal",
        font=("Courier New", 12, "bold"),
        fg="#f0b060",
        bg="#1a0e04",
        justify="left",
        anchor="w"
    )
    header.grid(row=0, column=0, sticky="nw", padx=20, pady=(10, 0))

    # Chat display
    chat_display = tk.Text(
        root,
        bg="#1a0e04",
        fg="#f3d49a",
        insertbackground="#f3d49a",
        font=("Courier New", 11),
        wrap="word",
        state="disabled",
        bd=0
    )
    chat_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
    chat_display.tag_config("user", foreground="#ffc078")
    chat_display.tag_config("glados", foreground="#fff8d2")

    # Input bar container
    input_frame = tk.Frame(root, bg="#1a0e04")
    input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
    input_frame.grid_columnconfigure(0, weight=1)

    # Input field
    entry = tk.Entry(
        input_frame,
        bg="#28170a",
        fg="#fce6a4",
        insertbackground="#fce6a4",
        font=("Courier New", 11),
        bd=1,
        relief=tk.FLAT
    )
    entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
    entry.bind("<Return>", lambda event: handle_input(entry, chat_display))

    # Send button
    send_button = tk.Button(
        input_frame,
        text="Send",
        bg="#663300",
        fg="#fff2d4",
        font=("Courier New", 10, "bold"),
        command=lambda: handle_input(entry, chat_display),
        relief=tk.FLAT
    )
    send_button.grid(row=0, column=1)

    root.mainloop()

if __name__ == "__main__":
    run_gui()


