import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
import random
import psutil
# --- IMPORTS for controlling Windows audio ---
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class RandomSoundPlayer:
    """
    A simple GUI application to play random audio files from a selected folder
    at a user-defined interval, muting other system sounds during playback—
    but never muting itself.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Random Soundtrack Player")
        self.master.geometry("450x275")

        # --- Initialize variables ---
        self.sound_folder = ""
        self.sound_files = []
        self.is_playing = False
        self.timer_id = None

        # Track our own process info
        self.own_pid = os.getpid()
        try:
            self.own_name = psutil.Process(self.own_pid).name()
        except Exception:
            self.own_name = None
        self.original_volumes = {}

        # --- Initialize Pygame Mixer ---
        pygame.mixer.init()

        # --- GUI Widgets ---
        self.folder_label = tk.Label(master, text="No folder selected.", wraplength=400)
        self.folder_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.select_button = tk.Button(master, text="Select Music Folder", command=self.select_folder)
        self.select_button.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        tk.Label(master, text="Interval (minutes):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.interval_entry = tk.Entry(master, width=10)
        self.interval_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.interval_entry.insert(0, "15")

        self.mute_var = tk.BooleanVar(value=True)
        self.mute_check = tk.Checkbutton(
            master,
            text="Mute other apps during playback",
            variable=self.mute_var
        )
        self.mute_check.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

        self.start_button = tk.Button(master, text="Start", command=self.start_playback, width=12)
        self.start_button.grid(row=4, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_playback, width=12, state=tk.DISABLED)
        self.stop_button.grid(row=4, column=1, padx=10, pady=10)

        self.status_label = tk.Label(master, text="Status: Stopped", fg="red")
        self.status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def manage_other_audio(self, mute: bool):
        """Mute or restore *other* apps—never this one."""
        if not self.mute_var.get():
            return

        try:
            for session in AudioUtilities.GetAllSessions():
                proc = session.Process
                # skip system sounds or sessions without a PID
                if not proc:
                    continue

                # Skip our own process
                if proc.pid == self.own_pid or proc.name() == self.own_name:
                    continue

                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                pid = proc.pid

                if mute:
                    # store original volume/mute
                    self.original_volumes[pid] = {
                        'vol': volume.GetMasterVolume(),
                        'muted': volume.GetMute()
                    }
                    volume.SetMute(1, None)
                else:
                    # restore if we have it
                    if pid in self.original_volumes:
                        orig = self.original_volumes.pop(pid)
                        volume.SetMasterVolume(orig['vol'], None)
                        volume.SetMute(orig['muted'], None)

            # clear any leftovers when unmuting
            if not mute:
                self.original_volumes.clear()

        except Exception as e:
            print(f"Audio control error: {e}")

    def check_music_finished(self):
        if not self.is_playing:
            return

        if not pygame.mixer.music.get_busy() and self.original_volumes:
            self.status_label.config(text="Track finished. Restoring audio...", fg="orange")
            self.manage_other_audio(mute=False)

        self.master.after(1000, self.check_music_finished)

    def select_folder(self):
        self.sound_folder = filedialog.askdirectory()
        if self.sound_folder:
            self.folder_label.config(text=f"Folder: {self.sound_folder}")
            exts = ('.mp3', '.wav', '.ogg', '.m4a')
            self.sound_files = [
                os.path.join(self.sound_folder, f)
                for f in os.listdir(self.sound_folder)
                if f.lower().endswith(exts)
            ]
            if not self.sound_files:
                messagebox.showwarning("Warning", "No supported audio files found.")
            else:
                self.status_label.config(text=f"Loaded {len(self.sound_files)} tracks. Ready to start.")

    def start_playback(self):
        if not self.sound_files:
            messagebox.showerror("Error", "Please select a folder with audio files first.")
            return
        try:
            self.interval_min = float(self.interval_entry.get())
            if self.interval_min <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for the interval.")
            return

        self.is_playing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.DISABLED)
        self.interval_entry.config(state=tk.DISABLED)
        self.mute_check.config(state=tk.DISABLED)

        self.play_random_sound()
        self.check_music_finished()

    def stop_playback(self):
        self.is_playing = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        pygame.mixer.music.stop()
        self.manage_other_audio(mute=False)

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.NORMAL)
        self.interval_entry.config(state=tk.NORMAL)
        self.mute_check.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Stopped", fg="red")

    def play_random_sound(self):
        if not self.is_playing:
            return

        try:
            track = random.choice(self.sound_files)
            pygame.mixer.music.load(track)

            self.status_label.config(text="Muting other audio...", fg="orange")
            self.master.after(100, lambda: self.manage_other_audio(mute=True))

            pygame.mixer.music.play()
            self.status_label.config(text=f"Playing: {os.path.basename(track)}", fg="blue")

            ms = int(self.interval_min * 60 * 1000)
            self.timer_id = self.master.after(ms, self.play_random_sound)
        except Exception as e:
            messagebox.showerror("Playback Error", f"An error occurred: {e}")
            self.stop_playback()

    def on_closing(self):
        if self.is_playing:
            self.stop_playback()
        pygame.mixer.quit()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RandomSoundPlayer(root)
    root.mainloop()
