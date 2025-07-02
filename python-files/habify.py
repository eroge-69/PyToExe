import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime

class HabifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habify")
        self.tasks = []
        self.current_theme = "Mint"

        self.themes = {
            "Dark": {"bg": "#1e1e1e", "fg": "#d4d4d4"},
            "Mint": {"bg": "#2b2f2e", "fg": "#aef8d3"},
            "Sunset": {"bg": "#3c1c3e", "fg": "#ffc4a3"},
            "Ocean": {"bg": "#102f3e", "fg": "#73d2de"},
            "Cyber": {"bg": "#000000", "fg": "#00ff9f"},
        }

        self.setup_ui()
        self.apply_theme(self.current_theme)

    def setup_ui(self):
        self.style = ttk.Style(self.root)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.header = tk.Label(self.main_frame, text="Habify", font=("Arial", 24, "bold"))
        self.header.pack(pady=10)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.checklist_tab = tk.Frame(self.notebook)
        self.calendar_tab = tk.Frame(self.notebook)
        self.settings_tab = tk.Frame(self.notebook)

        self.notebook.add(self.checklist_tab, text="Checklist")
        self.notebook.add(self.calendar_tab, text="Calendar")
        self.notebook.add(self.settings_tab, text="Settings")

        self.build_checklist_tab()
        self.build_calendar_tab()
        self.build_settings_tab()

    def build_checklist_tab(self):
        self.task_entry = tk.Entry(self.checklist_tab, font=("Arial", 14))
        self.task_entry.pack(pady=5)

        self.add_button = tk.Button(self.checklist_tab, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        self.task_listbox = tk.Listbox(self.checklist_tab, font=("Arial", 12), selectmode=tk.MULTIPLE)
        self.task_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.remove_button = tk.Button(self.checklist_tab, text="Remove Selected", command=self.remove_task)
        self.remove_button.pack(pady=5)

    def build_calendar_tab(self):
        self.calendar = Calendar(self.calendar_tab, selectmode='day', year=datetime.datetime.now().year,
                                 month=datetime.datetime.now().month, day=datetime.datetime.now().day)
        self.calendar.pack(pady=20)

    def build_settings_tab(self):
        tk.Label(self.settings_tab, text="Select Theme:", font=("Arial", 14)).pack(pady=10)
        for theme_name in self.themes.keys():
            tk.Button(self.settings_tab, text=theme_name, width=15, command=lambda t=theme_name: self.apply_theme(t)).pack(pady=2)

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)

    def remove_task(self):
        selected_indices = list(self.task_listbox.curselection())
        for index in reversed(selected_indices):
            self.task_listbox.delete(index)
            del self.tasks[index]

    def apply_theme(self, theme_name):
        theme = self.themes.get(theme_name, self.themes["Mint"])
        self.current_theme = theme_name
        bg = theme["bg"]
        fg = theme["fg"]

        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        self.header.configure(bg=bg, fg=fg)
        self.task_entry.configure(bg=bg, fg=fg, insertbackground=fg)
        self.add_button.configure(bg=bg, fg=fg, activebackground=fg)
        self.remove_button.configure(bg=bg, fg=fg, activebackground=fg)
        self.task_listbox.configure(bg=bg, fg=fg)
        self.checklist_tab.configure(bg=bg)
        self.calendar_tab.configure(bg=bg)
        self.settings_tab.configure(bg=bg)

        for child in self.settings_tab.winfo_children():
            if isinstance(child, tk.Label) or isinstance(child, tk.Button):
                child.configure(bg=bg, fg=fg, activebackground=fg)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabifyApp(root)
    root.geometry("600x500")
    root.mainloop()
