
import os, random, sys
import tkinter as tk
from tkinter import ttk
from screeninfo import get_monitors
from ffpyplayer.player import MediaPlayer
import threading
import keyboard

VIDEO_DIR = r"C:\VideoKiosk"
EXIT_COMBO = 'ctrl+alt+q'

class VideoKiosk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Kiosk")
        self.geometry("1080x1920+0+0")
        self.configure(bg='black')
        self.video_paths = [os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.lower().endswith('.mp4')]
        self.player = None
        self.play_thread = None
        self.create_widgets()
        keyboard.add_hotkey(EXIT_COMBO, self.exit_app)
        self.current_video = None

    def create_widgets(self):
        self.canvas = tk.Canvas(self, bg='gray15')
        self.canvas.pack(fill='both', expand=True)
        self.render_buttons()

    def render_buttons(self):
        self.canvas.delete("all")
        rows = 4; cols = 2
        btn_w = 1080//cols; btn_h = 1920//rows

        for idx, path in enumerate(self.video_paths):
            r = idx // cols; c = idx % cols
            x = c * btn_w; y = r * btn_h
            name = os.path.splitext(os.path.basename(path))[0]
            btn = tk.Button(self.canvas, text=name, command=lambda p=path: self.start_video(p),
                            font=("Helvetica", 24), bg='dark slate gray', fg='white')
            self.canvas.create_window(x+btn_w//2, y+btn_h//2, window=btn, width=btn_w-20, height=btn_h-20)

    def start_video(self, path):
        self.current_video = path
        if self.play_thread and self.play_thread.is_alive():
            self.stop_player()
        self.play_thread = threading.Thread(target=self.play_loop, daemon=True)
        self.play_thread.start()

    def play_loop(self):
        while True:
            self.play_video(self.current_video)
            self.current_video = random.choice(self.video_paths)

    def play_video(self, path):
        monitors = get_monitors()
        sec_mon = monitors[1] if len(monitors)>1 else monitors[0]
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{sec_mon.x},{sec_mon.y}"
        player = MediaPlayer(path, ff_opts={'output_format':'rawvideo','dr':'0','vout':'directx'})
        while True:
            frame, val = player.get_frame()
            if val == 'eof' or keyboard.is_pressed(EXIT_COMBO):
                player.close_player()
                if val == 'eof': break
                else: self.exit_app()
                return
        player.close_player()

    def stop_player(self):
        keyboard.press_and_release(EXIT_COMBO)

    def exit_app(self):
        os._exit(0)

if __name__ == "__main__":
    if not os.path.isdir(VIDEO_DIR):
        print(f"Ordner nicht gefunden: {VIDEO_DIR}")
        sys.exit(1)
    app = VideoKiosk()
    app.mainloop()
