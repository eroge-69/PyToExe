"""
vr_video_dual_monitors.py
=========================

This script provides a simple video player that streams a selected
video to two separate windows positioned on distinct monitors (for
example, the left and right displays of a Windows Mixed Reality
headset) while showing a preview on the primary display.  The idea is
to treat the VR headset as if it were two monitors—one per eye—and
render the same video frame into each window.  You can adapt the code
to send different images to each eye (e.g. for stereoscopic content).

The script uses only the standard library (via ``ctypes``) along with
``tkinter`` for the file dialog and ``OpenCV`` for video decoding and
display.  No external Windows‑specific libraries such as ``pywin32``
are required.  To build a self‑contained Windows executable, run

    pyinstaller --onefile vr_video_dual_monitors.py

on a Windows machine with Python and PyInstaller installed.  Ensure
that OpenCV is available in your Python environment:

    pip install opencv-python

The resulting EXE will let you choose a video file, then stream it to
both headset displays and a preview window.

"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
from pathlib import Path

try:
    import cv2  # type: ignore[import]
except ImportError:
    cv2 = None

import tkinter as tk
from tkinter import filedialog


def pick_video_file() -> Path | None:
    """Open a file dialog to select a video file.

    Returns
    -------
    Path | None
        Path to the selected file, or None if the dialog is canceled.
    """
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        title="Select a video file",
        filetypes=[
            ("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.wmv"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return Path(filename) if filename else None


class MonitorManager:
    """Enumerate and manipulate display monitors on Windows via ctypes."""

    def __init__(self) -> None:
        # Configure the process to be DPI aware so coordinates match actual pixels
        ctypes.windll.user32.SetProcessDPIAware()
        self.monitors: list[tuple[int, int, int, int]] = []  # (left, top, right, bottom)
        self._enumerate_monitors()

    def _enumerate_monitors(self) -> None:
        """Populate the ``monitors`` list with monitor rectangles."""
        # Callback type for EnumDisplayMonitors
        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double
        )

        def _callback(hMonitor: ctypes.c_ulong, hdcMonitor: ctypes.c_ulong, lprcMonitor, dwData) -> int:
            rect = lprcMonitor.contents
            self.monitors.append((rect.left, rect.top, rect.right, rect.bottom))
            return 1

        ctypes.windll.user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(_callback), 0)

    def move_window_to_monitor(self, hwnd: int, monitor_index: int, width: int, height: int) -> None:
        """Move and resize a window to a given monitor.

        Parameters
        ----------
        hwnd : int
            Window handle returned by the Win32 API.
        monitor_index : int
            Index into the ``monitors`` list; 0 is usually the primary monitor.
        width : int
            Desired width of the window.
        height : int
            Desired height of the window.
        """
        if monitor_index >= len(self.monitors):
            raise IndexError(f"Monitor index {monitor_index} out of range (found {len(self.monitors)})")
        left, top, right, bottom = self.monitors[monitor_index]
        # Center the window on the target monitor
        mon_width = right - left
        mon_height = bottom - top
        x = left + (mon_width - width) // 2
        y = top + (mon_height - height) // 2
        # Flags: SWP_NOZORDER | SWP_NOACTIVATE
        flags = 0x0004 | 0x0010
        ctypes.windll.user32.SetWindowPos(hwnd, 0, x, y, width, height, flags)


def show_video_on_monitors(video_path: Path) -> None:
    """Display a video simultaneously on two monitors and a preview window.

    This function opens three OpenCV windows—``Preview``, ``Left Eye`` and
    ``Right Eye``—then positions ``Left Eye`` on monitor 1, ``Right Eye``
    on monitor 2 (if available), and keeps ``Preview`` on the primary
    monitor.  It decodes frames in a loop and updates all three windows.
    The function exits when the video ends or when the user closes any
    window.
    """
    if cv2 is None:
        raise RuntimeError("OpenCV is not installed. Please run 'pip install opencv-python'.")

    # Open the video file
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = 1.0 / fps
    # Read the first frame to determine video resolution
    ret, frame = cap.read()
    if not ret:
        print("Video appears to be empty.")
        cap.release()
        return
    height, width = frame.shape[:2]
    # Create OpenCV windows
    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Left Eye", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Right Eye", cv2.WINDOW_NORMAL)
    # Resize windows to match video resolution
    cv2.resizeWindow("Preview", width // 2, height // 2)
    cv2.resizeWindow("Left Eye", width, height)
    cv2.resizeWindow("Right Eye", width, height)
    # Position windows on monitors
    mm = MonitorManager()
    # Get window handles using FindWindowW
    def get_hwnd(title: str) -> int:
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        return hwnd
    # Primary monitor preview (monitor 0)
    preview_hwnd = get_hwnd("Preview")
    mm.move_window_to_monitor(preview_hwnd, 0, width // 2, height // 2)
    # Left eye on second monitor (monitor 1) if available
    left_hwnd = get_hwnd("Left Eye")
    monitor_idx_left = 1 if len(mm.monitors) > 1 else 0
    mm.move_window_to_monitor(left_hwnd, monitor_idx_left, width, height)
    # Right eye on third monitor (monitor 2) if available, otherwise second
    right_hwnd = get_hwnd("Right Eye")
    monitor_idx_right = 2 if len(mm.monitors) > 2 else monitor_idx_left
    mm.move_window_to_monitor(right_hwnd, monitor_idx_right, width, height)

    # Display the first frame
    cv2.imshow("Preview", cv2.resize(frame, (width // 2, height // 2)))
    cv2.imshow("Left Eye", frame)
    cv2.imshow("Right Eye", frame)

    last_time = time.perf_counter()
    while True:
        # Poll for window close events
        key = cv2.waitKey(1)
        if key == 27:  # Esc key
            break
        ret, frame = cap.read()
        if not ret:
            break
        # Update windows
        cv2.imshow("Preview", cv2.resize(frame, (width // 2, height // 2)))
        cv2.imshow("Left Eye", frame)
        cv2.imshow("Right Eye", frame)
        # Wait to sync to frame rate
        now = time.perf_counter()
        sleep_time = frame_interval - (now - last_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
        last_time = time.perf_counter()

        # If any window was closed by the user, exit
        if cv2.getWindowProperty("Preview", cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.getWindowProperty("Left Eye", cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.getWindowProperty("Right Eye", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


def main() -> int:
    video = pick_video_file()
    if not video:
        print("No video selected. Exiting.")
        return 1
    try:
        show_video_on_monitors(video)
    except Exception as exc:
        print(f"Error during playback: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())