import pyaudio
import wave
import threading
import time
import requests
import io
import tkinter as tk
from tkinter import messagebox

class AudioRecorder:
    def __init__(self, upload_url, segment_duration=30, chunk=1024, channels=1, rate=22050):
        self.upload_url = upload_url
        self.segment_duration = segment_duration
        self.chunk = chunk
        self.channels = channels
        self.rate = rate

        self.audio_interface = pyaudio.PyAudio()
        self.stream = None

        self.is_recording = False
        self.is_paused = False

        self.frames_per_segment = int(self.rate / self.chunk * self.segment_duration)
        self.current_segment_frames = []
        self.segment_count = 0

        self.recording_thread = None

    def record(self):
        while self.is_recording:
            if self.is_paused:
                time.sleep(0.1)
                continue
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.current_segment_frames.append(data)
            if len(self.current_segment_frames) >= self.frames_per_segment:
                self.segment_count += 1
                frames_to_send = self.current_segment_frames.copy()
                self.current_segment_frames = []
                threading.Thread(target=self.save_and_upload_segment, args=(frames_to_send, self.segment_count), daemon=True).start()

    def start(self):
        if self.is_recording:
            return False
        self.stream = self.audio_interface.open(format=pyaudio.paInt16,
                                                channels=self.channels,
                                                rate=self.rate,
                                                input=True,
                                                frames_per_buffer=self.chunk)
        self.is_recording = True
        self.is_paused = False
        self.segment_count = 0
        self.current_segment_frames = []
        self.recording_thread = threading.Thread(target=self.record, daemon=True)
        self.recording_thread.start()
        return True

    def stop(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.recording_thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        if self.current_segment_frames:
            self.segment_count += 1
            self.save_and_upload_segment(self.current_segment_frames, self.segment_count)
            self.current_segment_frames = []

    def save_and_upload_segment(self, frames, segment_number):
        wav_buffer = io.BytesIO()
        wf = wave.open(wav_buffer, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        wav_buffer.seek(0)

        try:
            files = {'file': (f'segment_{segment_number}.wav', wav_buffer, 'audio/wav')}
            response = requests.post(self.upload_url, files=files)
            print(f"Ответ сервера: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Ошибка отправки файла: {e}")

    def toggle_pause(self):
        if not self.is_recording:
            return False
        self.is_paused = not self.is_paused
        return self.is_paused

    def exit(self):
        if self.is_recording:
            self.stop()
        self.audio_interface.terminate()

class RecorderGUI:
    def __init__(self, root, upload_url):
        self.root = root
        self.root.title("Audio Recorder")
        self.root.geometry("360x180")
        self.root.resizable(False, False)
        self.root.configure(bg="#2e2e2e")

        self.recorder = AudioRecorder(upload_url)

        self.status_var = tk.StringVar(value="Статус: остановлено")

        # Шрифты и цвета
        self.font_btn = ("Segoe UI", 11, "bold")
        self.font_status = ("Segoe UI", 10)
        self.color_bg = "#2e2e2e"
        self.color_btn = "#4a90e2"
        self.color_btn_disabled = "#6a8cc9"
        self.color_text = "#ffffff"
        self.color_status = "#d0d0d0"

        # Контейнер для кнопок
        btn_frame = tk.Frame(root, bg=self.color_bg)
        btn_frame.pack(pady=20)

        self.start_button = tk.Button(btn_frame, text="Старт", width=10, font=self.font_btn,
                                      bg=self.color_btn, fg=self.color_text, activebackground="#357ABD",
                                      command=self.start_recording)
        self.start_button.grid(row=0, column=0, padx=10)

        self.pause_button = tk.Button(btn_frame, text="Пауза", width=10, font=self.font_btn,
                                      bg=self.color_btn, fg=self.color_text, activebackground="#357ABD",
                                      state=tk.DISABLED, command=self.pause_recording)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.stop_button = tk.Button(btn_frame, text="Стоп", width=10, font=self.font_btn,
                                     bg=self.color_btn, fg=self.color_text, activebackground="#357ABD",
                                     state=tk.DISABLED, command=self.stop_recording)
        self.stop_button.grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(root, textvariable=self.status_var, font=self.font_status,
                                     bg=self.color_bg, fg=self.color_status)
        self.status_label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        if self.recorder.start():
            self.status_var.set("Статус: запись")
            self.start_button.config(state=tk.DISABLED, bg=self.color_btn_disabled)
            self.pause_button.config(state=tk.NORMAL, text="Пауза", bg=self.color_btn)
            self.stop_button.config(state=tk.NORMAL, bg=self.color_btn)
        else:
            messagebox.showwarning("Внимание", "Запись уже запущена")

    def pause_recording(self):
        paused = self.recorder.toggle_pause()
        if paused:
            self.status_var.set("Статус: пауза")
            self.pause_button.config(text="Продолжить")
        else:
            self.status_var.set("Статус: запись")
            self.pause_button.config(text="Пауза")

    def stop_recording(self):
        self.recorder.stop()
        self.status_var.set("Статус: остановлено")
        self.start_button.config(state=tk.NORMAL, bg=self.color_btn)
        self.pause_button.config(state=tk.DISABLED, text="Пауза", bg=self.color_btn_disabled)
        self.stop_button.config(state=tk.DISABLED, bg=self.color_btn_disabled)

    def on_closing(self):
        if self.recorder.is_recording:
            if messagebox.askokcancel("Выход", "Запись идет. Вы уверены, что хотите выйти?"):
                self.recorder.exit()
                self.root.destroy()
        else:
            self.recorder.exit()
            self.root.destroy()

if __name__ == "__main__":
    UPLOAD_URL = "http://5.253.40.66/upload"
    root = tk.Tk()
    app = RecorderGUI(root, UPLOAD_URL)
    root.mainloop()
