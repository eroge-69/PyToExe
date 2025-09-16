import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import urllib.request

LOCAL_JSON = "courses.json"
ONLINE_JSON_URL = "https://yourserver.com/courses.json"

def load_course_presets():
    course_data = {}
    if os.path.exists(LOCAL_JSON):
        with open(LOCAL_JSON, "r") as f:
            course_data = json.load(f)
    return course_data

def update_courses_from_online():
    try:
        with urllib.request.urlopen(ONLINE_JSON_URL) as response:
            online_data = json.loads(response.read().decode())
            with open(LOCAL_JSON, "w") as f:
                json.dump(online_data, f, indent=4)
            return online_data
    except:
        return None

COURSE_PRESETS = load_course_presets()

class RaceTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Horse Race Timer")
        self.root.geometry("650x600")

        tk.Label(root, text="Select Racecourse:").pack(pady=5)
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(root, textvariable=self.course_var, values=list(COURSE_PRESETS.keys()), width=50)
        self.course_combo.pack()
        self.course_combo.bind("&lt;&lt;ComboboxSelected&gt;&gt;", self.update_course)

        self.info_label = tk.Label(root, text="", justify="left", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.track_canvas = tk.Canvas(root, width=600, height=200, bg="white")
        self.track_canvas.pack(pady=10)

        self.timer_label = tk.Label(root, text="00:00", font=("Arial", 24))
        self.timer_label.pack(pady=10)

        self.start_btn = tk.Button(root, text="Start Timer", command=self.start_timer)
        self.start_btn.pack(side=tk.LEFT, padx=20)

        self.reset_btn = tk.Button(root, text="Reset Timer", command=self.reset_timer)
        self.reset_btn.pack(side=tk.RIGHT, padx=20)

        self.update_btn = tk.Button(root, text="Check for Course Updates", command=self.check_for_updates)
        self.update_btn.pack(pady=10)

        self.running = False
        self.start_time = 0

    def update_course(self, event=None):
        course = self.course_var.get()
        if course in COURSE_PRESETS:
            data = COURSE_PRESETS[course]
            info_text = (f"Distance: {data['distance']}\n"
                         f"Markers: {data['markers']}\n"
                         f"Run-in: {data['run_in']}\n"
                         f"Confidence: {data['confidence']}")
            self.info_label.config(text=info_text)
            self.draw_track(data['markers'], data['run_in'], data['distance'])
        else:
            self.info_label.config(text="Course data not found.")
            self.track_canvas.delete("all")

    def draw_track(self, markers, run_in, distance):
        self.track_canvas.delete("all")
        width = 580
        height = 180
        margin = 10
        self.track_canvas.create_rectangle(margin, margin, width, height, outline="black", width=2)

        try:
            total_furlongs = float(distance.replace('f',''))
        except:
            total_furlongs = 16.0

        # Draw markers
        for m in markers.split(','):
            try:
                f = float(m.replace('f',''))
                x = margin + (f / total_furlongs) * (width - 2*margin)
                self.track_canvas.create_line(x, margin, x, height, fill="red", width=2)
                self.track_canvas.create_text(x, height+15, text=m, fill="red")
            except:
                continue

        # Draw run-in
        try:
            run_f = float(run_in.replace('f',''))
            x_run = width - (run_f / total_furlongs) * (width - 2*margin)
            self.track_canvas.create_line(x_run, margin, x_run, height, fill="green", width=3)
            self.track_canvas.create_text(x_run, margin-10, text="3F Pole / Run-in", fill="green")
        except:
            pass

    def start_timer(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            self.update_timer()

    def update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)

    def reset_timer(self):
        self.running = False
        self.timer_label.config(text="00:00")

    def check_for_updates(self):
        updated = update_courses_from_online()
        if updated:
            global COURSE_PRESETS
            COURSE_PRESETS = updated
            self.course_combo['values'] = list(COURSE_PRESETS.keys())
            messagebox.showinfo("Update Complete", "Course data updated successfully.")
        else:
            messagebox.showwarning("Update Failed", "Could not fetch updates. Check your internet connection.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RaceTimerApp(root)
    root.mainloop()