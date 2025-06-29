import ctypes import tkinter as tk

ES_CONTINUOUS = 0x80000000 ES_SYSTEM_REQUIRED = 0x00000001 ES_DISPLAY_REQUIRED = 0x00000002

Start keeping PC awake

ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)

def close(): # Restore normal behavior ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS) root.destroy()

root = tk.Tk() root.title("Stay Awake")

btn = tk.Button(root, text="Close", command=close, width=30, height=3) btn.pack(padx=20, pady=20)

root.mainloop()