import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import csv
from collections import defaultdict

# -------------- Helper class for time input with AM/PM dropdown --------------
class TimeInput:
    def __init__(self, parent, row, label_text):
        tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=2)
        self.time_entry = tk.Entry(parent, width=10)
        self.time_entry.grid(row=row, column=1, sticky="w", padx=5)
        self.ampm_var = tk.StringVar(value="AM")
        self.ampm_menu = tk.OptionMenu(parent, self.ampm_var, "AM", "PM")
        self.ampm_menu.grid(row=row, column=2, sticky="w")
    def get_time(self):
        return f"{self.time_entry.get()} {self.ampm_var.get()}"

# -------------- Main Scheduler App --------------
class SchedulerApp:
    def __init__(self, master):
        self.master = master
        master.title("BICOL UNIVERSITY POLANGUI CLASS SCHEDULER PRO 4.0")
        master.geometry("1250x800")
        self.schedule_list = []
        self.create_header()
        self.create_feu_limit()
        self.create_inputs()
        self.create_buttons()
        self.create_schedule_display()

    def create_header(self):
        header = tk.Label(self.master, text="BICOL UNIVERSITY POLANGUI CLASS SCHEDULER PRO 4.0",
                          font=("Arial", 20, "bold"), fg="blue")
        header.pack(pady=10)

    def create_feu_limit(self):
        feu_frame = tk.Frame(self.master)
        feu_frame.pack(pady=5)
        tk.Label(feu_frame, text="Set Maximum FEU Limit:").grid(row=0, column=0, padx=5)
        self.feu_limit_entry = tk.Entry(feu_frame, width=5)
        self.feu_limit_entry.insert(0, "24")
        self.feu_limit_entry.grid(row=0, column=1, padx=5)

    def create_inputs(self):
        frame = tk.LabelFrame(self.master, text="Class Information", padx=10, pady=10)
        frame.pack(padx=10, pady=5, fill="x")

        tk.Label(frame, text="Faculty Name:").grid(row=0, column=0, sticky="e")
        self.faculty_entry = tk.Entry(frame, width=30)
        self.faculty_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame, text="Subject:").grid(row=0, column=2, sticky="e")
        self.subject_entry = tk.Entry(frame, width=30)
        self.subject_entry.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(frame, text="Program / Course:").grid(row=1, column=0, sticky="e")
        self.program_entry = tk.Entry(frame, width=30)
        self.program_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame, text="Year Level:").grid(row=1, column=2, sticky="e")
        self.yearlevel_entry = tk.Entry(frame, width=30)
        self.yearlevel_entry.grid(row=1, column=3, padx=5, pady=2)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        tk.Label(frame, text="--- Lecture Schedule ---", font=("Arial", 10, "bold")).grid(row=2, columnspan=4, pady=5)
        self.lecture_day_var = tk.StringVar(value="Monday")
        tk.Label(frame, text="Day:").grid(row=3, column=0, sticky="e")
        tk.OptionMenu(frame, self.lecture_day_var, *days).grid(row=3, column=1, sticky="w")
        self.lecture_start = TimeInput(frame, 4, "Start:")
        self.lecture_end = TimeInput(frame, 5, "End:")
        tk.Label(frame, text="Room:").grid(row=6, column=0, sticky="e")
        self.lecture_room_entry = tk.Entry(frame, width=10)
        self.lecture_room_entry.grid(row=6, column=1, sticky="w")
        tk.Label(frame, text="FEU:").grid(row=6, column=2, sticky="e")
        self.lecture_feu_entry = tk.Entry(frame, width=10)
        self.lecture_feu_entry.grid(row=6, column=3, sticky="w")

        tk.Label(frame, text="--- Laboratory Schedule ---", font=("Arial", 10, "bold")).grid(row=7, columnspan=4, pady=5)
        self.lab_day_var = tk.StringVar(value="Monday")
        tk.Label(frame, text="Day:").grid(row=8, column=0, sticky="e")
        tk.OptionMenu(frame, self.lab_day_var, *days).grid(row=8, column=1, sticky="w")
        self.lab_start = TimeInput(frame, 9, "Start:")
        self.lab_end = TimeInput(frame, 10, "End:")
        tk.Label(frame, text="Room:").grid(row=11, column=0, sticky="e")
        self.lab_room_entry = tk.Entry(frame, width=10)
        self.lab_room_entry.grid(row=11, column=1, sticky="w")
        tk.Label(frame, text="FEU:").grid(row=11, column=2, sticky="e")
        self.lab_feu_entry = tk.Entry(frame, width=10)
        self.lab_feu_entry.grid(row=11, column=3, sticky="w")

    def create_buttons(self):
        frame = tk.Frame(self.master)
        frame.pack(pady=10)
        tk.Button(frame, text="Add Schedule", command=self.add_schedule, width=18).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Delete Selected", command=self.delete_schedule, width=18).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Save", command=self.save_schedule, width=18).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Load", command=self.load_schedule, width=18).grid(row=0, column=3, padx=5)
        tk.Button(frame, text="FEU Summary", command=self.show_feu_summary_window, width=18).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Weekly Timetable", command=self.show_timetable, width=18).grid(row=0, column=5, padx=5)
        tk.Button(frame, text="Search Faculty", command=self.search_faculty_window, width=18).grid(row=0, column=6, padx=5)

    def create_schedule_display(self):
        frame = tk.LabelFrame(self.master, text="Class Schedule")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.schedule_listbox = tk.Listbox(frame, width=170, height=15)
        self.schedule_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar = tk.Scrollbar(frame, command=self.schedule_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.schedule_listbox.config(yscrollcommand=scrollbar.set)

    def add_schedule(self):
        faculty = self.faculty_entry.get().strip()
        subject = self.subject_entry.get().strip()
        program = self.program_entry.get().strip()
        yearlevel = self.yearlevel_entry.get().strip()
        if not faculty or not subject or not program or not yearlevel:
            messagebox.showerror("Input Error", "All fields are required.")
            return
        try:
            self.add_individual(faculty, subject, program, yearlevel, "Lecture",
                self.lecture_day_var.get(), self.lecture_start, self.lecture_end,
                self.lecture_room_entry.get(), self.lecture_feu_entry.get())
            self.add_individual(faculty, subject, program, yearlevel, "Laboratory",
                self.lab_day_var.get(), self.lab_start, self.lab_end,
                self.lab_room_entry.get(), self.lab_feu_entry.get())
            self.update_display()
            messagebox.showinfo("Success", "Schedule Added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_individual(self, faculty, subject, program, yearlevel, sched_type, day, start_obj, end_obj, room, feu):
        if not room or not feu: raise ValueError(f"{sched_type}: Room and FEU required.")
        try:
            feu_value = float(feu)
            if feu_value < 0: raise ValueError
        except ValueError:
            raise ValueError(f"{sched_type}: FEU must be positive.")
        try:
            start_dt = datetime.strptime(start_obj.get_time(), "%I:%M %p")
            end_dt = datetime.strptime(end_obj.get_time(), "%I:%M %p")
            if start_dt >= end_dt: raise ValueError(f"{sched_type}: End time must be after Start time.")
        except ValueError:
            raise ValueError(f"{sched_type}: Invalid time format.")
        for sched in self.schedule_list:
            if sched['day'] == day:
                existing_start = datetime.strptime(sched['start_time'], "%I:%M %p")
                existing_end = datetime.strptime(sched['end_time'], "%I:%M %p")
                overlap = not (end_dt <= existing_start or start_dt >= existing_end)
                if sched['room'] == room and overlap:
                    raise ValueError(f"{sched_type}: Room conflict at {day} {sched['start_time']} - {sched['end_time']}")
                if sched['faculty'] == faculty and overlap:
                    raise ValueError(f"{sched_type}: Faculty conflict at {day} {sched['start_time']} - {sched['end_time']}")
        self.schedule_list.append({'faculty': faculty, 'subject': subject, 'program': program, 'yearlevel': yearlevel,
            'type': sched_type, 'day': day, 'start_time': start_obj.get_time(), 'end_time': end_obj.get_time(),
            'room': room, 'feu': feu })

    def update_display(self):
        self.schedule_listbox.delete(0, tk.END)
        for sched in sorted(self.schedule_list, key=lambda x: (x['day'], datetime.strptime(x['start_time'], "%I:%M %p"))):
            entry = (f"{sched['day']} | {sched['faculty']} | {sched['subject']} | {sched['program']} | {sched['yearlevel']} | "
                     f"{sched['type']} | {sched['start_time']}-{sched['end_time']} | Room: {sched['room']} | FEU: {sched['feu']}")
            self.schedule_listbox.insert(tk.END, entry)

    def delete_schedule(self):
        selected = self.schedule_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No schedule selected.")
            return
        del self.schedule_list[selected[0]]
        self.update_display()

    def save_schedule(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file: return
        with open(file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'faculty','subject','program','yearlevel','type','day','start_time','end_time','room','feu'])
            writer.writeheader()
            writer.writerows(self.schedule_list)
        messagebox.showinfo("Saved", "Schedule saved successfully.")

    def load_schedule(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file: return
        try:
            with open(file, 'r') as f:
                reader = csv.DictReader(f)
                self.schedule_list = list(reader)
            self.update_display()
            messagebox.showinfo("Loaded", "Schedule loaded successfully.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def show_feu_summary_window(self):
        feu_summary = defaultdict(float)
        for sched in self.schedule_list:
            feu_summary[sched['faculty']] += float(sched['feu'])
        limit = float(self.feu_limit_entry.get())
        summary_window = tk.Toplevel(self.master)
        summary_window.title("Faculty FEU Summary")
        summary_window.geometry("400x400")
        text = tk.Text(summary_window, font=("Arial", 12))
        text.pack(fill="both", expand=True)
        for faculty, total_feu in feu_summary.items():
            status = "OVERLOAD" if total_feu > limit else "OK"
            text.insert(tk.END, f"{faculty}: {total_feu} FEU ({status})\n")

    def show_timetable(self):
        timetable = tk.Toplevel(self.master)
        timetable.title("Weekly Timetable View")
        timetable.geometry("1200x600")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        tk.Label(timetable, text="Weekly Timetable", font=("Arial", 16, "bold")).pack(pady=10)
        text = tk.Text(timetable, font=("Arial", 11))
        text.pack(fill="both", expand=True)
        for day in days:
            text.insert(tk.END, f"\n{day}:\n")
            daily_sched = [s for s in self.schedule_list if s['day'] == day]
            daily_sched.sort(key=lambda x: datetime.strptime(x['start_time'], "%I:%M %p"))
            for sched in daily_sched:
                text.insert(tk.END, f"  {sched['start_time']}-{sched['end_time']} | {sched['subject']} | {sched['faculty']} | Room: {sched['room']} | Type: {sched['type']}\n")

    def search_faculty_window(self):
        search_win = tk.Toplevel(self.master)
        search_win.title("Search Faculty Schedule")
        search_win.geometry("700x500")
        tk.Label(search_win, text="Enter Faculty Name:", font=("Arial", 12)).pack(pady=5)
        search_entry = tk.Entry(search_win, font=("Arial", 12), width=40)
        search_entry.pack(pady=5)
        result_box = tk.Text(search_win, font=("Arial", 11))
        result_box.pack(fill="both", expand=True)

        def search():
            name = search_entry.get().strip().lower()
            result_box.delete("1.0", tk.END)
            if not name:
                result_box.insert(tk.END, "Please enter faculty name.\n")
                return
            found = False
            for sched in self.schedule_list:
                if sched['faculty'].lower() == name:
                    found = True
                    result_box.insert(tk.END, f"{sched['day']} | {sched['start_time']}-{sched['end_time']} | {sched['subject']} | Room: {sched['room']} | {sched['type']}\n")
            if not found:
                result_box.insert(tk.END, "No schedule found for this faculty.")
        tk.Button(search_win, text="Search", font=("Arial", 12), command=search).pack(pady=10)

# -------------- Run the App --------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
