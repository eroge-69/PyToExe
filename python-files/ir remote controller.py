import serial
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import pyautogui
import os
from collections import deque

CONFIG_FILE = 'config.json'
MAX_HISTORY = 50  # Maximum number of codes to keep in history

# Load config from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save config to file
def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Perform action based on type
def perform_action(action):
    if action['type'] == 'key':
        pyautogui.press(action['value'])
    elif action['type'] == 'hotkey':
        keys = action['value'].split('+')
        pyautogui.hotkey(*keys)
    elif action['type'] == 'write':
        pyautogui.write(action['value'])
    elif action['type'] == 'run':
        os.system(action['value'])

# Serial listener thread
def serial_listener(port, baud, callback):
    try:
        ser = serial.Serial(port, baud)
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if '0x' in line:
                    code = '0x' + line.split('0x')[-1].upper()
                    callback(code)
    except Exception as e:
        print("Serial error:", e)

# GUI class
class IRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IR Remote Hotkey Mapper")
        self.config = load_config()
        self.code_history = deque(maxlen=MAX_HISTORY)  # Store received codes

        self.last_code = tk.StringVar()

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Left frame for controls
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side='left', fill='y')

        tk.Label(left_frame, text="Last IR Code:").pack()
        tk.Entry(left_frame, textvariable=self.last_code, font=('Arial', 14), width=30).pack(pady=5)

        self.action_type = tk.StringVar(value='key')
        self.action_value = tk.StringVar()

        frame = tk.Frame(left_frame)
        frame.pack(pady=10)

        tk.Label(frame, text="Action Type:").grid(row=0, column=0)
        ttk.Combobox(frame, textvariable=self.action_type, values=['key', 'hotkey', 'write', 'run'], width=15).grid(row=0, column=1)

        tk.Label(frame, text="Action Value:").grid(row=1, column=0)
        tk.Entry(frame, textvariable=self.action_value, width=30).grid(row=1, column=1)

        tk.Button(left_frame, text="Save Mapping", command=self.save_mapping).pack(pady=5)
        tk.Button(left_frame, text="Show Config", command=self.show_config).pack(pady=5)
        tk.Button(left_frame, text="Show Received Codes", command=self.show_received_codes).pack(pady=5)

        # Right frame for code history
        self.history_text = scrolledtext.ScrolledText(main_frame, wrap='word', width=40, height=20)
        self.history_text.pack(side='right', fill='both', expand=True, padx=10)
        self.history_text.insert('1.0', "Received IR Codes will appear here...\n")
        self.history_text.config(state='disabled')

        # Start serial thread
        threading.Thread(target=serial_listener, args=('COM3', 9600, self.on_code), daemon=True).start()

    def on_code(self, code):
        print("Received:", code)
        self.last_code.set(code)
        self.code_history.append(code)
        
        # Update history display
        self.history_text.config(state='normal')
        self.history_text.insert('end', f"{code}\n")
        self.history_text.see('end')
        self.history_text.config(state='disabled')
        
        if code in self.config:
            perform_action(self.config[code])

    def save_mapping(self):
        code = self.last_code.get()
        if not code:
            messagebox.showerror("Error", "No IR code to map.")
            return
        self.config[code] = {
            'type': self.action_type.get(),
            'value': self.action_value.get()
        }
        save_config(self.config)
        messagebox.showinfo("Saved", f"Mapping saved for {code}.")

    def show_config(self):
        msg = json.dumps(self.config, indent=2)
        top = tk.Toplevel(self.root)
        top.title("Current Config")
        txt = tk.Text(top, wrap='word', width=60, height=20)
        txt.insert('1.0', msg)
        txt.pack()
        txt.config(state='disabled')

    def show_received_codes(self):
        top = tk.Toplevel(self.root)
        top.title("Received IR Codes History")
        txt = scrolledtext.ScrolledText(top, wrap='word', width=60, height=20)
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        
        if not self.code_history:
            txt.insert('1.0', "No IR codes received yet.")
        else:
            txt.insert('1.0', "Received IR Codes:\n\n")
            for code in self.code_history:
                txt.insert('end', f"{code}\n")
        
        txt.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = IRApp(root)
    root.mainloop()