import tkinter as tk
import datetime

class TimeLane:
    def __init__(self, canvas, color="#44aa44"):
        self.canvas = canvas
        self.color = color

    def draw(self, width, bar_y, bar_h, ms):
        pad = 10
        w = max(width - 2 * pad, 100)
        frac = ms / 1000.0
        fill_w = int(w * frac)

        x0 = pad
        x1 = pad + fill_w
        y0 = bar_y
        y1 = bar_y + bar_h

        # background bar
        self.canvas.create_rectangle(pad, y0, pad + w, y1, fill="#e6e6e6", outline="")
        # filled part
        if fill_w > 0:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.color, outline="")

class SyncClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sync Clock Bar")
        try:
            self.root.state("zoomed")  # Максимизировать окно (Windows)
        except Exception:
            pass

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.lane = TimeLane(self.canvas, "#44aa44")
        self.update_loop()

    def update_loop(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # place bar around upper third and time text below it
        bar_y = int(height * 0.28)
        bar_h = 48  # высота полоски

        now = datetime.datetime.now()
        ms = now.microsecond // 1000
        time_str = now.strftime("%H:%M:%S")  # без миллисекунд

        # draw lane
        self.lane.draw(width, bar_y, bar_h, ms)

        # draw time text centered below the bar
        text_y = bar_y + bar_h + 40
        self.canvas.create_text(
            width // 2, text_y,
            text=time_str,
            fill="black",
            font=("Consolas", 48, "bold")
        )

        self.root.after(10, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncClockApp(root)
    root.mainloop()
