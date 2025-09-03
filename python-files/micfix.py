import tkinter as tk
from tkinter import ttk
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

class MicVolumeControl:
    def __init__(self, root):
        self.root = root
        self.root.title("Mikrofon-Lautstärkeregler")
        self.root.geometry("400x300")
        
        self.devices = self.get_mic_devices()
        self.create_widgets()

    def get_mic_devices(self):
        """Sucht und gibt eine Liste von Mikrofonen zurück."""
        devices = AudioUtilities.GetSpeakers().GetSpeakers()
        mic_devices = []
        for device in devices:
            if "microphone" in device.FriendlyName.lower() or "input" in device.FriendlyName.lower():
                mic_devices.append(device)
        return mic_devices

    def set_volume_to_100(self):
        """Setzt die Lautstärke des ausgewählten Mikrofons auf 100%."""
        selected_mic_name = self.mic_combobox.get()
        if not selected_mic_name:
            self.status_label.config(text="Bitte wähle ein Mikrofon aus.", foreground="red")
            return

        selected_mic = None
        for device in self.devices:
            if device.FriendlyName == selected_mic_name:
                selected_mic = device
                break

        if selected_mic:
            try:
                interface = selected_mic.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Setzt die Lautstärke auf 100% (1.0 in pycaw)
                volume.SetMasterVolumeLevelScalar(1.0, None)
                
                self.status_label.config(text=f"'{selected_mic_name}' auf 100% gestellt!", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Fehler: {e}", foreground="red")
        else:
            self.status_label.config(text="Ausgewähltes Mikrofon nicht gefunden.", foreground="red")

    def create_widgets(self):
        """Erstellt die GUI-Elemente."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(main_frame, text="Mikrofon auswählen", font=("Helvetica", 16))
        title_label.pack(pady=10)

        # Dropdown-Menü (Combobox) für die Mikrofon-Auswahl
        mic_names = [device.FriendlyName for device in self.devices]
        self.mic_combobox = ttk.Combobox(main_frame, values=mic_names, state="readonly")
        self.mic_combobox.pack(pady=10, fill="x")
        if mic_names:
            self.mic_combobox.set(mic_names[0])

        # Button zum Einstellen der Lautstärke
        set_volume_button = ttk.Button(main_frame, text="Lautstärke auf 100% stellen", command=self.set_volume_to_100)
        set_volume_button.pack(pady=20, fill="x")

        # Status-Label zur Anzeige von Nachrichten
        self.status_label = ttk.Label(main_frame, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MicVolumeControl(root)
    root.mainloop()