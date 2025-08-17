import tkinter as tk
from tkinter import messagebox
import os
import threading
import subprocess

class ShutdownTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shutdown Timer")

        self.time_left_seconds = 0
        self.timer_thread = None
        self.stop_event = threading.Event()
        
        # Determine the correct shutdown command based on the OS
        self.shutdown_command = self._get_shutdown_command()

        # UI Elements
        self.setup_ui()

    def _get_shutdown_command(self):
        """
        Returns the appropriate shutdown command for the current OS.
        """
        if os.name == 'nt':  # Windows
            return "shutdown /s /t 1"
        elif os.uname().sysname == 'Darwin':  # macOS
            return "sudo shutdown -h now"
        else:  # Linux and other Unix-like systems
            return "sudo shutdown -h now"

    def setup_ui(self):
        """
        Sets up all the user interface widgets.
        """
        tk.Label(self.root, text="Timer (in Sekunden):").pack(pady=5)
        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=5)
        self.entry.focus()

        self.start_button = tk.Button(self.root, text="Starten", command=self.start_shutdown)
        self.start_button.pack(pady=10)

        self.cancel_button = tk.Button(self.root, text="Abbrechen", command=self.cancel_shutdown, state=tk.DISABLED)
        self.cancel_button.pack(pady=10)

        self.time_label = tk.Label(self.root, text="Zeit bis zum Herunterfahren: -- Sekunden", font=('Arial', 12))
        self.time_label.pack(pady=5)

    def start_shutdown(self):
        """
        Starts the shutdown timer based on user input.
        """
        try:
            seconds = int(self.entry.get())
            if seconds <= 0:
                messagebox.showerror("Fehler", "Bitte eine positive Zahl eingeben.")
                return
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.")
            return

        self.time_left_seconds = seconds
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.stop_event.clear()
        
        # Start the background thread for the timer
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()

    def _run_timer(self):
        """
        Manages the countdown in a separate thread.
        """
        while self.time_left_seconds > 0 and not self.stop_event.is_set():
            # Schedule the GUI update in the main thread
            self.root.after(0, self._update_label)
            time.sleep(1)
            self.time_left_seconds -= 1
        
        if not self.stop_event.is_set():
            self.root.after(0, self._perform_shutdown)

    def _update_label(self):
        """
        Updates the UI label with the remaining time.
        This function is called by root.after() in the main thread.
        """
        self.time_label.config(text=f"Zeit bis zum Herunterfahren: {self.time_left_seconds} Sekunden")

    def _perform_shutdown(self):
        """
        Executes the shutdown command.
        """
        messagebox.showinfo("Herunterfahren", "Der Timer ist abgelaufen. Der Computer wird heruntergefahren.")
        try:
            subprocess.run(self.shutdown_command.split(), check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Fehler", f"Fehler beim Ausführen des Befehls zum Herunterfahren: {e}")
        finally:
            self.root.destroy()
            
    def cancel_shutdown(self):
        """
        Cancels the shutdown timer.
        """
        self.stop_event.set()
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        
        # Execute the cancel command for the respective OS
        if os.name == 'nt':
            cancel_command = "shutdown /a"
        else:
            cancel_command = "sudo shutdown -c"
        
        try:
            subprocess.run(cancel_command.split(), check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Fehler", f"Fehler beim Abbrechen des Befehls: {e}")
            
        messagebox.showinfo("Abgebrochen", "Das Herunterfahren wurde abgebrochen.")
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.time_label.config(text="Zeit bis zum Herunterfahren: -- Sekunden")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShutdownTimerApp(root)
    root.mainloop()

