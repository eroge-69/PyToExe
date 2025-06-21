import tkinter as tk
import vlc
from tkinter import filedialog
from datetime import timedelta
import time


class MediaPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Neon Player")
        self.geometry("900x600")
        self.configure(bg="#121212")
        self.initialize_player()

    def initialize_player(self):
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.current_file = None
        self.playing_video = False
        self.video_paused = False
        self.slider_dragging = False
        self.create_widgets()

    def create_widgets(self):
        # Video display
        self.video_frame = tk.Frame(self, bg="#000000", bd=0, highlightthickness=0)
        self.video_frame.pack(pady=(20, 10), padx=20, fill=tk.BOTH, expand=True)

        self.media_canvas = tk.Canvas(self.video_frame, bg="#000000", width=860, height=400)
        self.media_canvas.pack(fill=tk.BOTH, expand=True)

        # Time display
        self.time_frame = tk.Frame(self, bg="#121212")
        self.time_frame.pack(fill=tk.X, padx=20)

        self.current_time_label = tk.Label(
            self.time_frame,
            text="00:00:00",
            font=("Segoe UI", 10),
            fg="#FFFFFF",
            bg="#121212",
            width=8
        )
        self.current_time_label.pack(side=tk.LEFT)

        self.time_separator = tk.Label(
            self.time_frame,
            text="/",
            font=("Segoe UI", 10),
            fg="#AAAAAA",
            bg="#121212"
        )
        self.time_separator.pack(side=tk.LEFT, padx=2)

        self.total_time_label = tk.Label(
            self.time_frame,
            text="00:00:00",
            font=("Segoe UI", 10),
            fg="#AAAAAA",
            bg="#121212",
            width=8
        )
        self.total_time_label.pack(side=tk.LEFT)

        # Progress slider (без отображения процентов)
        self.progress_frame = tk.Frame(self, bg="#121212")
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.progress_slider = tk.Scale(
            self.progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.on_slider_move,
            bg="#252525",
            fg="#FFFFFF",
            troughcolor="#353535",
            activebackground="#4A4A4A",
            highlightthickness=0,
            sliderrelief=tk.FLAT,
            bd=0,
            length=860,
            width=15,
            showvalue=0  # Отключаем отображение значений
        )
        self.progress_slider.pack(fill=tk.X)
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Control buttons
        self.control_buttons_frame = tk.Frame(self, bg="#121212")
        self.control_buttons_frame.pack(pady=(0, 20))

        button_style = {
            "font": ("Segoe UI", 11),
            "bg": "#252525",
            "fg": "#FFFFFF",
            "activebackground": "#353535",
            "activeforeground": "#FFFFFF",
            "relief": tk.FLAT,
            "bd": 0,
            "width": 8,
            "height": 1,
            "padx": 15,
            "pady": 8
        }

        self.play_button = tk.Button(
            self.control_buttons_frame,
            text="▶ Play",
            command=self.play_video,
            **button_style
        )
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(
            self.control_buttons_frame,
            text="⏸ Pause",
            command=self.pause_video,
            **button_style
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            self.control_buttons_frame,
            text="⏹ Stop",
            command=self.stop,
            **button_style
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Volume control
        self.volume_frame = tk.Frame(self.control_buttons_frame, bg="#121212")
        self.volume_frame.pack(side=tk.LEFT, padx=(20, 0))

        self.volume_icon = tk.Label(
            self.volume_frame,
            text="🔊",
            font=("Segoe UI", 11),
            fg="#FFFFFF",
            bg="#121212"
        )
        self.volume_icon.pack(side=tk.LEFT)

        self.volume_scale = tk.Scale(
            self.volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.set_volume,
            bg="#121212",
            fg="#FFFFFF",
            highlightthickness=0,
            troughcolor="#353535",
            activebackground="#4A4A4A",
            sliderrelief=tk.FLAT,
            bd=0,
            length=120,
            width=15,
            showvalue=0  # Отключаем отображение значений
        )
        self.volume_scale.set(70)
        self.volume_scale.pack(side=tk.LEFT, padx=5)

        # File selection button
        self.select_file_button = tk.Button(
            self,
            text="📁 Open Media",
            font=("Segoe UI", 11),
            command=self.select_file,
            bg="#252525",
            fg="#FFFFFF",
            activebackground="#353535",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=5
        )
        self.select_file_button.pack(pady=(0, 15))

    def set_volume(self, volume):
        if self.playing_video:
            self.media_player.audio_set_volume(int(volume))

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Media Files", "*.mp4 *.avi *.mkv *.mov *.wmv")]
        )
        if file_path:
            self.current_file = file_path
            self.play_video()

    def format_time(self, milliseconds):
        seconds = max(0, milliseconds) // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def play_video(self):
        if not self.playing_video and self.current_file:
            media = self.instance.media_new(self.current_file)
            self.media_player.set_media(media)
            self.media_player.set_hwnd(self.media_canvas.winfo_id())
            self.media_player.play()

            # Wait for video to initialize
            for _ in range(50):
                time.sleep(0.1)
                total_duration = self.media_player.get_length()
                if total_duration > 0:
                    break

            self.playing_video = True
            self.video_paused = False
            self.media_player.audio_set_volume(self.volume_scale.get())
            self.play_button.config(text="⏹ Stop", command=self.stop)
            self.pause_button.config(text="⏸ Pause")

            total_duration = self.media_player.get_length()
            self.total_time_label.config(text=self.format_time(total_duration))

    def pause_video(self):
        if self.playing_video:
            if self.video_paused:
                self.media_player.play()
                self.video_paused = False
                self.pause_button.config(text="⏸ Pause")
            else:
                self.media_player.pause()
                self.video_paused = True
                self.pause_button.config(text="▶ Resume")

    def stop(self):
        if self.playing_video:
            self.media_player.stop()
            self.playing_video = False
        self.current_time_label.config(text="00:00:00")
        self.progress_slider.set(0)
        self.play_button.config(text="▶ Play", command=self.play_video)
        self.pause_button.config(text="⏸ Pause")

    def on_slider_move(self, value):
        if self.slider_dragging and self.playing_video:
            total_duration = self.media_player.get_length()
            position = int((float(value) / 100) * total_duration)
            self.media_player.set_time(position)

    def on_slider_press(self, event):
        self.slider_dragging = True

    def on_slider_release(self, event):
        self.slider_dragging = False

    def update_video_progress(self):
        if self.playing_video and not self.slider_dragging:
            total_duration = self.media_player.get_length()
            current_time = self.media_player.get_time()

            if total_duration > 0 and current_time >= 0:
                progress_percentage = (current_time / total_duration) * 100
                self.progress_slider.set(progress_percentage)
                self.current_time_label.config(text=self.format_time(current_time))

        self.after(100, self.update_video_progress)


if __name__ == "__main__":
    app = MediaPlayerApp()
    app.update_video_progress()
    app.mainloop()