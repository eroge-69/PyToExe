import tkinter as tk
from tkinter import messagebox, ttk
import time

# Questions
questions = [
    "Do you like games?",
    "Are you ready to play Clean Fight?",
    "Do you think you will win?",
    "Should we continue?",
    "Do you like Garic?"
]

current_question = 0

def ask_question():
    global current_question
    if current_question < len(questions) - 1:
        response = messagebox.askyesno("Question", questions[current_question])
        current_question += 1
        ask_question()
    else:
        # Last question: only "No" closes it
        answer = messagebox.askyesno("Final Question", questions[-1])
        if answer:  # If Yes
            messagebox.showwarning("Blocked", "You can't quit by pressing Yes 😅")
            ask_question()
        else:
            messagebox.showinfo("End", "Thanks for playing! 🎉")
            root.destroy()

def show_loading():
    loading_window = tk.Toplevel(root)
    loading_window.title("Loading...")
    loading_window.geometry("400x120")
    loading_window.resizable(False, False)

    label = tk.Label(loading_window, text="Loading, please wait...")
    label.pack(pady=10)

    progress = ttk.Progressbar(loading_window, orient="horizontal",
                               length=300, mode="determinate", maximum=100)
    progress.pack(pady=10)

    loading_window.update()

    # Run fake loading 3 times
    for _ in range(3):
        for i in range(101):
            progress['value'] = i
            loading_window.update_idletasks()
            time.sleep(0.02)
        for i in range(100, -1, -1):
            progress['value'] = i
            loading_window.update_idletasks()
            time.sleep(0.01)

    messagebox.showinfo("Just Joking!", "😂 I'm just joking! Everything is fine.")
    loading_window.destroy()

    # After loading, start questions
    ask_question()

# Root window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Disable X button so user can’t close app directly
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Start with loading screen
show_loading()

root.mainloop()
