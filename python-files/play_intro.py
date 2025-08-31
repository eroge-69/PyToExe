import sys
import os
import time
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import vlc

class VideoPlayer(tk.Tk):
    def __init__(self, video_path, video_length):
        super().__init__()
        self.video_path = video_path
        self.video_length = video_length
        self.skip = False
        self.title("Wake Up Samurai")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.overrideredirect(True)  # Remove window border to simulate fullscreen
        self.focus_set()

        # VLC player setup
        self.instance = vlc.Instance("--no-video-title-show")
        self.player = self.instance.media_player_new()

        # Embed VLC video in tkinter frame
        self.video_panel = tk.Frame(self)
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # Set the handle where VLC will render the video
        self._set_vlc_handle()

        # Load media
        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)
        self.player.play()

        # Bind events
        self.bind("<space>", self.on_space)
        self.bind("<Button>", lambda e: "break")  # Ignore all mouse clicks
        self.bind("<Double-Button>", lambda e: "break")  # Ignore double clicks

        # Start a thread to monitor video end or skip
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _set_vlc_handle(self):
        # Different OS need different handle types
        if sys.platform == "win32":
            self.player.set_hwnd(self.video_panel.winfo_id())
        elif sys.platform == "linux":
            self.player.set_xwindow(self.video_panel.winfo_id())
        elif sys.platform == "darwin":
            from ctypes import c_void_p
            self.player.set_nsobject(c_void_p(self.video_panel.winfo_id()))

    def on_space(self, event):
        print("Space pressed - skipping video")
        self.skip = True
        self.player.stop()

    def _monitor(self):
        start_time = time.time()
        while True:
            if self.skip:
                break
            state = self.player.get_state()
            if state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
                break
            if time.time() - start_time > self.video_length + 1:
                break
            time.sleep(0.1)

        # After video ends or skipped, close window and launch background.py
        self.player.stop()
        self.destroy()
        self.launch_background()

    def launch_background(self):
        # Launch background.py in separate process
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        background_script = os.path.join(base_path, "background.py")
        python_exe = sys.executable
        subprocess.Popen([python_exe, background_script])

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    video_path = os.path.join(base_path, "wakeup.mp4")
    video_length = 18  # adjust if your video length differs

    app = VideoPlayer(video_path, video_length)
    app.mainloop()
