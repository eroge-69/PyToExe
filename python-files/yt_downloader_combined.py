"""
A standalone YouTube to MP4 downloader with a Tkinter GUI.

This single-file script combines the core downloading logic using
pytube with a simple Tkinter-based graphical interface. It allows
users to paste a YouTube URL, choose a resolution (480p, 720p,
1080p or 4K), and download the video as an MP4 file to a chosen
folder. A progress bar updates during download, and status
messages report success or failure.

**Disclaimer:** Downloading videos from YouTube may violate the
platform's Terms of Service. Only download content that you own
or have permission to download.
"""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Callable, Optional

# Attempt to import pytube lazily to provide a clear error if it's
# missing. The Py to EXE builder should install dependencies via
# its workflow, but we handle the ImportError gracefully.
try:
    from pytube import YouTube
    from pytube.cli import on_progress
except Exception:
    YouTube = None  # type: ignore
    on_progress = None  # type: ignore


class DownloadError(Exception):
    """Raised when a video cannot be downloaded."""


def download_video(
    url: str,
    resolution: str,
    output_path: str = ".",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> Path:
    """Download a YouTube video as an MP4 file at a specified resolution.

    Parameters
    ----------
    url : str
        The full URL of the YouTube video to download.
    resolution : str
        Desired resolution ("480p", "720p", "1080p", or "4k").
    output_path : str, optional
        Directory to save the downloaded file (default is current working
        directory).
    progress_callback : Callable[[int, int], None], optional
        A callback function that will be invoked with two integer
        arguments: bytes downloaded and total file size. This can be
        used to update a GUI progress bar.

    Returns
    -------
    pathlib.Path
        Path to the downloaded file.

    Raises
    ------
    DownloadError
        If the video cannot be downloaded (e.g., no suitable stream
        is available).
    ValueError
        If an invalid resolution string is passed.
    """
    if YouTube is None:
        raise ImportError(
            "The 'pytube' library is required but not installed. "
            "Run 'pip install pytube' and try again."
        )

    # Normalise resolution aliases
    resolution_map = {
        "480p": "480p",
        "480": "480p",
        "720p": "720p",
        "720": "720p",
        "1080p": "1080p",
        "1080": "1080p",
        "4k": "2160p",
        "2160p": "2160p",
        "2160": "2160p",
    }

    res_key = resolution.lower().replace(" ", "")
    if res_key not in resolution_map:
        raise ValueError(
            f"Unsupported resolution '{resolution}'. "
            "Use one of: 480p, 720p, 1080p, 4k."
        )
    target_res = resolution_map[res_key]

    yt = YouTube(
        url,
        on_progress_callback=(progress_callback or on_progress),
    )

    # Filter for mp4 streams. For 1080p and above, progressive streams
    # aren't always available. We first attempt to find a progressive
    # stream at the desired resolution.
    stream = (
        yt.streams.filter(
            file_extension="mp4", progressive=True, resolution=target_res
        ).first()
    )
    if stream is None:
        # If the exact resolution isn't available, fall back to the
        # highest resolution progressive stream.
        stream = (
            yt.streams.filter(file_extension="mp4", progressive=True)
            .order_by("resolution")
            .desc()
            .first()
        )

    if stream is None:
        # If still None, try adaptive streams (video only) and pick
        # nearest resolution; this will require merging audio and video,
        # which pytube does automatically when using ``download``.
        stream = (
            yt.streams.filter(file_extension="mp4", adaptive=True, res=target_res)
            .order_by("resolution")
            .desc()
            .first()
        )

    if stream is None:
        raise DownloadError(
            f"No MP4 stream available for resolution {target_res} on this video."
        )

    # Ensure output directory exists
    out_dir = Path(output_path).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Download video. Pytube will merge audio and video for adaptive streams.
    downloaded_path = stream.download(output_path=out_dir)
    return Path(downloaded_path)


class YouTubeDownloaderApp(tk.Tk):
    """Main application window for the YouTube downloader."""

    def __init__(self) -> None:
        super().__init__()
        self.title("YouTube to MP4 Downloader")
        self.geometry("500x250")
        self.resizable(False, False)

        # Video URL input
        tk.Label(self, text="YouTube Video URL:").pack(pady=(10, 0))
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(self, textvariable=self.url_var, width=70)
        self.url_entry.pack(padx=10, pady=5)

        # Resolution dropdown
        tk.Label(self, text="Select Quality:").pack(pady=(10, 0))
        self.resolution_var = tk.StringVar(value="720p")
        self.res_combo = ttk.Combobox(
            self,
            textvariable=self.resolution_var,
            values=["480p", "720p", "1080p", "4K"],
            state="readonly",
        )
        self.res_combo.pack(pady=5)

        # Output directory selection
        tk.Label(self, text="Save to:").pack(pady=(10, 0))
        self.output_var = tk.StringVar(value=".")
        out_frame = tk.Frame(self)
        out_frame.pack(pady=5, padx=10, fill="x")
        self.out_entry = tk.Entry(out_frame, textvariable=self.output_var, width=55)
        self.out_entry.pack(side="left", fill="x", expand=True)
        tk.Button(out_frame, text="Browse", command=self.browse_output).pack(side="right")

        # Progress bar and status
        self.progress = ttk.Progressbar(self, length=460, mode="determinate")
        self.progress.pack(pady=10)
        self.status_var = tk.StringVar(value="Idle")
        self.status_label = tk.Label(self, textvariable=self.status_var)
        self.status_label.pack(pady=(0, 10))

        # Download button
        tk.Button(self, text="Download", command=self.start_download).pack(pady=5)

    def browse_output(self) -> None:
        """Open a directory chooser to select the output folder."""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)

    def start_download(self) -> None:
        """Validate inputs and start the download in a new thread."""
        url = self.url_var.get().strip()
        res = self.resolution_var.get().lower()
        output_dir = self.output_var.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube video URL.")
            return
        if not output_dir:
            messagebox.showerror("Error", "Please choose an output directory.")
            return

        # Reset progress bar and status
        self.progress.config(value=0)
        self.status_var.set("Starting download...")

        # Launch download in a separate thread to keep GUI responsive
        thread = threading.Thread(
            target=self.download_video_thread,
            args=(url, res, output_dir),
            daemon=True,
        )
        thread.start()

    def update_progress(self, bytes_downloaded: int, total_bytes: int) -> None:
        """Update progress bar based on bytes downloaded."""
        if total_bytes > 0:
            percentage = (bytes_downloaded / total_bytes) * 100
            self.progress.config(value=percentage)
            self.progress.update_idletasks()

    def download_video_thread(self, url: str, res: str, output_dir: str) -> None:
        """Perform the actual download and handle result messages."""
        try:
            # Map human‑readable labels to resolution strings understood by core
            resolution_map = {
                "480p": "480p",
                "720p": "720p",
                "1080p": "1080p",
                "4k": "4k",
            }
            target = resolution_map.get(res, res)
            file_path = download_video(
                url,
                target,
                output_path=output_dir,
                progress_callback=self.update_progress,
            )
        except DownloadError as de:
            self.status_var.set(f"Download failed: {de}")
            messagebox.showerror("Download Error", str(de))
            return
        except Exception as exc:
            self.status_var.set("An unexpected error occurred.")
            messagebox.showerror("Error", str(exc))
            return

        # Update status on success
        self.status_var.set(f"Downloaded to: {file_path}")
        messagebox.showinfo("Success", f"Video downloaded to:\n{file_path}")


def main() -> None:
    """Run the GUI application."""
    app = YouTubeDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
