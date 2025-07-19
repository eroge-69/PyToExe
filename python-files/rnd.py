import tkinter as tk
from tkinter import messagebox
import random

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=32, padding=18, color_bg="#393E46", color_fg="#FFD369", color_active="#00ADB5", font=("Segoe UI", 18, "bold")):
        tk.Canvas.__init__(self, parent, borderwidth=0, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.radius = radius
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_active = color_active
        self.font = font
        self.text = text
        self.padding = padding
        self.width = 260
        self.height = 2 * radius + padding
        self.configure(width=self.width, height=self.height)
        self.button = self.create_rounded_rect(2, 2, self.width-2, self.height-2, radius, fill=color_bg, outline=color_bg)
        self.label = self.create_text(self.width//2, self.height//2, text=text, fill=color_fg, font=font)
        self.bind_events()

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1,
                  x2-r, y1,
                  x2, y1,
                  x2, y1+r,
                  x2, y2-r,
                  x2, y2,
                  x2-r, y2,
                  x1+r, y2,
                  x1, y2,
                  x1, y2-r,
                  x1, y1+r,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def bind_events(self):
        self.tag_bind(self.button, "<Button-1>", self.on_click)
        self.tag_bind(self.label, "<Button-1>", self.on_click)
        self.tag_bind(self.button, "<Enter>", self.on_enter)
        self.tag_bind(self.label, "<Enter>", self.on_enter)
        self.tag_bind(self.button, "<Leave>", self.on_leave)
        self.tag_bind(self.label, "<Leave>", self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.itemconfig(self.button, fill=self.color_active, outline=self.color_active)
        self.itemconfig(self.label, fill="#222831")

    def on_leave(self, event):
        self.itemconfig(self.button, fill=self.color_bg, outline=self.color_bg)
        self.itemconfig(self.label, fill=self.color_fg)

class RandomNumberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sayı Oluşturucu")
        self.root.configure(bg="#222831")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.center_window(980, 420)

        self.main_frame = tk.Frame(root, bg="#222831")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(self.main_frame, text="🎲 Sayı Oluşturucu 🎲", font=("Segoe UI", 32, "bold"), fg="#FFD369", bg="#222831")
        self.title_label.pack(pady=(32, 18), fill=tk.X, expand=False)

        self.numbers_var = tk.StringVar()
        self.numbers_label = tk.Label(
            self.main_frame, textvariable=self.numbers_var, font=("Segoe UI", 38, "bold"), fg="#00ADB5", bg="#393E46",
            padx=60, pady=24, bd=0, relief=tk.FLAT, highlightthickness=0
        )
        self.numbers_label.pack(pady=28, fill=tk.X, expand=False)
        self.numbers_label.configure(borderwidth=0, highlightbackground="#393E46", highlightcolor="#393E46")
        self.numbers_label.after(10, lambda: self.numbers_label.config(bg="#393E46"))

        self.btn_frame = tk.Frame(self.main_frame, bg="#222831")
        self.btn_frame.pack(pady=18, fill=tk.BOTH, expand=True)

        self.generate_btn = RoundedButton(
            self.btn_frame, text="Sayı Oluştur", command=self.generate_numbers,
            color_bg="#393E46", color_fg="#FFD369", color_active="#00ADB5"
        )
        self.generate_btn.grid(row=0, column=0, padx=24, sticky="ew")

        self.copy_btn = RoundedButton(
            self.btn_frame, text="Kopyala", command=self.copy_numbers,
            color_bg="#393E46", color_fg="#FFD369", color_active="#00ADB5"
        )
        self.copy_btn.grid(row=0, column=1, padx=24, sticky="ew")

        self.clear_btn = RoundedButton(
            self.btn_frame, text="Temizle", command=self.clear_numbers,
            color_bg="#393E46", color_fg="#FFD369", color_active="#00ADB5"
        )
        self.clear_btn.grid(row=0, column=2, padx=24, sticky="ew")

        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        self.btn_frame.columnconfigure(2, weight=1)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def generate_numbers(self):
        numbers = random.sample(range(1, 61), 6)
        self.numbers_var.set("   ".join(map(str, numbers)))

    def copy_numbers(self):
        numbers = self.numbers_var.get()
        if numbers:
            self.root.clipboard_clear()
            self.root.clipboard_append(numbers)
            messagebox.showinfo("Copied", "Numbers copied to clipboard!")
        else:
            messagebox.showwarning("No Numbers", "Please generate numbers first.")

    def clear_numbers(self):
        self.numbers_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomNumberApp(root)
    root.mainloop()