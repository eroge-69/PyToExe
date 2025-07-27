import tkinter as tk
from tkinter import messagebox
import time
import subprocess
import sys

class CircularTimer(tk.Canvas):
    def __init__(self, parent, radius=100, width=15, countdown=10, **kwargs):
        super().__init__(parent, width=2*(radius+width), height=2*(radius+width), bg='black', highlightthickness=0, **kwargs)
        self.radius = radius
        self.width = width
        self.countdown = countdown
        self.start_time = None
        self.paused_time = 0
        self.arc = None
        self.text = None
        self.running = False
        self.paused = False
        
        self.create_oval(width, width, 2*radius+width, 2*radius+width, outline='gray30', width=width)  # background circle
        self.text = self.create_text(radius+width, radius+width, text=str(self.countdown), fill='white', font=('Helvetica', 40, 'bold'))

    def start(self):
        if not self.running:
            self.running = True
            self.paused = False
            if self.start_time is None:
                self.start_time = time.time() - self.paused_time
            else:
                self.start_time = time.time() - self.paused_time
            self._update()

    def pause(self):
        if self.running:
            self.paused = True
            self.running = False
            self.paused_time = time.time() - self.start_time

    def reset(self, new_countdown=None):
        self.running = False
        self.paused = False
        self.start_time = None
        self.paused_time = 0
        if new_countdown:
            self.countdown = new_countdown
        self.delete("all")
        # Redraw background circle
        self.create_oval(self.width, self.width, 2*self.radius+self.width, 2*self.radius+self.width, outline='gray30', width=self.width)
        self.text = self.create_text(self.radius+self.width, self.radius+self.width, text=str(self.countdown), fill='white', font=('Helvetica', 40, 'bold'))

    def _update(self):
        if not self.running:
            return
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.countdown - elapsed)
        
        self.itemconfigure(self.text, text=str(int(remaining)+1))
        
        angle = 360 * (remaining / self.countdown)
        
        if self.arc:
            self.delete(self.arc)
        
        bbox = (self.width, self.width, 2*self.radius+self.width, 2*self.radius+self.width)
        self.arc = self.create_arc(bbox, start=90, extent=-angle, style='arc', outline='cyan', width=self.width)
        
        if remaining > 0:
            self.after(16, self._update)
        else:
            self.running = False
            self.paused_time = 0
            self.itemconfigure(self.text, text="Done!")
            self.create_text(self.radius+self.width, 2*self.radius+self.width+20, text="Timer finished", fill='cyan', font=('Helvetica', 16))

def start_relax():
    answer = messagebox.askyesno("Relax", "Are you sure you want to relax?")
    if answer:
        # Try to launch satis.py first
        try:
            subprocess.Popen([sys.executable, "satis.py"])
        except Exception as e:
            # If that fails, try satis.exe
            try:
                subprocess.Popen(["satis.exe"])
            except Exception as e2:
                messagebox.showerror("Error", f"Could not launch relax program.\n{e}\n{e2}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fancy Circular Countdown Timer")
    root.config(bg='black')
    
    frame = tk.Frame(root, bg='black')
    frame.pack(padx=20, pady=20)
    
    # Time input
    time_var = tk.StringVar(value="10")
    tk.Label(frame, text="Set time (seconds):", bg='black', fg='white', font=('Helvetica', 12)).grid(row=0, column=0, sticky='e')
    time_entry = tk.Entry(frame, textvariable=time_var, width=5, font=('Helvetica', 12))
    time_entry.grid(row=0, column=1, sticky='w', padx=(5,15))
    
    timer = CircularTimer(frame, radius=120, width=15, countdown=int(time_var.get()))
    timer.grid(row=1, column=0, columnspan=4, pady=10)
    
    def start_btn_cmd():
        try:
            val = int(time_var.get())
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a positive integer for time.")
            return
        if timer.running:
            pass
        else:
            if timer.countdown != val or timer.start_time is None:
                timer.reset(new_countdown=val)
            timer.start()
    
    def pause_btn_cmd():
        timer.pause()
    
    def reset_btn_cmd():
        try:
            val = int(time_var.get())
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a positive integer for time.")
            return
        timer.reset(new_countdown=val)
    
    start_btn = tk.Button(frame, text="Start", command=start_btn_cmd, font=('Helvetica', 14), bg='cyan', fg='black', width=8)
    pause_btn = tk.Button(frame, text="Pause", command=pause_btn_cmd, font=('Helvetica', 14), bg='orange', fg='black', width=8)
    reset_btn = tk.Button(frame, text="Reset", command=reset_btn_cmd, font=('Helvetica', 14), bg='red', fg='white', width=8)
    relax_btn = tk.Button(frame, text="Relax", command=start_relax, font=('Helvetica', 14), bg='green', fg='white', width=8)
    
    start_btn.grid(row=2, column=0, pady=10, padx=5)
    pause_btn.grid(row=2, column=1, pady=10, padx=5)
    reset_btn.grid(row=2, column=2, pady=10, padx=5)
    relax_btn.grid(row=2, column=3, pady=10, padx=5)
    
    root.mainloop()
