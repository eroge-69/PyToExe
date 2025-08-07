import tkinter as tk
from tkinter import messagebox
import requests

API_URL = "https://status.uniflowonline.com/api/v2/status.json"

class StatusApp(tk.Tk):
    """Simple GUI to display the uniFLOW Online service status."""

    def __init__(self):
        super().__init__()
        self.title("uniFLOW Online Status")
        self.geometry("420x160")

        self.status_label = tk.Label(self, text="Lade Status...", wraplength=380, font=("Arial", 12))
        self.status_label.pack(pady=20)

        refresh = tk.Button(self, text="Aktualisieren", command=self.update_status)
        refresh.pack()

        self.update_status()

    def update_status(self):
        """Fetch the current service status and update the label."""
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            status = data.get("status", {})
            description = status.get("description", "Keine Beschreibung")
            indicator = status.get("indicator", "unbekannt")
            self.status_label.config(text=f"{description} ({indicator})")
        except Exception as exc:
            messagebox.showerror("Fehler", f"Status konnte nicht abgerufen werden: {exc}")

if __name__ == "__main__":
    app = StatusApp()
    app.mainloop()
