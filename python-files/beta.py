import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
import sqlite3
import bcrypt
from datetime import datetime
import json
from tkcalendar import DateEntry
import requests
import threading
from gpt4all import GPT4All
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller bundle """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)




def ask_mistral_instruct(prompt, model_path=None):
    if model_path is None:
        # Use _internal since your build extracts files into _internal
        model_path = resource_path(os.path.join("LLM", "mistral-7b-instruct-v0.1.Q4_0.gguf"))
    model_name = "mistral-7b-instruct-v0.1.Q4_0.gguf"
    try:
        with GPT4All(model_name=model_name, model_path=model_path) as model:
            response = model.generate(prompt)
            return response
    except Exception as e:
        print(f"Error during model generation: {e}")
        return None




# SQLite database setup functions
def create_connection(db_path="app.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    try:
        cursor = conn.cursor()

        # Existing login_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)

        # NEW: plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                plan_name TEXT,
                plan_json TEXT,
                FOREIGN KEY (username) REFERENCES login_info (username)
            );
        """)

        conn.commit()
    except sqlite3.Error as e:
        print(e)

def load_latest_plan_for_user(conn, username):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT plan_name, plan_json FROM plans WHERE username = ? ORDER BY id DESC LIMIT 1",
        (username,)
    )
    row = cursor.fetchone()
    if row:
        plan_name, plan_json = row
        import json
        plan_data = json.loads(plan_json)
        return plan_name, plan_data
    return None, None


def insert_user(conn, username, password):
    try:
        cursor = conn.cursor()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO login_info (username, password_hash) VALUES (?, ?);",
                       (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM login_info WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row is None:
        return False
    stored_hash = row[0]
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


def save_plan(conn, user_id, plan_data, plan_name="My Plan"):
    cursor = conn.cursor()
    plan_json = json.dumps(plan_data)
    cursor.execute(
        "INSERT INTO plans (username, plan_name, plan_json) VALUES (?, ?, ?)",
        (user_id, plan_name, plan_json)
    )
    conn.commit()


def load_all_plans_for_user(conn, username):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, plan_name, plan_json FROM plans WHERE username = ? ORDER BY id DESC",
        (username,)
    )
    rows = cursor.fetchall()
    plans = []
    import json
    for pid, name, pjson in rows:
        try:
            plans.append((pid, name, json.loads(pjson)))
        except:
            plans.append((pid, name, {}))
    return plans


def delete_plan_by_id(conn, plan_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
    conn.commit()


def update_plan_name(conn, plan_id, new_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET plan_name = ? WHERE id = ?", (new_name, plan_id))
    conn.commit()


def update_plan_json_in_db(conn, plan_id, updated_data, plan_name=None):
    cursor = conn.cursor()
    plan_json_str = json.dumps(updated_data)
    if plan_name:
        cursor.execute(
            "UPDATE plans SET plan_json = ?, plan_name = ? WHERE id = ?",
            (plan_json_str, plan_name, plan_id),
        )
    else:
        cursor.execute(
            "UPDATE plans SET plan_json = ? WHERE id = ?",
            (plan_json_str, plan_id),
        )
    conn.commit()



def extract_json(text):
    import json

    start = text.find('{')
    if start == -1:
        print("No opening brace found.")
        return None

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1

        if brace_count == 0:
            json_str = text[start:i+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None

    print("No balanced JSON object found.")
    return None

        




class Dashboard:
    def __init__(self, master, username, conn):
        self.master = master
        self.username = username
        self.conn = conn
        

        # Theming
        self.BG_COLOR = "#2e3440"
        self.FG_COLOR = "#d8dee9"
        self.SIDEBAR_COLOR = "#393e4c"

        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.button_font = font.Font(family="Segoe UI", size=12, weight="bold")

        self.master.configure(bg=self.BG_COLOR)
        self.setup_ui()
        self.load_plans()

    def setup_ui(self):
        self.master.title(f"Dashboard - {self.username}")
        self.master.configure(bg=self.BG_COLOR)

        root_frame = tk.Frame(self.master, bg=self.BG_COLOR)
        root_frame.pack(fill=tk.BOTH, expand=True)

        # LEFT SIDEBAR frame for To-Do List
        sidebar = tk.Frame(root_frame, width=220, bg=self.SIDEBAR_COLOR)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        sidebar_label = tk.Label(sidebar, text="To-Do List", font=self.title_font,
                                bg=self.SIDEBAR_COLOR, fg=self.FG_COLOR)
        sidebar_label.pack(pady=(16, 12))

        self.todo_entry = tk.Entry(sidebar, font=self.label_font, width=18)
        self.todo_entry.pack(pady=6, padx=14)
        add_btn = tk.Button(sidebar, text="Add", font=self.label_font,
                            command=self.add_todo)
        add_btn.pack(pady=(0, 10))

        todo_scroll_frame = tk.Frame(sidebar, bg=self.SIDEBAR_COLOR)
        todo_scroll_frame.pack(padx=7, pady=(0, 10), fill=tk.BOTH, expand=True)

        self.todo_canvas = tk.Canvas(todo_scroll_frame, bg="#434c5e", highlightthickness=0, bd=0)
        self.todo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.todo_checkbox_frame = tk.Frame(self.todo_canvas, bg="#434c5e")
        self.todo_canvas.create_window((0,0), window=self.todo_checkbox_frame, anchor="nw")

        todo_scrollbar = tk.Scrollbar(todo_scroll_frame, orient="vertical", command=self.todo_canvas.yview)
        todo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_canvas.config(yscrollcommand=todo_scrollbar.set)

        self.todo_checkbox_frame.bind(
            "<Configure>",
            lambda e: self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all"))
        )

        self.todo_vars = []  # List of (Checkbutton Variable, Task Text)
        self.todo_checkbuttons = []  # List of Checkbutton widgets

        del_btn = tk.Button(sidebar, text="Delete Selected", font=self.label_font,
                            command=self.del_todo)
        del_btn.pack(pady=(0, 8))

        # ---- Main Area ----
        main_area = tk.Frame(root_frame, bg=self.BG_COLOR)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_area.pack_propagate(False)

        welcome_text = f"Welcome, {self.username}!"
        welcome_label = tk.Label(main_area, text=welcome_text, font=self.title_font,
                                bg=self.BG_COLOR, fg=self.FG_COLOR)
        welcome_label.pack(pady=(35, 20))

        plan_selection_label = tk.Label(main_area, text="Select a Plan:", font=self.label_font,
                                        bg=self.BG_COLOR, fg=self.FG_COLOR)
        plan_selection_label.pack(anchor='w', padx=10)

        self.plan_selector = ttk.Combobox(main_area, state="readonly", width=40)
        self.plan_selector.pack(padx=10, pady=(0, 15))
        # Populate with existing loaded plans' names
        plan_names = [name for _, name, _ in getattr(self, "all_plans", [])]
        self.plan_selector['values'] = plan_names
        if plan_names:
            self.plan_selector.current(0)

        btn_style = {
            "font": self.button_font,
            "bg": "#88c0d0",
            "fg": "#2e3440",
            "activebackground": "#81a1c1",
            "activeforeground": "#2e3440",
            "relief": tk.FLAT,
            "bd": 0,
            "width": 18,
            "height": 2,
            "cursor": "hand2"
        }

        view_plan_btn = tk.Button(main_area, text="View Current Plan",
                                command=self.view_plan, **btn_style)
        view_plan_btn.pack(pady=15)

        create_plan_btn = tk.Button(main_area, text="Create a Plan",
                                command=self.create_plan, **btn_style)
        create_plan_btn.pack(pady=10)


        


    # ---- To-Do List with Checkboxes methods ----
    def add_todo(self):
        task = self.todo_entry.get().strip()
        if task:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                self.todo_checkbox_frame, text=task, font=self.label_font,
                variable=var, bg="#434c5e", fg=self.FG_COLOR,
                selectcolor="#3b4252", activebackground="#434c5e",
                anchor="w", relief=tk.FLAT, highlightthickness=0
            )
            chk.pack(fill="x", anchor="w", pady=2, padx=3)
            self.todo_vars.append((var, task))
            self.todo_checkbuttons.append(chk)
            self.todo_entry.delete(0, tk.END)
            self.todo_canvas.yview_moveto(1.0)  # Scroll to bottom

    def del_todo(self):
        # Remove checked tasks
        to_keep_vars = []
        to_keep_widgets = []
        for var_chk, chkbtn in zip(self.todo_vars, self.todo_checkbuttons):
            var, task = var_chk
            # If checked, remove
            if not var.get():
                to_keep_vars.append((var, task))
                to_keep_widgets.append(chkbtn)
            else:
                chkbtn.destroy()
        self.todo_vars = to_keep_vars
        self.todo_checkbuttons = to_keep_widgets

    # ---- Dashboard button actions ----
    def view_plan(self):
        index = self.plan_selector.current()
        if index < 0 or index >= len(self.all_plans):
            messagebox.showwarning("Missing Plan", "Please select a plan to view.")
            return

        plan_id, plan_name, plan_data = self.all_plans[index]

        plan_window = tk.Toplevel(self.master)
        ViewPlanWindow(plan_window, plan_data, plan_name, plan_id, self.conn, [self.all_plans[index]])

    def create_plan(self):
    # Open Create Plan window
        CreatePlanWindow(self.master, self.username, self.conn)

    def load_plans(self):
        self.all_plans = load_all_plans_for_user(self.conn, self.username)
        plan_names = [name for _, name, _ in self.all_plans]
        self.plan_selector['values'] = plan_names
        if plan_names:
            self.plan_selector.current(0)

import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import tkinter as tk
from tkinter import ttk, messagebox


class ViewPlanWindow:
    def __init__(self, master, plan_data, plan_name, plan_id, conn, plan_list):
        self.master = master
        self.plan_data = plan_data
        self.plan_name = plan_name
        self.plan_id = plan_id  # Needed to update DB
        self.conn = conn        # Needed for DB operations
        self.all_plans = plan_list # Full plans list
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.task_timers = {}  # key: (date, subject, module), value: {"elapsed": seconds, "active": bool}
        self.active_timer_key = None
        self.timer_update_interval = 1000  # milliseconds (1 second)



        self.master.title(f"View Plan - {self.plan_name}")
        self.setup_ui()
        self.load_schedule()

    def setup_ui(self):
        self.generate_btn = ttk.Button(self.master, text="Generate LLM Schedule", command=self.generate_schedule)
        self.generate_btn.pack(pady=8)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.full_schedule_frame = ttk.Frame(self.notebook)
        self.completed_frame = ttk.Frame(self.notebook)
        self.incomplete_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.full_schedule_frame, text="Full Schedule")
        self.notebook.add(self.completed_frame, text="Completed Tasks")
        self.notebook.add(self.incomplete_frame, text="Incomplete Tasks")

        columns = ("Date", "Subject", "Module", "Estimated Hours", "Status")
        self.full_schedule_tree = ttk.Treeview(self.full_schedule_frame, columns=columns, show="headings")
        self.completed_tree = ttk.Treeview(self.completed_frame, columns=columns, show="headings")
        self.incomplete_tree = ttk.Treeview(self.incomplete_frame, columns=columns, show="headings")
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Plan Info")
        self.plan_text = tk.Text(self.info_frame, wrap="word", state="disabled")
        self.plan_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.display_plan_info()
        # --- Timer Controls: Add below the main UI ---
        controls_frame = ttk.Frame(self.master)
        controls_frame.pack(pady=10)

        self.start_btn = ttk.Button(controls_frame, text="Start", command=self.start_timer, state="disabled")
        self.pause_btn = ttk.Button(controls_frame, text="Pause", command=self.pause_timer, state="disabled")
        self.stop_btn = ttk.Button(controls_frame, text="Stop", command=self.stop_timer, state="disabled")

        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.timer_label = ttk.Label(self.master, text="00:00:00")
        self.timer_label.pack(pady=5)





        for tree in [self.full_schedule_tree, self.completed_tree, self.incomplete_tree]:
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor='center')
            tree.pack(fill=tk.BOTH, expand=True)
        self.full_schedule_tree.bind('<<TreeviewSelect>>', self.on_task_select)

    def start_timer(self):
        key = self.active_timer_key
        if key is None:
            return

        estimated_hours = self.get_estimated_hours_for_key(key)
        if estimated_hours is None:
            return

        remaining_seconds = int(estimated_hours * 3600)
        timer = self.task_timers.setdefault(key, {"remaining": remaining_seconds, "active": False})

        # If timer was previously paused, preserve remaining time
        if "remaining" not in timer or timer["remaining"] <= 0:
            timer["remaining"] = remaining_seconds

        timer["active"] = True
        self.update_timer_buttons()
        self.run_timer(key)

    def pause_timer(self):
        key = self.active_timer_key
        if key in self.task_timers:
            self.task_timers[key]["active"] = False
            self.update_timer_buttons()

    def stop_timer(self):
        key = self.active_timer_key
        if key in self.task_timers:
            self.task_timers[key]["active"] = False
            # Reset remaining time to full estimated time
            estimated_hours = self.get_estimated_hours_for_key(key) or 0
            self.task_timers[key]["remaining"] = int(estimated_hours * 3600)
            self.update_timer_buttons()
            self.update_timer_display(key)  # reset timer label

    def update_timer_buttons(self):
        key = self.active_timer_key
        if key is None:
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            return

        timer = self.task_timers.get(key, {"active": False})
        if timer["active"]:
            # Timer running: enable pause, stop; disable start
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
        else:
            # Timer paused or stopped: enable start, stop; disable pause
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="normal")


    def run_timer(self, key):
        timer = self.task_timers.get(key)
        if not timer or not timer["active"]:
            return

        timer["remaining"] -= 1

        self.update_timer_display(key)

        if timer["remaining"] <= 0:
            self.mark_task_completed(key)
            self.pause_timer()
            return

        self.master.after(self.timer_update_interval, lambda: self.run_timer(key))

    def update_timer_display(self, key):
        remaining_seconds = self.task_timers[key]["remaining"]
        remaining_str = self.seconds_to_hhmmss(remaining_seconds)
        self.timer_label.config(text=remaining_str)

    def seconds_to_hhmmss(self, seconds):
        h = max(seconds, 0) // 3600
        m = (max(seconds, 0) % 3600) // 60
        s = max(seconds, 0) % 60
        return f"{h:02d}:{m:02d}:{s:02d}"


    def get_estimated_hours_for_key(self, key):
        date, subject, module = key
        schedule = self.plan_data.get('schedule', {})
        day_tasks = schedule.get(date, [])
        for task in day_tasks:
            if task.get('subject') == subject and task.get('module') == module:
                try:
                    return float(task.get('estimated_hours', 0))
                except ValueError:
                    return 0
        return None

    def mark_task_completed(self, key):
        date, subject, module = key

        # Update status in plan_data
        schedule = self.plan_data.get('schedule', {})
        if date in schedule:
            for task in schedule[date]:
                if task.get('subject') == subject and task.get('module') == module:
                    task['status'] = 'completed'

        # Update Treeview display
        for item_id in self.full_schedule_tree.get_children():
            values = self.full_schedule_tree.item(item_id)['values']
            if values[0] == date and values[1] == subject and values[2] == module:
                new_values = list(values)
                new_values[-1] = 'completed'  # updating status column
                self.full_schedule_tree.item(item_id, values=new_values)
                break

        # Show completion message
        self.timer_label.config(text="Completed!")

    def on_task_select(self, event):
        selected = self.full_schedule_tree.selection()
        if not selected:
            self.active_timer_key = None
            self.update_timer_buttons()
            return

        item_id = selected[0]
        item = self.full_schedule_tree.item(item_id)
        values = item.get('values', [])
        if len(values) < 3:
            self.active_timer_key = None
            self.update_timer_buttons()
            return

        # The key uniquely identifying the task: (date, subject, module)
        key = (values[0], values[1], values[2])
        self.active_timer_key = key

        # Update UI buttons based on whether the timer is running for this task
        self.update_timer_buttons()

    def display_plan_info(self):
        lines = []
        lines.append(f"Plan Name: {self.plan_name}")
        grade = self.plan_data.get('grade', '')
        if grade:
            lines.append(f"Grade/Class: {grade}")
        subjects = self.plan_data.get("subjects", [])
        if subjects:
            lines.append("Subjects:")
            for subj in subjects:
                lines.append(f" - {subj.get('name', '')} ({subj.get('credits', '')} credits)")
        modules = self.plan_data.get("modules", {})
        if modules:
            lines.append("Modules:")
            for subj, mods in modules.items():
                lines.append(f" {subj}:")
                for m in mods:
                    mod_name = m.get('module', '')
                    diff = m.get('difficulty', '')
                    lines.append(f"   - {mod_name} [{diff}]")
                    if "topics" in m and m["topics"]:
                        lines.append(f"     Topics: {', '.join(m['topics'])}")
        schedule = self.plan_data.get("schedule", {})
        if schedule:
            lines.append("Schedule Setup:")
            for k, v in schedule.items():
                # Only show string metadata values, not generated schedule tasks
                if isinstance(v, str):
                    pretty = k.replace("_", " ").title()
                    lines.append(f"  {pretty}: {v}")
        text = "\n".join(lines)
        self.plan_text.config(state="normal")
        self.plan_text.delete(1.0, tk.END)
        self.plan_text.insert(tk.END, text)
        self.plan_text.config(state="disabled")


    def show_loading_popup(self, message="Generating schedule..."):
        popup = tk.Toplevel(self.master)
        popup.title("Please wait")
        popup.geometry("320x100")
        popup.transient(self.master)
        popup.grab_set()

        label = ttk.Label(popup, text=message, font=self.label_font)
        label.pack(pady=10)

        progress = ttk.Progressbar(popup, mode='indeterminate', length=280)
        progress.pack(pady=10)
        progress.start(10)
        popup.progress = progress
        return popup

    def generate_schedule(self):
        loading_popup = self.show_loading_popup("Generating schedule, please wait...")

        def finish(result):
            loading_popup.destroy()
            self.generate_btn.config(state='normal')
            self.display_llm_schedule(result)
            messagebox.showinfo("Schedule Generated", "AI-generated schedule response shown below.")

        def worker():
            self.master.after(0, lambda: self.generate_btn.config(state='disabled'))

            index = 0
            if index < 0 or index >= len(self.all_plans):
                self.master.after(0, lambda: loading_popup.destroy())
                self.master.after(0, lambda: self.generate_btn.config(state='normal'))
                self.master.after(0, lambda: messagebox.showwarning("Missing Plan", "Please select a plan to generate schedule."))
                return

            plan_id, plan_name, plan_data = self.all_plans[index]

            prompt = f"""
You are an expert educational planner.

Given the following details:

- Student's grade/class: {plan_data.get('grade', '')}
- Subjects: {json.dumps(plan_data.get('subjects', []))}
- Modules per subject: {json.dumps(plan_data.get('modules', {}))}
- Scheduling constraints: {json.dumps(plan_data.get('schedule', {}))}

Please generate a study schedule covering the entire specified period.

Requirements:

1. Output exactly one valid JSON object.
2. The JSON object keys should be ISO-formatted dates (YYYY-MM-DD).
3. Each key maps to a list of study tasks with:
   - subject (string)
   - module (string)
   - estimated_hours (number)
   - status (string, always "pending")
4. The JSON output must be properly formatted, no extra text.
5. Begin JSON immediately with '{{' and end with '}}'.

Output exactly one valid JSON object only, without any explanations or additional text before or after.
Begin JSON output with '{{' and end with '}}'.

Example output:
{{
  "2025-08-31": [
    {{"subject": "Business Environment", "module": "Technological environment", "estimated_hours": 4, "status": "pending"}}
  ],
  "2025-09-01": [
    {{"subject": "Business Environment", "module": "Globalization", "estimated_hours": 6, "status": "pending"}}
  ]
}}

Start generating the schedule now.
"""


            response = ask_mistral_instruct(prompt)

            print("LLM RAW RESPONSE:\n", response)

            if response is not None:
                schedule_data = extract_json(response)
            else:
                self.master.after(0, lambda: loading_popup.destroy())
                self.master.after(0, lambda: self.generate_btn.config(state='normal'))
                self.master.after(0, lambda: messagebox.showerror("LLM Error", "No response received from the model."))
                return

            if not schedule_data:
                self.master.after(0, lambda: loading_popup.destroy())
                self.master.after(0, lambda: self.generate_btn.config(state='normal'))
                self.master.after(0, lambda: messagebox.showerror("LLM Error", "Failed to parse schedule response."))
                return

            # Create a new SQLite connection inside this thread to avoid threading issues
            thread_conn = sqlite3.connect("app.db")  # Ensure this path matches your DB path
            try:
                plan_data["schedule"] = schedule_data
                update_plan_json_in_db(thread_conn, plan_id, plan_data, plan_name)
                thread_conn.commit()
            except Exception as e:
                self.master.after(0, lambda: loading_popup.destroy())
                self.master.after(0, lambda: self.generate_btn.config(state='normal'))
                self.master.after(0, lambda e=e: messagebox.showerror("Database Error", f"Unable to save updated schedule: {e}"))
                return
            finally:
                thread_conn.close()

            self.master.after(0, lambda: finish(response))
            self.populate_schedule_tabs(schedule_data)


        threading.Thread(target=worker, daemon=True).start()

    def load_schedule(self):
        schedule = self.plan_data.get("schedule", {})
        if schedule:
            self.populate_schedule_tabs(schedule)
        else:
            messagebox.showinfo("No Schedule", "This plan does not have a schedule.")

    def populate_schedule_tabs(self, schedule_dict):
        for tree in [self.full_schedule_tree, self.completed_tree, self.incomplete_tree]:
            for item in tree.get_children():
                tree.delete(item)

        for date, tasks in schedule_dict.items():
            if not isinstance(tasks, list):
                continue
            for task in tasks:
                if isinstance(task, dict):
                    # Handle keys possibly in camelCase or snake_case
                    estimated_hours = task.get('estimated_hours', task.get('estimatedStudyHours', ''))
                    status = task.get('status', task.get('taskStatus', 'Pending'))

                    values = (
                        date,
                        task.get('subject', ''),
                        task.get('module', ''),
                        estimated_hours,
                        status
                    )
                    self.full_schedule_tree.insert('', 'end', values=values)

                    status_lower = status.lower()
                    if status_lower == 'completed':
                        self.completed_tree.insert('', 'end', values=values)
                    elif status_lower in ('pending', 'incomplete'):
                        self.incomplete_tree.insert('', 'end', values=values)
                else:
                    print(f"Warning: Skipping invalid task entry for date {date}: {task}")




    def display_llm_schedule(self, output):
        # Optional: display raw LLM schedule JSON string in a pop-up or tab if desired
        pass



class ScrollableFrame(ttk.Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class CreatePlanWindow:
    def __init__(self, master, username, conn):
        self.master = tk.Toplevel(master)
        self.master.title("Create a Plan")
        self.master.geometry("700x500")
        self.username = username
        self.conn = conn

        # Theme & fonts
        self.BG_COLOR = "#2e3440"
        self.FG_COLOR = "#d8dee9"
        self.master.configure(bg=self.BG_COLOR)
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11)

        # Data for the plan
        self.plan_data = {
            "subjects": [],   # list of {name, credits}
            "modules": {},    # dict: subject -> [{module, difficulty}]
            "schedule": {}    # dict with schedule info
        }
        self.module_entries = {}

        # Step frames
        self.step_frames = []
        self.current_step = 0

        self.container = ttk.Frame(self.master, padding=10)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Build steps
        self.step_frames.append(self.create_subjects_credits_frame())
        self.step_frames.append(self.create_modules_difficulty_frame())
        self.step_frames.append(self.create_schedule_frame())

        self.show_current_step()

    def show_current_step(self):
        """Show only the current step frame"""
        for i, frame in enumerate(self.step_frames):
            if i == self.current_step:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

    # ---------- STEP 1 ----------
    
    def create_subjects_credits_frame(self):
        frame = ttk.Frame(self.container)
        # Label for Grade/Class
        ttk.Label(frame, text="Enter Your Grade/Class:", font=self.label_font).pack(anchor="w", pady=(5, 0))

        # Free text entry for any value (numbers, strings, mixed)
        self.grade_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.grade_var, width=30).pack(anchor="w", pady=(0, 10))

        
        ttk.Label(frame, text="Step 1: Add Subjects and Credits", font=self.title_font).pack(pady=10)

        #  🔹 Scrollable area for subject rows
        scrollable = ScrollableFrame(frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=5)
        self.subjects_frame = scrollable.scrollable_frame  # add rows inside this

        # Lists to keep track of TK variables for subjects and credits
        self.subject_entries = []
        self.credits_entries = []

        # Add the first subject row by default
        self.add_subject_row()

        # "Add Another Subject" button
        ttk.Button(frame, text="Add Another Subject", command=self.add_subject_row).pack(pady=(5, 15))

        # Navigation buttons (always visible, outside scrollable area)
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill=tk.X, pady=10)
        ttk.Button(nav_frame, text="Next", command=self.step1_next).pack(side=tk.RIGHT)

        return frame


    def add_subject_row(self):
        # Create a frame for this subject row inside the scrollable subjects_frame
        row_frame = ttk.Frame(self.subjects_frame)
        row_frame.pack(fill=tk.X, pady=5)

        # Variables for subject name and credits
        subject_var = tk.StringVar()
        credits_var = tk.StringVar()

        # Subject name entry
        ttk.Label(row_frame, text="Subject:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Entry(row_frame, textvariable=subject_var, width=30).pack(side=tk.LEFT, padx=5)

        # Credits entry
        ttk.Label(row_frame, text="Credits:", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Entry(row_frame, textvariable=credits_var, width=10).pack(side=tk.LEFT, padx=5)

        # Remove button for this row
        def remove_row():
            # Remove tracked variables for this row
            if subject_var in self.subject_entries:
                self.subject_entries.remove(subject_var)
            if credits_var in self.credits_entries:
                self.credits_entries.remove(credits_var)
            # Destroy the row frame to remove it from the UI
            row_frame.destroy()

        remove_btn = ttk.Button(row_frame, text="Remove", command=remove_row)
        remove_btn.pack(side=tk.LEFT, padx=10)

        # Track this row's variables in the lists
        self.subject_entries.append(subject_var)
        self.credits_entries.append(credits_var)


    def step1_next(self):
        self.plan_data["subjects"] = []
        for subj_var, cred_var in zip(self.subject_entries, self.credits_entries):
            subject = subj_var.get().strip()
            credits = cred_var.get().strip()

            if not subject:
                messagebox.showerror("Input Error", "Subject name cannot be empty.")
                return
            if not credits:
                messagebox.showerror("Input Error", "Credits cannot be empty.")
                return

            self.plan_data["subjects"].append({"name": subject, "credits": credits})

        self.current_step = 1
        self.show_current_step()
        self.load_modules_frame()

    # ---------- STEP 2 ----------
    def create_modules_difficulty_frame(self):
        frame = ttk.Frame(self.container)
        ttk.Label(frame, text="Step 2: Add Modules and Difficulty", font=self.title_font).pack(pady=10)

        # --- Scrollable area for modules ---
        scrollable = ScrollableFrame(frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=5)
        self.modules_container = scrollable.scrollable_frame  # <-- This line is crucial!

        # Navigation buttons (below scroll area)
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x", pady=10)
        ttk.Button(nav_frame, text="Back", command=self.step2_back).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="Next", command=self.step2_next).pack(side=tk.RIGHT)

        return frame




    def load_modules_frame(self):
        # Clear existing widgets
        for widget in self.modules_container.winfo_children():
            widget.destroy()

        self.module_entries = {}

        for subject in self.plan_data.get("subjects", []):
            subj_name = subject['name']

            # Subject label
            ttk.Label(
                self.modules_container,
                text=f"Subject: {subj_name}",
                font=self.label_font
            ).pack(anchor=tk.W, pady=(10, 2))

            # Frame for this subject's modules
            frame_subject = ttk.Frame(self.modules_container)
            frame_subject.pack(fill=tk.X, pady=3)

            self.module_entries[subj_name] = []

            def add_module_row(current_subj=subj_name, parent_frame=frame_subject):
                row_frame = ttk.Frame(parent_frame)
                row_frame.pack(fill=tk.X, pady=2)
                module_var = tk.StringVar()
                difficulty_var = tk.StringVar()

                # Module name entry
                ttk.Entry(row_frame, textvariable=module_var, width=30).pack(side=tk.LEFT, padx=5)
                # Difficulty dropdown
                combo = ttk.Combobox(
                    row_frame,
                    textvariable=difficulty_var,
                    values=['Easy', 'Medium', 'Hard'],
                    width=10,
                    state="readonly"
                )
                combo.pack(side=tk.LEFT, padx=5)
                combo.set('Medium')

                # ------ Topic Entry Section ------
                topics_var = []  # List to store topics for this module

                topic_entry = tk.Entry(row_frame, width=18)
                topic_entry.pack(side=tk.LEFT, padx=(5,0))

                topics_label = tk.Label(row_frame, text="", anchor="w")
                topics_label.pack(side=tk.LEFT, padx=(4,0))

                def add_topic():
                    topic = topic_entry.get().strip()
                    if topic:
                        topics_var.append(topic)
                        topic_entry.delete(0, tk.END)
                        topics_label.config(text="; ".join(topics_var))

                add_topic_btn = ttk.Button(row_frame, text="Add Topic", command=add_topic)
                add_topic_btn.pack(side=tk.LEFT, padx=(4,0))
                # ---------------------------------

                # Remove button for this module row
                def remove_row():
                    if (module_var, difficulty_var, topics_var) in self.module_entries[current_subj]:
                        self.module_entries[current_subj].remove((module_var, difficulty_var, topics_var))
                    row_frame.destroy()

                remove_btn = ttk.Button(row_frame, text="Remove", command=remove_row)
                remove_btn.pack(side=tk.LEFT, padx=10)

                # Store the module with its topics
                self.module_entries[current_subj].append((module_var, difficulty_var, topics_var))



            # Add initial row for this subject
            add_module_row()

            # Button to add more modules for this subject
            ttk.Button(
                frame_subject,
                text="Add Module",
                command=lambda s=subj_name, f=frame_subject: add_module_row(s, f)
            ).pack(pady=5, anchor=tk.W)

    def step2_back(self):
        self.current_step = 0
        self.show_current_step()

    def step3_back(self):
        self.current_step = 1
        self.show_current_step()


    def step2_next(self):
        modules = {}
        for subject, entries in self.module_entries.items():
            mod_list = []
            for mod_var, diff_var, topics_var in entries:
                mod_name = mod_var.get().strip()
                diff = diff_var.get().strip()
                if not mod_name:
                    messagebox.showerror("Input Error", f"Module name cannot be empty for subject {subject}.")
                    return
                if not diff:
                    messagebox.showerror("Input Error", f"Please select difficulty for module {mod_name}.")
                    return
                mod_list.append({
                    "module": mod_name,
                    "difficulty": diff,
                    "topics": topics_var  # List of topic strings
                })
            modules[subject] = mod_list
        self.plan_data["modules"] = modules
        self.current_step = 2
        self.show_current_step()
        self.create_schedule_frame()


    def create_schedule_frame(self):
        frame = ttk.Frame(self.container)
        ttk.Label(frame, text="Plan Name:", font=self.label_font).pack(anchor="w", pady=(0,5))
        self.plan_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.plan_name_var, width=40).pack(anchor="w", pady=(0,10))


        ttk.Label(frame, text="Step 3: Schedule Timing", font=self.title_font).pack(pady=10)
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)

        # --- Start Date ---
        ttk.Label(form_frame, text="Start Date:", font=self.label_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        start_date_entry = DateEntry(form_frame, textvariable=self.start_date_var, date_pattern='yyyy-mm-dd', width=12)
        start_date_entry.grid(row=0, column=1, pady=5)

        # --- End Date ---
        ttk.Label(form_frame, text="End Date:", font=self.label_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_date_var = tk.StringVar()
        end_date_entry = DateEntry(form_frame, textvariable=self.end_date_var, date_pattern='yyyy-mm-dd', width=12)
        end_date_entry.grid(row=1, column=1, pady=5)

        # --- Time selectors ---
        hours = [f"{h:02}" for h in range(0, 24)]
        minutes = ["00", "15", "30", "45"]

        # Daily Start
        ttk.Label(form_frame, text="Daily Start Time:", font=self.label_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.day_start_hour = tk.StringVar(value="09")
        self.day_start_min = tk.StringVar(value="00")
        ttk.Combobox(form_frame, textvariable=self.day_start_hour, values=hours, width=3, state="readonly").grid(row=2, column=1, sticky=tk.W)
        ttk.Label(form_frame, text=":").grid(row=2, column=1, padx=(35, 0), sticky=tk.W)
        ttk.Combobox(form_frame, textvariable=self.day_start_min, values=minutes, width=3, state="readonly").grid(row=2, column=1, padx=(45, 0), sticky=tk.W)

        # Daily End
        ttk.Label(form_frame, text="Daily End Time:", font=self.label_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.day_end_hour = tk.StringVar(value="18")
        self.day_end_min = tk.StringVar(value="00")
        ttk.Combobox(form_frame, textvariable=self.day_end_hour, values=hours, width=3, state="readonly").grid(row=3, column=1, sticky=tk.W)
        ttk.Label(form_frame, text=":").grid(row=3, column=1, padx=(35, 0), sticky=tk.W)
        ttk.Combobox(form_frame, textvariable=self.day_end_min, values=minutes, width=3, state="readonly").grid(row=3, column=1, padx=(45, 0), sticky=tk.W)

        # --- Free Time Slots (Add / Remove Rows) ---
        ttk.Label(form_frame, text="Free Time Slots:", font=self.label_font).grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.free_time_rows = []  # store tuples of vars
        slot_frame = ttk.Frame(form_frame)
        slot_frame.grid(row=4, column=1, sticky=tk.W)

        def add_free_time_row():
            row = ttk.Frame(slot_frame)
            row.pack(anchor=tk.W, pady=2)

            start_h = tk.StringVar(value="13")
            start_m = tk.StringVar(value="00")
            end_h = tk.StringVar(value="15")
            end_m = tk.StringVar(value="00")

            ttk.Combobox(row, textvariable=start_h, values=hours, width=3, state="readonly").pack(side=tk.LEFT)
            ttk.Label(row, text=":").pack(side=tk.LEFT)
            ttk.Combobox(row, textvariable=start_m, values=minutes, width=3, state="readonly").pack(side=tk.LEFT)
            ttk.Label(row, text=" – ").pack(side=tk.LEFT)
            ttk.Combobox(row, textvariable=end_h, values=hours, width=3, state="readonly").pack(side=tk.LEFT)
            ttk.Label(row, text=":").pack(side=tk.LEFT)
            ttk.Combobox(row, textvariable=end_m, values=minutes, width=3, state="readonly").pack(side=tk.LEFT)

            def remove_row():
                self.free_time_rows.remove((start_h, start_m, end_h, end_m, row))
                row.destroy()

            ttk.Button(row, text="Remove", command=remove_row).pack(side=tk.LEFT, padx=3)
            self.free_time_rows.append((start_h, start_m, end_h, end_m, row))

        ttk.Button(slot_frame, text="+ Add Slot", command=add_free_time_row).pack(pady=5, anchor=tk.W)
        add_free_time_row()  # default one row

        # Navigation buttons
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(pady=20, fill=tk.X)
        ttk.Button(nav_frame, text="Back", command=self.step3_back).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="Commence Plan", command=self.step3_submit).pack(side=tk.RIGHT)

        return frame


    def step3_submit(self):
        self.plan_data['grade'] = self.grade_var.get().strip()

        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()

        # Use correct variable names for time selectors
        day_start = f"{self.day_start_hour.get()}:{self.day_start_min.get()}"
        day_end = f"{self.day_end_hour.get()}:{self.day_end_min.get()}"

        free_slots = []
        for start_h, start_m, end_h, end_m, _ in self.free_time_rows:
            slot = f"{start_h.get()}:{start_m.get()}-{end_h.get()}:{end_m.get()}"
            free_slots.append(slot)
        free_times = ', '.join(free_slots)

        # Validate date formats
        for date_str in [start_date, end_date]:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
                return

        # Validate time formats
        for time_str in [day_start, day_end]:
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                messagebox.showerror("Input Error", f"Invalid time format: {time_str}. Use HH:MM.")
                return

        # Update schedule info in plan data
        self.plan_data["schedule"] = {
            "start_date": start_date,
            "end_date": end_date,
            "day_start_time": day_start,
            "day_end_time": day_end,
            "free_time_slots": free_times,
        }

        # ----- IMPORTANT: No LLM call here -----
        # Just save the plan to DB for now

        try:
            save_plan(
                self.conn,
                self.username,
                self.plan_data,
                plan_name=f"Plan created on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save the plan: {e}")
            return

        messagebox.showinfo("Plan Saved", "Your plan has been saved successfully.")
        self.master.destroy()










class CurrentPlanWindow:
    def __init__(self, master, username, conn):
        self.master = tk.Toplevel(master)
        self.master.title("Current Plan")
        self.master.geometry("800x600")

        self.username = username
        self.conn = conn

        # Colors/fonts
        self.BG_COLOR = "#2e3440"
        self.FG_COLOR = "#d8dee9"
        self.master.configure(bg=self.BG_COLOR)

        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=12)

        self.setup_ui()

    def setup_ui(self):
    # Title
        header = ttk.Label(
            self.master,
            text=f"Current Plans for {self.username}",
            font=self.title_font
        )
        header.pack(pady=10)

        # --- Dropdown + Delete ---
        top_frame = ttk.Frame(self.master, padding=10)
        top_frame.pack(fill=tk.X)

        self.all_plans = load_all_plans_for_user(self.conn, self.username)
        plan_names = [name for _, name, _ in self.all_plans] if self.all_plans else []

        ttk.Label(top_frame, text="Select a Plan:", font=self.label_font).pack(side=tk.LEFT, padx=(0, 5))
        self.plan_selector = ttk.Combobox(top_frame, values=plan_names, state="readonly", width=40)
        self.plan_selector.pack(side=tk.LEFT, padx=5)
        if plan_names:
            self.plan_selector.current(0)
        self.plan_selector.bind("<<ComboboxSelected>>", self.display_selected_plan)

        del_btn = ttk.Button(top_frame, text="Delete Plan", command=self.delete_selected_plan)
        del_btn.pack(side=tk.LEFT, padx=5)

        # --- Rename ---
        rename_frame = ttk.Frame(self.master, padding=10)
        rename_frame.pack(fill=tk.X)

        ttk.Label(rename_frame, text="Plan Name:", font=self.label_font).pack(side=tk.LEFT)
        self.plan_name_edit = ttk.Entry(rename_frame, width=50)
        self.plan_name_edit.pack(side=tk.LEFT, padx=5)
        update_btn = ttk.Button(rename_frame, text="Update Name", command=self.rename_selected_plan)
        update_btn.pack(side=tk.LEFT, padx=5)

        # --- Generate Schedule Button ---
        self.generate_btn = ttk.Button(top_frame, text="Generate Schedule", command=self.generate_schedule)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        # --- Tabs ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.info_frame = ttk.Frame(self.notebook)
        self.schedule_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.info_frame, text="Plan Info")
        self.notebook.add(self.schedule_frame, text="Generated Schedule")

        # --- Text widget for Plan Info tab ---
        self.plan_text = tk.Text(self.info_frame, wrap="word", state="disabled")
        self.plan_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.plan_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.plan_text.config(yscrollcommand=scrollbar.set)

        # Display first plan if any
        if plan_names:
            self.display_selected_plan()
        else:
            self.show_message("No saved plans found.")

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.full_schedule_frame = ttk.Frame(self.notebook)
        self.completed_frame = ttk.Frame(self.notebook)
        self.incomplete_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.full_schedule_frame, text="Full Schedule")
        self.notebook.add(self.completed_frame, text="Completed Tasks")
        self.notebook.add(self.incomplete_frame, text="Incomplete Tasks")

        # Add Treeviews for each tab
        columns = ("Date", "Subject", "Module", "Estimated Hours", "Status")
        self.full_schedule_tree = ttk.Treeview(self.full_schedule_frame, columns=columns, show="headings")
        self.completed_tree = ttk.Treeview(self.completed_frame, columns=columns, show="headings")
        self.incomplete_tree = ttk.Treeview(self.incomplete_frame, columns=columns, show="headings")

        for tree in [self.full_schedule_tree, self.completed_tree, self.incomplete_tree]:
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor='center')
            tree.pack(fill=tk.BOTH, expand=True)

        # Placeholder: You can add scrollbar and timer buttons per task row later

        # Load and display the current plan's schedule data
        self.display_selected_plan()
    
    def show_loading_popup(self, message="Generating schedule..."):
        popup = tk.Toplevel(self.master)
        popup.title("Please wait")
        popup.geometry("300x80")
        popup.transient(self.master)
        popup.grab_set()
        label = ttk.Label(popup, text=message, font=self.label_font)
        label.pack(expand=True, pady=25)
        popup.update_idletasks()
        return popup



    def display_selected_plan(self, event=None):
        index = self.plan_selector.current()
        if index >= 0 and index < len(self.all_plans):
            plan_id, plan_name, plan_data = self.all_plans[index]
            # Populate editable name field
            self.plan_name_edit.delete(0, tk.END)
            self.plan_name_edit.insert(0, plan_name)
            # Display details
            self.display_plan(plan_data, plan_name)

    def display_plan(self, plan_data, plan_name):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Create fresh Text widget with scrollbar inside info_frame
        self.plan_text = tk.Text(self.info_frame, wrap="word", state="disabled")
        self.plan_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.plan_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.plan_text.config(yscrollcommand=scrollbar.set)

        # Build plan detail lines
        lines = []
        lines.append(f"Plan Name: {plan_name}\n")

        grade = plan_data.get('grade', '')
        if grade:
            lines.append(f"Grade/Class: {grade}\n")

        subjects = plan_data.get("subjects", [])
        if subjects:
            lines.append("Subjects:")
            for subj in subjects:
                lines.append(f"  - {subj['name']} ({subj['credits']} credits)")
            lines.append("")

        modules = plan_data.get("modules", {})
        if modules:
            lines.append("Modules:")
            for subj, mods in modules.items():
                lines.append(f"  {subj}:")
                for m in mods:
                    lines.append(f" - {m['module']} [{m['difficulty']}]")
                    if "topics" in m and m["topics"]:
                        lines.append(f"     Topics: {', '.join(m['topics'])}")
            lines.append("")

        schedule = plan_data.get("schedule", {})
        if schedule:
            lines.append("Schedule:")
            for k, v in schedule.items():
                pretty_name = k.replace("_", " ").title()
                lines.append(f"  {pretty_name}: {v}")
            lines.append("")

        # Insert all lines into Text widget
        self.plan_text.config(state="normal")
        self.plan_text.delete(1.0, tk.END)
        self.plan_text.insert(tk.END, "\n".join(lines))
        self.plan_text.config(state="disabled")

        # Populate the schedule tabs (new method)
        self.populate_schedule_tabs(schedule)

    def populate_schedule_tabs(self, schedule_dict):
    # Clear existing data in trees
        for tree in [self.full_schedule_tree, self.completed_tree, self.incomplete_tree]:
            for item in tree.get_children():
                tree.delete(item)

        for date, tasks in schedule_dict.items():
            for task in tasks:
                values = (
                    date,
                    task.get('subject', ''),
                    task.get('module', ''),
                    task.get('estimated_hours', ''),
                    task.get('status', 'Pending')
                )
                # Insert into Full Schedule tab
                self.full_schedule_tree.insert('', 'end', values=values)

                # Insert into Completed or Incomplete tabs based on status
                status = task.get('status', 'Pending').lower()
                if status == 'completed':
                    self.completed_tree.insert('', 'end', values=values)
                elif status == 'pending' or status == 'incomplete':
                    self.incomplete_tree.insert('', 'end', values=values)




        

    def show_message(self, message):
        self.plan_text.config(state="normal")
        self.plan_text.delete(1.0, tk.END)
        self.plan_text.insert(tk.END, message)
        self.plan_text.config(state="disabled")

    def delete_selected_plan(self):
        index = self.plan_selector.current()
        if index < 0 or index >= len(self.all_plans):
            messagebox.showwarning("Delete Plan", "Please select a plan to delete.")
            return

        plan_id, plan_name, _ = self.all_plans[index]
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the plan '{plan_name}'?"
        )
        if confirm:
            delete_plan_by_id(self.conn, plan_id)
            messagebox.showinfo("Plan Deleted", f"Plan '{plan_name}' has been deleted.")
            self.refresh_dropdown()

    def rename_selected_plan(self):
        index = self.plan_selector.current()
        if index < 0 or index >= len(self.all_plans):
            messagebox.showwarning("Rename Plan", "Please select a plan.")
            return

        new_name = self.plan_name_edit.get().strip()
        if not new_name:
            messagebox.showerror("Rename Plan", "Plan name cannot be empty.")
            return

        plan_id, _, plan_data = self.all_plans[index]
        update_plan_name(self.conn, plan_id, new_name)
        messagebox.showinfo("Rename Plan", f"Plan name updated to '{new_name}'.")
        self.refresh_dropdown(select_index=index)

    def refresh_dropdown(self, select_index=0):
        self.all_plans = load_all_plans_for_user(self.conn, self.username)
        plan_names = [name for _, name, _ in self.all_plans]
        self.plan_selector['values'] = plan_names

        if plan_names:
            if select_index >= len(plan_names):
                select_index = 0
            self.plan_selector.current(select_index)
            self.display_selected_plan()
        else:
            self.plan_selector.set('')
            self.show_message("No saved plans found.")
    
    def display_schedule_table(self, schedule_dict):
        # Clear previous widgets inside the details_frame
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        columns = ("Date", "Subject", "Module", "Hours", "Status")
        tree = ttk.Treeview(self.info_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for date, tasks in schedule_dict.items():
            for task in tasks:
                tree.insert("", "end", values=(
                    date,
                    task.get('subject', ''),
                    task.get('module', ''),
                    task.get('estimated_hours', ''),
                    task.get('status', 'pending')
                ))

        scrollbar = ttk.Scrollbar(self.info_frame_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    


   





    def display_llm_schedule(self, output):
    # Clear schedule tab contents
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        # Create read-only Text widget and insert output text
        txt = tk.Text(self.schedule_frame, wrap="word")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("end", output)
        txt.config(state="disabled")
        # Switch to the 'Generated Schedule' tab to show output immediately
        self.notebook.select(self.schedule_frame)





def refresh_plan(self):
            # Placeholder for refreshing or updating schedule data from storage or LLM
            messagebox.showinfo("Refresh", "This is where the current plan would be refreshed.")


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x320")
        self.root.resizable(True, True)  # Allow resizing

        # Colors
        self.BG_COLOR = "#2e3440"
        self.FG_COLOR = "#d8dee9"
        self.ENTRY_BG_COLOR = "#3b4252"
        self.BTN_COLOR = "#88c0d0"
        self.BTN_HOVER_COLOR = "#81a1c1"

        self.root.configure(bg=self.BG_COLOR)

        # Configure root grid to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Fonts - Medium sized
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=10)
        self.entry_font = font.Font(family="Segoe UI", size=10)

        # Style setup
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.style.configure("TLabel",
                             background=self.BG_COLOR,
                             foreground=self.FG_COLOR,
                             font=self.label_font)

        self.style.configure("TEntry",
                             fieldbackground=self.ENTRY_BG_COLOR,
                             foreground=self.FG_COLOR,
                             font=self.entry_font)

        self.style.configure("TButton",
                             background=self.BTN_COLOR,
                             foreground=self.BG_COLOR,
                             font=self.label_font,
                             borderwidth=0)

        self.style.map("TButton",
                       background=[('active', self.BTN_HOVER_COLOR)])

        # Main container frame that expands with window
        self.container = ttk.Frame(self.root, style="TFrame")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure container grid to center form
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Login form frame - centered within container
        self.main_frame = ttk.Frame(self.container, padding=20, style="TFrame")
        self.main_frame.grid(row=0, column=0)

        # Title
        self.title_label = ttk.Label(self.main_frame, text="Welcome Back", font=self.title_font)
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username
        self.username_var = tk.StringVar()
        self.username_label = ttk.Label(self.main_frame, text="Username:")
        self.username_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var, width=25, font=self.entry_font)
        self.username_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.username_entry.focus()

        # Password
        self.password_var = tk.StringVar()
        self.password_label = ttk.Label(self.main_frame, text="Password:")
        self.password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.main_frame, textvariable=self.password_var, width=25, show="*", font=self.entry_font)
        self.password_entry.grid(row=2, column=1, pady=5, sticky="w")

        # Buttons: Login and Register
        self.login_button = ttk.Button(self.main_frame, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, pady=20, sticky=tk.EW, padx=5)
        self.register_button = ttk.Button(self.main_frame, text="Register", command=self.register)
        self.register_button.grid(row=3, column=1, pady=20, sticky=tk.EW, padx=5)

        # Padding for all widgets in main_frame
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=10)

        # Database connection
        self.conn = create_connection()
        if self.conn:
            create_table(self.conn)

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        if verify_user(self.conn, username, password):
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            self.open_dashboard(username)  # Open dashboard after success
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        success = insert_user(self.conn, username, password)
        if success:
            messagebox.showinfo("Registration Success", f"User '{username}' registered successfully! You can now log in.")
            self.username_var.set("")
            self.password_var.set("")
        else:
            messagebox.showerror("Registration Failed", "Username already exists. Please choose a different username.")

    def open_dashboard(self, username):
        # Create a new Toplevel window for the dashboard
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.geometry("600x400")
        Dashboard(dashboard_window, username, self.conn)  # Instantiate Dashboard class


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
