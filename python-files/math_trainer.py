import tkinter as tk
import random
import threading
import time

# Get screen size from a hidden root window
root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

def create_math_window():
    win = tk.Tk()
    win.title("Math Trainer")
    win.geometry("300x150")
    win.resizable(False, False)

    # Random starting position
    x = random.randint(0, screen_width - 300)
    y = random.randint(0, screen_height - 150)
    win.geometry(f"+{x}+{y}")

    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-"])
    answer = a + b if op == "+" else abs(a - b)
    problem_text = f"{max(a, b)} {op} {min(a, b)}"

    lbl = tk.Label(win, text=problem_text, font=("Arial", 16))
    lbl.pack(pady=10)

    entry = tk.Entry(win, font=("Arial", 14), justify="center")
    entry.pack(pady=5)

    feedback = tk.Label(win, text="", font=("Arial", 12))
    feedback.pack(pady=5)

    def check_answer(event=None):
        try:
            if int(entry.get()) == answer:
                win.destroy()
            else:
                feedback.config(text="Try again.", fg="red")
        except:
            feedback.config(text="Enter a number.", fg="red")

    entry.bind("<Return>", check_answer)

    dx = random.choice([-1, 1]) * 5
    dy = random.choice([-1, 1]) * 5

    def bounce():
        nonlocal x, y, dx, dy
        try:
            while True:
                x += dx
                y += dy

                # Bounce & Duplicate
                bounced = False
                if x <= 0 or x >= screen_width - 300:
                    dx = -dx
                    bounced = True
                if y <= 0 or y >= screen_height - 150:
                    dy = -dy
                    bounced = True
                if bounced:
                    threading.Thread(target=create_math_window, daemon=True).start()

                win.geometry(f"+{x}+{y}")
                time.sleep(0.03)
        except:
            pass  # Window closed

    threading.Thread(target=bounce, daemon=True).start()
    win.mainloop()

def spawn_initial_window():
    threading.Thread(target=create_math_window, daemon=True).start()

if __name__ == "__main__":
    spawn_initial_window()
    while True:
        time.sleep(1)



