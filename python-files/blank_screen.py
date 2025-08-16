import tkinter as tk

root = tk.Tk()
root.title("Animated Cursors")  # window title
root.geometry("600x400")
root.overrideredirect(True)  # remove default OS title bar
root.configure(bg="#2b2b2b")
root.attributes("-alpha", 0.0)

# Fade-in effect
def fade_in(alpha=0.0):
    if alpha < 1.0:
        alpha += 0.02
        root.attributes("-alpha", alpha)
        root.after(20, fade_in, alpha)

fade_in()

# Top bar drag
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

top_bar = tk.Frame(root, bg="#1e1e1e", height=30)
top_bar.pack(fill="x")
top_bar.bind("<Button-1>", start_move)
top_bar.bind("<ButtonRelease-1>", stop_move)
top_bar.bind("<B1-Motion>", do_move)

# Button hover helpers
def hover_in(btn):
    btn['bg'] = btn.hover_color
    btn['cursor'] = "hand2"

def hover_out(btn):
    btn['bg'] = btn.default_color
    btn['cursor'] = ""

# Close button
close_btn = tk.Label(top_bar, text="✕", bg="#ff5f57", fg="white", width=4)
close_btn.default_color = "#ff5f57"
close_btn.hover_color = "#ff7875"
close_btn.pack(side="right", padx=2, pady=2)
close_btn.bind("<Enter>", lambda e: hover_in(close_btn))
close_btn.bind("<Leave>", lambda e: hover_out(close_btn))
close_btn.bind("<Button-1>", lambda e: root.destroy())

# Minimize button
min_btn = tk.Label(top_bar, text="━", bg="#ffbd2e", fg="white", width=4)
min_btn.default_color = "#ffbd2e"
min_btn.hover_color = "#ffdb4a"
min_btn.pack(side="right", padx=2, pady=2)
min_btn.bind("<Enter>", lambda e: hover_in(min_btn))
min_btn.bind("<Leave>", lambda e: hover_out(min_btn))
min_btn.bind("<Button-1>", lambda e: root.iconify())

# Maximize/restore button
def toggle_maximize(event):
    if root.state() == "normal":
        root.state("zoomed")
    else:
        root.state("normal")

max_btn = tk.Label(top_bar, text="⬜", bg="#28c940", fg="white", width=4)
max_btn.default_color = "#28c940"
max_btn.hover_color = "#50e060"
max_btn.pack(side="right", padx=2, pady=2)
max_btn.bind("<Enter>", lambda e: hover_in(max_btn))
max_btn.bind("<Leave>", lambda e: hover_out(max_btn))
max_btn.bind("<Button-1>", toggle_maximize)

# Main content
content = tk.Frame(root, bg="#2b2b2b")
content.pack(expand=True, fill="both")
label = tk.Label(content, text="Hello! Custom Window Controls.", bg="#2b2b2b", fg="white", font=("Segoe UI", 16))
label.pack(pady=100)

root.mainloop()  # fully exits when window closes
