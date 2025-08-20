import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pywhatkit as kit
import time
from datetime import datetime
import threading

csv_file = ""
stop_sending = False  # Flag to stop sending messages

# --- Thread-safe UI updates ---
def append_status(text):
    """Append text to status box from any thread"""
    status_box.after(0, lambda: status_box.insert(tk.END, text + "\n"))
    status_box.after(0, lambda: status_box.see(tk.END))

def update_counter(total, sent_count):
    """Update total/sent label from any thread"""
    total_label.after(0, lambda: total_label.config(text=f"Total: {total} | Sent: {sent_count}"))

# --- Helper Functions ---
def browse_file():
    global csv_file
    csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    file_label.config(text=csv_file if csv_file else "No file selected")

def clean_phone(number):
    number = str(number).strip().replace(' ', '').replace('-', '')
    if number.startswith('0'):
        number = number[1:]
    if not number.startswith('+'):
        number = '+91' + number
    return number

def stop_messages():
    global stop_sending
    stop_sending = True
    append_status("⏹️ Stopping messages...")

# --- Sending Messages Thread ---
def send_messages_thread():
    global csv_file, stop_sending
    stop_sending = False
    use_csv = csv_radio_var.get() == 1

    # Prepare contacts
    if use_csv:
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        try:
            df = pd.read_csv(csv_file, dtype={'Phone': str})
            if 'Name' not in df.columns or 'Phone' not in df.columns:
                messagebox.showerror("Error", "CSV must have 'Name' and 'Phone' columns")
                return
            df['Phone'] = df['Phone'].apply(clean_phone)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {e}")
            return
    else:
        name = adhoc_name_entry.get().strip()
        phone = adhoc_phone_entry.get().strip()
        if not name or not phone:
            messagebox.showerror("Error", "Please enter Name and Phone")
            return
        df = pd.DataFrame([[name, clean_phone(phone)]], columns=['Name','Phone'])

    # Message
    msg_template = msg_text.get("1.0", tk.END).strip()
    if not msg_template:
        messagebox.showerror("Error", "Please enter a message")
        return

    # Time between messages
    try:
        wait_seconds = int(time_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Time between messages must be a number")
        return

    # Optional schedule time
    schedule_time_str = sched_hour.get() + ":" + sched_min.get()
    if schedule_time_str.strip() and schedule_time_str != "00:00":
        try:
            hh, mm = map(int, schedule_time_str.split(":"))
            now = datetime.now()
            delay_seconds = ((hh - now.hour) * 3600 + (mm - now.minute) * 60 - now.second)
            if delay_seconds < 0:
                delay_seconds += 86400  # next day
            append_status(f"⏳ Waiting {delay_seconds} seconds until scheduled start...")
            time.sleep(delay_seconds)
        except Exception:
            append_status("⚠️ Invalid schedule time. Sending immediately.")

    # Initialize counters
    total = len(df)
    sent_count = 0
    update_counter(total, sent_count)

    # Send messages
    for idx, row in df.iterrows():
        if stop_sending:
            append_status("⏹️ Message sending stopped by user.")
            break
        name = row['Name']
        phone = row['Phone']
        message = msg_template.replace("{name}", name)
        try:
            kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)
            sent_count += 1
            append_status(f"✅ Sent to {name} ({phone})")
        except Exception as e:
            append_status(f"❌ Failed for {name} ({phone}): {e}")
        update_counter(total, sent_count)
        time.sleep(wait_seconds)

# --- Tkinter UI ---
root = tk.Tk()
root.title("WhatsApp Bulk Sender")
root.geometry("750x720")

# Mode selection
csv_radio_var = tk.IntVar(value=1)
tk.Label(root, text="Select Mode:").pack(pady=5)
tk.Radiobutton(root, text="Upload CSV", variable=csv_radio_var, value=1).pack()
tk.Radiobutton(root, text="Adhoc Entry", variable=csv_radio_var, value=2).pack()

# CSV selection
tk.Button(root, text="Browse CSV", command=browse_file, width=20).pack()
file_label = tk.Label(root, text="No file selected", fg="blue")
file_label.pack(pady=5)

# Adhoc entry
tk.Label(root, text="Or enter Name and Phone manually:").pack(pady=5)
adhoc_frame = tk.Frame(root)
adhoc_frame.pack(pady=5)
tk.Label(adhoc_frame, text="Name:").grid(row=0, column=0)
adhoc_name_entry = tk.Entry(adhoc_frame, width=20)
adhoc_name_entry.grid(row=0, column=1, padx=5)
tk.Label(adhoc_frame, text="Phone:").grid(row=0, column=2)
adhoc_phone_entry = tk.Entry(adhoc_frame, width=20)
adhoc_phone_entry.grid(row=0, column=3, padx=5)

# Message body
tk.Label(root, text="Enter Message (use {name} for personalization)").pack(pady=5)
msg_text = tk.Text(root, height=5, width=70)
msg_text.pack(pady=5)

# Time between messages
tk.Label(root, text="Time Between Messages (seconds)").pack(pady=5)
time_entry = tk.Entry(root)
time_entry.insert(0, "5")
time_entry.pack(pady=5)

# Schedule start time
tk.Label(root, text="Schedule Start Time (HH:MM, 24h) - leave 00:00 to run immediately").pack(pady=5)
frame_sched = tk.Frame(root)
frame_sched.pack(pady=5)
sched_hour = tk.Spinbox(frame_sched, from_=0, to=23, width=5, format="%02.0f")
sched_hour.pack(side=tk.LEFT, padx=5)
sched_min = tk.Spinbox(frame_sched, from_=0, to=59, width=5, format="%02.0f")
sched_min.pack(side=tk.LEFT, padx=5)

# Buttons
button_frame = tk.Frame(root, bg="#2E2E2E")  # Dark background for frame
button_frame.pack(pady=10)

start_btn = tk.Button(button_frame, text="Start Sending",
                      command=lambda: threading.Thread(target=send_messages_thread).start(),
                      bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white",
                      width=20, relief="raised", bd=2)
start_btn.pack(side=tk.LEFT, padx=10)

stop_btn = tk.Button(button_frame, text="Stop Sending",
                     command=stop_messages,
                     bg="#f44336", fg="white", activebackground="#da190b", activeforeground="white",
                     width=20, relief="raised", bd=2)
stop_btn.pack(side=tk.LEFT, padx=10)

# Total / Sent counters
total_label = tk.Label(root, text="Total: 0 | Sent: 0", font=("Arial", 12, "bold"))
total_label.pack(pady=5)

# Status box
tk.Label(root, text="Status").pack(pady=5)
status_box = tk.Text(root, height=20, width=85)
status_box.pack(pady=5)

root.mainloop()
