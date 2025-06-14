import os
import threading
import time
import cv2
import numpy as np
import tkinter as tk
import sounddevice as sd
import tkinter.filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from PIL import Image, ImageDraw
from scipy.io.wavfile import write, read
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import tkinter.filedialog as filedialog
from scipy.io.wavfile import write as write_wav
import customtkinter as ctk
import tempfile
from pydub import AudioSegment
from pydub.effects import speedup
import pygame


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# === ICON CREATION ===
def create_icon(shape, size=(20, 20), color="black"):
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    w, h = size
    if shape == "circle":
        draw.ellipse((4, 4, w - 4, h - 4), fill=color)
    elif shape == "square":
        draw.rectangle((4, 4, w - 4, h - 4), fill=color)
    elif shape == "triangle":
        draw.polygon([(w // 4, h // 4), (w // 4, 3 * h // 4), (3 * w // 4, h // 2)], fill=color)
    elif shape == "pause":
        draw.rectangle((5, 4, 9, h - 4), fill=color)
        draw.rectangle((11, 4, 15, h - 4), fill=color)
    elif shape == "resume":
        draw.polygon([(5, 4), (15, h // 2), (5, h - 4)], fill=color)
    elif shape == "x":
        draw.line((5, 5, w - 5, h - 5), fill=color, width=2)
        draw.line((w - 5, 5, 5, h - 5), fill=color, width=2)
    elif shape == "forward":
        draw.polygon([(5, h // 4), (5, 3 * h // 4), (12, h // 2)], fill=color)
        draw.polygon([(10, h // 4), (10, 3 * h // 4), (17, h // 2)], fill=color)
    elif shape == "backward":
        draw.polygon([(15, h // 4), (15, 3 * h // 4), (8, h // 2)], fill=color)
        draw.polygon([(10, h // 4), (10, 3 * h // 4), (3, h // 2)], fill=color)
    return ctk.CTkImage(light_image=image, dark_image=image)


# === VOICE RECORDER FRAME ===
class VoiceRecorderAppFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.recording = False
        self.paused = False
        self.playing = False
        self.is_mixed = False
        self.audio_data_list = []
        self.original_audio_data = None
        self.play_audio_data = None
        self.speed_adjusted_audio_data = None
        self.background_audio_segment = None
        self.samplerate = 44100
        self.play_index = 0
        self.original_audio_length = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.pause_start = 0
        self.total_pause_duration = 0
        self.playback_speed = 1.0
        self.icon_start_record = create_icon("circle", color="red")
        self.icon_stop_record = create_icon("square", color="black")
        self.icon_pause = create_icon("pause", color="red")
        self.icon_resume = create_icon("resume", color="black")
        self.icon_play = create_icon("triangle", color="white")
        self.icon_stop_play = create_icon("x", color="red")
        self.icon_forward = create_icon("forward", color="white")
        self.icon_backward = create_icon("backward", color="white")

        self.setup_ui()

    def setup_ui(self):
        self.action_button = ctk.CTkButton(self, image=self.icon_start_record, text="", command=self.toggle_recording, width=60)
        self.action_button.place(relx=0.4, y=30, anchor="n")

        self.pause_button = ctk.CTkButton(self, image=self.icon_pause, text="", command=self.toggle_pause, width=60)
        self.pause_button.place(relx=0.6, y=30, anchor="n")
        self.pause_button.configure(state="disabled")

        self.label_record = ctk.CTkLabel(self, text="Start Recording", font=("Arial", 12))
        self.label_record.place(relx=0.4, y=80, anchor="n")

        self.label_pause = ctk.CTkLabel(self, text="Pause", font=("Arial", 12))
        self.label_pause.place(relx=0.6, y=80, anchor="n")

        self.canvas = ctk.CTkCanvas(self, width=500, height=100, bg="white")
        self.canvas.place(relx=0.5, rely=0.2, anchor="n")
        self.waveform_data = np.zeros(500)

        self.setup_playback_controls()

        self.seek_var = tk.DoubleVar()
        self.seek_slider = ctk.CTkSlider(self, from_=0, to=1, variable=self.seek_var, command=self.seek_audio, width=500)
        self.seek_slider.place(relx=0.5, rely=0.53, anchor="n")
        self.seek_slider.configure(state="disabled")

        self.left_time_label = ctk.CTkLabel(self, text="00:00", font=("Arial", 12))
        self.left_time_label.place(relx=0.05, rely=0.53, anchor="w")

        self.right_time_label = ctk.CTkLabel(self, text="00:00", font=("Arial", 12))
        self.right_time_label.place(relx=0.95, rely=0.53, anchor="e")

        self.timer_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.timer_label.place(relx=0.5, rely=0.58, anchor="n")

        self.export_button = ctk.CTkButton(self, text="💾 Save / Export", command=self.export_audio)
        self.export_button.place(relx=0.5, rely=0.65, anchor="n")

        self.import_button = ctk.CTkButton(self, text="📁 Import Audio", command=self.import_audio)
        self.import_button.place(relx=0.5, rely=0.7, anchor="n")

        self.trim_start_entry = ctk.CTkEntry(self, placeholder_text="Start Time (sec)", width=120)
        self.trim_start_entry.place(relx=0.3, rely=0.74, anchor="n")

        self.trim_end_entry = ctk.CTkEntry(self, placeholder_text="End Time (sec)", width=120)
        self.trim_end_entry.place(relx=0.7, rely=0.74, anchor="n")

        self.trim_button = ctk.CTkButton(self, text="Trim", command=self.trim_audio)
        self.trim_button.place(relx=0.5, rely=0.79, anchor="n")
        
        self.speed_var = ctk.StringVar(value="1.0x")
        self.speed_menu = ctk.CTkOptionMenu(self, values=["0.5x", "1.0x", "1.5x", "2.0x"],
                                                      variable=self.speed_var, command=self.set_speed)
        self.speed_menu.place(relx=0.5, rely=0.89, anchor="n")
        
        self.voice_volume_slider = ctk.CTkSlider(self, from_=-20, to=10, number_of_steps=30, width=200, command=self._update_mix_on_slider_change)
        self.voice_volume_slider.set(0)
        self.voice_volume_slider.place(relx=0.25, rely=0.93, anchor="n")
        ctk.CTkLabel(self, text="Voice Volume").place(relx=0.25, rely=0.9, anchor="n")
        
        self.noise_volume_slider = ctk.CTkSlider(self, from_=-40, to=10, number_of_steps=50, width=200, command=self._update_mix_on_slider_change)
        self.noise_volume_slider.set(-10)
        self.noise_volume_slider.place(relx=0.75, rely=0.93, anchor="n")
        ctk.CTkLabel(self, text="Background Noise Volume").place(relx=0.75, rely=0.9, anchor="n")

    def setup_playback_controls(self):
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.place(relx=0.5, rely=0.4, anchor="n")

        self.backward_button = ctk.CTkButton(self.controls_frame, image=self.icon_backward, text="", command=self.skip_backward, width=40)
        self.backward_button.grid(row=0, column=0, padx=5)

        self.play_button = ctk.CTkButton(self.controls_frame, image=self.icon_play, text="", command=self.toggle_playback, state="disabled", width=60)
        self.play_button.grid(row=0, column=1, padx=5)

        self.forward_button = ctk.CTkButton(self.controls_frame, image=self.icon_forward, text="", command=self.skip_forward, width=40)
        self.forward_button.grid(row=0, column=2, padx=5)

        self.label_back = ctk.CTkLabel(self.controls_frame, text="<<5", font=("Arial", 12))
        self.label_back.grid(row=1, column=0)

        self.label_playback = ctk.CTkLabel(self.controls_frame, text="Play", font=("Arial", 12))
        self.label_playback.grid(row=1, column=1)

        self.label_forward = ctk.CTkLabel(self.controls_frame, text="5>>", font=("Arial", 12))
        self.label_forward.grid(row=1, column=2)
        
        self.add_background_button = ctk.CTkButton(self, text="🎵 Add Background Noise", command=self.add_background_audio)
        self.add_background_button.place(relx=0.3, rely=0.84, anchor="n")

        self.remove_background_button = ctk.CTkButton(self, text="🗑️ Remove Background Noise", command=self.remove_background_audio, state="disabled")
        self.remove_background_button.place(relx=0.7, rely=0.84, anchor="n")

    def _reset_mix_state(self):
        self.is_mixed = False; self.background_audio_segment = None
        self.remove_background_button.configure(state="disabled")

    def toggle_recording(self):
        if not self.recording: self.start_audio_recording()
        else: self.stop_audio_recording()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_start = time.time()
            self.pause_button.configure(image=self.icon_resume)
        else:
            self.total_pause_duration += time.time() - self.pause_start
            self.pause_button.configure(image=self.icon_pause)

    def start_audio_recording(self):
        self.recording = True
        self.paused = False
        self.audio_data_list = []
        self.start_time = time.time()
        self.total_pause_duration = 0
        self.action_button.configure(image=self.icon_stop_record)
        self.label_record.configure(text="Stop Recording")
        self.pause_button.configure(state="normal")
        self.play_button.configure(state="disabled")
        self.seek_slider.configure(state="disabled")
        self._reset_mix_state()
        threading.Thread(target=self.record_audio_thread, daemon=True).start()
        self.update_waveform()
        self.update_timer()

    def stop_audio_recording(self):
        self.recording = False
        self.action_button.configure(image=self.icon_start_record)
        self.label_record.configure(text="Start Recording")
        self.pause_button.configure(state="disabled")
        self.label_pause.configure(text="Pause")
        self.pause_button.configure(image=self.icon_pause)
        if self.audio_data_list:
            audio_np = np.concatenate(self.audio_data_list, axis=0)
            self.original_audio_data = audio_np.copy()
            self.play_audio_data = audio_np.copy()
            self._reset_mix_state() 
            self.play_button.configure(state="normal")
            self.seek_slider.configure(state="normal")
            self.timer_label.configure(text=f"Recording Finished")
            self._apply_speed_effect()
    
    def import_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            try:
                audio = AudioSegment.from_file(file_path).set_channels(1)
                self.samplerate = audio.frame_rate
                samples = np.array(audio.get_array_of_samples())
                data_float = (samples / (2**(audio.sample_width * 8 - 1))).astype(np.float32)
                self.original_audio_data = data_float.reshape(-1, 1)
                self.play_audio_data = self.original_audio_data.copy()
                self.play_index = 0
                self._reset_mix_state() 
                self.seek_slider.configure(state="normal")
                self.play_button.configure(state="normal")
                self.timer_label.configure(text="Audio Imported.")
                self._apply_speed_effect()
            except Exception as e:
                self.timer_label.configure(text=f"Import failed: {e}")

    def trim_audio(self):
        if self.play_audio_data is None: return
        try:
            start_time = float(self.trim_start_entry.get())
            original_duration = len(self.original_audio_data) / self.samplerate
            end_time = float(self.trim_end_entry.get())
            if start_time >= end_time or start_time < 0 or end_time > original_duration:
                self.timer_label.configure(text="Invalid trim times."); return
            start_sample = int(start_time * self.samplerate)
            end_sample = int(end_time * self.samplerate)
            trimmed_data = self.original_audio_data[start_sample:end_sample]
            self.original_audio_data = trimmed_data.copy()
            self.play_audio_data = trimmed_data.copy()
            self.play_index = 0
            self._reset_mix_state()
            self.timer_label.configure(text="Trimmed successfully.")
            self._apply_speed_effect()
        except Exception as e:
            self.timer_label.configure(text=f"Trim failed: {e}")

    def add_background_audio(self):
        if self.original_audio_data is None: return
        bg_file_path = filedialog.askopenfilename(title="Select Background Audio File", filetypes=[("Audio Files", "*.wav *.mp3")])
        if not bg_file_path: return
        try:
            background_audio = AudioSegment.from_file(bg_file_path).set_channels(1)
            voice_duration_ms = len(self.original_audio_data) * 1000 / self.samplerate
            if len(background_audio) < voice_duration_ms:
                background_audio = (background_audio * (int(voice_duration_ms / len(background_audio)) + 1))
            self.background_audio_segment = background_audio[:voice_duration_ms]
            self.is_mixed = True
            self.remove_background_button.configure(state="normal")
            self._update_mix() 
            self.timer_label.configure(text="Background audio added.")
        except Exception as e:
            self.timer_label.configure(text=f"Error adding background: {str(e)}")

    def _update_mix_on_slider_change(self, _=None):
        if self.is_mixed: self._update_mix()

    def _update_mix(self):
        if not self.is_mixed or self.original_audio_data is None or self.background_audio_segment is None: return
        voice_audio = AudioSegment((self.original_audio_data * 32767).astype(np.int16).tobytes(), frame_rate=self.samplerate, sample_width=2, channels=1)
        voice_vol_dB = self.voice_volume_slider.get(); bg_vol_dB = self.noise_volume_slider.get()
        mixed_audio = (voice_audio + voice_vol_dB).overlay(self.background_audio_segment + bg_vol_dB)
        samples = np.array(mixed_audio.get_array_of_samples())
        mixed_float = (samples / (2**(mixed_audio.sample_width * 8 - 1))).astype(np.float32)
        self.play_audio_data = mixed_float.reshape(-1, 1)
        if self.playing: self.stop_audio()
        self.timer_label.configure(text="Mix updated.")
        self._apply_speed_effect()

    def remove_background_audio(self):
        if not self.is_mixed or self.original_audio_data is None: return
        self.play_audio_data = self.original_audio_data.copy()
        self._reset_mix_state()
        self.play_index = 0
        self.timer_label.configure(text="Background audio removed.")
        self._apply_speed_effect()

    def _apply_speed_effect(self):
        if self.play_audio_data is None:
            self.speed_adjusted_audio_data = None; self.original_audio_length = 0
            return
        self.timer_label.configure(text=f"Processing speed: {self.playback_speed}x...")
        self.update()
        self.original_audio_length = len(self.play_audio_data) / self.samplerate
        if self.playback_speed == 1.0:
            self.speed_adjusted_audio_data = self.play_audio_data.copy()
        else:
            source_segment = AudioSegment((self.play_audio_data * 32767).astype(np.int16).tobytes(), frame_rate=self.samplerate, sample_width=2, channels=1)
            sped_up_segment = speedup(source_segment, playback_speed=self.playback_speed)
            samples = np.array(sped_up_segment.get_array_of_samples())
            self.speed_adjusted_audio_data = (samples / (2**(sped_up_segment.sample_width * 8 - 1))).astype(np.float32).reshape(-1, 1)
        self.play_index = 0
        self.seek_slider.set(0)
        self.left_time_label.configure(text="00:00")
        self.right_time_label.configure(text=self.format_time(self.original_audio_length))
        self.timer_label.configure(text=f"Speed set to {self.playback_speed}x. Ready.")

    def toggle_playback(self):
        if self.playing: self.stop_audio()
        else: self.play_audio()

    def play_audio(self):
        if self.speed_adjusted_audio_data is None: return
        self.playing = True
        self.play_button.configure(image=self.icon_stop_play)
        self.seek_slider.configure(state="normal")
        threading.Thread(target=self._play_audio_thread, daemon=True).start()
        self.update_waveform()
        self.update_timer()

    def stop_audio(self):
        self.playing = False
        self.play_button.configure(image=self.icon_play)

    def _play_audio_thread(self):
        stream = sd.OutputStream(samplerate=self.samplerate, channels=1, dtype='float32')
        stream.start()
        while self.playing and self.play_index < len(self.speed_adjusted_audio_data):
            remaining = len(self.speed_adjusted_audio_data) - self.play_index
            chunk_size = min(1024, remaining)
            chunk = self.speed_adjusted_audio_data[self.play_index : self.play_index + chunk_size]
            stream.write(chunk)
            self.waveform_data = chunk[:, 0]
            self.play_index += chunk_size
        stream.stop()
        stream.close()
        if self.play_index >= len(self.speed_adjusted_audio_data):
            self.play_index = 0
            self.seek_slider.set(0)
        self.waveform_data = np.zeros(500)
        self.stop_audio()
        if not self.playing: self.timer_label.configure(text="Playback Finished")

    def seek_audio(self, value):
        if self.speed_adjusted_audio_data is not None and self.original_audio_length > 0:
            target_time_original = float(value) * self.original_audio_length
            target_time_adjusted = target_time_original / self.playback_speed
            self.play_index = int(target_time_adjusted * self.samplerate)

    def update_waveform(self):
        if not (self.recording or self.playing):
            self.canvas.delete("wave"); return
        if self.recording and self.paused:
            self.after(50, self.update_waveform); return
        self.canvas.delete("wave")
        h, w = 100, 500; center = h // 2
        data = np.abs(self.waveform_data) 
        if len(data) > w: step = len(data) // w if w > 0 else 1; data = data[::step][:w]
        else: data = np.pad(data, (0, w - len(data)))
        scaled = data * h 
        for i in range(w):
            y = scaled[i]
            self.canvas.create_line(i, center - y, i, center + y, fill="#0077ff", tags="wave")
        self.after(50, self.update_waveform)

    def update_timer(self):
        if self.recording and not self.paused:
            self.elapsed_time = time.time() - self.start_time - self.total_pause_duration
            current_time_str = self.format_time(self.elapsed_time)
            self.timer_label.configure(text=f"Recording: {current_time_str}")
            self.left_time_label.configure(text=current_time_str)
            self.right_time_label.configure(text=current_time_str)
        elif self.playing:
            time_elapsed_in_played_audio = self.play_index / self.samplerate if self.samplerate > 0 else 0
            equivalent_original_time = time_elapsed_in_played_audio * self.playback_speed
            current_time_str = self.format_time(equivalent_original_time)
            self.timer_label.configure(text=f"Playing: {current_time_str}")
            self.left_time_label.configure(text=current_time_str)
            if self.original_audio_length > 0:
                self.seek_slider.set(equivalent_original_time / self.original_audio_length)
        self.after(200, self.update_timer)

    def format_time(self, seconds):
        mins = int(seconds // 60); secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def export_audio(self):
        if self.speed_adjusted_audio_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP4 files", "*.mp4")])
            if file_path:
                write(file_path, self.samplerate, self.speed_adjusted_audio_data)
                self.timer_label.configure(text="Audio exported successfully.")
    
    def set_speed(self, speed_str: str):
        speed_map = {"0.5x": 0.5, "1.0x": 1.0, "1.5x": 1.5, "2.0x": 2.0}
        new_speed = speed_map.get(speed_str, 1.0)
        if new_speed == self.playback_speed: return
        was_playing = self.playing
        if was_playing: self.stop_audio()
        self.playback_speed = new_speed
        self._apply_speed_effect()
        if was_playing: self.play_audio()

    def skip_forward(self):
        if self.speed_adjusted_audio_data is not None:
            new_index = self.play_index + int(5 * self.samplerate)
            self.play_index = min(new_index, len(self.speed_adjusted_audio_data))

    def skip_backward(self):
        if self.speed_adjusted_audio_data is not None:
            new_index = self.play_index - int(5 * self.samplerate)
            self.play_index = max(new_index, 0)

    def record_audio_thread(self):
        def callback(indata, frames, time_info, status):
            if self.recording and not self.paused:
                self.audio_data_list.append(indata.copy())
                self.waveform_data = indata[:, 0]
        with sd.InputStream(samplerate=self.samplerate, channels=1, callback=callback, dtype='float32'):
            while self.recording: sd.sleep(100)
    
# === VIDEO RECORDER FRAME ===
class VideoRecorderAppFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.set_appearance_mode("Light")

        self.recording, self.paused_recording, self.preview_thread_active = False, False, True
        self.current_video_clip, self.background_audio_sound, self.background_audio_channel = None, None, None
        self.is_playing, self.is_slider_dragging, self.playback_after_id = False, False, None
        self.playback_start_time, self.playback_start_pos, self.current_position, self.video_duration = 0, 0, 0, 0.0
        self.record_elapsed_time = 0
        self.temp_dir = tempfile.TemporaryDirectory()
        self.playback_video_path, self.background_audio_path, self.temp_preview_audio_path = None, None, None
        self.available_cameras = self.get_available_cameras()
        self.camera_index = self.available_cameras[0] if self.available_cameras else 0
        self.frame_rate = 30.0
        self.audio_samplerate = 44100
        self.recorded_audio_frames = []
        self.playback_speed = 1.0
        pygame.mixer.init(frequency=self.audio_samplerate)
        pygame.mixer.set_num_channels(8)
        self.setup_ui()
        self.start_live_preview()
        # --- FIX: REMOVED protocol handler. It belongs on the main App window. ---

    def get_available_cameras(self, max_cameras_to_check=5):
        available_indices = []
        for i in range(max_cameras_to_check):
            cap = cv2.VideoCapture(i)
            if cap.isOpened() and cap.read()[0]:
                available_indices.append(i)
            cap.release()
        return available_indices

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        self.camera_dropdown = ctk.CTkOptionMenu(self, values=[f"Camera {i}" for i in self.available_cameras], command=self.switch_camera)
        if self.available_cameras: self.camera_dropdown.set(f"Camera {self.camera_index}")
        else: self.camera_dropdown.set("No cameras found"); self.camera_dropdown.configure(state="disabled")
        self.camera_dropdown.grid(row=0, column=0, pady=(10, 0))

        self.preview_container_frame = ctk.CTkFrame(self, fg_color="transparent") 
        self.preview_container_frame.grid(row=1, column=0, pady=(5,0), padx=20, sticky="nsew") 

        self.video_preview_label = ctk.CTkLabel(self.preview_container_frame, text="") 
        self.video_preview_label.pack(expand=True)
        
        self.rec_status_overlay_label = ctk.CTkLabel(
            self.preview_container_frame, text="", font=("Arial", 18, "bold"), 
            text_color="red", bg_color="transparent"
        )
        self.rec_status_overlay_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        self.status_label = ctk.CTkLabel(self, text="Live Preview", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, pady=(5, 5))

        controls_main_frame = ctk.CTkFrame(self)
        controls_main_frame.grid(row=3, column=0, pady=(0, 20), padx=20, sticky="ew")
        controls_main_frame.grid_columnconfigure(0, weight=1)
        
        seek_frame = ctk.CTkFrame(controls_main_frame, fg_color="transparent")
        seek_frame.pack(fill="x", padx=10, pady=(10, 5), side="top")
        self.left_time_label = ctk.CTkLabel(seek_frame, text="00:00", width=45)
        self.left_time_label.pack(side="left", padx=(0, 10))
        self.seek_slider = ctk.CTkSlider(seek_frame, from_=0, to=100, command=self.seek_from_slider, state="disabled")
        self.seek_slider.pack(side="left", fill="x", expand=True)
        self.seek_slider.bind("<Button-1>", self.on_slider_press)
        self.seek_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.right_time_label = ctk.CTkLabel(seek_frame, text="00:00", width=45)
        self.right_time_label.pack(side="right", padx=(10, 0))

        playback_options_frame = ctk.CTkFrame(controls_main_frame)
        playback_options_frame.pack(pady=5, side="top")
        playback_controls_frame = ctk.CTkFrame(playback_options_frame)
        playback_controls_frame.pack(side="left", padx=(0, 20))
        btn_font = ("Arial", 22)

        self.record_button = ctk.CTkButton(playback_controls_frame, text="🔴", font=btn_font, command=self.toggle_recording, width=60)
        self.record_button.grid(row=0, column=0, padx=10, pady=5); self.record_label = ctk.CTkLabel(playback_controls_frame, text="Start Recording"); self.record_label.grid(row=1, column=0)
        self.pause_button = ctk.CTkButton(playback_controls_frame, text="⏸️", font=btn_font, command=self.toggle_pause_record, width=60, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=10, pady=5); self.pause_label = ctk.CTkLabel(playback_controls_frame, text="Pause"); self.pause_label.grid(row=1, column=1)
        self.backward_button = ctk.CTkButton(playback_controls_frame, text="<<5", font=btn_font, command=self.skip_backward, width=60, state="disabled")
        self.backward_button.grid(row=0, column=2, padx=10, pady=5)
        self.play_button = ctk.CTkButton(playback_controls_frame, text="▶️", font=btn_font, command=self.toggle_playback, width=60, state="disabled")
        self.play_button.grid(row=0, column=3, padx=10, pady=5); self.play_label = ctk.CTkLabel(playback_controls_frame, text="Play"); self.play_label.grid(row=1, column=3)
        self.forward_button = ctk.CTkButton(playback_controls_frame, text="5>>", font=btn_font, command=self.skip_forward, width=60, state="disabled")
        self.forward_button.grid(row=0, column=4, padx=10, pady=5)

        speed_frame = ctk.CTkFrame(playback_options_frame, fg_color="transparent")
        speed_frame.pack(side="left", padx=(10, 0), anchor="s", pady=5)
        ctk.CTkLabel(speed_frame, text="Speed:").pack()
        self.speed_dropdown = ctk.CTkOptionMenu(speed_frame, values=["0.5x", "1x", "1.5x", "2x"], command=self.set_speed, state="disabled")
        self.speed_dropdown.set("1x")
        self.speed_dropdown.pack()

        self.trim_frame = ctk.CTkFrame(controls_main_frame)
        self.trim_frame.pack(pady=5, side="top")
        self.trim_start_entry = ctk.CTkEntry(self.trim_frame, placeholder_text="Trim Start (s)", width=120)
        self.trim_start_entry.grid(row=0, column=0, padx=5)
        self.trim_end_entry = ctk.CTkEntry(self.trim_frame, placeholder_text="Trim End (s)", width=120)
        self.trim_end_entry.grid(row=0, column=1, padx=5)
        self.trim_button = ctk.CTkButton(self.trim_frame, text="Trim Video", command=self.trim_video)
        self.trim_button.grid(row=0, column=2, padx=5)
        self.trim_button.configure(state="disabled")

        import_export_frame = ctk.CTkFrame(controls_main_frame)
        import_export_frame.pack(pady=5, side="top")
        self.import_button = ctk.CTkButton(import_export_frame, text="📁 Import Video", command=self.import_video)
        self.import_button.grid(row=0, column=0, pady=5, padx=10)
        self.export_button = ctk.CTkButton(import_export_frame, text="💾 Save / Export", command=self.export_video, state="disabled")
        self.export_button.grid(row=0, column=1, pady=5, padx=10)

        audio_volume_frame = ctk.CTkFrame(controls_main_frame)
        audio_volume_frame.pack(pady=(5, 10), fill="x", padx=10, side="top")
        audio_volume_frame.grid_columnconfigure((0, 3), weight=1)
        audio_volume_frame.grid_columnconfigure((1, 2), weight=0)
        bg_volume_container = ctk.CTkFrame(audio_volume_frame, fg_color="transparent")
        bg_volume_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(bg_volume_container, text="Background Volume").pack()
        self.bg_volume_slider = ctk.CTkSlider(bg_volume_container, from_=0, to=1.5, number_of_steps=15, command=self.set_bg_volume, state="disabled")
        self.bg_volume_slider.set(0.5); self.bg_volume_slider.pack(fill="x", pady=(0, 10))
        self.add_bg_button = ctk.CTkButton(audio_volume_frame, text="🎵 Add Background Noise", command=self.add_background_audio, state="disabled")
        self.add_bg_button.grid(row=0, column=1, padx=5, pady=(20, 0))
        self.remove_bg_button = ctk.CTkButton(audio_volume_frame, text="🗑️ Remove Background Noise", command=self.remove_background_audio_and_show_popup, state="disabled")
        self.remove_bg_button.grid(row=0, column=2, padx=5, pady=(20, 0))
        video_volume_container = ctk.CTkFrame(audio_volume_frame, fg_color="transparent")
        video_volume_container.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(video_volume_container, text="Video Volume").pack()
        self.voice_volume_slider = ctk.CTkSlider(video_volume_container, from_=0, to=1.5, number_of_steps=15, command=self.set_main_volume, state="disabled")
        self.voice_volume_slider.set(1.0); self.voice_volume_slider.pack(fill="x", pady=(0, 10))
        
        self.update_time_labels()

    def set_speed(self, speed_str: str):
        speed_map = {"0.5x": 0.5, "1x": 1.0, "1.5x": 1.5, "2x": 2.0}
        new_speed = speed_map.get(speed_str, 1.0)
        if new_speed == self.playback_speed: return
        was_playing = self.is_playing
        if was_playing: self.stop_playback()
        self.playback_speed = new_speed
        if self.playback_speed != 1.0:
            self.status_label.configure(text=f"Speed: {speed_str} (Audio Muted)")
        else:
            if self.current_video_clip:
                self.status_label.configure(text=f"Loaded: {os.path.basename(self.playback_video_path)}")
        if was_playing: self.start_playback()
    
    def start_recording(self):
        self.stop_live_preview(); self.stop_playback()
        self.recording = True
        self.paused_recording = False
        self.recorded_audio_frames = []
        self.record_elapsed_time = 0
        self.record_button.configure(text="⏹️")
        self.record_label.configure(text="Stop Recording")
        self.pause_button.configure(state="normal")
        self.camera_dropdown.configure(state="disabled")
        self.status_label.configure(text=f"Recording from Camera {self.camera_index}...")
        threading.Thread(target=self._record_video_thread, daemon=True).start()
        threading.Thread(target=self._record_audio_thread, daemon=True).start()
        threading.Thread(target=self._update_recording_status_thread, daemon=True).start()

    def stop_recording(self):
        self.recording = False
        self.rec_status_overlay_label.configure(text="")
        self.record_button.configure(text="🔴")
        self.record_label.configure(text="Start Recording")
        self.pause_button.configure(state="disabled")
        self.import_button.configure(state="normal") 
        self.status_label.configure(text="Merging audio and video..."); self.update_idletasks()
        time.sleep(1)
        threading.Thread(target=self._merge_and_load_recording, daemon=True).start()

    def _update_recording_status_thread(self):
        start_time = time.time()
        while self.recording:
            if not self.paused_recording:
                self.record_elapsed_time = time.time() - start_time
                time_str = self.format_time(self.record_elapsed_time)
                self.rec_status_overlay_label.configure(text=f"● REC\n{time_str}")
                time.sleep(0.6)
                if not self.recording: break
                self.rec_status_overlay_label.configure(text=f" \n{time_str}")
                time.sleep(0.6)
            else:
                start_time = time.time() - self.record_elapsed_time
                time_str = self.format_time(self.record_elapsed_time)
                self.rec_status_overlay_label.configure(text=f"⏸ Paused\n{time_str}")
                time.sleep(0.5)
        self.rec_status_overlay_label.configure(text="")

    def toggle_pause_record(self):
        self.paused_recording = not self.paused_recording
        if self.paused_recording:
            self.pause_button.configure(text="▶️")
            self.pause_label.configure(text="Resume")
            self.status_label.configure(text="Recording Paused")
        else:
            self.pause_button.configure(text="⏸️")
            self.pause_label.configure(text="Pause")
            self.status_label.configure(text=f"Recording from Camera {self.camera_index}...")

    def trim_video(self):
        if not self.current_video_clip:
            messagebox.showerror("Error", "No video loaded to trim.")
            return
        try:
            start_time = float(self.trim_start_entry.get())
            end_time = float(self.trim_end_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid trim times. Please enter numeric values for start and end.")
            return
        if start_time < 0 or end_time <= start_time:
            messagebox.showerror("Error", "Invalid times. End time must be greater than start time, and both must be positive.")
            return
        if end_time > self.video_duration:
            messagebox.showerror("Error", f"End time ({end_time}s) exceeds video duration ({self.video_duration:.2f}s).")
            return
        self.stop_playback()
        self.status_label.configure(text="Trimming video..."); self.update_idletasks()
        try:
            trimmed_clip = self.current_video_clip.subclip(start_time, end_time)
            temp_trimmed_path = os.path.join(self.temp_dir.name, f"trimmed_{int(time.time())}.mp4")
            trimmed_clip.write_videofile(temp_trimmed_path, codec="libx264", audio_codec="aac", logger=None)
            trimmed_clip.close()
            if self.current_video_clip: self.current_video_clip.close()
            self.playback_video_path = temp_trimmed_path
            self._on_video_load()
            messagebox.showinfo("Trim Complete", "Video trimmed successfully.")
            self.trim_start_entry.delete(0, 'end')
            self.trim_end_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Trim Error", f"An error occurred during trimming: {e}")
            self.status_label.configure(text="Trim failed.")

    def start_playback(self):
        if not self.current_video_clip or self.is_playing: return
        if self.current_position >= self.video_duration: self.current_position = 0
        self.is_playing = True
        self.play_button.configure(text="⏸️"); self.play_label.configure(text="Pause")
        if self.playback_speed == 1.0:
            if self.temp_preview_audio_path: pygame.mixer.music.play(start=self.current_position)
            if self.background_audio_sound and self.background_audio_channel:
                self.background_audio_channel.play(self.background_audio_sound, loops=-1)
        self.playback_start_time = time.time()
        self.playback_start_pos = self.current_position
        self.play_step()

    def stop_playback(self):
        if not self.is_playing: return
        self.is_playing = False
        self.play_button.configure(text="▶️"); self.play_label.configure(text="Play")
        pygame.mixer.music.stop()
        if self.background_audio_channel: self.background_audio_channel.stop()
        if self.playback_after_id: self.after_cancel(self.playback_after_id); self.playback_after_id = None
        if not self.is_slider_dragging:
             elapsed = time.time() - self.playback_start_time
             self.current_position = self.playback_start_pos + (elapsed * self.playback_speed)
             self.current_position = min(self.current_position, self.video_duration)
        self.update_time_labels()

    def play_step(self):
        if not self.is_playing: return
        if not self.is_slider_dragging:
            elapsed_wall_time = time.time() - self.playback_start_time
            self.current_position = self.playback_start_pos + (elapsed_wall_time * self.playback_speed)
        if self.current_position >= self.video_duration:
            self.stop_playback()
            self.current_position = 0
            self.update_video_frame(self.current_position)
            self.update_time_labels()
            return
        self.update_video_frame(self.current_position)
        self.update_time_labels()
        self.playback_after_id = self.after(int(1000 / self.frame_rate), self.play_step)

    def switch_camera(self, choice: str):
        if self.current_video_clip or self.recording:
            messagebox.showwarning("Warning", "Cannot switch camera while a video is loaded or recording is in progress.")
            self.camera_dropdown.set(f"Camera {self.camera_index}")
            return
        try:
            selected_index = int(choice.split()[-1])
        except (ValueError, IndexError): return 
        if selected_index == self.camera_index: return
        self.stop_live_preview()
        self.camera_index = selected_index
        self.start_live_preview()
        self.status_label.configure(text=f"Live Preview (Camera {self.camera_index})")

    def update_video_frame(self, pos):
        if not self.current_video_clip: return
        try:
            pos = max(0, min(pos, self.video_duration))
            frame_rgb = self.current_video_clip.get_frame(pos)
            self.update_preview_image(frame_rgb)
        except Exception: pass

    def update_preview_image(self, frame_rgb):
        try:
            container_w, container_h = self.preview_container_frame.winfo_width(), self.preview_container_frame.winfo_height()
            if container_w < 2 or container_h < 2: return
            img_h, img_w, _ = frame_rgb.shape
            if img_w == 0 or img_h == 0: return
            aspect_ratio = img_w / img_h
            new_w, new_h = container_w, int(container_w / aspect_ratio)
            if new_h > container_h: new_h, new_w = container_h, int(container_h * aspect_ratio)
            if new_w <= 0 or new_h <= 0: return
            resized_frame = cv2.resize(frame_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
            img_to_show = Image.fromarray(resized_frame)
            img_tk = ImageTk.PhotoImage(image=img_to_show)
            self.video_preview_label.configure(image=img_tk, text=""); self.video_preview_label.image = img_tk
        except Exception: pass

    def import_video(self):
        self.stop_playback()
        path = filedialog.askopenfilename(title="Select a video file", filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All Video Files", "*.mp4 ,*.avi")])
        if not path: return
        self.stop_live_preview()
        self.playback_video_path = path
        self._on_video_load()

    def _on_video_load(self):
        self.status_label.configure(text="Loading video...")
        self.camera_dropdown.configure(state="disabled") 
        self.update_idletasks()
        try:
            self.stop_playback(); pygame.mixer.music.stop(); pygame.mixer.music.unload()
            if self.current_video_clip: self.current_video_clip.close()
            self.current_video_clip = VideoFileClip(self.playback_video_path)
            self.video_duration = self.current_video_clip.duration
            if self.current_video_clip.audio:
                self._cleanup_temp_file("preview")
                self.temp_preview_audio_path = os.path.join(self.temp_dir.name, "preview_audio.wav")
                self.current_video_clip.audio.write_audiofile(self.temp_preview_audio_path, codec='pcm_s16le', logger=None)
                pygame.mixer.music.load(self.temp_preview_audio_path)
                self.set_main_volume(self.voice_volume_slider.get())
            else: self.temp_preview_audio_path = None
            self.update_ui_for_new_video()
            self.after(50, lambda: self.update_video_frame(0))
            self.status_label.configure(text=f"Loaded: {os.path.basename(self.playback_video_path)}")
            messagebox.showinfo("Done Recording", f"Waiting for playback:\n{self.playback_video_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load video: {e}")
            self.current_video_clip = None
            self.start_live_preview()

    def toggle_playback(self):
        if self.is_playing: self.stop_playback()
        else: self.start_playback()

    def on_slider_press(self, event):
        if not self.current_video_clip: return
        self.is_slider_dragging = True
        if self.is_playing: pygame.mixer.music.pause()

    def on_slider_release(self, event):
        if not self.current_video_clip: return
        self.is_slider_dragging = False
        self.playback_start_pos = self.current_position
        self.playback_start_time = time.time()
        if self.is_playing and self.playback_speed == 1.0:
            pygame.mixer.music.set_pos(self.current_position); pygame.mixer.music.unpause()

    def seek_from_slider(self, value):
        if self.current_video_clip and self.video_duration > 0:
            self.current_position = (float(value) / 100) * self.video_duration
            self.update_video_frame(self.current_position)
            self.update_time_labels()
            if self.is_playing and not self.is_slider_dragging and self.playback_speed == 1.0:
                self.playback_start_pos = self.current_position
                self.playback_start_time = time.time()
                pygame.mixer.music.set_pos(self.current_position)

    def start_live_preview(self):
        if not self.available_cameras:
            self.status_label.configure(text="Error: No cameras detected.")
            self.update_preview_image(np.zeros((480, 640, 3), dtype=np.uint8))
            self.video_preview_label.configure(text="No Camera")
            return
        self.camera_dropdown.configure(state="normal")
        self.preview_thread_active = True
        threading.Thread(target=self._live_preview_thread, daemon=True).start()

    def _live_preview_thread(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened(): 
            self.status_label.configure(text=f"Error: Cannot open camera {self.camera_index}.")
            return
        while self.preview_thread_active:
            ret, frame = cap.read()
            if not ret: break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.update_preview_image(frame_rgb)
            time.sleep(1/self.frame_rate)
        cap.release()

    def _record_video_thread(self):
        temp_video_path = os.path.join(self.temp_dir.name, "temp_video.avi")
        cap = cv2.VideoCapture(self.camera_index)
        w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(temp_video_path, fourcc, self.frame_rate, (w, h))
        while self.recording:
            if self.paused_recording: time.sleep(0.1); continue
            ret, frame = cap.read()
            if ret:
                writer.write(frame)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.update_preview_image(frame_rgb)
        writer.release(); cap.release()
    
    def update_ui_for_new_video(self):
        self.seek_slider.configure(to=100, state="normal"); self.seek_slider.set(0)
        self.update_time_labels()
        self.play_button.configure(state="normal"); self.export_button.configure(state="normal")
        self.add_bg_button.configure(state="normal"); self.voice_volume_slider.configure(state="normal")
        self.bg_volume_slider.configure(state="normal"); self.backward_button.configure(state="normal")
        self.forward_button.configure(state="normal")
        self.trim_button.configure(state="normal")
        self.speed_dropdown.configure(state="normal")
        self.remove_background_audio()

    def add_background_audio(self):
        self.stop_playback()
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if not path: return
        try:
            self.status_label.configure(text="Loading background audio..."); self.update_idletasks()
            self.remove_background_audio()
            self.background_audio_path = path
            self.background_audio_sound = pygame.mixer.Sound(path)
            self.background_audio_channel = pygame.mixer.find_channel(True)
            self.set_bg_volume(self.bg_volume_slider.get())
            self.remove_bg_button.configure(state="normal")
            self.status_label.configure(text=f"Added BG Audio: {os.path.basename(path)}")
            messagebox.showinfo("Noise Added", "Background noise added successfully.")
        except Exception as e: self.status_label.configure(text=f"Error loading audio: {e}")

    def remove_background_audio_and_show_popup(self):
        self.remove_background_audio()
        messagebox.showinfo("Noise Removal", "Background noise removed successfully.")

    def remove_background_audio(self):
        if self.background_audio_channel: self.background_audio_channel.stop()
        self.background_audio_sound, self.background_audio_channel, self.background_audio_path = None, None, None
        self.remove_bg_button.configure(state="disabled")
        if self.current_video_clip:
            self.status_label.configure(text=f"Loaded: {os.path.basename(self.playback_video_path)}")

    def set_main_volume(self, value): pygame.mixer.music.set_volume(float(value))
    def set_bg_volume(self, value):
        if self.background_audio_channel: self.background_audio_channel.set_volume(float(value))

    def skip_forward(self):
        if not self.current_video_clip or self.video_duration <= 0: return
        was_playing = self.is_playing
        if was_playing: self.stop_playback()
        self.current_position = min(self.current_position + 5, self.video_duration)
        self.update_video_frame(self.current_position); self.update_time_labels()
        if was_playing: self.start_playback()

    def skip_backward(self):
        if not self.current_video_clip or self.video_duration <= 0: return
        was_playing = self.is_playing
        if was_playing: self.stop_playback()
        self.current_position = max(self.current_position - 5, 0)
        self.update_video_frame(self.current_position); self.update_time_labels()
        if was_playing: self.start_playback()

    def toggle_recording(self):
        if not self.available_cameras:
            messagebox.showerror("Error", "No camera detected. Cannot start recording.")
            return
        if self.recording: self.stop_recording()
        else: self.start_recording()

    def _record_audio_thread(self):
        def callback(indata, frames, time_info, status):
            if not self.paused_recording: self.recorded_audio_frames.append(indata.copy())
        with sd.InputStream(samplerate=self.audio_samplerate, channels=1, callback=callback, dtype='float32'):
            while self.recording: sd.sleep(100)

    def _merge_and_load_recording(self):
        temp_video_path = os.path.join(self.temp_dir.name, "temp_video.avi")
        temp_audio_path = os.path.join(self.temp_dir.name, "temp_audio.wav")
        if not self.recorded_audio_frames or not os.path.exists(temp_video_path):
            self.status_label.configure(text="Recording failed."); self.start_live_preview(); return
        audio_data = np.concatenate(self.recorded_audio_frames, axis=0)
        write_wav(temp_audio_path, self.audio_samplerate, audio_data)
        video_clip = VideoFileClip(temp_video_path); audio_clip = AudioFileClip(temp_audio_path)
        final_clip = video_clip.set_audio(audio_clip)
        output_filename = f"rec_{int(time.time())}.mp4"
        self.playback_video_path = os.path.join(self.temp_dir.name, output_filename)
        final_clip.write_videofile(self.playback_video_path, codec="libx264", audio_codec="aac", logger=None)
        video_clip.close(); audio_clip.close(); final_clip.close()
        self.after(0, self._on_video_load)

    def export_video(self):
        self.stop_playback()
        if not self.current_video_clip: return
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi")])
        if not path: return
        self.status_label.configure(text="Exporting..."); self.update_idletasks()
        self.export_button.configure(state="disabled")
        threading.Thread(target=self._export_worker, args=(path,), daemon=True).start()

    def _export_worker(self, export_path):
        try:
            self.after(0, lambda: self.status_label.configure(text="Preparing final clip..."))
            final_clip = self.current_video_clip.copy()
            if self.background_audio_sound:
                self.after(0, lambda: self.status_label.configure(text="Mixing audio..."))
                bg_audio = AudioFileClip(self.background_audio_path)
                bg_audio = bg_audio.subclip(0, final_clip.duration) if bg_audio.duration > final_clip.duration else bg_audio.fx(AudioFileClip.loop, duration=final_clip.duration)
                bg_audio = bg_audio.volumex(self.bg_volume_slider.get())
                if final_clip.audio:
                    main_audio = final_clip.audio.volumex(self.voice_volume_slider.get())
                    final_audio = CompositeAudioClip([main_audio, bg_audio])
                    final_clip.audio = final_audio
                else: final_clip.audio = bg_audio
                if 'bg_audio' in locals(): bg_audio.close()
                if 'main_audio' in locals(): main_audio.close()
            elif final_clip.audio:
                final_clip.audio = final_clip.audio.volumex(self.voice_volume_slider.get())
            self.after(0, lambda: self.status_label.configure(text=f"Writing video file..."))
            final_clip.write_videofile(export_path, codec='libx264', audio_codec='aac', logger='bar')
            self.after(0, lambda: self.status_label.configure(text=f"Export complete!"))
            self.after(0, lambda: messagebox.showinfo("Export Successful", f"Video exported to:\n{export_path}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Export Error", f"Export failed: {e}"))
            self.after(0, lambda: self.status_label.configure(text=f"Export failed."))
        finally:
            if 'final_clip' in locals() and final_clip: final_clip.close()
            self.after(0, lambda: self.export_button.configure(state="normal"))

    def stop_live_preview(self): 
        self.preview_thread_active = False
        time.sleep(0.1)

    def update_time_labels(self):
        if self.current_video_clip and self.video_duration > 0:
            self.left_time_label.configure(text=self.format_time(self.current_position))
            self.right_time_label.configure(text=self.format_time(self.video_duration))
            if not self.is_slider_dragging:
                slider_val = (self.current_position / self.video_duration) * 100
                self.seek_slider.set(slider_val)
        else:
            self.left_time_label.configure(text="00:00"); self.right_time_label.configure(text="00:00")
            self.seek_slider.set(0)

    def format_time(self, seconds):
        seconds = max(0, seconds)
        mins, secs = divmod(seconds, 60)
        return f"{int(mins):02d}:{int(secs):02d}"

    def _cleanup(self):
        self.preview_thread_active = False
        self.recording = False
        self.stop_playback()
        if self.current_video_clip: self.current_video_clip.close()
        pygame.mixer.quit()
        try:
            self.temp_dir.cleanup()
        except Exception as e:
            print(f"Error cleaning up temp directory: {e}")
        # The App class will handle the final 'destroy' call.

    def _cleanup_temp_file(self, file_type):
        path = None
        if file_type == "preview":
            path, self.temp_preview_audio_path = self.temp_preview_audio_path, None
        if path and os.path.exists(path):
            try: os.remove(path)
            except OSError: pass

# === LANGUAGE DEFINITIONS ===
LANGUAGES = {
    'en': "English",
    'fr': "Français",
    'zu': "isiZulu",
    'es': "Español",
    'zh': "简体中文" 
}

TRANSLATIONS = {
    'project_title': {
        'en': "  V.V.T Software", 'fr': "  Logiciel V.V.T", 'zu': "  Isofthiwe ye-V.V.T",
        'es': "  Software V.V.T", 'zh': "  V.V.T 软件"
    },
    'home': {
        'en': "Home", 'fr': "Accueil", 'zu': "Ekhaya", 'es': "Inicio", 'zh': "主页"
    },
    'voice_recording': {
        'en': "Voice Recording", 'fr': "Enregistrement Vocal", 'zu': "Ukuqoshwa Kwezwi",
        'es': "Grabación de Voz", 'zh': "录音"
    },
    'video_recording': {
        'en': "Video Recording", 'fr': "Enregistrement Vidéo", 'zu': "Ukuqoshwa Kwevidiyo",
        'es': "Grabación de Video", 'zh': "视频录制"
    },
    'exit': {
        'en': "Exit", 'fr': "Quitter", 'zu': "Phuma", 'es': "Salir", 'zh': "退出"
    },
    'language_label': {
         'en': "Language:", 'fr': "Langue :", 'zu': "Ulimi:", 'es': "Idioma:", 'zh': "语言:"
    },
    'appearance_mode': {
        'en': "Appearance Mode:", 'fr': "Mode d'Apparence :", 'zu': "Imodi Yokubukeka:",
        'es': "Modo de Apariencia:", 'zh': "外观模式："
    },
    'light_mode': {
        'en': "Light", 'fr': "Clair", 'zu': "Kukhanya", 'es': "Claro", 'zh': "浅色"
    },
    'dark_mode': {
        'en': "Dark", 'fr': "Sombre", 'zu': "Mnyama", 'es': "Oscuro", 'zh': "深色"
    }
}


# === MAIN APP ===
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Software for Recording Voice & Video and Time Editing")
        self.geometry("1000x700")

        self.current_language = 'en'  # Default language
        self.appearance_mode_reverse_map = {} # To map translated mode back to English

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        if not os.path.exists(image_path):
            os.makedirs(image_path)
            # Create dummy images if they don't exist
            dummy_img = Image.new('RGB', (100, 100), color='grey')
            for img_name in ["audio_video_logo.jpg", "article.jpg", "mic_light.jpg", "mic_dark.jpg", "video_light.jpg", "video_dark.png", "users_dark.png", "users_light.png", "home_dark.png", "home_light.png"]:
                dummy_path = os.path.join(image_path, img_name)
                if not os.path.exists(dummy_path):
                    dummy_img.save(dummy_path)


        self.logo_image = ctk.CTkImage(Image.open(os.path.join(image_path, "audio_video_logo.jpg")), size=(40, 40))
        self.large_image = ctk.CTkImage(Image.open(os.path.join(image_path, "article.jpg")), size=(1500, 800))
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "mic_light.jpg")), dark_image=Image.open(os.path.join(image_path, "mic_dark.jpg")), size=(20, 20))
        self.chats_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "video_light.jpg")), dark_image=Image.open(os.path.join(image_path, "video_dark.png")), size=(20, 20))
        self.users_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "users_dark.png")), dark_image=Image.open(os.path.join(image_path, "users_light.png")), size=(20, 20))
        self.homes_image = ctk.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")), dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))

        # === Navigation Frame ===
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        self.navigation_frame.grid_rowconfigure(5, weight=1) 

        self.navigation_label = ctk.CTkLabel(self.navigation_frame, text="", image=self.logo_image, compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.button_home = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=0, text="", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=self.homes_image, anchor="w", command=self.show_home)
        self.button_home.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=0, text="", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=self.home_image, anchor="w", command=self.show_voice_frame)
        self.home_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.chats_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=0, text="", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=self.chats_image, anchor="w", command=self.show_video_frame)
        self.chats_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.users_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=0, text="", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), image=self.users_image, anchor="w", command=self._on_closing)
        self.users_button.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # === Language and Appearance Controls at the bottom ===
        self.language_label = ctk.CTkLabel(self.navigation_frame, text="", anchor="w")
        self.language_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.language_menu = ctk.CTkOptionMenu(self.navigation_frame, values=list(LANGUAGES.values()), command=self.change_language)
        self.language_menu.grid(row=7, column=0, padx=20, pady=(0, 10))

        self.appearance_mode_label = ctk.CTkLabel(self.navigation_frame, text="", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode = ctk.CTkOptionMenu(self.navigation_frame, values=[], command=self.change_appearance_mode_event)
        self.appearance_mode.grid(row=9, column=0, padx=20, pady=(0, 20))

        # === Main Frame ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.large_image_label = ctk.CTkLabel(self.main_frame, text="", image=self.large_image)
        self.large_image_label.pack(fill="both", expand=True)

        self.voice_recorder_frame = VoiceRecorderAppFrame(self.main_frame)
        self.video_recorder_frame = VideoRecorderAppFrame(self.main_frame)

        self.voice_recorder_frame.pack_forget()
        self.video_recorder_frame.pack_forget()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.update_ui_text() # Set initial text on startup

    def _on_closing(self):
        """Called when the user closes the window or clicks Exit."""
        if hasattr(self, 'video_recorder_frame') and self.video_recorder_frame.winfo_exists():
            self.video_recorder_frame._cleanup()
        self.destroy()

    def change_language(self, language_name: str):
        """Finds language code from name and updates the UI."""
        for code, name in LANGUAGES.items():
            if name == language_name:
                self.current_language = code
                break
        self.update_ui_text()

    def update_ui_text(self):
        """Applies the current language translations to the UI widgets."""
        lang = self.current_language
        
        # Update labels and buttons
        self.navigation_label.configure(text=TRANSLATIONS['project_title'][lang])
        self.button_home.configure(text=TRANSLATIONS['home'][lang])
        self.home_button.configure(text=TRANSLATIONS['voice_recording'][lang])
        self.chats_button.configure(text=TRANSLATIONS['video_recording'][lang])
        self.users_button.configure(text=TRANSLATIONS['exit'][lang])
        self.language_label.configure(text=TRANSLATIONS['language_label'][lang])
        self.appearance_mode_label.configure(text=TRANSLATIONS['appearance_mode'][lang])

        # Update Appearance Mode dropdown options
        light_text = TRANSLATIONS['light_mode'][lang]
        dark_text = TRANSLATIONS['dark_mode'][lang]
        
        # Create a reverse map to find the English value from the translated one
        self.appearance_mode_reverse_map = {
            light_text: "Light",
            dark_text: "Dark"
        }
        
        new_values = [light_text, dark_text]
        self.appearance_mode.configure(values=new_values)
        
        # Set the current selection in the dropdown to the correct translation
        current_mode_english = ctk.get_appearance_mode()
        if current_mode_english == "Light":
            self.appearance_mode.set(light_text)
        else:
            self.appearance_mode.set(dark_text)

    def change_appearance_mode_event(self, translated_mode: str):
        """Changes the appearance mode using the translated selection."""
        # Use the reverse map to get the English value that customtkinter understands
        english_mode = self.appearance_mode_reverse_map.get(translated_mode, "System")
        ctk.set_appearance_mode(english_mode)

    def show_voice_frame(self):
        self.large_image_label.pack_forget()
        self.video_recorder_frame.pack_forget()
        self.voice_recorder_frame.pack(fill="both", expand=True)

    def show_video_frame(self):
        self.large_image_label.pack_forget()
        self.voice_recorder_frame.pack_forget()
        self.video_recorder_frame.pack(fill="both", expand=True)

    def show_home(self):
        self.voice_recorder_frame.pack_forget()
        self.video_recorder_frame.pack_forget()
        self.large_image_label.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()