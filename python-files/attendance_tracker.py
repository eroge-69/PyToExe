
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime

STATUS_OPTIONS = [
    "Work from Home",
    "Work from Office",
    "Full Day Leave",
    "Half Day Leave (WFH)",
    "Half Day Leave (WFO)"
]

STATUS_COLORS = {
    "Work from Home": "lightblue",
    "Work from Office": "lightgreen",
    "Full Day Leave": "lightcoral",
    "Half Day Leave (WFH)": "khaki",
    "Half Day Leave (WFO)": "orange"
}

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Tracker")

        self.today = datetime.today()
        self.year = self.today.year
        self.month = self.today.month

        self.attendance_data = {}

        self.create_widgets()
        self.draw_calendar()

    def create_widgets(self):
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)

        self.prev_btn = tk.Button(nav_frame, text="<", command=self.prev_month)
        self.prev_btn.pack(side=tk.LEFT)

        self.month_year_label = tk.Label(nav_frame, text="")
        self.month_year_label.pack(side=tk.LEFT, padx=10)

        self.next_btn = tk.Button(nav_frame, text=">", command=self.next_month)
        self.next_btn.pack(side=tk.LEFT)

        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack()

        self.stats_label = tk.Label(self.root, text="", font=("Arial", 12), justify=tk.LEFT)
        self.stats_label.pack(pady=10)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_year_label.config(text=f"{calendar.month_name[self.month]} {self.year}")

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=("Arial", 10, "bold")).grid(row=0, column=i)

        month_calendar = calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month)

        for r, week in enumerate(month_calendar, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                btn = tk.Button(self.calendar_frame, text=str(day), width=4,
                                command=lambda d=day: self.toggle_status(d))
                key = (self.year, self.month, day)
                status = self.attendance_data.get(key)
                if status:
                    btn.config(bg=STATUS_COLORS[status])
                btn.grid(row=r, column=c)

        self.update_stats()

    def toggle_status(self, day):
        key = (self.year, self.month, day)
        current_status = self.attendance_data.get(key)
        if current_status:
            next_index = (STATUS_OPTIONS.index(current_status) + 1) % len(STATUS_OPTIONS)
        else:
            next_index = 0
        new_status = STATUS_OPTIONS[next_index]
        self.attendance_data[key] = new_status
        self.draw_calendar()

    def update_stats(self):
        total_days = calendar.monthrange(self.year, self.month)[1]
        stats = {status: 0 for status in STATUS_OPTIONS}

        for day in range(1, total_days + 1):
            status = self.attendance_data.get((self.year, self.month, day))
            if status:
                stats[status] += 1

        total_present = stats["Work from Home"] + stats["Work from Office"] +                          0.5 * (stats["Half Day Leave (WFH)"] + stats["Half Day Leave (WFO)"])
        total_leave = stats["Full Day Leave"] + 0.5 * (stats["Half Day Leave (WFH)"] + stats["Half Day Leave (WFO)"])

        percent_present = (total_present / total_days) * 100
        percent_leave = (total_leave / total_days) * 100

        summary = (
            f"Attendance Summary for {calendar.month_name[self.month]} {self.year}:
"
            f"- Present: {percent_present:.1f}%
"
            f"- Leave: {percent_leave:.1f}%
"
            f"- Work from Office: {stats['Work from Office']} days
"
            f"- Work from Home: {stats['Work from Home']} days
"
            f"- Full Day Leave: {stats['Full Day Leave']} days
"
            f"- Half Day Leave (WFH): {stats['Half Day Leave (WFH)']} days
"
            f"- Half Day Leave (WFO): {stats['Half Day Leave (WFO)']} days"
        )
        self.stats_label.config(text=summary)

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

if __name__ == '__main__':
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
