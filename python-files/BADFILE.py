import tkinter as tk
import random

class SpamApp:
    def __init__(self, root, char_set):
        self.root = root
        self.char_set = char_set
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.start_spam()

    def start_spam(self):
        self.root.after(1, self.spam_string)
        self.root.after(1, self.show_error)
        self.root.after(1, self.show_warning)
        self.root.after(1, self.start_spam)

    def spam_string(self):
        self.spam = ''.join(random.choices(self.char_set, k=10))
        print(f'{self.spam}')

    def show_error(self):
        error = tk.Toplevel(self.root)
        error.title("{self.spam}")
        tk.Label(error, text=f"{self.spam}", fg="red").pack()
        tk.Button(error, text="OK", command=error.destroy).pack()
        error.attributes("-topmost", True)
        x_position = random.randint(0, self.screen_width - 200)
        y_position = random.randint(0, self.screen_height - 100)
        error.geometry(f"+{x_position}+{y_position}")
    
    def show_warning(self):
        warning = tk.Toplevel(self.root)
        warning.title("{self.spam}")
        tk.Label(warning, text=f"{self.spam}", fg="orange").pack()
        tk.Button(warning, text="OK", command=warning.destroy).pack()
        warning.attributes("-topmost", True)
        x_position = random.randint(0, self.screen_width - 200)
        y_position = random.randint(0, self.screen_height - 100)
        warning.geometry(f"+{x_position}+{y_position}")

if __name__ == "__main__":
    root = tk.Tk()
    char_set = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()[]{}:;'\",<.>/?`~"  # Customizable character set
    app = SpamApp(root, char_set)
    root.mainloop()
