import tkinter as tk
import pygetwindow as gw
import psutil
import threading
import time
import pyautogui

# Tooltip window
class ToolTip(tk.Toplevel):
    def __init__(self, widget, text="info"):
        super().__init__(widget)
        self.withdraw()
        self.overrideredirect(True)
        self.label = tk.Label(self, text=text, background="#ffffe0", relief='solid',
                              borderwidth=1, font=("Arial", 10), justify='left')
        self.label.pack()

    def show(self, x, y, text):
        self.label.config(text=text)
        self.geometry(f"+{x + 20}+{y + 20}")
        self.deiconify()

    def hide(self):
        self.withdraw()

# Match process info by title
def get_resource_info(title):
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if title.lower() in proc.info['name'].lower():
                cpu = proc.info['cpu_percent']
                mem = proc.info['memory_percent']
                total_mem = psutil.virtual_memory().total / (1024 ** 3)
                used_mem = psutil.virtual_memory().used / (1024 ** 3)
                available_mem = psutil.virtual_memory().available / (1024 ** 3)

                return f"CPU: {cpu:.1f}%\nRAM Used: {mem:.1f}%\n\nSystem RAM:\nUsed: {used_mem:.1f} GB\nAvailable: {available_mem:.1f} GB\nTotal: {total_mem:.1f} GB"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return "Process info not found."

# Filter system windows
def list_open_windows():
    all_windows = gw.getAllTitles()
    system_keywords = [
        "program manager", "settings", "explorer", "task manager",
        "start menu", "windows default", "desktop", "lock screen", "shell"
    ]

    listbox.delete(0, tk.END)

    for title in all_windows:
        clean_title = title.strip().lower()
        if clean_title and not any(sys_key in clean_title for sys_key in system_keywords):
            listbox.insert(tk.END, title)

# Events
def on_motion(event):
    index = listbox.nearest(event.y)
    if 0 <= index < listbox.size():
        title = listbox.get(index)
        info = get_resource_info(title)
        tooltip.show(event.x_root, event.y_root, info)

def on_leave(event):
    tooltip.hide()

# Mouse clicker logic
clicker_running = False
click_count = 0

def start_clicker():
    global clicker_running
    selected = listbox.curselection()
    if not selected:
        lbl_status.config(text="❌ Select a window first", fg="red")
        return

    try:
        interval = float(entry_interval.get())
        if interval <= 0:
            raise ValueError
    except ValueError:
        lbl_status.config(text="❌ Invalid interval", fg="red")
        return

    clicker_running = True
    threading.Thread(target=click_loop, args=(listbox.get(selected[0]), interval), daemon=True).start()
    btn_clicker.config(text="Dont ClicKeith!", bg="red")
    lbl_status.config(text="✅ Clicker running", fg="green")

def stop_clicker():
    global clicker_running
    clicker_running = False
    btn_clicker.config(text="Start Clicker", bg="green")
    lbl_status.config(text="⏹️ Clicker stopped", fg="blue")

def toggle_clicker():
    if clicker_running:
        stop_clicker()
    else:
        start_clicker()

def click_loop(window_title, interval):
    global click_count
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
    except IndexError:
        lbl_status.config(text="❌ Window not found", fg="red")
        stop_clicker()
        return

    while clicker_running:
        if not win.isMinimized:
            x = win.left + win.width // 2
            y = win.top + win.height // 2
            pyautogui.click(x, y)
            click_count += 1
            lbl_counter.config(text=f"🖱️ Total Clicks: {click_count}")
        time.sleep(interval)

# GUI setup
root = tk.Tk()
root.title("Window Viewer + Targeted Clicker")
root.geometry("580x550")

btn_refresh = tk.Button(root, text="Refresh List", command=list_open_windows)
btn_refresh.pack(pady=5)

listbox = tk.Listbox(root, width=70, height=16)
listbox.pack(pady=5)

tooltip = ToolTip(root)
listbox.bind("<Motion>", on_motion)
listbox.bind("<Leave>", on_leave)

# Interval input
frame_interval = tk.Frame(root)
frame_interval.pack(pady=5)
tk.Label(frame_interval, text="Interval (seconds): ").pack(side=tk.LEFT)
entry_interval = tk.Entry(frame_interval, width=10)
entry_interval.insert(0, "10")
entry_interval.pack(side=tk.LEFT)

# Clicker button
btn_clicker = tk.Button(root, text="Start Clicker", bg="green", fg="white", font=("Arial", 12), command=toggle_clicker)
btn_clicker.pack(pady=10)

# Click counter and status
lbl_counter = tk.Label(root, text="🖱️ Total Clicks: 0", font=("Arial", 11))
lbl_counter.pack()

lbl_status = tk.Label(root, text="Status: Idle", font=("Arial", 10), fg="gray")
lbl_status.pack(pady=5)

list_open_windows()
root.mainloop()
