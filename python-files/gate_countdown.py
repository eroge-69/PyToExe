import tkinter as tk
from datetime import datetime
import random
import threading
import socket
import google.generativeai as genai
import sys
import winreg
# ----------------- CONFIG -----------------
exam_date = datetime(2026, 2, 1)
study_start = datetime(2025, 7, 25)  # Adjust if you start later

apis = [
    "AIzaSyC0JRpR9A8cGNDbZYxT6FzOlgkZnf1jtUI",
    "AIzaSyApEgrC0hX7tOHEsm2Kvq-QCLk6uWk95IU",
    "AIzaSyAMPBD98YbdfQciEN9vCkzrgbjcljWL_4o",
    "AIzaSyD5V0_D8H-IvXlaA6mFw2lpwhfyAodnh1g",
    "AIzaSyAWv1huaDSO-708mBU1yWNNQagnWqPVllw"
]
api_key = random.choice(apis)
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

spinner_frames = ["⠋", "⠙", "⠸", "⠴", "⠦", "⠇"]
spinner_index = 0
spinner_running = False

# ----------------- LOAD SCHEDULE -----------------
def load_schedule_from_file(path=r"C:\Users\sachi\OneDrive\Desktop\Python\timer\schedule.txt"):
    weekday_schedule = {}
    weekly_topics = {}
    section = None

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line == "[WEEKLY_TOPICS]":
                section = "weekly"
                continue
            elif line == "[WEEKDAY_SCHEDULE]":
                section = "weekday"
                continue

            if section == "weekly":
                key, val = line.split("=", 1)
                weekly_topics[int(key.strip())] = val.strip()
            elif section == "weekday":
                key, val = line.split("=", 1)
                weekday_schedule[key.strip()] = [item.strip() for item in val.split(";")]

    return weekday_schedule, weekly_topics

try:
    weekday_schedule, weekly_topics = load_schedule_from_file("schedule.txt")
except FileNotFoundError:
    print("schedule.txt not found. Exiting.")
    exit(1)

# ----------------- INTERNET CHECK -----------------
def check_internet(host="8.8.8.8", port=53, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# ----------------- FUNCTIONS -----------------
def update_days_left():
    today = datetime.now()
    delta = exam_date - today
    countdown_label.config(text=f"{delta.days} Days Left for GATE 2026")

def start_spinner():
    global spinner_running, spinner_index
    spinner_running = True
    spinner_index = 0
    animate_spinner()

def stop_spinner():
    global spinner_running
    spinner_running = False

def animate_spinner():
    global spinner_index
    if spinner_running:
        char = spinner_frames[spinner_index % len(spinner_frames)]
        quote_label.config(text=f"Fetching quote... {char}")
        spinner_index += 1
        root.after(100, animate_spinner)

def fetch_quote():
    if not check_internet():
        quote_label.config(text="Believe in yourself. You got this!")
        return

    start_spinner()
    def worker():
        try:
            response = model.generate_content("Give one short motivational quote for GATE exam preparation (max 1-2 lines).")
            quote = response.text.strip().replace("*", "")
        except Exception:
            quote = "Believe in yourself. You got this!"
        stop_spinner()
        quote_label.config(text=f"{quote}")
    threading.Thread(target=worker, daemon=True).start()

def show_today_plan():
    today = datetime.now()
    weekday = today.strftime("%A")
    week_no = ((today - study_start).days // 7) + 1
    total_weeks = max(weekly_topics.keys())
    week_no = min(week_no, total_weeks)  # Don't go beyond last week

    week_topic = weekly_topics.get(week_no, "Review & Practice")
    plan_lines = weekday_schedule.get(weekday, ["Rest / Custom Study Plan"])
    today_text = f"📅 {weekday} Plan:\n" + "\n".join("• " + item for item in plan_lines)
    week_text = f"🧭 Week {week_no}/{total_weeks} Focus: {week_topic}"
    today_plan_label.config(text=today_text)
    week_plan_label.config(text=week_text)

def update_wraplength():
    width = root.winfo_width()
    quote_label.config(wraplength=width - 40)
    countdown_label.config(wraplength=width - 40)
    today_plan_label.config(wraplength=width - 40)
    week_plan_label.config(wraplength=width - 40)

def close_app(event=None):
    root.destroy()

def start_move(event):
    root._drag_start_x = event.x
    root._drag_start_y = event.y

def do_move(event):
    x = event.x_root - root._drag_start_x
    y = event.y_root - root._drag_start_y
    root.geometry(f"+{x}+{y}")

def bind_drag(widget):
    widget.bind("<Button-1>", start_move)
    widget.bind("<B1-Motion>", do_move)

# ----------------- GUI -----------------
root = tk.Tk()
root.title("GATE Countdown")
# Position the window to the right side of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 440
window_height = 370
x = screen_width - window_width - 1  # 20px padding from right
y = 1  # distance from top
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.configure(bg="#121212")
root.overrideredirect(True)

container = tk.Frame(root, bg="#1f1f1f", highlightthickness=2, highlightbackground="#3f3f3f")
container.pack(fill="both", expand=True, padx=6, pady=6)

# Top bar
top_bar = tk.Frame(container, bg="#1f1f1f")
top_bar.pack(fill="x", padx=6, pady=(4, 0))

refresh_btn = tk.Label(top_bar, text="🔄", font=("Segoe UI Emoji", 12), bg="#1f1f1f", fg="#888", cursor="hand2")
refresh_btn.pack(side="left")
refresh_btn.bind("<ButtonRelease-1>", lambda e: fetch_quote())
bind_drag(refresh_btn)

close_btn = tk.Label(top_bar, text="❌", font=("Segoe UI Emoji", 12), bg="#1f1f1f", fg="#888", cursor="hand2")
close_btn.pack(side="right")
close_btn.bind("<ButtonRelease-1>", close_app)
bind_drag(close_btn)

bind_drag(top_bar)

# Labels
countdown_label = tk.Label(container, text="", font=("Segoe UI", 16, "bold"), fg="#FFD369", bg="#1f1f1f", justify="center")
countdown_label.pack(pady=(8, 4), padx=10, fill="x")
bind_drag(countdown_label)

quote_label = tk.Label(
    container,
    text="Fetching quote...",
    font=("Segoe UI", 12, "italic"),
    fg="#FFD369",
    bg="#1f1f1f",
    wraplength=400,
    justify="center",
    anchor="center",
    padx=12,
    pady=10
)
quote_label.pack(pady=(5, 10), padx=10, fill="x")
bind_drag(quote_label)

today_plan_label = tk.Label(container, text="", font=("Segoe UI", 10), fg="#CCCCCC", bg="#1f1f1f", justify="left")
today_plan_label.pack(pady=(0, 4), padx=10, fill="x")
bind_drag(today_plan_label)

week_plan_label = tk.Label(container, text="", font=("Segoe UI", 10, "bold"), fg="#AAAFFF", bg="#1f1f1f", justify="left")
week_plan_label.pack(pady=(0, 10), padx=10, fill="x")
bind_drag(week_plan_label)

root.bind("<Configure>", lambda e: update_wraplength())

# ----------------- START -----------------
update_days_left()
fetch_quote()
show_today_plan()
root.mainloop()
