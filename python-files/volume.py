"""
Menagjimi i zërit
===================

This module implements a cross‑platform volume control application with a
finger‑friendly user interface.  The app is designed for Windows,
macOS and other platforms, adapting its behaviour as follows:

* **Windows** – Uses the `pycaw` library to control the master volume via
  the Core Audio APIs.  Each button adjusts the volume by a fixed
  increment or decrement, clamping the value to the range 0–100%.  When
  `pycaw` or its dependencies are missing, the application falls back to
  a mock backend and informs the user via a pop‑up message.

* **macOS** – Uses AppleScript via the `osascript` command to read and
  set the system’s output volume.  The `MacVolume` class encapsulates
  these interactions.

* **Other platforms** – Falls back to a mock volume backend so the UI
  remains interactive even when there’s no supported audio API.

The graphical interface is built with Tkinter.  All widgets are
arranged using the `grid` geometry manager with row/column weights to
ensure that the six volume buttons always remain visible and scale
proportionally when the window is resized.  A footer message at the
bottom expresses affection from “Komshiu”.  This layout draws from
recommendations on configuring grids with `rowconfigure`/`columnconfigure` and
using `sticky="nsew"` so that each cell expands to fill available space
【784616246471754†L1048-L1059】.

Run this script directly with Python 3.  On Windows, install the
dependencies via `pip install pycaw comtypes`.  On macOS, no external
dependencies are required beyond a functional `osascript` binary.
"""

import platform
import subprocess
import tkinter as tk
from tkinter import messagebox


class WinVolume:
    """Control master output volume on Windows via PyCAW."""

    def __init__(self) -> None:
        try:
            from ctypes import POINTER, cast  # type: ignore
            from comtypes import CLSCTX_ALL  # type: ignore
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            self._volume = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as exc:
            raise RuntimeError(
                "Failed to initialise PyCAW. Install pycaw and comtypes."
            ) from exc

    def get_percent(self) -> int:
        """Return the current master volume as an integer 0–100."""
        return int(round(self._volume.GetMasterVolumeLevelScalar() * 100))

    def set_percent(self, percent: int) -> None:
        """Set the master volume to the given percentage (clamped)."""
        clamped = max(0, min(100, percent)) / 100.0
        self._volume.SetMasterVolumeLevelScalar(clamped, None)

    def change(self, delta: int) -> int:
        """Increment or decrement the volume and return the new value."""
        new_val = self.get_percent() + delta
        self.set_percent(new_val)
        return self.get_percent()


class MacVolume:
    """Control master output volume on macOS via AppleScript."""

    def __init__(self) -> None:
        # Verify that osascript is available
        try:
            subprocess.run(
                ["osascript", "-e", "return 1"],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception as exc:
            raise RuntimeError(
                "osascript is not available; cannot control system volume."
            ) from exc

    def _run(self, script: str) -> str:
        """Execute a short AppleScript command and return stdout."""
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "AppleScript error")
        return result.stdout.strip()

    def get_percent(self) -> int:
        """Get the current output volume as a 0–100 integer."""
        out = self._run("output volume of (get volume settings)")
        try:
            return int(out)
        except ValueError:
            return 0

    def set_percent(self, percent: int) -> None:
        """Set the output volume to a given percentage (clamped)."""
        clamped = max(0, min(100, percent))
        self._run(f"set volume output volume {clamped}")

    def change(self, delta: int) -> int:
        """Adjust the volume by delta and return the new value."""
        new_val = self.get_percent() + delta
        self.set_percent(new_val)
        return self.get_percent()


class MockVolume:
    """Mock volume backend for unsupported platforms or when dependencies fail."""

    def __init__(self) -> None:
        self._percent = 50

    def get_percent(self) -> int:
        return self._percent

    def set_percent(self, percent: int) -> None:
        self._percent = max(0, min(100, percent))

    def change(self, delta: int) -> int:
        self.set_percent(self._percent + delta)
        return self._percent


def get_backend() -> object:
    """Return an appropriate volume controller for the host OS."""
    system = platform.system()
    if system == "Windows":
        try:
            return WinVolume()
        except Exception as exc:
            messagebox.showwarning(
                "Menagjimi i zërit",
                f"Cannot initialise Windows volume control. Using mock backend.\n\n{exc}",
            )
            return MockVolume()
    elif system == "Darwin":  # macOS
        try:
            return MacVolume()
        except Exception as exc:
            messagebox.showwarning(
                "Menagjimi i zërit",
                f"Cannot initialise macOS volume control. Using mock backend.\n\n{exc}",
            )
            return MockVolume()
    else:
        return MockVolume()


class App(tk.Tk):
    """Main Tkinter application window with self‑resizing button layout."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Menagjimi i zërit")
        # Start with a phone‑like portrait window size; users can resize
        self.geometry("360x640")
        self.configure(bg="#f7f7fb")

        # Configure root grid so row 0 (main content) expands and row 1 (footer) stays fixed
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)

        # Instantiate the appropriate volume backend
        self.backend = get_backend()

        # Main container frame uses grid to host label and buttons
        container = tk.Frame(self, bg="#f7f7fb")
        container.grid(row=0, column=0, sticky="nsew", padx=16, pady=(16, 8))
        # Configure rows: first row for volume label (no weight), next six for buttons
        container.rowconfigure(0, weight=0)
        for i in range(1, 7):
            container.rowconfigure(i, weight=1)
        container.columnconfigure(0, weight=1)

        # Variable to display current volume
        self.vol_var = tk.StringVar(value=f"Volumi: {self.backend.get_percent()}%")

        # Volume label at top
        lbl = tk.Label(
            container,
            textvariable=self.vol_var,
            fg="#222",
            bg="#f7f7fb",
            font=("Segoe", 20, "bold"),
        )
        lbl.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Button creation helper
        def make_button(row: int, text: str, delta: int, bg_color: str) -> None:
            def on_click() -> None:
                newv = self.backend.change(delta)
                self.vol_var.set(f"Volumi: {newv}%")

            btn = tk.Button(
                container,
                text=text,
                command=on_click,
                bg=bg_color,
                fg="black",  # black text as requested
                activebackground=bg_color,
                activeforeground="black",
                relief="flat",
                padx=16,
                pady=14,
                bd=0,
                height=2,
            )
            # Make the button fill the entire grid cell
            btn.grid(row=row, column=0, sticky="nsew", pady=4)

        # Create six buttons with light pastel colours for contrast
        make_button(1, "+10", +10, "#e0f7e9")  # light green
        make_button(2, "-10", -10, "#fde2e2")  # light red
        make_button(3, "+5", +5, "#e4f0ff")   # light blue
        make_button(4, "-5", -5, "#ffe9d6")   # light orange
        make_button(5, "+1", +1, "#ece6ff")   # light violet
        make_button(6, "-1", -1, "#ffe6e1")   # light coral

        # Footer label sits outside the main container so it doesn't stretch
        footer = tk.Label(
            self,
            text="Me dashuri nga Komshiu <3",
            fg="#666",
            bg="#f7f7fb",
            font=("Segoe", 14),
        )
        footer.grid(row=1, column=0, pady=(0, 12))

        # Periodically refresh the volume display in case the system volume changes externally
        if isinstance(self.backend, (WinVolume, MacVolume)):
            self.after(750, self._poll_volume)

    def _poll_volume(self) -> None:
        try:
            self.vol_var.set(f"Volumi: {self.backend.get_percent()}%")
        finally:
            self.after(750, self._poll_volume)


if __name__ == "__main__":
    # Show a helpful error if dependencies are missing on Windows
    try:
        app = App()
        app.mainloop()
    except Exception as exc:
        # Display a simple error message instead of crashing
        messagebox.showerror("Menagjimi i zërit", str(exc))