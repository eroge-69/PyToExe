import tkinter as tk
from tkinter import ttk, Menu, simpledialog, messagebox, scrolledtext
from datetime import datetime, timedelta
import os
import json
import calendar
from plyer import notification

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# -------- FILES & GLOBALS --------
SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 🔐 For saving token
GATE_DATE = datetime(2026, 2, 1).date()

RECORD_FILE = os.path.join(BASE_DIR, 'revision_schedule.json')
BACKLOG_FILE = os.path.join(BASE_DIR, 'backlog.json')
ASSIGN_FILE = os.path.join(BASE_DIR, 'assignments.json')
EVENT_FILE = os.path.join(BASE_DIR, 'calendar_events.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')

# -------- LOAD / SAVE JSON --------
def load_json(file): return json.load(open(file)) if os.path.exists(file) else {}
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)
def get_date_only(d): return d.split(", ")[1] if ", " in d else d

# -------- SMART DATE PARSER --------
def parse_natural_date(date_str):
    date_str = date_str.strip().lower()
    today = datetime.today()
    if date_str in ['today', 'now']: return today.date()
    if date_str == 'tomorrow': return (today + timedelta(days=1)).date()
    try: return datetime.strptime(date_str, '%Y-%m-%d').date()
    except: pass
    days = {d.lower(): i for i, d in enumerate(calendar.day_name)}
    parts = date_str.split()
    if len(parts) == 2 and parts[0] in ['this', 'next'] and parts[1] in days:
        target = days[parts[1]]
        delta = (target - today.weekday()) % 7
        delta = delta + (7 if parts[0] == 'next' else 0)
        return (today + timedelta(days=delta)).date()
    return None

def get_schedule(start):
    intervals = [0, 3, 15] + [30 * i for i in range(1, 13)]
    result = []
    for offset in intervals:
        d = start + timedelta(days=offset)
        if d.weekday() == 6: d += timedelta(days=1)
        result.append(d.strftime("%a, %Y-%m-%d"))
    return result
# -------- GOOGLE CALENDAR WITH STABLE TOKEN --------
def create_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        try:
            creds = flow.run_local_server(port=0)
        except:
            creds = flow.run_console()
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def add_event(service, topic, date, event_index):
    body = {
        "summary": f"Revision: {topic}",
        "start": {"date": date, "timeZone": "Asia/Kolkata"},
        "end": {"date": date, "timeZone": "Asia/Kolkata"},
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]},
    }
    event = service.events().insert(calendarId="primary", body=body).execute()
    event_index[f"{topic}__{date}"] = event.get("id")

def notify_revisions():
    today = datetime.today().strftime("%Y-%m-%d")
    items = [(t, i+1) for t, ds in records.items() for i, d in enumerate(ds) if get_date_only(d) == today]
    if items:
        note = "\n".join([f"{t} - Rev {r}" for t, r in items])
        notification.notify(title="📚 Today's Revisions", message=note, timeout=8)

def notify_assignments_due():
    today = datetime.today().date()
    soon = []
    for v in assignments.values():
        if v["status"] == "Pending":
            due = datetime.strptime(v["due"], "%Y-%m-%d").date()
            if 0 <= (due - today).days <= 2:
                soon.append(f"{v['task']} due on {v['due']}")
    if soon:
        notification.notify(title="📝 Assignments Due Soon", message="\n".join(soon), timeout=10)

# -------- APP ACTIONS --------
def add_topic():
    topic = simpledialog.askstring("Add Topic", "📘 Topic name:")
    if not topic or topic in records: return
    date_str = simpledialog.askstring("Start Date", "e.g. today, next monday, 2025-08-10:", initialvalue="today")
    start_date = parse_natural_date(date_str)
    if not start_date:
        messagebox.showerror("❌", "Invalid date format.")
        return
    schedule = get_schedule(start_date)
    records[topic] = schedule
    save_json(RECORD_FILE, records)
    service = create_calendar_service()
    events = load_json(EVENT_FILE)
    for d in schedule:
        add_event(service, topic, get_date_only(d), events)
    save_json(EVENT_FILE, events)
    messagebox.showinfo("✅", f"Revision topic '{topic}' scheduled successfully.")
    refresh_all()

def view_topics():
    text.config(state=tk.NORMAL)
    text.delete(1.0, tk.END)
    for i, topic in enumerate(records, 1):
        text.insert(tk.END, f"{i}. {topic}\n")
    text.config(state=tk.DISABLED)

def view_schedule():
    text.config(state=tk.NORMAL)
    text.delete(1.0, tk.END)
    for topic, dates in records.items():
        text.insert(tk.END, f"\n📘 {topic}\n")
        for i, d in enumerate(dates, 1):
            text.insert(tk.END, f"  Rev {i}: {d}\n")
    text.config(state=tk.DISABLED)

def revise_today():
    today = datetime.today().strftime("%Y-%m-%d")
    items = [(t, i+1, get_date_only(d)) for t, ds in records.items() for i, d in enumerate(ds) if get_date_only(d) == today]
    if not items:
        return messagebox.showinfo("✅", "No revisions scheduled for today.")
    if messagebox.askyesno("Complete?", "Mark all today's revisions as complete?"): return
    top = tk.Toplevel(root)
    checks = []
    def submit():
        for i in range(len(items)):
            if not checks[i].get():
                t, r, d = items[i]
                note = simpledialog.askstring("Partial Info", f"{t} - Rev {r}")
                backlog[f"{t}__{d}"] = {"topic": t, "rev_num": r, "date": d, "partial": note or "None"}
        save_json(BACKLOG_FILE, backlog)
        top.destroy()
    for i, (t, r, _) in enumerate(items):
        v = tk.BooleanVar(value=True)
        tk.Checkbutton(top, text=f"{t} - Rev {r}", variable=v).pack(anchor="w")
        checks.append(v)
    ttk.Button(top, text="Submit", command=submit).pack(pady=5)

def view_backlog():
    text.config(state=tk.NORMAL)
    text.delete(1.0, tk.END)
    if not backlog:
        text.insert(tk.END, "✅ Backlog is empty.\n")
    else:
        for i, (k, b) in enumerate(backlog.items(), 1):
            text.insert(tk.END, f"{i}. {b['topic']} Rev {b['rev_num']} ({b['date']}) - {b['partial']}\n")
    text.config(state=tk.DISABLED)

def add_assignment():
    task = simpledialog.askstring("Assignment", "📝 Assignment task:")
    due = simpledialog.askstring("Due Date", "📅 YYYY-MM-DD:", initialvalue=datetime.today().strftime("%Y-%m-%d"))
    key = f"{task}_{due}"
    assignments[key] = {"task": task, "due": due, "status": "Pending"}
    save_json(ASSIGN_FILE, assignments)
    body = {
        'summary': f"Assignment: {task}",
        'start': {'date': due, 'timeZone': 'Asia/Kolkata'},
        'end': {'date': due, 'timeZone': 'Asia/Kolkata'},
        'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 10}]}
    }
    service = create_calendar_service()
    event = service.events().insert(calendarId='primary', body=body).execute()
    event_id = event.get('id')
    events = load_json(EVENT_FILE)
    events[key] = event_id
    save_json(EVENT_FILE, events)
    messagebox.showinfo("✅", f"Assignment added.")
    refresh_all()

def edit_assignments():
    keys = [k for k in assignments if assignments[k]['status'] != 'Done']
    if not keys:
        return messagebox.showinfo("✅", "No pending assignments.")
    text.config(state=tk.NORMAL)
    text.delete(1.0, tk.END)
    for i, key in enumerate(keys, 1):
        data = assignments[key]
        text.insert(tk.END, f"{i}. {data['task']} (Due: {data['due']})\n")
    text.config(state=tk.DISABLED)
    nums = simpledialog.askstring("Completed", "Enter numbers (comma-separated):")
    if not nums: return
    for i in map(int, nums.split(',')):
        assignments[keys[i - 1]]["status"] = "Done"
    save_json(ASSIGN_FILE, assignments)
    refresh_all()

def delete_topic():
    name = simpledialog.askstring("Delete", "Topic name:")
    if name not in records:
        return messagebox.showerror("❌", "Topic not found.")
    if not messagebox.askyesno("Confirm", f"Delete '{name}' and related calendar events?"): return
    service = create_calendar_service()
    event_list = load_json(EVENT_FILE)
    for d in records[name]:
        date = get_date_only(d)
        key = f"{name}__{date}"
        if key in event_list:
            try:
                service.events().delete(calendarId='primary', eventId=event_list[key]).execute()
                del event_list[key]
            except Exception:
                pass
    del records[name]
    save_json(RECORD_FILE, records)
    save_json(EVENT_FILE, event_list)
    messagebox.showinfo("✅", f"'{name}' removed.")
    refresh_all()

def show_countdown():
    days = (GATE_DATE - datetime.today().date()).days
    label_countdown.config(text=f"🎯 GATE in {days} days")

def refresh_all():
    global records, assignments, backlog
    records = load_json(RECORD_FILE)
    assignments = load_json(ASSIGN_FILE)
    backlog = load_json(BACKLOG_FILE)
    show_countdown()
    notify_assignments_due()
    notify_revisions()

# -------- GUI SETUP & MENU BAR --------
root = tk.Tk()
root.title("📘 GATE Planner with Google Calendar")
root.geometry("1050x650")
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

menu_bar = Menu(root)
root.config(menu=menu_bar)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=root.destroy)
menu_bar.add_cascade(label="File", menu=file_menu)
rev_menu = Menu(menu_bar, tearoff=0)
rev_menu.add_command(label="Add Topic", command=add_topic)
rev_menu.add_command(label="View Topics", command=view_topics)
rev_menu.add_command(label="View Schedule", command=view_schedule)
rev_menu.add_command(label="Revisions Today", command=revise_today)
rev_menu.add_command(label="Backlog", command=view_backlog)
rev_menu.add_command(label="Delete Topic", command=delete_topic)
menu_bar.add_cascade(label="Revision", menu=rev_menu)
assign_menu = Menu(menu_bar, tearoff=0)
assign_menu.add_command(label="Add Assignment", command=add_assignment)
assign_menu.add_command(label="Edit Assignments", command=edit_assignments)
menu_bar.add_cascade(label="Assignment", menu=assign_menu)
menu_bar.add_command(label="Help", command=lambda: messagebox.showinfo("About", "Created by Sahin using Python 💡"))

label_countdown = ttk.Label(root, font=("Helvetica", 14), foreground="blue")
label_countdown.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
frame_main = tk.Frame(root)
frame_main.grid(row=1, column=0, columnspan=2, sticky="nsew")
frame_main.columnconfigure(0, weight=2)
frame_main.columnconfigure(1, weight=1)
text = scrolledtext.ScrolledText(frame_main, font=("Courier", 10), wrap="word", state="disabled")
text.grid(row=0, column=0, sticky="nsew", padx=10)
panel = scrolledtext.ScrolledText(frame_main, font=("Arial", 10), bg="#f5f5f5", wrap="word", state="disabled", width=50)
panel.grid(row=0, column=1, sticky="nsew", padx=10)

entry_today = ttk.Entry(root, width=25)
entry_today.grid(row=3, column=0, padx=10, sticky='w')

records, assignments, backlog = {}, {}, {}
refresh_all()
root.mainloop()
