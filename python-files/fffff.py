import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import sounddevice as sd
import numpy as np
import threading
import queue
import time
import keyboard
import wave
import os
import sys

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Озвучивание текста в микрофон")
        self.root.geometry("600x400")
        self.root.attributes('-topmost', True)

        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.stream = None
        self.stream2 = None
        self.engine = None
        self.initialize_engine()

        self.output_devices = self.get_output_devices()
        self.selected_device = sd.default.device[1] if sd.default.device else 0

        self.create_ui()

        self.playback_thread = threading.Thread(target=self.audio_playback_loop, daemon=True)
        self.playback_thread.start()

        keyboard.add_hotkey('alt', self.toggle_window)
        self.is_visible = True

    def initialize_engine(self):
        """Инициализация движка синтеза речи"""
        if self.engine:
            try:
                self.engine.stop()
                del self.engine
            except:
                pass
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.7)

    def get_output_devices(self):
        devices = sd.query_devices()
        output_devices = [(i, dev['name']) for i, dev in enumerate(devices) if dev['max_output_channels'] > 0]
        return output_devices

    def toggle_window(self):
        if self.is_visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.focus_force()
            self.text_entry.focus_set()
        self.is_visible = not self.is_visible

    def create_ui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Введите текст для озвучивания:").pack(anchor=tk.W)
        self.text_entry = tk.Text(frame, height=10, wrap=tk.WORD)
        self.text_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X)

        ttk.Button(buttons, text="Озвучить (Ctrl+Enter)", command=self.speak_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons, text="Остановить (Esc)", command=self.stop_playback).pack(side=tk.LEFT)

        settings = ttk.LabelFrame(frame, text="Настройки", padding="10")
        settings.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(settings, text="Устройство вывода:").grid(row=0, column=0, sticky=tk.W)
        self.device_combobox = ttk.Combobox(settings, values=[d[1] for d in self.output_devices])
        if self.output_devices:
            default_name = sd.query_devices(self.selected_device)['name']
            self.device_combobox.set(default_name)
        self.device_combobox.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        self.device_combobox.bind("<<ComboboxSelected>>", self.on_device_select)

        ttk.Button(settings, text="VB-Cable", command=self.set_vb_cable).grid(row=0, column=2, padx=(5, 0))

        ttk.Label(settings, text="Скорость речи:").grid(row=1, column=0, sticky=tk.W)
        self.speed_slider = ttk.Scale(settings, from_=50, to=300, value=150, command=self.update_speech_rate)
        self.speed_slider.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0))

        ttk.Label(settings, text="Громкость:").grid(row=2, column=0, sticky=tk.W)
        self.volume_slider = ttk.Scale(settings, from_=0, to=1, value=0.7, command=self.update_volume)
        self.volume_slider.grid(row=2, column=1, sticky=tk.EW, padx=(5, 0))

        hotkeys = ttk.LabelFrame(frame, text="Горячие клавиши", padding="10")
        hotkeys.pack(fill=tk.X, pady=(10, 0))
        hotkeys_text = ("Alt - показать/скрыть окно\nCtrl+Enter - озвучить текст\nEsc - остановить")
        ttk.Label(hotkeys, text=hotkeys_text).pack(anchor=tk.W)

        self.root.bind('<Control-Return>', lambda e: self.speak_text())
        self.root.bind('<Return>', lambda e: self.speak_text())
        self.root.bind('<Escape>', lambda e: self.stop_playback())

    def on_device_select(self, event):
        selected_name = self.device_combobox.get()
        for idx, name in self.output_devices:
            if name == selected_name:
                self.selected_device = idx
                break

    def speak_text(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите текст.")
            return

        self.stop_playback()
        time.sleep(0.2)  # Даем время для остановки

        # Переинициализируем движок перед каждым использованием
        self.initialize_engine()

        threading.Thread(target=self.generate_speech, args=(text,), daemon=True).start()
        self.text_entry.delete("1.0", tk.END)

    def generate_speech(self, text):
        filename = "temp_speech.wav"
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            
            # Даем движку время завершить работу
            time.sleep(0.5)
            
            with wave.open(filename, 'rb') as wf:
                channels = wf.getnchannels()
                framerate = wf.getframerate()
                sampwidth = wf.getsampwidth()
                frames = wf.readframes(wf.getnframes())

                dtype = np.int16 if sampwidth == 2 else np.int8
                audio_data = np.frombuffer(frames, dtype=dtype)

                volume = float(self.volume_slider.get())
                if volume != 1.0:
                    audio_data = (audio_data * volume).astype(dtype)

                dev_info = sd.query_devices(self.selected_device)
                out_channels = min(dev_info['max_output_channels'], 2)

                if out_channels == 2 and channels == 1:
                    audio_data = np.column_stack([audio_data, audio_data])

                # Очищаем очередь перед добавлением новых данных
                while not self.audio_queue.empty():
                    self.audio_queue.get_nowait()
                    
                # Разбиваем данные на блоки и добавляем в очередь
                block_size = 1024 * out_channels
                for i in range(0, len(audio_data), block_size):
                    self.audio_queue.put((audio_data[i:i+block_size], framerate))
                
                # Сигнал окончания воспроизведения
                self.audio_queue.put((None, None))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка озвучки: {str(e)}")
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    def audio_playback_loop(self):
        while True:
            try:
                data, rate = self.audio_queue.get()

                if data is None:
                    self.close_streams()
                    self.is_playing = False
                    continue

                if not self.is_playing:
                    self.is_playing = True
                    dev_info = sd.query_devices(self.selected_device)
                    channels = min(dev_info['max_output_channels'], 2)
                    
                    self.stream = sd.OutputStream(
                        device=self.selected_device,
                        samplerate=rate,
                        channels=channels,
                        dtype='int16',
                        blocksize=1024
                    )
                    self.stream.start()

                    # Дополнительный поток для устройства по умолчанию
                    default_dev = sd.default.device[1] if sd.default.device else self.selected_device
                    if default_dev != self.selected_device:
                        dev2 = sd.query_devices(default_dev)
                        channels2 = min(dev2['max_output_channels'], 2)
                        self.stream2 = sd.OutputStream(
                            device=default_dev,
                            samplerate=rate,
                            channels=channels2,
                            dtype='int16',
                            blocksize=1024
                        )
                        self.stream2.start()
                    else:
                        self.stream2 = None

                if self.stream:
                    self.stream.write(data)
                if self.stream2:
                    self.stream2.write(data)

            except Exception as e:
                print(f"Ошибка воспроизведения: {str(e)}")
                self.is_playing = False
                self.close_streams()
                time.sleep(0.1)

    def close_streams(self):
        for stream in [self.stream, self.stream2]:
            if stream:
                try:
                    stream.stop()
                    stream.close()
                except:
                    pass
        self.stream = None
        self.stream2 = None

    def stop_playback(self):
        # Очищаем очередь
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Добавляем сигнал остановки
        self.audio_queue.put((None, None))
        
        # Закрываем потоки
        self.close_streams()
        
        # Сбрасываем флаг воспроизведения
        self.is_playing = False

    def update_speech_rate(self, value):
        self.engine.setProperty('rate', float(value))

    def update_volume(self, value):
        self.engine.setProperty('volume', float(value))

    def on_closing(self):
        keyboard.unhook_all()
        self.stop_playback()
        self.root.destroy()
        os._exit(0)

    def set_vb_cable(self):
        for idx, name in self.output_devices:
            if "CABLE" in name.upper():
                self.selected_device = idx
                self.device_combobox.set(name)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()