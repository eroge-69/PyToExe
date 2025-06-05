import tkinter as tk
from tkinter import ttk
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Sound Controller")

        # Get default audio device and volume interface
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Get current volume (0.0 to 1.0)
        current_vol = self.volume.GetMasterVolumeLevelScalar()

        # Volume slider
        self.slider = ttk.Scale(root, from_=0, to=100, orient='horizontal',
                                command=self.on_volume_change)
        self.slider.set(current_vol * 100)
        self.slider.pack(padx=20, pady=10, fill='x')

        # Mute button
        self.mute_button = ttk.Button(root, text="Mute", command=self.toggle_mute)
        self.mute_button.pack(pady=10)

        # Update mute button text based on current mute state
        self.update_mute_button()

    def on_volume_change(self, event):
        new_vol = self.slider.get() / 100
        self.volume.SetMasterVolumeLevelScalar(new_vol, None)
        # If volume is raised, unmute
        if self.volume.GetMute():
            self.volume.SetMute(0, None)
            self.update_mute_button()

    def toggle_mute(self):
        muted = self.volume.GetMute()
        self.volume.SetMute(not muted, None)
        self.update_mute_button()

    def update_mute_button(self):
        if self.volume.GetMute():
            self.mute_button.config(text="Unmute")
        else:
            self.mute_button.config(text="Mute")

if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeApp(root)
    root.mainloop()
