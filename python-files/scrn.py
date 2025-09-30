import tkinter as tk
from PIL import ImageGrab
import datetime
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# Colors
BG_COLOR = "#0b1e3b"  # Dark blue
FG_COLOR = "white"
BTN_COLOR = "#1e3f66"
BTN_HOVER_COLOR = "#305a99"
RERECORD_BTN_COLOR = "#1f618d"
EXIT_BTN_COLOR = "#b22222"
TITLE_BAR_COLOR = "#0a162a"
TITLE_FG = "white"

# Helper to create rounded buttons
def create_rounded_button(parent, text, bg, fg, command=None):
    btn = tk.Button(parent, text=text, bg=bg, fg=fg, bd=0, relief="ridge",
                    activebackground=BTN_HOVER_COLOR, activeforeground=fg, command=command)
    btn.config(font=("Arial", 11), highlightthickness=0)
    return btn

# Overlay for screenshot selection
class ScreenshotOverlay:
    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg=BG_COLOR)
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.canvas = tk.Canvas(self.root, cursor="cross", bg=BG_COLOR)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = self.canvas.winfo_pointerx()
        self.start_y = self.canvas.winfo_pointery()
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = None

    def on_move_press(self, event):
        cur_x = self.canvas.winfo_pointerx()
        cur_y = self.canvas.winfo_pointery()
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y, outline='red', width=2
        )
        triangle_size = 10
        self.canvas.create_polygon(
            self.start_x, self.start_y,
            self.start_x + triangle_size, self.start_y,
            self.start_x, self.start_y + triangle_size,
            fill='red'
        )

    def on_button_release(self, event):
        end_x = self.canvas.winfo_pointerx()
        end_y = self.canvas.winfo_pointery()
        self.root.destroy()

        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)

        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_img = f"screenshots/screenshot_{timestamp}.png"
        filename_txt = f"screenshots/screenshot_{timestamp}.txt"
        filename_wav = f"screenshots/screenshot_{timestamp}.wav"

        screenshot.save(filename_img)

        # Open note/audio dialog in center
        NoteAudioDialog(filename_txt, filename_wav)


class NoteAudioDialog:
    def __init__(self, filename_txt, filename_wav):
        self.filename_txt = filename_txt
        self.filename_wav = filename_wav
        self.fs = 44100
        self.recording = []
        self.stream = None

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        w, h = 380, 260
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=BG_COLOR)

        # Title bar
        self.title_bar = tk.Frame(self.root, bg=TITLE_BAR_COLOR, height=28)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        tk.Label(self.title_bar, text="Note & Audio Recorder", bg=TITLE_BAR_COLOR, fg=TITLE_FG,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        close_btn = tk.Button(self.title_bar, text="✖", bg=TITLE_BAR_COLOR, fg=TITLE_FG, bd=0, command=self.root.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        #min_btn = tk.Button(self.title_bar, text="—", bg=TITLE_BAR_COLOR, fg=TITLE_FG, bd=0, command=self.minimize)
        #min_btn.pack(side=tk.RIGHT)

        tk.Label(self.root, text="Enter a note:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        self.note_entry = tk.Text(self.root, height=5, width=45, bg="gray20", fg=FG_COLOR, insertbackground=FG_COLOR)
        self.note_entry.pack(pady=5)

        self.record_btn = create_rounded_button(self.root, "Press & Hold to Record", BTN_COLOR, FG_COLOR)
        self.record_btn.bind("<ButtonPress-1>", self.start_recording)
        self.record_btn.bind("<ButtonRelease-1>", self.stop_recording)
        self.record_btn.pack(pady=5)

        self.rerecord_btn = create_rounded_button(self.root, "Re-record", RERECORD_BTN_COLOR, FG_COLOR, self.rerecord)
        self.rerecord_btn.pack_forget()

        self.save_btn = create_rounded_button(self.root, "Save Note & Audio", BTN_COLOR, FG_COLOR, self.save_all)
        self.save_btn.pack(pady=8)

        self.status_label = tk.Label(self.root, text="", fg="cyan", bg=BG_COLOR)
        self.status_label.pack(pady=5)

        self.root.mainloop()

    def move_window(self, event):
        x = event.x_root - event.x
        y = event.y_root - event.y
        self.root.geometry(f"+{x}+{y}")

    def minimize(self):
        self.root.withdraw()  # workaround for overrideredirect
        self.root.after(0, self.root.deiconify)

    def start_recording(self, event):
        self.recording = []
        self.stream = sd.InputStream(samplerate=self.fs, channels=2, callback=self.callback)
        self.stream.start()
        self.status_label.config(text="Recording...")
        self.record_btn.config(bg="red")

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.recording.append(indata.copy())

    def stop_recording(self, event):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        if self.recording:
            audio_data = np.concatenate(self.recording, axis=0)
            write(self.filename_wav, self.fs, audio_data)
            self.status_label.config(text=f"Audio saved: {self.filename_wav}")
            self.record_btn.config(bg=BTN_COLOR)
            self.rerecord_btn.pack(pady=5)

    def rerecord(self):
        if os.path.exists(self.filename_wav):
            os.remove(self.filename_wav)
        self.recording = []
        self.status_label.config(text="Re-record ready. Press & Hold to Record")
        self.rerecord_btn.pack_forget()

    def save_all(self):
        note_text = self.note_entry.get("1.0", tk.END).strip()
        with open(self.filename_txt, "w") as f:
            f.write(note_text)
        self.root.destroy()
        # Show dark-themed saved window
        SavedWindow(f"Screenshot, note, and audio saved successfully.")


class SavedWindow:
    def __init__(self, message):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        w, h = 350, 120
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=BG_COLOR)

        self.title_bar = tk.Frame(self.root, bg=TITLE_BAR_COLOR, height=28)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        tk.Label(self.title_bar, text="Info", bg=TITLE_BAR_COLOR, fg=TITLE_FG, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        close_btn = tk.Button(self.title_bar, text="✖", bg=TITLE_BAR_COLOR, fg=TITLE_FG, bd=0, command=self.root.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

        tk.Label(self.root, text=message, bg=BG_COLOR, fg="cyan", wraplength=320).pack(pady=30)

        # Close window on any mouse click
        self.root.bind("<Button-1>", lambda e: self.root.destroy())
        self.root.mainloop()

    def move_window(self, event):
        x = event.x_root - event.x
        y = event.y_root - event.y
        self.root.geometry(f"+{x}+{y}")


class ControlWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        w, h = 200, 120
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = screen_w - w - 20
        y = screen_h - h - 60
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-topmost", True)

        self.title_bar = tk.Frame(self.root, bg=TITLE_BAR_COLOR, height=28)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.bind("<B1-Motion>", self.move_window)
        tk.Label(self.title_bar, text="Screenshot Tool", bg=TITLE_BAR_COLOR, fg=TITLE_FG,
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        close_btn = tk.Button(self.title_bar, text="✖", bg=TITLE_BAR_COLOR, fg=TITLE_FG, bd=0, command=self.root.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        #min_btn = tk.Button(self.title_bar, text="—", bg=TITLE_BAR_COLOR, fg=TITLE_FG, bd=0, command=self.minimize)
        #min_btn.pack(side=tk.RIGHT)

        capture_btn = create_rounded_button(self.root, "Capture", BTN_COLOR, FG_COLOR, lambda: ScreenshotOverlay(self.root))
        capture_btn.pack(expand=True, fill="both", padx=10, pady=10)

        self.root.mainloop()

    def move_window(self, event):
        x = event.x_root - event.x
        y = event.y_root - event.y
        self.root.geometry(f"+{x}+{y}")

    def minimize(self):
        # Workaround for overrideredirect window
        self.root.withdraw()
        self.root.after(0, self.root.deiconify)


if __name__ == "__main__":
    ControlWindow()
