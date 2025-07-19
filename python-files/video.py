import tkinter as tk
from tkinter import messagebox
import pyautogui
import numpy as np
import cv2
import sounddevice as sd
import soundfile as sf
import threading
import time
import queue

class VerticalShortsRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Shorts Recorder")
        self.root.attributes('-topmost', True)

        # --- State Variables ---
        self.is_recording = False
        self.is_selecting = False
        self.selection_box = None
        self.start_x = None
        self.start_y = None
        self.region = None
        self.video_writer = None
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

        # --- Configuration ---
        self.ASPECT_RATIO = 9 / 16
        self.VIDEO_FPS = 30.0
        self.VIDEO_CODEC = 'mp4v' # A widely compatible codec
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHANNELS = 1 # Mono audio is standard for this use case

        # --- UI Elements ---
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack()

        self.label = tk.Label(self.main_frame, text="1. Click and drag on the screen to select the recording area.\nIt will automatically lock to a 9:16 aspect ratio.", justify=tk.LEFT)
        self.label.pack(pady=(0, 10))

        self.select_button = tk.Button(self.main_frame, text="Select Recording Area", command=self.start_selection_mode)
        self.select_button.pack(fill=tk.X, pady=5)

        self.start_button = tk.Button(self.main_frame, text="Start Recording", command=self.start_recording, state=tk.DISABLED)
        self.start_button.pack(fill=tk.X, pady=5)

        self.stop_button = tk.Button(self.main_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=5)
        
        self.quit_button = tk.Button(self.main_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(self.main_frame, text="Status: Ready", fg="blue")
        self.status_label.pack(pady=(10, 0))

    def start_selection_mode(self):
        self.root.withdraw() # Hide main window
        time.sleep(0.2) # Give time for window to hide
        self.is_selecting = True
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.configure(bg='grey')
        self.selection_window.bind("<ButtonPress-1>", self.on_mouse_down)
        self.selection_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.selection_window.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.selection_canvas = tk.Canvas(self.selection_window, cursor="cross", bg='grey', highlightthickness=0)
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.selection_box:
            self.selection_canvas.delete(self.selection_box)
        self.selection_box = self.selection_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        cur_x, cur_y = event.x, event.y
        width = abs(cur_x - self.start_x)
        height = int(width / self.ASPECT_RATIO)
        
        # Adjust direction of rectangle based on drag
        end_x = self.start_x + width if cur_x > self.start_x else self.start_x - width
        end_y = self.start_y + height if cur_y > self.start_y else self.start_y - height

        self.selection_canvas.coords(self.selection_box, self.start_x, self.start_y, end_x, end_y)

    def on_mouse_up(self, event):
        x1, y1, x2, y2 = self.selection_canvas.coords(self.selection_box)

        # Ensure correct coordinates regardless of drag direction
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        self.region = (int(left), int(top), int(width), int(height))
        
        self.selection_window.destroy()
        self.root.deiconify() # Show main window again
        self.is_selecting = False
        self.start_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Area Selected: {width}x{height}", fg="green")

    def audio_recorder(self):
        try:
            with sd.InputStream(samplerate=self.AUDIO_SAMPLE_RATE, channels=self.AUDIO_CHANNELS, callback=self.audio_callback):
                self.stop_event.wait()
        except Exception as e:
            # Put exception in queue to be handled by main thread
            self.audio_queue.put(e)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.audio_queue.put(indata.copy())

    def start_recording(self):
        if self.is_recording:
            return
        
        if not self.region:
            messagebox.showerror("Error", "Please select a recording area first.")
            return

        self.is_recording = True
        self.stop_event.clear()
        
        output_filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}"
        self.video_filepath = f"{output_filename}.mp4"
        self.audio_filepath = f"{output_filename}.wav"

        # --- Initialize Video Writer ---
        width, height = self.region[2], self.region[3]
        self.video_writer = cv2.VideoWriter(self.video_filepath, cv2.VideoWriter_fourcc(*self.VIDEO_CODEC), self.VIDEO_FPS, (width, height))

        # --- Initialize and Start Audio Recording ---
        self.audio_thread = threading.Thread(target=self.audio_recorder)
        self.audio_thread.start()

        # Check for immediate audio errors
        try:
            exc = self.audio_queue.get(block=False)
            if isinstance(exc, Exception):
                messagebox.showerror("Audio Error", f"Could not start audio recording. Is a microphone connected?\n\nDetails: {exc}")
                self.is_recording = False
                self.video_writer.release()
                return
            else:
                # Put it back if it's not an exception
                self.audio_queue.put(exc)
        except queue.Empty:
            pass # No error, continue

        # --- Start Video Frame Capture ---
        self.video_thread = threading.Thread(target=self.video_frame_grabber)
        self.video_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Recording...", fg="red")

    def video_frame_grabber(self):
        while self.is_recording:
            start_time = time.time()
            img = pyautogui.screenshot(region=self.region)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.video_writer.write(frame)
            
            # Sleep to maintain FPS
            elapsed_time = time.time() - start_time
            sleep_time = (1/self.VIDEO_FPS) - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.stop_event.set() # Signal audio and video threads to stop

        self.video_thread.join()
        self.audio_thread.join()

        self.video_writer.release()
        
        # --- Save the audio file ---
        try:
            with sf.SoundFile(self.audio_filepath, mode='w', samplerate=self.AUDIO_SAMPLE_RATE, channels=self.AUDIO_CHANNELS) as file:
                while not self.audio_queue.empty():
                    file.write(self.audio_queue.get())
            
            self.combine_audio_video()

        except Exception as e:
            messagebox.showerror("File Error", f"Failed to save audio or combine files.\n\nDetails: {e}")

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Ready", fg="blue")

    def combine_audio_video(self):
        self.status_label.config(text="Status: Combining files...", fg="orange")
        self.root.update()

        try:
            video_clip = cv2.VideoCapture(self.video_filepath)
            audio_clip = sf.SoundFile(self.audio_filepath)

            # FFMPEG is required for this step. If not available, we can't combine.
            # We will use OpenCV's VideoCapture to read frames and a separate process for combining later
            # For simplicity, this script produces separate files. Combining requires FFMPEG.
            
            messagebox.showinfo("Success", f"Recording saved!\n\nVideo: {self.video_filepath}\nAudio: {self.audio_filepath}\n\nYou will need to combine these files using video editing software.")
            
            # A more advanced implementation would use ffmpeg-python or subprocess to combine them.
            # Example using command line ffmpeg:
            # import os
            # final_filename = self.video_filepath.replace('.mp4', '_final.mp4')
            # command = f"ffmpeg -y -i {self.video_filepath} -i {self.audio_filepath} -c:v copy -c:a aac {final_filename}"
            # os.system(command)

        except Exception as e:
            messagebox.showerror("Combining Error", f"Failed to combine video and audio. Please ensure FFmpeg is installed and accessible in your system's PATH.\n\nDetails: {e}")
        finally:
            self.status_label.config(text="Status: Ready", fg="blue")


    def quit_app(self):
        if self.is_recording:
            if messagebox.askyesno("Confirm", "You are currently recording. Are you sure you want to quit? The recording will be lost."):
                self.is_recording = False
                self.stop_event.set()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VerticalShortsRecorder(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    root.mainloop()