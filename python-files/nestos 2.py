import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os

root = tk.Tk()
root.title("NestOS GUI Desktop (No Pillow)")
root.geometry("950x600")
root.config(bg="#1f1f1f")

tk.Label(root, text="NestOS Desktop — Powered by Nestoras 🧠", fg="white", bg="#1f1f1f", font=("Segoe UI", 16)).pack(pady=10)

# 📝 NestPad
def open_nestpad():
    win = tk.Toplevel()
    win.title("NestPad 📝")
    text = tk.Text(win, font=("Segoe UI", 11))
    text.pack(expand=True, fill="both")

    def save():
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", tk.END))
            messagebox.showinfo("Saved", f"Text saved:\n{file}")

    def load():
        file = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                text.delete("1.0", tk.END)
                text.insert("1.0", f.read())

    bar = tk.Frame(win)
    bar.pack()
    tk.Button(bar, text="💾 Save", command=save).pack(side="left", padx=5)
    tk.Button(bar, text="📂 Open", command=load).pack(side="left", padx=5)

# 🎨 NestPaint
def open_nestpaint():
    win = tk.Toplevel()
    win.title("NestPaint 🎨")
    canvas = tk.Canvas(win, bg="white", width=500, height=400)
    canvas.pack()
    color = "#000000"

    def draw(event):
        x, y = event.x, event.y
        canvas.create_oval(x-2, y-2, x+2, y+2, fill=color, outline=color)

    def pick_color():
        nonlocal color
        new = colorchooser.askcolor()[1]
        if new:
            color = new
            swatch.config(bg=color)

    def save_art():
        file = filedialog.asksaveasfilename(defaultextension=".ps")
        if file:
            canvas.postscript(file=file)
            messagebox.showinfo("Saved", f"Artwork saved as:\n{file}")

    canvas.bind("<B1-Motion>", draw)
    controls = tk.Frame(win)
    controls.pack()
    swatch = tk.Label(controls, bg=color, width=3, height=1)
    swatch.pack(side="left", padx=5)
    tk.Button(controls, text="🎨 Color", command=pick_color).pack(side="left", padx=5)
    tk.Button(controls, text="💾 Save as .ps", command=save_art).pack(side="left", padx=5)

# 💻 NestCMD
def open_cmd():
    win = tk.Toplevel()
    win.title("NestCMD 💻")
    output = tk.Text(win, height=15, bg="black", fg="lime", insertbackground="lime")
    output.pack()
    entry = tk.Entry(win, bg="gray", fg="white")
    entry.pack(fill="x")

    def run_cmd(e=None):
        cmd = entry.get()
        entry.delete(0, tk.END)
        try:
            result = os.popen(cmd).read()
            output.insert(tk.END, f"> {cmd}\n{result}\n")
        except:
            output.insert(tk.END, f"> {cmd}\nError\n")

    entry.bind("<Return>", run_cmd)

# 🎞️ NestAnimator
def open_animator():
    win = tk.Toplevel()
    win.title("NestAnimator 🎞️")
    canvas = tk.Canvas(win, bg="white", width=500, height=300)
    canvas.pack()

    def paint(event):
        canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="black")

    def save_frame():
        file = filedialog.asksaveasfilename(defaultextension=".ps")
        if file:
            canvas.postscript(file=file)
            messagebox.showinfo("Saved", f"Frame saved as .ps:\n{file}")

    canvas.bind("<B1-Motion>", paint)
    tk.Button(win, text="📸 Save Frame", command=save_frame).pack(pady=5)

# 🎬 MovieMaker (Preview .ps list — simulated)
def open_movie_maker():
    win = tk.Toplevel()
    win.title("NestMovieMaker 🎬")
    tk.Label(win, text="This previews saved .ps files.\n(Open externally to view animation)", font=("Segoe UI", 11)).pack(pady=30)

# 🖥️ Desktop App Buttons
apps = [
    ("📄 NestPad", open_nestpad),
    ("🎨 NestPaint", open_nestpaint),
    ("🎞️ Animator", open_animator),
    ("🎬 MovieMaker", open_movie_maker),
    ("💻 CMD", open_cmd),
]

for i, (name, func) in enumerate(apps):
    tk.Button(root, text=name, font=("Segoe UI", 11), width=15, command=func).place(x=100 + i * 160, y=120)

root.mainloop()
