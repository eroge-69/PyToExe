import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue, Empty
from datetime import datetime
from pynput import mouse

APP_TITLE = "Click Coordinate Recorder"

class CoordinateRecorder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("480x360")
        self.capturing = tk.BooleanVar(value=False)
        self.coords = []
        self.queue = Queue()

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.toggle_btn = ttk.Button(top, text="▶ Start", command=self.toggle_capture)
        self.toggle_btn.pack(side="left")

        self.status_lbl = ttk.Label(top, text="Idle", foreground="gray")
        self.status_lbl.pack(side="left", padx=12)

        self.aot_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Always on top", variable=self.aot_var, command=self.apply_aot).pack(side="right")

        mid = ttk.Frame(self, padding=(10,0))
        mid.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(mid, font=("Consolas", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(mid, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Copy Selected", command=self.copy_selected).pack(side="left")
        ttk.Button(bottom, text="Clear", command=self.clear_all).pack(side="left", padx=8)

        self.count_lbl = ttk.Label(bottom, text="0 points")
        self.count_lbl.pack(side="right")

        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.daemon = True
        self.listener.start()

        self.after(60, self.drain_queue)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
        if not self.capturing.get():
            return
        if button == mouse.Button.left:
            self.queue.put(("ADD", x, y, datetime.now()))

    def toggle_capture(self):
        if self.capturing.get():
            self.capturing.set(False)
            self.toggle_btn.config(text="▶ Start")
            self.status_lbl.config(text="Idle", foreground="gray")
        else:
            self.capturing.set(True)
            self.toggle_btn.config(text="⏸ Stop")
            self.status_lbl.config(text="Recording…", foreground="#0a7f2e")

    def apply_aot(self):
        self.wm_attributes("-topmost", bool(self.aot_var.get()))

    def drain_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg[0] == "ADD":
                    _, x, y, ts = msg
                    self.add_point(x, y, ts)
        except Empty:
            pass
        self.after(60, self.drain_queue)

    def add_point(self, x, y, ts):
        self.coords.append((x,y,ts))
        idx = len(self.coords)
        row = f"{idx:04d} | x={x:<5} y={y:<5} | {ts.strftime('%H:%M:%S')}"
        self.listbox.insert("end", row)
        self.count_lbl.config(text=f"{len(self.coords)} points")
        self.listbox.see("end")

    def copy_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo(APP_TITLE, "Select a row first.")
            return
        i = sel[0]
        x,y,_ = self.coords[i]
        text = f"{x},{y}"
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo(APP_TITLE, f"Copied: {text}")

    def clear_all(self):
        self.coords.clear()
        self.listbox.delete(0, "end")
        self.count_lbl.config(text="0 points")

    def on_close(self):
        try:
            if self.listener and self.listener.running:
                self.listener.stop()
        except: pass
        self.destroy()

if __name__ == "__main__":
    app = CoordinateRecorder()
    app.mainloop()
