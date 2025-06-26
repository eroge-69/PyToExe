import numpy as np
import sounddevice as sd
import soundfile as sf
from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioSamplerApp:
    def __init__(self, master):
        self.master = master
        master.title("Демонстрация дискретизации звука")
        
        # Загрузка файла
        self.load_button = Button(master, text="Загрузить аудио", command=self.load_audio)
        self.load_button.pack()
        
        # Параметры дискретизации
        Label(master, text="Частота дискретизации (Гц):").pack()
        self.sample_entry = Entry(master)
        self.sample_entry.insert(0, "1000")
        self.sample_entry.pack()
        
        # Кнопки управления
        self.play_original = Button(master, text="Исходный звук", command=self.play_original)
        self.play_original.pack()
        
        self.play_sampled = Button(master, text="Дискретизированный", command=self.play_sampled)
        self.play_sampled.pack()
        
        # График
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack()
        
        self.audio_data = None
        self.sample_rate = None

    def load_audio(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if filepath:
            self.audio_data, self.sample_rate = sf.read(filepath)
            if len(self.audio_data.shape) > 1:  # Если стерео, берем один канал
                self.audio_data = self.audio_data[:, 0]
            self.plot_waveform()

    def plot_waveform(self):
        self.ax.clear()
        time = np.arange(len(self.audio_data)) / self.sample_rate
        self.ax.plot(time, self.audio_data, alpha=0.5)
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Амплитуда')
        self.canvas.draw()

    def apply_sampling(self):
        target_rate = int(self.sample_entry.get())
        if target_rate <= 0:
            return None
            
        # Искусственная дискретизация (имитация)
        step = int(self.sample_rate / target_rate)
        sampled = self.audio_data.copy()
        sampled[::step] = 0  # Эффект "ступенек"
        return sampled

    def play_original(self):
        if self.audio_data is not None:
            sd.play(self.audio_data, self.sample_rate)

    def play_sampled(self):
        if self.audio_data is not None:
            sampled = self.apply_sampling()
            if sampled is not None:
                sd.play(sampled, self.sample_rate)
                self.show_sampled_waveform(sampled)

    def show_sampled_waveform(self, sampled):
        self.ax.clear()
        time = np.arange(len(self.audio_data)) / self.sample_rate
        
        # Показываем эффект дискретизации
        self.ax.plot(time, self.audio_data, 'b-', alpha=0.3, label='Исходный')
        self.ax.stem(time[::int(self.sample_rate/int(self.sample_entry.get()))], 
                    sampled[::int(self.sample_rate/int(self.sample_entry.get()))], 
                    linefmt='r-', markerfmt='ro', basefmt=" ", label='Дискретизированный')
        
        self.ax.legend()
        self.canvas.draw()

root = Tk()
app = AudioSamplerApp(root)
root.mainloop()