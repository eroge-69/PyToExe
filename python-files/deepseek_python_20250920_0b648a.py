# JEE_TRACKER_MODERN.py
# Convert this to EXE using: pyinstaller, auto-py-to-exe, or any online converter

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
from collections import defaultdict
import os

# Modern color scheme
DARK_BG = "#1e293b"
LIGHT_BG = "#f8fafc"
PRIMARY = "#2563eb"
SUCCESS = "#22c55e"
DANGER = "#ef4444"
TEXT_LIGHT = "white"
TEXT_DARK = "black"

class ModernJEETracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 JEE Study Tracker Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg=DARK_BG)
        
        self.log_file = "jee_progress.txt"
        self.dark_mode = True
        self.setup_ui()
        self.load_progress()
        
    def setup_ui(self):
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main container
        main_container = tk.Frame(self.root, bg=DARK_BG)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Header
        header = tk.Frame(main_container, bg=DARK_BG, height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        title_label = tk.Label(header, text="🔥 JEE STUDY TRACKER PRO", 
                              font=("Arial", 20, "bold"), fg="#fbbf24", bg=DARK_BG)
        title_label.pack(pady=20)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg=DARK_BG, width=200, relief="raised", bd=2)
        sidebar.grid(row=1, column=0, sticky="ns", padx=(0, 20))
        sidebar.grid_propagate(False)
        
        # Sidebar buttons
        buttons = [
            ("📝 Log Progress", self.log_progress),
            ("📊 View Progress", self.view_progress),
            ("📅 Weekly Summary", self.weekly_summary),
            ("📈 Subject Analysis", self.subject_analysis),
            ("🔄 Reset Progress", self.reset_progress),
            ("🎯 Analytics", self.show_analytics),
            ("🌙 Toggle Theme", self.toggle_theme),
            ("❌ Exit", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, command=command,
                           font=("Arial", 12), bg=PRIMARY, fg="white",
                           width=20, height=2, relief="flat", cursor="hand2")
            btn.pack(pady=5, padx=10, fill="x")
        
        # Display area
        display_frame = tk.Frame(main_container, bg=DARK_BG)
        display_frame.grid(row=1, column=1, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)
        
        self.text_area = scrolledtext.ScrolledText(display_frame, 
                                                  font=("Consolas", 11),
                                                  bg="#2d3748", fg="white",
                                                  relief="flat", bd=2)
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Status bar
        self.status_bar = tk.Label(self.root, 
                                  text="Ready • Sessions: 0 • Last: Never",
                                  font=("Arial", 10), 
                                  fg="#64748b", bg=DARK_BG)
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
    def log_progress(self):
        log_window = tk.Toplevel(self.root)
        log_window.title("📝 Log Study Session")
        log_window.geometry("500x600")
        log_window.configure(bg=DARK_BG)
        log_window.resizable(False, False)
        
        # Form fields
        fields = [
            ("Subject", "combobox", ["Physics", "Chemistry", "Maths"]),
            ("Chapter", "entry", "Enter chapter name"),
            ("Source", "entry", "NCERT, HC Verma, PYQs, etc."),
            ("Questions Solved", "entry", "0"),
            ("Study Time (hours)", "entry", "0.0"),
            ("Difficulty", "combobox", ["Easy", "Medium", "Hard"]),
            ("Notes", "entry", "Optional notes...")
        ]
        
        entries = {}
        for i, (label, field_type, options) in enumerate(fields):
            tk.Label(log_window, text=label, font=("Arial", 11, "bold"), 
                    fg="white", bg=DARK_BG).grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            if field_type == "combobox":
                entry = ttk.Combobox(log_window, values=options, font=("Arial", 11), width=25)
                entry.set(options[0])
            else:
                entry = tk.Entry(log_window, font=("Arial", 11), width=28, 
                                bg="#374151", fg="white", insertbackground="white")
                entry.insert(0, options)
            
            entry.grid(row=i, column=1, padx=20, pady=10, sticky="w")
            entries[label] = entry
        
        def save_session():
            try:
                date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                log_entry = (
                    f"Date: {date}\n"
                    f"Subject: {entries['Subject'].get()}\n"
                    f"Chapter: {entries['Chapter'].get()}\n"
                    f"Source: {entries['Source'].get()}\n"
                    f"Questions: {entries['Questions Solved'].get()}\n"
                    f"Time: {entries['Study Time (hours)'].get()} hrs\n"
                    f"Difficulty: {entries['Difficulty'].get()}\n"
                    f"Notes: {entries['Notes'].get()}\n"
                    f"{'='*50}\n"
                )
                
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                
                messagebox.showinfo("Success", "✅ Study session logged successfully!")
                log_window.destroy()
                self.view_progress()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        save_btn = tk.Button(log_window, text="💾 Save Session", command=save_session,
                            font=("Arial", 12, "bold"), bg=SUCCESS, fg="white",
                            width=15, height=2, cursor="hand2")
        save_btn.grid(row=len(fields), column=1, pady=20, sticky="e")
        
        log_window.grid_columnconfigure(1, weight=1)
    
    def view_progress(self):
        self.clear_display()
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = f.read()
                if content:
                    self.text_area.insert("end", "📊 YOUR STUDY PROGRESS 📊\n\n")
                    self.text_area.insert("end", content)
                    session_count = content.count('='*50)
                    self.update_status(session_count)
                else:
                    self.text_area.insert("end", "🎯 No logs yet. Start your JEE journey! 🚀")
        except FileNotFoundError:
            self.text_area.insert("end", "📝 Welcome! Log your first study session to begin!")
    
    def weekly_summary(self):
        self.clear_display()
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs = f.readlines()
            
            weekly_data = defaultdict(lambda: {"Physics": 0, "Chemistry": 0, "Maths": 0, "Time": 0.0})
            
            for i in range(0, len(logs), 9):
                if i + 8 >= len(logs):
                    continue
                    
                try:
                    date_str = logs[i].split(": ")[1].strip()
                    date = datetime.datetime.strptime(date_str, "%d-%m-%Y %H:%M")
                    week_num = date.isocalendar()[1]
                    
                    subject = logs[i+1].split(": ")[1].strip()
                    questions = int(logs[i+4].split(": ")[1])
                    time = float(logs[i+5].split(": ")[1].split()[0])
                    
                    weekly_data[week_num][subject] += questions
                    weekly_data[week_num]["Time"] += time
                except:
                    continue
            
            self.text_area.insert("end", "📅 WEEKLY SUMMARY 📅\n\n")
            for week, data in weekly_data.items():
                self.text_area.insert("end", f"Week {week}:\n")
                for subject in ["Physics", "Chemistry", "Maths"]:
                    if data[subject] > 0:
                        self.text_area.insert("end", f"  {subject}: {data[subject]} questions\n")
                self.text_area.insert("end", f"  Total Time: {data['Time']:.1f} hrs\n\n")
                
        except FileNotFoundError:
            self.text_area.insert("end", "No data yet. Log your first session! 🚀")
    
    def subject_analysis(self):
        self.clear_display()
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs = f.readlines()
            
            subject_data = defaultdict(lambda: {"Questions": 0, "Time": 0.0, "Chapters": set()})
            
            for i in range(0, len(logs), 9):
                if i + 8 >= len(logs):
                    continue
                    
                try:
                    subject = logs[i+1].split(": ")[1].strip()
                    chapter = logs[i+2].split(": ")[1].strip()
                    questions = int(logs[i+4].split(": ")[1])
                    time = float(logs[i+5].split(": ")[1].split()[0])
                    
                    subject_data[subject]["Questions"] += questions
                    subject_data[subject]["Time"] += time
                    subject_data[subject]["Chapters"].add(chapter)
                except:
                    continue
            
            self.text_area.insert("end", "📈 SUBJECT-WISE ANALYSIS 📈\n\n")
            for subject, data in subject_data.items():
                self.text_area.insert("end", f"{subject}:\n")
                self.text_area.insert("end", f"  Total Questions: {data['Questions']}\n")
                self.text_area.insert("end", f"  Total Time: {data['Time']:.1f} hrs\n")
                self.text_area.insert("end", f"  Chapters Covered: {len(data['Chapters'])}\n\n")
                
        except FileNotFoundError:
            self.text_area.insert("end", "No data yet. Log your first session! 🚀")
    
    def show_analytics(self):
        self.clear_display()
        self.text_area.insert("end", "📈 STUDY ANALYTICS\n\n")
        self.text_area.insert("end", "• Time spent per subject\n")
        self.text_area.insert("end", "• Weak topics identification\n")
        self.text_area.insert("end", "• Daily study streaks\n")
        self.text_area.insert("end", "• Progress over time\n")
        self.text_area.insert("end", "• Comparison with targets\n")
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.root.configure(bg=DARK_BG)
            self.text_area.configure(bg="#2d3748", fg="white")
        else:
            self.root.configure(bg=LIGHT_BG)
            self.text_area.configure(bg="white", fg="black")
        messagebox.showinfo("Theme", f"Theme changed to {'Dark' if self.dark_mode else 'Light'}")
    
    def reset_progress(self):
        if messagebox.askyesno("Confirm", "⚠️ Delete ALL progress? This cannot be undone!"):
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("")
                messagebox.showinfo("Success", "✅ Progress reset successfully!")
                self.view_progress()
            except:
                messagebox.showerror("Error", "Could not reset progress")
    
    def update_status(self, session_count):
        last_update = datetime.datetime.now().strftime("%H:%M")
        self.status_bar.configure(
            text=f"✅ Ready • Sessions: {session_count} • Last: {last_update}"
        )
    
    def clear_display(self):
        self.text_area.delete("1.0", "end")
    
    def load_progress(self):
        self.view_progress()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernJEETracker(root)
    root.mainloop()