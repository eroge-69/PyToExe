import subprocess
import time
import sys
import threading
import tkinter as tk
from win10toast import ToastNotifier

class NetworkMonitorApp:
    """
    A simple application that displays a colored dot to show network status
    and sends a notification when the connection is lost.
    """
    def __init__(self, master, dot_size=4, notif_enabled=True):
        self.master = master
        self.dot_size = dot_size
        self.notif_enabled = notif_enabled
        self.notifier = ToastNotifier()
        self.is_connected = None  # Initial status is unknown

        self.setup_gui()
        
        # Start the connection check in a separate thread to avoid freezing the GUI
        self.check_thread = threading.Thread(target=self.check_connection_loop, daemon=True)
        self.check_thread.start()

    def setup_gui(self):
        """
        Configures the main window and canvas for the dot.
        """
        # Remove the window's title bar and borders
        self.master.overrideredirect(True)
        
        # Set the window to always be on top of other applications
        self.master.attributes('-topmost', True)
        
        # Set the background to be transparent
        self.master.wm_attributes('-transparentcolor', '#ffffff')
        self.master.config(bg='white')
        
        # Set a small window size and initial position
        self.master.geometry(f"{self.dot_size + 10}x{self.dot_size + 10}+0+0")
        
        self.canvas = tk.Canvas(
            self.master, 
            width=self.dot_size, 
            height=self.dot_size, 
            bg='white', 
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)
        
        # Create the dot
        self.dot = self.canvas.create_oval(
            0, 0, self.dot_size, self.dot_size, fill="gray", outline=""
        )

        # Variables for moving the window
        self._drag_data = {"x": 0, "y": 0}

        # Bind events for dragging the window
        self.canvas.bind("<ButtonPress-1>", self.on_press_event)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_event)
        self.canvas.bind("<B1-Motion>", self.on_motion_event)

    def on_press_event(self, event):
        """Saves the initial position of the mouse click."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_release_event(self, event):
        """Resets the drag data on mouse button release."""
        self._drag_data["x"] = None
        self._drag_data["y"] = None

    def on_motion_event(self, event):
        """Updates the window position while dragging."""
        x = self.master.winfo_x() + event.x - self._drag_data["x"]
        y = self.master.winfo_y() + event.y - self._drag_data["y"]
        self.master.geometry(f"+{x}+{y}")

    def update_dot_color(self, color):
        """Updates the dot's color on the canvas."""
        self.canvas.itemconfig(self.dot, fill=color)

    def send_notification(self, title, message):
        """Sends a desktop notification using win10toast."""
        if self.notif_enabled:
            # The 'threading=True' argument prevents the notifier from blocking the main loop
            self.notifier.show_toast(title, message, duration=5, threaded=True)

    def check_connection_loop(self):
        """
        The main loop for checking network status. This runs in a separate thread.
        """
        # Ping command depends on the operating system
        if sys.platform.startswith('win'):
            ping_command = ['ping', '8.8.8.8', '-n', '1', '-l', '1']
        else:
            ping_command = ['ping', '8.8.8.8', '-c', '1']

        while True:
            try:
                result = subprocess.run(
                    ping_command,
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                # Check for successful output
                status = "Connected"
                if "Reply from 8.8.8.8" not in result.stdout and "1 packets transmitted, 1 received" not in result.stdout:
                    status = "Disconnected"
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                status = "Disconnected"
            except Exception as e:
                status = "Disconnected"
                print(f"An error occurred: {e}")

            # Check if the status has changed
            if self.is_connected is None:
                # First check, just set the status
                self.is_connected = (status == "Connected")
            elif self.is_connected and status == "Disconnected":
                # Connection was lost
                self.send_notification("Network Status", "Connection has been lost.")
                self.is_connected = False
            elif not self.is_connected and status == "Connected":
                # Connection was restored
                self.is_connected = True

            # Schedule the GUI update in the main thread
            if status == "Connected":
                self.master.after(0, self.update_dot_color, "green")
                print("connected")

            else:
                self.master.after(0, self.update_dot_color, "red")
                print("disconnected")

            time.sleep(1)

if __name__ == "__main__":
    # You can change these variables here:
    DOT_SIZE = 20  # Size of the dot in pixels
    ENABLE_NOTIFICATIONS = False  # Set to False to disable notifications

    root = tk.Tk()
    app = NetworkMonitorApp(root, dot_size=DOT_SIZE, notif_enabled=ENABLE_NOTIFICATIONS)
    root.mainloop()

