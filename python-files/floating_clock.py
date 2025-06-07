import tkinter as tk
import time

class FloatingClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("悬浮时钟")
        self.attributes("-topmost", True)  # 永远置顶
        self.overrideredirect(True)  # 去掉窗口边框
        self.config(bg="black")
        
        self.label = tk.Label(self, font=("Arial", 24), fg="white", bg="black")
        self.label.pack()
        
        self.update_time()
        
        # 支持拖动窗口
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<ButtonRelease-1>", self.stop_move)
        self.label.bind("<B1-Motion>", self.do_move)

        self._offset_x = 0
        self._offset_y = 0

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.label.config(text=current_time)
        self.after(1000, self.update_time)

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def stop_move(self, event):
        self._offset_x = 0
        self._offset_y = 0

    def do_move(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = FloatingClock()
    app.mainloop()