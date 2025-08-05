import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime

class LogViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")
        self.root.geometry("1000x600")

        self.create_widgets()

    def create_widgets(self):
        # Filters Frame
        filter_frame = ttk.LabelFrame(self.root, text="Filters", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Level
        ttk.Label(filter_frame, text="Level:").grid(row=0, column=0, sticky="w")
        self.level_entry = ttk.Entry(filter_frame)
        self.level_entry.grid(row=0, column=1, padx=5)

        # Process
        ttk.Label(filter_frame, text="Process:").grid(row=0, column=2, sticky="w")
        self.process_entry = ttk.Entry(filter_frame)
        self.process_entry.grid(row=0, column=3, padx=5)

        # Thread
        ttk.Label(filter_frame, text="Thread:").grid(row=0, column=4, sticky="w")
        self.thread_entry = ttk.Entry(filter_frame)
        self.thread_entry.grid(row=0, column=5, padx=5)

        # Message
        ttk.Label(filter_frame, text="Message contains:").grid(row=1, column=0, sticky="w")
        self.message_entry = ttk.Entry(filter_frame, width=40)
        self.message_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="w")

        # Start and End Time
        ttk.Label(filter_frame, text="Start Time (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=0, sticky="w")
        self.start_time_entry = ttk.Entry(filter_frame, width=25)
        self.start_time_entry.grid(row=2, column=1, padx=5, sticky="w")

        ttk.Label(filter_frame, text="End Time (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=2, sticky="w")
        self.end_time_entry = ttk.Entry(filter_frame, width=25)
        self.end_time_entry.grid(row=2, column=3, padx=5, sticky="w")

        # Buttons
        ttk.Button(filter_frame, text="Open Log File", command=self.open_log_file).grid(row=3, column=0, pady=5)
        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=3, column=1, pady=5)

        # Results Frame
        self.tree = ttk.Treeview(self.root, columns=("timestamp", "level", "process", "thread", "file", "line", "message"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def open_log_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.load_logs()

    def load_logs(self):
        self.logs = []
        try:
            with open(self.file_path, encoding='utf-8') as f:
                for line in f:
                    try:
                        self.logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logs: {e}")

    def apply_filters(self):
        if not hasattr(self, 'logs'):
            messagebox.showwarning("Warning", "Please open a log file first.")
            return

        filtered_logs = []
        level = self.level_entry.get().strip()
        process = self.process_entry.get().strip()
        thread = self.thread_entry.get().strip()
        message_text = self.message_entry.get().strip().lower()
        start_time_str = self.start_time_entry.get().strip()
        end_time_str = self.end_time_entry.get().strip()

        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S') if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S') if end_time_str else None
        except ValueError:
            messagebox.showerror("Error", "Invalid datetime format.")
            return

        for log in self.logs:
            try:
                log_time = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
                if level and log['level'] != level:
                    continue
                if process and str(log['process']) != process:
                    continue
                if thread and str(log['thread']) != thread:
                    continue
                if message_text and message_text not in log['message'].lower():
                    continue
                if start_time and log_time < start_time:
                    continue
                if end_time and log_time > end_time:
                    continue
                filtered_logs.append(log)
            except Exception:
                continue

        self.display_logs(filtered_logs)

    def display_logs(self, logs):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for log in logs:
            self.tree.insert("", "end", values=(
                log['timestamp'], log['level'], log['process'], log['thread'],
                log.get('file', ''), log.get('line', ''), log['message']
            ))

if __name__ == '__main__':
    root = tk.Tk()
    app = LogViewer(root)
    root.mainloop()
