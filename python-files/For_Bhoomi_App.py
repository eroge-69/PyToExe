
import tkinter as tk
from tkinter import messagebox

# Main window
root = tk.Tk()
root.title("For Bhoomi 💖")
root.geometry("500x400")
root.configure(bg='#fff0f5')  # soft pink

# Canvas for heart background
canvas = tk.Canvas(root, width=500, height=400, bg='#fff0f5', highlightthickness=0)
canvas.place(x=0, y=0)

# Message label
main_message = tk.Label(
    root,
    text="Hey Bhoomi 💕\nHere’s a little surprise just for you 😊",
    font=("Comic Sans MS", 16, "bold"),
    bg='#fff0f5',
    fg='#d6336c',
    justify='center'
)
main_message.pack(pady=(40, 20))

# Animated text label
animated_label = tk.Label(
    root,
    text="",
    font=("Lucida Handwriting", 12),
    bg='#fff0f5',
    fg='#a83279',
    justify='center'
)
animated_label.pack(pady=(0, 20))

# Animation logic
messages = [
    "🌸 Hey SleepyHead ",
    "🌟 Good Morning ",
    "💖 I hope You Have a Wonderful Day",
    "✨ You’re magical"
]
index = 0

# Ask Practice Function
def ask_practice():
    response = messagebox.askquestion("Reminder 🔁", "Aaj practice krychi ahe ki nahi?")
    if response == 'yes':
        messagebox.showinfo("Good Job 👏", "That's the spirit! Keep going 💪")
    else:
        messagebox.showinfo("No Worries 🤗", "Take rest today, but don’t give up!")

# Practice Reminder Button
practice_btn = tk.Button(
    root,
    text="Practice Reminder 📝",
    font=("Arial Rounded MT Bold", 12),
    bg='#a29bfe',
    fg='white',
    activebackground='#b2a0ff',
    activeforeground='white',
    relief='raised',
    bd=3,
    command=ask_practice
)
practice_btn.pack(pady=(10, 20))

def animate_text():
    global index
    animated_label.config(text=messages[index])
    index = (index + 1) % len(messages)
    root.after(2500, animate_text)

animate_text()

# Surprise message
def show_surprise():
    messagebox.showinfo(
        "You're Special 💌",
        "💗 Reason #1: You’re stronger than you think 💪\n\n"
        "💬 Reason #2: One step at a time, you’re getting there 🚶‍♀️\n\n"
        "🌈 Reason #3: You bring magic wherever you go ✨\n\n"
        "P.S. You Have a lot more skills that you think 💌"
    )

# Button
btn = tk.Button(
    root,
    text="Click Me 💌",
    font=("Arial Rounded MT Bold", 13),
    bg='#ff69b4',
    fg='white',
    activebackground='#ff85c1',
    activeforeground='white',
    relief='raised',
    bd=3,
    command=show_surprise
)
btn.pack()

# Start the app
root.mainloop()
