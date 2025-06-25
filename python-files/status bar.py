import cv2
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import re

class VideoScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Screenshot Tool")
        self.video_path = None
        self.cap = None
        self.frame = None
        self.screenshot_count = 0

        self.window_width = 1000
        self.window_height = 600
        self.video_width = int(self.window_width * 0.7)
        self.controls_width = self.window_width - self.video_width

        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        # Frame for video (70%)
        self.video_frame = tk.Frame(root, width=self.video_width, height=self.window_height, bg="black")
        self.video_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.video_frame.pack_propagate(False)

        # Frame for controls (30%)
        self.controls_frame = tk.Frame(root, width=self.controls_width, height=self.window_height, bg="#f0f0f0")
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.controls_frame.pack_propagate(False)

        # Video label inside fixed-size frame
        self.label = tk.Label(self.video_frame, bg="black")
        self.label.pack(expand=True)

        # Progress bar for MKV to MP4 conversion
        self.progress = ttk.Progressbar(self.video_frame, orient="horizontal", length=self.video_width, mode="determinate")
        self.progress.pack(pady=5, fill=tk.X)
        self.progress["value"] = 0

        # Controls
        self.title_label = tk.Label(self.controls_frame, text="Controls", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        self.btn_open = tk.Button(self.controls_frame, text="Open Video", width=20, command=self.open_video)
        self.btn_open.pack(pady=10)

        self.btn_screenshot = tk.Button(self.controls_frame, text="Take Screenshot", width=20, command=self.take_screenshot, state=tk.DISABLED)
        self.btn_screenshot.pack(pady=10)

        self.btn_convert = tk.Button(self.controls_frame, text="Convert MKV to MP4", width=20, command=self.convert_to_mp4)
        self.btn_convert.pack(pady=10)

        self.btn_quit = tk.Button(self.controls_frame, text="Quit", width=20, command=self.quit)
        self.btn_quit.pack(pady=10)

    def open_video(self):
        self.video_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")]
        )
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            self.btn_screenshot.config(state=tk.NORMAL)
            self.show_frame()

    def show_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resized = cv2.resize(frame_rgb, (self.video_width, self.window_height))

                img = Image.fromarray(resized)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)
                self.root.after(30, self.show_frame)
            else:
                self.cap.release()

    def take_screenshot(self):
        if self.frame is not None:
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            output_dir = f"{video_name}_screenshots"
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"screenshot_{self.screenshot_count:03d}.jpg")
            cv2.imwrite(filename, self.frame)
            print(f"Saved screenshot: {filename}")
            self.screenshot_count += 1

    def convert_to_mp4(self):
        input_path = filedialog.askopenfilename(
            title="Select an MKV video to convert",
            filetypes=[("MKV files", "*.mkv")]
        )
        if not input_path:
            return

        output_path = os.path.splitext(input_path)[0] + "_converted.mp4"

        try:
            # Get total duration
            result = subprocess.run(
                ['ffmpeg', '-i', input_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)
            if not duration_match:
                messagebox.showerror("Error", "Could not read video duration.")
                return

            h, m, s = map(float, duration_match.groups())
            total_seconds = h * 3600 + m * 60 + s

            # Start conversion
            process = subprocess.Popen(
                ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac', output_path, '-y'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=True
            )

            for line in process.stderr:
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match:
                    ch, cm, cs = map(float, time_match.groups())
                    current_sec = ch * 3600 + cm * 60 + cs
                    progress_percent = (current_sec / total_seconds) * 100
                    self.progress["value"] = min(progress_percent, 100)
                    self.root.update_idletasks()

            process.wait()
            self.progress["value"] = 100
            messagebox.showinfo("Conversion Complete", f"File saved as:\n{output_path}")

        except FileNotFoundError:
            messagebox.showerror("FFmpeg Not Found", "Make sure FFmpeg is installed and added to your PATH.")
        except Exception as e:
            messagebox.showerror("Conversion Failed", f"Error: {e}")

    def quit(self):
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScreenshotApp(root)
    root.mainloop()
