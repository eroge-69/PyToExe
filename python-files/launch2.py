import tkinter as tk
from tkinter import ttk
import time
import os

# === Raketenbestand aus Datei ===
MISSILE_FILE = "missiles.txt"
STARTING_MISSILES = 731

def load_missile_count():
    if not os.path.exists(MISSILE_FILE):
        with open(MISSILE_FILE, "w") as f:
            f.write(str(STARTING_MISSILES))
        return STARTING_MISSILES
    with open(MISSILE_FILE, "r") as f:
        return int(f.read().strip())

def save_missile_count(count):
    with open(MISSILE_FILE, "w") as f:
        f.write(str(count))

missile_total = load_missile_count()
assigned_missiles = {}  # Ziel→Anzahl-Zuweisung

# === Globale Variablen ===
attempts_remaining = 3
override_code = "2008"
correct_code = "1234567891234567"
selected_targets = []

# === Hauptfenster ===
root = tk.Tk()
root.attributes("-fullscreen", True)
root.title("Nuclear Missile Launch Control")
root.configure(bg="black")
root.geometry("1000x600")

def blink_label(label):
    def toggle():
        current = label.cget("fg")
        label.config(fg="red" if current == "black" else "black")
        label.after(500, toggle)
    toggle()

def build_lockout_screen():
    for widget in root.winfo_children():
        widget.destroy()

    lock_label = tk.Label(root, text="ALL ATTEMPTS EXHAUSTED", font=("Courier", 20, "bold"),
                          fg="red", bg="black")
    lock_label.pack(pady=(60, 20))
    blink_label(lock_label)

    override_label = tk.Label(root, text="Enter override code", font=("Courier", 16),
                              fg="white", bg="black")
    override_label.pack(pady=(30, 10))

    override_entry = tk.Entry(root, font=("Courier", 18), width=10, justify='center',
                              fg="white", bg="gray15", insertbackground="white")
    override_entry.pack()

    def check_override(event=None):
        if override_entry.get() == override_code:
            global attempts_remaining
            attempts_remaining = 3
            build_launch_screen()
        else:
            tk.Label(root, text="Invalid override code", font=("Courier", 14),
                     fg="red", bg="black").pack()

    override_entry.bind("<Return>", check_override)

def build_launch_screen(error_message=None):
    global code_boxes
    for widget in root.winfo_children():
        widget.destroy()

    title = tk.Label(root, text="NUCLEAR MISSILE LAUNCH CONTROL", font=("Courier", 20, "bold"),
                     fg="red", bg="black")
    title.pack(pady=(40, 10))

    subtitle = tk.Label(root, text="Please enter launch code", font=("Courier", 16), fg="white", bg="black")
    subtitle.pack(pady=(10, 20))

    code_frame = tk.Frame(root, bg="black")
    code_frame.pack()

    error_label = tk.Label(root, text=error_message or "", font=("Courier", 14), fg="red", bg="black")
    error_label.pack(pady=10)

    code_boxes = []

    def validate_digit(P):
        return P.isdigit() and len(P) <= 1

    def handle_invalid_code():
        global attempts_remaining
        attempts_remaining -= 1
        if attempts_remaining == 0:
            build_lockout_screen()
        else:
            build_launch_screen(error_message=f"Invalid code. {attempts_remaining} attempt(s) remaining.")

    def validate_code(entered):
        for widget in root.winfo_children():
            widget.destroy()

        validating = tk.Label(root, text="Validating code...", font=("Courier", 18), fg="white", bg="black")
        validating.pack(pady=20)
        progress = ttk.Progressbar(root, length=400, mode='determinate')
        progress.pack(pady=20)

        def finish():
            for i in range(101):
                progress['value'] = i
                root.update()
                time.sleep(0.01)
            if entered == correct_code:
                tk.Label(root, text="Code correct", font=("Courier", 18), fg="green", bg="black").pack(pady=20)
                root.after(2000, build_target_selection)
            else:
                handle_invalid_code()

        root.after(500, finish)

    def on_key(event, idx):
        if event.keysym.isdigit():
            if idx < 15:
                code_boxes[idx + 1].focus_set()
        elif event.keysym == "BackSpace":
            if code_boxes[idx].get() == "" and idx > 0:
                code_boxes[idx - 1].focus_set()
        entered = ''.join(box.get() for box in code_boxes)
        if len(entered) == 16:
            validate_code(entered)

    vcmd = (root.register(validate_digit), '%P')

    for i in range(16):
        entry = tk.Entry(code_frame, font=("Courier", 18), width=2, justify='center',
                         fg="white", bg="gray15", insertbackground="white",
                         validate='key', validatecommand=vcmd)
        entry.grid(row=0, column=i, padx=5)
        entry.bind("<KeyRelease>", lambda event, idx=i: on_key(event, idx))
        code_boxes.append(entry)

    code_boxes[0].focus_set()
# === Seite 2: TARGET SELECTION ===
def build_target_selection():
    for widget in root.winfo_children():
        widget.destroy()
    selected_targets.clear()

    countries = sorted([
        "United States", "Russia", "China", "Germany", "France", "United Kingdom", "India",
        "Japan", "Brazil", "Canada", "Australia", "South Korea", "Italy", "Mexico", "Spain",
        "Turkey", "Ukraine", "South Africa", "Egypt", "Argentina", "Poland", "Netherlands",
        "Sweden", "Saudi Arabia", "Iran", "Pakistan", "Indonesia", "Norway", "Switzerland",
        "Vietnam", "Thailand", "Israel", "Greece", "Portugal", "Belgium", "Finland"
    ])

    title = tk.Label(root, text="SELECT TARGET", font=("Courier", 20, "bold"), fg="red", bg="black")
    title.place(x=500, y=30, anchor="center")
    blink_label(title)

    center_frame = tk.Frame(root, bg="black")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    search_var = tk.StringVar()
    entry = tk.Entry(center_frame, textvariable=search_var, font=("Courier", 16),
                     fg="white", bg="gray15", insertbackground="white", width=30)
    entry.pack()

    suggestion_frame = tk.Frame(center_frame, bg="black")
    suggestion_frame.pack()

    selected_label = tk.Label(center_frame, text="Selected Targets: None", font=("Courier", 14),
                               fg="white", bg="black")
    selected_label.pack(pady=10)

    def update_selected_label():
        if selected_targets:
            selected_label.config(text="Selected Targets: " + ", ".join(selected_targets))
            next_button.config(state="normal", bg="red")
        else:
            selected_label.config(text="Selected Targets: None")
            next_button.config(state="disabled", bg="gray25")

    def show_suggestions(*args):
        text = search_var.get().strip().lower()
        for widget in suggestion_frame.winfo_children():
            widget.destroy()
        if not text: return
        matches = [c for c in countries if c.lower().startswith(text)]
        for country in matches[:4]:
            btn = tk.Button(suggestion_frame, text=country, font=("Courier", 14),
                            command=lambda c=country: select_country(c),
                            fg="white", bg="gray25", activebackground="gray40")
            btn.pack(pady=2)

    def select_country(name):
        if name not in selected_targets:
            selected_targets.append(name)
        search_var.set("")
        update_selected_label()
        show_suggestions()

    search_var.trace("w", show_suggestions)

    next_button = tk.Button(root, text="NEXT", font=("Courier", 14, "bold"),
                            state="disabled", bg="gray25", fg="white", padx=20, pady=5,
                            command=build_missile_assignment)
    next_button.place(x=830, y=560)
# === Seite 3: MISSILE ASSIGNMENT ===
def build_missile_assignment():
    for widget in root.winfo_children():
        widget.destroy()

    title = tk.Label(root, text="SELECT NUMBER OF MISSILES", font=("Courier", 20, "bold"), fg="red", bg="black")
    title.place(x=500, y=30, anchor="center")
    blink_label(title)

    count_label = tk.Label(root, text=f"Available missiles: {missile_total}", font=("Courier", 12),
                           fg="white", bg="black")
    count_label.place(x=10, y=10)

    assignment_frame = tk.Frame(root, bg="black")
    assignment_frame.place(relx=0.5, rely=0.5, anchor="center")

    fields = {}
    for target in selected_targets:
        row = tk.Frame(assignment_frame, bg="black")
        row.pack(pady=5)
        tk.Label(row, text=target, font=("Courier", 14), fg="white", bg="black", width=25, anchor="w").pack(side="left")
        var = tk.StringVar(value="0")
        entry = tk.Entry(row, textvariable=var, font=("Courier", 14),
                         fg="white", bg="gray15", insertbackground="white", width=5, justify="center")
        entry.pack(side="left")
        fields[target] = var

    warning = tk.Label(root, text="", font=("Courier", 14), fg="red", bg="black")
    warning.place(relx=0.5, rely=0.9, anchor="center")

    def validate_and_save():
        try:
            counts = [int(fields[t].get()) for t in selected_targets]
        except ValueError:
            warning.config(text="All values must be numbers.")
            return

        total_requested = sum(counts)
        global missile_total, assigned_missiles

        if missile_total == 0:
            warning.config(text="No missiles left to assign.")
            return

        if total_requested > missile_total:
            warning.config(text="Not enough missiles available.")
            return

        missile_total -= total_requested
        save_missile_count(missile_total)
        count_label.config(text=f"Available missiles: {missile_total}")
        assigned_missiles = {target: int(fields[target].get()) for target in selected_targets}
        warning.config(fg="green", text="Missile assignment saved successfully.")
        confirm_button.config(state="disabled", bg="gray25")

        root.after(1500, build_launch_overview)

    confirm_button = tk.Button(root, text="CONFIRM LAUNCH", font=("Courier", 14, "bold"),
                               bg="red", fg="white", padx=20, pady=5, command=validate_and_save)
    confirm_button.place(x=780, y=550)
def build_launch_overview():
    for widget in root.winfo_children():
        widget.destroy()
    root.title("LAUNCH OVERVIEW")

    # Überschrift (bleibt konstant rot)
    title = tk.Label(root, text="LAUNCH SEQUENCE OVERVIEW", font=("Courier", 20, "bold"),
                     fg="red", bg="black")
    title.pack(pady=20)

    # Übersicht aller Ziele
    overview_frame = tk.Frame(root, bg="black")
    overview_frame.pack(pady=10)

    for target in selected_targets:
        count = assigned_missiles.get(target, 0)
        label = tk.Label(overview_frame, text=f"{target}: {count} missile(s)", font=("Courier", 14),
                         fg="white", bg="black")
        label.pack()

    # Blinkende Startaufforderung
    launch_msg = tk.Label(root, text="PRESS RED BUTTON TO LAUNCH", font=("Courier", 16, "bold"),
                          fg="red", bg="black")
    launch_msg.pack(pady=40)

    def blink():
        current = launch_msg.cget("fg")
        launch_msg.config(fg="red" if current == "black" else "black")
        launch_msg.after(500, blink)
    blink()

    # POS1-Taste (Home) löst Start aus
    def on_pos1(event):
        build_terminal_sequence()

    root.bind("<Home>", on_pos1)
# === Seite 5: TERMINAL SEQUENCE ===
def build_terminal_sequence():
    for widget in root.winfo_children():
        widget.destroy()
    root.title("MISSILE LAUNCH TERMINAL")

    terminal = tk.Text(root, font=("Courier", 14), bg="black", fg="white", width=80, height=20)
    terminal.pack(pady=20)
    terminal.config(state="disabled")

    impact_timer = tk.Label(root, text="TIME TO IMPACT: 24:00", font=("Courier", 16, "bold"), fg="red", bg="black")
    impact_timer.pack()

    def append_line(text):
        terminal.config(state="normal")
        terminal.insert("end", text + "\n")
        terminal.config(state="disabled")
        terminal.see("end")

    def animate_dots(prefix, seconds, after=None):
        def tick(i=0):
            if i < seconds:
                append_line(prefix + "." * i)
                root.after(1000, lambda: tick(i + 1))
            else:
                if after:
                    after()
        tick()

    def launch_countdown():
        total = 180
        def tick():
            nonlocal total
            mins = total // 60
            secs = total % 60
            append_line(f"Launch in progress: {mins:02}:{secs:02}")
            total -= 1
            if total >= 0:
                root.after(1000, tick)
            else:
                post_launch_steps()
        tick()

    def post_launch_steps():
        messages = [
            "Stabilizing gyroscopes...",
            "Calibrating targeting systems...",
            "Uploading trajectory...",
            "Confirming satellite lock...",
            "Payloads armed. Trajectory stabilized.",
            "Open Missile Silo.",
            "Open Missile Silo..",
            "Open Missile Silo...",
            "Missile Silo Open",
            "Refueling of the first stage has started",
            "refuel first stag 1%",
            "refuel first stag 5%",
            "refuel first stag 10%",
            "refuel first stag 15%",
            "refuel first stag 20%",
            "refuel first stag 25%",
            "refuel first stag 30%",
            "refuel first stag 35%",
            "refuel first stag 40%",
            "refuel first stag 45%",
            "refuel first stag 50%",
            "refuel first stag 55%",
            "refuel first stag 60%",
            "refuel first stag 65%",
            "refuel first stag 70%",
            "refuel first stag 75%",
            "refuel first stag 80%",
            "refuel first stag 85%",
            "refuel first stag 90%",
            "refuel first stag 95%",
            "refuel first stag completed",
            "Refueling of the second stage has started",
            "refuel second stag 1%",
            "refuel second stag 5%",
            "refuel second stag 10%",
            "refuel second stag 15%",
            "refuel second stag 20%",
            "refuel second stag 25%",
            "refuel second stag 30%",
            "refuel second stag 35%",
            "refuel second stag 40%",
            "refuel second stag 45%",
            "refuel second stag 50%",
            "refuel second stag 55%",
            "refuel second stag 60%",
            "refuel second stag 65%",
            "refuel second stag 70%",
            "refuel second stag 75%",
            "refuel second stag 80%",
            "refuel second stag 85%",
            "refuel second stag 90%",
            "refuel second stag 95%",
            "refuel second stag completed",
            "engine started",
            "Missile Launch Confirm"
        ]
        for i, msg in enumerate(messages):
            root.after(i * 1500, lambda m=msg: append_line(m))
        root.after(len(messages)*1500 + 1000, impact_countdown)

    def impact_countdown():
        mins, secs = 24, 0
        def tick():
            nonlocal mins, secs
            impact_timer.config(text=f"TIME TO IMPACT: {mins:02}:{secs:02}")
            if mins == 0 and secs == 0:
                append_line("💥 IMPACT DETECTED — CONNECTION LOST.")
                return
            if secs == 0:
                mins -= 1
                secs = 59
            else:
                secs -= 1
            root.after(1000, tick)
        tick()

    append_line("Transmitting data to control center")
    animate_dots("Transmitting data", 20, launch_countdown)
# === Programmstart ===
build_launch_screen()
root.mainloop()
"create from Leon Gutsmiedl"