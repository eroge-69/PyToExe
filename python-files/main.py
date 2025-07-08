import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import time

macros = []
global_running = True  # Global toggle flag

class Macro:
    def __init__(self, hotkey, action_type, action_value, delay, loop):
        self.hotkey = hotkey
        self.action_type = action_type
        self.action_value = action_value
        self.delay = delay / 1000  # convert to seconds
        self.loop = loop
        self.thread = None
        self.running = False

    def run(self):
        keyboard.add_hotkey(self.hotkey, self.start_thread)

    def stop(self):
        keyboard.remove_hotkey(self.hotkey)
        self.running = False

    def start_thread(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.execute)
            self.thread.daemon = True
            self.thread.start()

    def execute(self):
        while self.running and global_running:
            time.sleep(self.delay)
            if self.action_type == "Press Key":
                keyboard.press_and_release(self.action_value)
            elif self.action_type == "Type Text":
                keyboard.write(self.action_value)
            if not self.loop:
                break

def toggle_global():
    global global_running
    global_running = not global_running
    status_label.config(text=f"Status: {'ON' if global_running else 'OFF'}", fg='green' if global_running else 'red')

def start_macros():
    for macro in macros:
        macro.run()

def stop_macros():
    for macro in macros:
        macro.stop()

def add_macro():
    hotkey = entry_hotkey.get().strip()
    action_type = combo_action.get()
    action_value = entry_value.get().strip()
    try:
        delay = int(entry_delay.get())
    except:
        delay = 0
    loop = loop_var.get()

    if hotkey and action_type and action_value:
        macro = Macro(hotkey, action_type, action_value, delay, loop)
        macros.append(macro)
        listbox.insert(tk.END, f"{hotkey} -> {action_type}({action_value}) Delay:{delay}ms Loop:{loop}")
        entry_hotkey.delete(0, tk.END)
        entry_value.delete(0, tk.END)

# GUI Setup
window = tk.Tk()
window.title("Keyboard Macro Tool")
window.geometry("500x400")

frame = tk.Frame(window)
frame.pack(pady=10)

tk.Label(frame, text="Hotkey").grid(row=0, column=0)
entry_hotkey = tk.Entry(frame)
entry_hotkey.grid(row=0, column=1)

tk.Label(frame, text="Action").grid(row=1, column=0)
combo_action = ttk.Combobox(frame, values=["Press Key", "Type Text"])
combo_action.grid(row=1, column=1)
combo_action.set("Press Key")

tk.Label(frame, text="Value").grid(row=2, column=0)
entry_value = tk.Entry(frame)
entry_value.grid(row=2, column=1)
tk.Label(frame, text="(ex: W, Enter, Hello)").grid(row=2, column=2)

tk.Label(frame, text="Delay (ms)").grid(row=3, column=0)
entry_delay = tk.Entry(frame)
entry_delay.grid(row=3, column=1)
entry_delay.insert(0, "0")

loop_var = tk.BooleanVar()
tk.Checkbutton(frame, text="Loop?", variable=loop_var).grid(row=4, column=1)

tk.Button(frame, text="Tambah Macro", command=add_macro).grid(row=5, column=0, columnspan=2, pady=5)

listbox = tk.Listbox(window)
listbox.pack(fill=tk.BOTH, expand=True)

tk.Button(window, text="Start Macros", command=start_macros).pack(side=tk.LEFT, expand=True, fill=tk.X)
tk.Button(window, text="Stop Macros", command=stop_macros).pack(side=tk.RIGHT, expand=True, fill=tk.X)

status_label = tk.Label(window, text="Status: ON", fg='green')
status_label.pack(pady=5)

# Global toggle with F12
keyboard.add_hotkey('F12', toggle_global)

window.mainloop()
