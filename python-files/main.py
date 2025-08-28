import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import pygame


class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("John Ball Music Player")
        # Start fullscreen
        self.root.attributes("-fullscreen", True)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Hot pink color
        self.hot_pink = "#FF69B4"

        # Make background hot pink
        self.root.configure(bg=self.hot_pink)

        # Initialize pygame mixer
        self.mixer_available = True
        try:
            pygame.mixer.init()
        except Exception as e:
            self.mixer_available = False
            messagebox.showerror(
                "Audio Initialization Error",
                f"Could not initialize audio mixer:\n{e}\nPlayback will not work."
            )

        # Playback state
        self.playlist = []
        self.current_index = -1
        self.paused = False
        self.playing = False

        self.build_ui()

        # Polling to detect track end
        self.root.after(500, self._playback_watcher)

    def build_ui(self):
        # Main container (hot pink)
        main = tk.Frame(self.root, bg=self.hot_pink)
        main.pack(fill=tk.BOTH, expand=True)

        # Playlist area
        list_frame = tk.Frame(main, bg=self.hot_pink)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        self.scrollbar = tk.Scrollbar(list_frame, bg=self.hot_pink, troughcolor=self.hot_pink, activebackground=self.hot_pink)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox styled hot pink
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=self.scrollbar.set,
            bg=self.hot_pink,
            fg="black",
            selectbackground="#FF85C8",  # slightly lighter hot pink for selection
            selectforeground="black",
            activestyle="none",
            font=("Helvetica", 14),
            bd=0,
            highlightthickness=0
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_song())

        self.scrollbar.config(command=self.listbox.yview)

        # Controls (buttons)
        controls = tk.Frame(main, bg=self.hot_pink)
        controls.pack(pady=10)

        btn_style = {"bg": self.hot_pink, "fg": "black", "activebackground": "#FF85C8", "bd": 0, "width": 12}

        btn_add = tk.Button(controls, text="Add Files", command=self.add_files, **btn_style)
        btn_add.grid(row=0, column=0, padx=6)

        btn_play = tk.Button(controls, text="Play", command=self.play_song, **btn_style)
        btn_play.grid(row=0, column=1, padx=6)

        self.btn_pause = tk.Button(controls, text="Pause", command=self.toggle_pause, **btn_style)
        self.btn_pause.grid(row=0, column=2, padx=6)

        btn_stop = tk.Button(controls, text="Stop", command=self.stop_song, **btn_style)
        btn_stop.grid(row=0, column=3, padx=6)

        btn_prev = tk.Button(controls, text="Previous", command=self.prev_song, **btn_style)
        btn_prev.grid(row=0, column=4, padx=6)

        btn_next = tk.Button(controls, text="Next", command=self.next_song, **btn_style)
        btn_next.grid(row=0, column=5, padx=6)

        # Bottom: volume and status
        bottom = tk.Frame(main, bg=self.hot_pink)
        bottom.pack(fill=tk.X, padx=20, pady=(0, 20))

        vol_label = tk.Label(bottom, text="Volume", bg=self.hot_pink, fg="black")
        vol_label.pack(side=tk.LEFT)

        # Scale (volume) - try to style trough where supported
        self.volume_slider = tk.Scale(
            bottom,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.set_volume,
            length=300,
            bg=self.hot_pink,
            troughcolor="#FF85C8",
            fg="black",
            highlightthickness=0
        )
        self.volume_slider.set(70)
        self.volume_slider.pack(side=tk.LEFT, padx=(6, 12))
        if self.mixer_available:
            pygame.mixer.music.set_volume(0.7)

        # Status label
        self.status_var = tk.StringVar(value="No track playing")
        status_label = tk.Label(bottom, textvariable=self.status_var, bg=self.hot_pink, fg="black")
        status_label.pack(side=tk.LEFT, padx=10)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select MP3 or FLAC files",
            filetypes=(("Audio Files", "*.mp3 *.flac"), ("All files", "*.*"))
        )
        if not files:
            return
        added = 0
        for f in files:
            path = os.path.abspath(f)
            if path not in self.playlist:
                self.playlist.append(path)
                self.listbox.insert(tk.END, os.path.basename(path))
                added += 1
        if added == 0:
            messagebox.showinfo("Add files", "No new files were added (duplicates removed).")

    def play_song(self):
        if not self.mixer_available:
            messagebox.showerror("Playback Error", "Audio mixer not available.")
            return

        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
        else:
            idx = self.current_index if self.current_index >= 0 else (0 if self.playlist else -1)

        if idx == -1:
            messagebox.showinfo("No tracks", "Add some MP3/FLAC files first.")
            return

        if idx == self.current_index and self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True
            self.btn_pause.config(text="Pause")
            self._update_status()
            return

        self.current_index = idx
        path = self.playlist[self.current_index]

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
            self.btn_pause.config(text="Pause")
            self.listbox.select_clear(0, tk.END)
            self.listbox.select_set(self.current_index)
            self.listbox.activate(self.current_index)
            self._update_status()
        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not play:\n{path}\n\n{e}")
            self.playing = False
            self._update_status()

    def toggle_pause(self):
        if not self.mixer_available:
            return

        if pygame.mixer.music.get_busy():
            if not self.paused:
                pygame.mixer.music.pause()
                self.paused = True
                self.btn_pause.config(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.paused = False
                self.btn_pause.config(text="Pause")
            self._update_status()
        else:
            if self.playlist:
                self.play_song()

    def stop_song(self):
        if self.mixer_available:
            pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.btn_pause.config(text="Pause")
        self._update_status()

    def next_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_song()

    def prev_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_song()

    def set_volume(self, val):
        if not self.mixer_available:
            return
        try:
            v = float(val) / 100.0
            pygame.mixer.music.set_volume(max(0.0, min(1.0, v)))
        except Exception:
            pass

    def _update_status(self):
        if 0 <= self.current_index < len(self.playlist):
            name = os.path.basename(self.playlist[self.current_index])
        else:
            name = "No track"

        if self.playing:
            state = "Paused" if self.paused else "Playing"
        else:
            state = "Stopped"

        self.status_var.set(f"{state}: {name}")

    def _playback_watcher(self):
        try:
            if self.mixer_available and self.playlist:
                busy = pygame.mixer.music.get_busy()
                if self.playing and not busy and not self.paused:
                    self.playing = False
                    if len(self.playlist) > 1:
                        self.current_index = (self.current_index + 1) % len(self.playlist)
                        self.play_song()
                    else:
                        self._update_status()
        except Exception:
            pass
        finally:
            self.root.after(500, self._playback_watcher)

    def toggle_fullscreen(self, event=None):
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    def on_close(self):
        try:
            if self.mixer_available:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayer(root)
    root.mainloop()