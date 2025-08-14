#!/usr/bin/env python3
# videooralannotation.py
# A simple video annotation tool with audio recording capabilities.
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import cv2
from PIL import Image, ImageTk
import threading
import pyaudio
import wave

class VideoAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotation Tool")
        self.folder_path = None
        self.video_files = []
        self.current_video = None
        self.audio_stream = None
        self.recording_thread = None
        self.is_recording = False

        # Main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame: Video list
        self.list_frame = tk.Frame(self.main_frame)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)


        # Select folder button
        self.select_button = tk.Button(self.list_frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(side=tk.LEFT, pady=5)

        # Add metadata button
        self.metadata_button = tk.Button(self.list_frame, text="Add Metadata", command=self.open_metadata_editor, state=tk.DISABLED)
        self.metadata_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Listbox for video files
        self.video_listbox = tk.Listbox(self.list_frame, width=40, height=20)
        self.video_listbox.pack(fill=tk.Y, expand=True)
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)

        # Right frame: Video player and audio controls
        self.media_frame = tk.Frame(self.main_frame)
        self.media_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Video player section
        self.video_label = tk.Label(self.media_frame, text="No video selected")
        self.video_label.pack()

        self.video_controls = tk.Frame(self.media_frame)
        self.video_controls.pack(pady=5)

        self.play_video_button = tk.Button(self.video_controls, text="Play Video", command=self.play_video, state=tk.DISABLED)
        self.play_video_button.pack(side=tk.LEFT, padx=5)

        self.stop_video_button = tk.Button(self.video_controls, text="Stop Video", command=self.stop_video, state=tk.DISABLED)
        self.stop_video_button.pack(side=tk.LEFT, padx=5)

        # Audio annotation section
        self.audio_frame = tk.Frame(self.media_frame)
        self.audio_frame.pack(pady=10)

        self.audio_label = tk.Label(self.audio_frame, text="No audio annotation")
        self.audio_frame.pack()

        self.audio_controls = tk.Frame(self.audio_frame)
        self.audio_controls.pack(pady=5)

        self.play_audio_button = tk.Button(self.audio_controls, text="Play Audio", command=self.play_audio, state=tk.DISABLED)
        self.play_audio_button.pack(side=tk.LEFT, padx=5)

        self.stop_audio_button = tk.Button(self.audio_controls, text="Stop Audio", command=self.stop_audio, state=tk.DISABLED)
        self.stop_audio_button.pack(side=tk.LEFT, padx=5)

        self.record_button = tk.Button(self.audio_controls, text="Record Audio", command=self.toggle_recording, state=tk.DISABLED)
        self.record_button.pack(side=tk.LEFT, padx=5)

        # Video playback state
        self.playing_video = False
        self.cap = None

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Folder with Video Files")
        if self.folder_path:
            self.load_video_files()

    def load_video_files(self):
        self.video_listbox.delete(0, tk.END)
        extensions = ('.mpg', '.mpeg', '.mp4', '.avi', '.mkv', '.mov')
        self.video_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(extensions)]
        self.video_files.sort()
        for video in self.video_files:
            self.video_listbox.insert(tk.END, video)
        self.current_video = None
        self.update_media_controls()
        self.metadata_button.config(state=tk.NORMAL)
    def open_metadata_editor(self):
        metadata_path = os.path.join(self.folder_path, "metadata.txt")
        default_content = (
            "name: \n"
            "date: \n"
            "location: \n"
            "researcher: \n"
            "speaker: \n"
            "permissions for use given by speaker: \n"
        )
        if not os.path.exists(metadata_path):
            with open(metadata_path, "w") as f:
                f.write(default_content)
        with open(metadata_path, "r") as f:
            content = f.read()

        # Remove previous editor if present
        if hasattr(self, "metadata_editor_frame") and self.metadata_editor_frame:
            self.metadata_editor_frame.destroy()

        self.metadata_editor_frame = tk.Frame(self.list_frame)
        self.metadata_editor_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.metadata_editor_frame, text="Edit Metadata", font=("Arial", 12, "bold")).pack()
        self.metadata_text = tk.Text(self.metadata_editor_frame, width=40, height=10)
        self.metadata_text.pack(pady=5, fill=tk.BOTH, expand=True)
        self.metadata_text.insert(tk.END, content)

        save_btn = tk.Button(self.metadata_editor_frame, text="Save", command=self.save_metadata)
        save_btn.pack(pady=5)

    def save_metadata(self):
        metadata_path = os.path.join(self.folder_path, "metadata.txt")
        content = self.metadata_text.get("1.0", tk.END)
        with open(metadata_path, "w") as f:
            f.write(content)
        messagebox.showinfo("Saved", "Metadata saved!")

    def on_video_select(self, event):
        selection = self.video_listbox.curselection()
        if not selection:
            return
        self.current_video = self.video_listbox.get(selection[0])
        self.update_media_controls()
        self.show_first_frame()

    def show_first_frame(self):
        if not self.current_video:
            self.video_label.config(image='', text="No video selected")
            return
        video_path = os.path.join(self.folder_path, self.current_video)
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk, text="")
        else:
            # Show black frame if video can't be read
            img = Image.new('RGB', (640, 480), color='black')
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk, text="")
        cap.release()

    def update_media_controls(self):
        if self.current_video:
            self.play_video_button.config(state=tk.NORMAL)
            self.stop_video_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL, text="Record Audio" if not self.is_recording else "Stop Recording")
            wav_path = os.path.join(self.folder_path, os.path.splitext(self.current_video)[0] + '.wav')
            if os.path.exists(wav_path):
                self.audio_label.config(text=f"Audio: {os.path.splitext(self.current_video)[0]}.wav")
                self.play_audio_button.config(state=tk.NORMAL)
                self.stop_audio_button.config(state=tk.NORMAL)
            else:
                self.audio_label.config(text="No audio annotation")
                self.play_audio_button.config(state=tk.DISABLED)
                self.stop_audio_button.config(state=tk.DISABLED)
        else:
            self.video_label.config(text="No video selected")
            self.play_video_button.config(state=tk.DISABLED)
            self.stop_video_button.config(state=tk.DISABLED)
            self.audio_label.config(text="No audio annotation")
            self.play_audio_button.config(state=tk.DISABLED)
            self.stop_audio_button.config(state=tk.DISABLED)
            self.record_button.config(state=tk.DISABLED, text="Record Audio")

    def play_video(self):
        if not self.current_video:
            return
        self.stop_video()  # Stop any ongoing video
        video_path = os.path.join(self.folder_path, self.current_video)
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open video file")
            return

        self.playing_video = True
        self.video_label.config(text="")
        def update_frame():
            if self.playing_video:
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (640, 480))  # Resize for display
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                    self.video_label.after(30, update_frame)  # ~30 fps
                else:
                    self.stop_video()

        update_frame()

    def stop_video(self):
        self.playing_video = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.show_first_frame()

    def play_audio(self):
        if not self.current_video:
            return
        self.stop_audio()  # Stop any ongoing audio
        wav_path = os.path.join(self.folder_path, os.path.splitext(self.current_video)[0] + '.wav')
        if not os.path.exists(wav_path):
            return

        try:
            p = pyaudio.PyAudio()
            wf = wave.open(wav_path, 'rb')
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            def playback():
                try:
                    data = wf.readframes(1024)
                    while data and self.audio_stream == stream:
                        stream.write(data)
                        data = wf.readframes(1024)
                except Exception as e:
                    messagebox.showerror("Error", f"Audio playback failed: {e}")
                finally:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    wf.close()

            self.audio_stream = stream
            threading.Thread(target=playback, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {e}")

    def stop_audio(self):
        self.audio_stream = None  # Stops playback loop

    def toggle_recording(self):
        if not self.current_video:
            return

        if self.is_recording:
            # Stop recording
            self.is_recording = False
            if self.recording_thread:
                self.recording_thread.join(timeout=1.0)  # Ensure thread completes
                self.recording_thread = None
            self.update_media_controls()
        else:
            # Start recording
            wav_path = os.path.join(self.folder_path, os.path.splitext(self.current_video)[0] + '.wav')
            if os.path.exists(wav_path):
                if not messagebox.askyesno("Overwrite?", "Audio file already exists. Overwrite?"):
                    return

            try:
                p = pyaudio.PyAudio()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                frames_per_buffer=1024)

                frames = []
                self.is_recording = True
                self.record_button.config(text="Stop Recording")

                def record():
                    try:
                        while self.is_recording:
                            data = stream.read(1024, exception_on_overflow=False)
                            frames.append(data)
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Recording failed: {e}"))
                    finally:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        if frames and not self.is_recording:  # Save only if stopped intentionally
                            wf = wave.open(wav_path, 'wb')
                            wf.setnchannels(1)
                            wf.setsampwidth(2)  # 16-bit
                            wf.setframerate(44100)
                            wf.writeframes(b''.join(frames))
                            wf.close()
                            self.root.after(0, lambda: messagebox.showinfo("Saved", "Recording saved!"))
                        self.root.after(0, self.update_media_controls)

                self.recording_thread = threading.Thread(target=record, daemon=True)
                self.recording_thread.start()
            except Exception as e:
                self.is_recording = False
                self.record_button.config(text="Record Audio")
                messagebox.showerror("Error", f"Failed to start recording: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnnotationApp(root)
    root.geometry("1400x800")  # Set window size larger for all controls
    root.mainloop()