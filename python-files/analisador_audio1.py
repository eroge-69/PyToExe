import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import pyaudio
import tkinter as tk
from tkinter import ttk
import queue
import time
from collections import deque

class AudioAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Áudio")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')

        # Configurações de áudio
        self.CHUNK = 1024 * 4
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.p = pyaudio.PyAudio()

        # Variáveis de controle
        self.is_listening = False
        self.current_effect = 0
        self.color_scheme = 0
        self.audio_queue = queue.Queue()
        self.audio_data = np.zeros(self.CHUNK)
        self.histogram_data = deque(maxlen=100)

        # Lista de efeitos
        self.effects = [
            "Espectrograma",
            "Analisador de Espectro em Tempo Real",
            "Analisador de Espectro com Média",
            "FFT",
            "Analisador de Onda",
            "Vetorscópio",
            "Correlação de Fase",
            "Goniômetro",
            "Loudness Meter",
            "Analisador de Faixa de Oitava"
        ]

        # Esquemas de cores
        self.color_schemes = [
            plt.cm.viridis,
            plt.cm.plasma,
            plt.cm.inferno,
            plt.cm.magma,
            plt.cm.coolwarm,
            plt.cm.jet,
            plt.cm.seismic,
            plt.cm.rainbow
        ]

        # Configurar interface
        self.setup_gui()

        # Descobrir dispositivos de áudio
        self.setup_audio_devices()

    def setup_gui(self):
        # Frame de controle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Configurar estilo para fundo escuro com texto preto nos botões
        style = ttk.Style()
        style.configure('TFrame', background='black')
        style.configure('TLabel', background='black', foreground='white')
        style.configure('TButton', background='lightgray', foreground='black')
        style.configure('TCombobox', fieldbackground='gray30', background='gray30', foreground='white')
        #style.configure('TCombobox', fieldbackground='black', background='black', foreground='white')

        # Botão para mudar efeito
        self.effect_btn = ttk.Button(control_frame, text="Próximo Efeito", command=self.next_effect)
        self.effect_btn.pack(side=tk.LEFT, padx=5)

        # Botão para mudar esquema de cores
        self.color_btn = ttk.Button(control_frame, text="Mudar Cores", command=self.next_color_scheme)
        self.color_btn.pack(side=tk.LEFT, padx=5)

        # Dropdown para seleção de dispositivo de áudio
        ttk.Label(control_frame, text="Dispositivo de Áudio:").pack(side=tk.LEFT, padx=5)
        self.audio_device_var = tk.StringVar()
        self.audio_devices_dropdown = ttk.Combobox(control_frame, textvariable=self.audio_device_var)
        self.audio_devices_dropdown.pack(side=tk.LEFT, padx=5)
        self.audio_devices_dropdown.bind('<<ComboboxSelected>>', self.change_audio_device)

        # Botão para iniciar/parar
        self.start_stop_btn = ttk.Button(control_frame, text="Iniciar", command=self.toggle_listening)
        self.start_stop_btn.pack(side=tk.RIGHT, padx=5)

        # Frame para os canvases
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Criar figuras e canvases para os dois canais com fundo cinza claro
        self.fig_left, self.ax_left = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        #self.fig_left, self.ax_left = plt.subplots(figsize=(6, 4), facecolor='black')
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, canvas_frame)
        self.canvas_left.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_right, self.ax_right = plt.subplots(figsize=(6, 4), facecolor='lightgray')
        #self.fig_right, self.ax_right = plt.subplots(figsize=(6, 4), facecolor='black')
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, canvas_frame)
        self.canvas_right.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Atualizar label do efeito atual
        self.effect_label = ttk.Label(self.root, text=f"Efeito: {self.effects[self.current_effect]}")
        self.effect_label.pack(side=tk.BOTTOM, pady=10)

        # Inicialmente, ambos os canvases estão visíveis
        self.canvas_left.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_right.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Variável para controlar a visibilidade do canvas direito
        self.right_canvas_visible = True

    def setup_audio_devices(self):
        # Encontrar todos os dispositivos de áudio disponíveis
        self.audio_devices = []
        default_device = self.p.get_default_input_device_info()

        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.audio_devices.append((i, device_info['name']))

        # Configurar dropdown
        device_names = [f"{i}: {name}" for i, name in self.audio_devices]
        self.audio_devices_dropdown['values'] = device_names

        # Selecionar dispositivo padrão
        if self.audio_devices:
            default_index = next((i for i, (idx, name) in enumerate(self.audio_devices)
                                  if idx == default_device['index']), 0)
            self.audio_devices_dropdown.current(default_index)
            self.selected_device_index = self.audio_devices[default_index][0]

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
            self.start_stop_btn.config(text="Iniciar")
        else:
            self.start_listening()
            self.start_stop_btn.config(text="Parar")

    def start_listening(self):
        self.is_listening = True
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=False,
            frames_per_buffer=self.CHUNK,
            input_device_index=self.selected_device_index,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()
        self.update_plots()

    def stop_listening(self):
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def next_effect(self):
        # Restaurar canvas direito se estava oculto
        if not self.right_canvas_visible:
            self.canvas_right.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self.right_canvas_visible = True
            self.ax_right.set_visible(True)

        self.current_effect = (self.current_effect + 1) % len(self.effects)
        self.effect_label.config(text=f"Efeito: {self.effects[self.current_effect]}")
        self.histogram_data.clear()  # Limpar dados históricos ao mudar de efeito

        # Ocultar canvas direito para efeitos que usam apenas um canvas
        if self.current_effect in [5, 6, 7]:  # Efeitos que usam apenas um canvas
            self.canvas_right.get_tk_widget().pack_forget()
            self.right_canvas_visible = False

    def next_color_scheme(self):
        self.color_scheme = (self.color_scheme + 1) % len(self.color_schemes)

    def change_audio_device(self, event):
        selection = self.audio_devices_dropdown.current()
        if selection >= 0:
            self.selected_device_index = self.audio_devices[selection][0]
            if self.is_listening:
                self.stop_listening()
                self.start_listening()

    def update_plots(self):
        if not self.is_listening:
            return

        try:
            # Obter dados de áudio da fila
            while True:
                try:
                    data = self.audio_queue.get_nowait()
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    # Separar canais esquerdo e direito
                    if self.CHANNELS == 2:
                        self.audio_data_left = audio_data[0::2]
                        self.audio_data_right = audio_data[1::2]
                    else:
                        self.audio_data_left = audio_data
                        self.audio_data_right = audio_data

                except queue.Empty:
                    break

            # Processar e mostrar o efeito selecionado
            self.process_effect()

        finally:
            # Agendar próxima atualização
            self.root.after(30, self.update_plots)

    def process_effect(self):
        # Limpar eixos
        self.ax_left.clear()
        self.ax_right.clear()

        # Configurar fundo dos eixos (cinza mais claro)
        #self.ax_left.set_facecolor('lightgray')
        #self.ax_right.set_facecolor('lightgray')
        self.ax_left.set_facecolor('black')
        self.ax_right.set_facecolor('black')

        # Obter esquema de cores atual
        cmap = self.color_schemes[self.color_scheme]

        # Processar de acordo com o efeito selecionado
        if self.current_effect == 0:  # Espectrograma
            self.plot_spectrogram(self.ax_left, self.audio_data_left, cmap)
            self.plot_spectrogram(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 1:  # Analisador de Espectro em Tempo Real
            self.plot_rt_spectrum(self.ax_left, self.audio_data_left, cmap)
            self.plot_rt_spectrum(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 2:  # Analisador de Espectro com Média
            self.plot_avg_spectrum(self.ax_left, self.audio_data_left, cmap)
            self.plot_avg_spectrum(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 3:  # FFT
            self.plot_fft(self.ax_left, self.audio_data_left, cmap)
            self.plot_fft(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 4:  # Analisador de Onda
            self.plot_waveform(self.ax_left, self.audio_data_left, cmap)
            self.plot_waveform(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 5:  # Vetorscópio
            self.plot_vectorscope(self.ax_left, self.audio_data_left, self.audio_data_right, cmap)

        elif self.current_effect == 6:  # Correlação de Fase
            self.plot_phase_correlation(self.ax_left, self.audio_data_left, self.audio_data_right, cmap)

        elif self.current_effect == 7:  # Goniômetro
            self.plot_goniometer(self.ax_left, self.audio_data_left, self.audio_data_right, cmap)

        elif self.current_effect == 8:  # Loudness Meter
            self.plot_loudness(self.ax_left, self.audio_data_left, cmap)
            self.plot_loudness(self.ax_right, self.audio_data_right, cmap)

        elif self.current_effect == 9:  # Analisador de Faixa de Oitava
            self.plot_octave_bands(self.ax_left, self.audio_data_left, cmap)
            self.plot_octave_bands(self.ax_right, self.audio_data_right, cmap)

        # Atualizar canvases
        self.canvas_left.draw()
        self.canvas_right.draw()

    def plot_spectrogram(self, ax, data, cmap):
        # Implementação básica de espectrograma
        Pxx, freqs, bins, im = ax.specgram(data, NFFT=512, Fs=self.RATE, cmap=cmap)
        ax.set_title('Espectrograma', color='black')
        ax.set_ylabel('Frequência (Hz)', color='black')
        ax.set_xlabel('Tempo (s)', color='black')
        ax.tick_params(colors='black')

    def plot_rt_spectrum(self, ax, data, cmap):
        # Espectro em tempo real
        fft_data = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), 1.0/self.RATE)
        magnitude = np.abs(fft_data) / len(data)

        ax.semilogx(freq, 20 * np.log10(magnitude), color=cmap(0.5))
        ax.set_title('Espectro em Tempo Real', color='black')
        ax.set_xlabel('Frequência (Hz)', color='black')
        ax.set_ylabel('Amplitude (dB)', color='black')
        ax.set_xlim(20, self.RATE/2)


        # >>> Fixar o eixo Y para não ficar subindo/descendo
        ax.set_ylim(-100, 100)



        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_avg_spectrum(self, ax, data, cmap):
        # Espectro com média (implementação simplificada)
        fft_data = np.fft.rfft(data)
        freq = np.fft.rfftfreq(len(data), 1.0/self.RATE)
        magnitude = np.abs(fft_data) / len(data)

        # Manter histórico para média
        self.histogram_data.append(magnitude)
        avg_magnitude = np.mean(self.histogram_data, axis=0) if self.histogram_data else magnitude

        ax.semilogx(freq, 20 * np.log10(avg_magnitude), color=cmap(0.5))
        ax.set_title('Espectro com Média', color='black')
        ax.set_xlabel('Frequência (Hz)', color='black')
        ax.set_ylabel('Amplitude (dB)', color='black')
        ax.set_xlim(20, self.RATE/2)


        # >>> Fixar o eixo Y para não ficar subindo/descendo
        ax.set_ylim(-100, 100)



        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_fft(self, ax, data, cmap):
        # FFT de alta resolução
        fft_data = np.fft.fft(data)
        freq = np.fft.fftfreq(len(data), 1.0/self.RATE)

        # Apenas frequências positivas
        positive_freq = freq[:len(freq)//2]
        positive_fft = np.abs(fft_data[:len(fft_data)//2]) / len(data)

        ax.plot(positive_freq, 20 * np.log10(positive_fft), color=cmap(0.5))
        ax.set_title('FFT de Alta Resolução', color='black')
        ax.set_xlabel('Frequência (Hz)', color='black')
        ax.set_ylabel('Amplitude (dB)', color='black')
        ax.set_xlim(20, self.RATE/2)

        # >>> Fixar o eixo Y para não ficar subindo/descendo
        ax.set_ylim(-70, 70)


        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_waveform(self, ax, data, cmap):
        # Forma de onda
        time_axis = np.linspace(0, len(data)/self.RATE, len(data))
        ax.plot(time_axis, data, color=cmap(0.5))
        ax.set_title('Forma de Onda', color='black')
        ax.set_xlabel('Tempo (s)', color='black')
        ax.set_ylabel('Amplitude', color='black')

        # >>> Fixar o eixo Y para não ficar subindo/descendo
        ax.set_ylim(-3000, 3000)

        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_vectorscope(self, ax, left_data, right_data, cmap):
        # Vetorscópio (relação entre canais) com maior sensibilidade
        # Garantir que os arrays tenham o mesmo tamanho
        min_len = min(len(left_data), len(right_data))
        left_data = left_data[:min_len].astype(np.float32) / 32768.0 * 40  # Aumentar sensibilidade
        right_data = right_data[:min_len].astype(np.float32) / 32768.0 * 40  # Aumentar sensibilidade

        ax.scatter(left_data, right_data, s=1, alpha=0.5, color=cmap(0.5))
        ax.set_title('Vetorscópio', color='black')
        ax.set_xlabel('Canal Esquerdo', color='black')
        ax.set_ylabel('Canal Direito', color='black')
        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(0, color='black', lw=0.5)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)

    def plot_phase_correlation(self, ax, left_data, right_data, cmap):
        # Correlação de fase
        min_len = min(len(left_data), len(right_data))
        left_data = left_data[:min_len].astype(np.float32)
        right_data = right_data[:min_len].astype(np.float32)

        # Calcular correlação
        correlation = np.correlate(left_data, right_data, mode='full')

        # Normalizar para ficar sempre entre -1 e 1
        if np.max(np.abs(correlation)) > 0:
            correlation = correlation / np.max(np.abs(correlation))

        lags = np.arange(-min_len + 1, min_len)

        ax.plot(lags, correlation, color=cmap(0.5))
        ax.set_title('Correlação de Fase', color='black')
        ax.set_xlabel('Atraso (amostras)', color='black')
        ax.set_ylabel('Correlação', color='black')

        # Fixar limites
        ax.set_xlim(-min_len, min_len)
        ax.set_ylim(-1, 1)



        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_goniometer(self, ax, left_data, right_data, cmap):
        # Goniômetro (visualização estéreo) com maior sensibilidade
        min_len = min(len(left_data), len(right_data))
        left_data = left_data[:min_len].astype(np.float32) / 32768.0 * 40  # Aumentar sensibilidade
        right_data = right_data[:min_len].astype(np.float32) / 32768.0 * 40  # Aumentar sensibilidade

        # Calcular soma e diferença
        sum_lr = left_data + right_data
        diff_lr = left_data - right_data

        ax.scatter(sum_lr, diff_lr, s=1, alpha=0.5, color=cmap(0.5))
        ax.set_title('Goniômetro', color='black')
        ax.set_xlabel('Soma (L+R)', color='black')
        ax.set_ylabel('Diferença (L-R)', color='black')
        ax.grid(True, color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(0, color='black', lw=0.5)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)

    def plot_loudness(self, ax, data, cmap):
        # Medidor de loudness (implementação simplificada)
        rms = np.sqrt(np.mean(data**2))
        db = 20 * np.log10(rms / 32768.0) if rms > 0 else -100

        ax.bar(0, db, color=cmap(0.5))
        ax.set_title('Medidor de Loudness', color='black')
        ax.set_ylabel('Loudness (dBFS)', color='black')
        ax.set_ylim(-80, 0)
        ax.set_xlim(-0.5, 0.5)
        ax.text(0, db + 2, f'{db:.1f} dBFS', ha='center', color='black')
        ax.grid(True, axis='y', color='white', alpha=0.3)
        ax.set_xticks([])
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def plot_octave_bands(self, ax, data, cmap):
        # Bandas de oitava (implementação simplificada)
        # Frequências centrais padrão para bandas de oitava
        center_freqs = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

        # Calcular magnitude em cada banda (simplificado)
        fft_data = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), 1.0/self.RATE)
        magnitude = np.abs(fft_data) / len(data)

        band_magnitudes = []
        for cf in center_freqs:
            # Encontrar índices próximos à frequência central
            lower = cf / np.sqrt(2)
            upper = cf * np.sqrt(2)
            indices = np.where((freqs >= lower) & (freqs <= upper))

            if len(indices[0]) > 0:
                band_mag = np.mean(magnitude[indices])
                band_magnitudes.append(20 * np.log10(band_mag) if band_mag > 0 else -100)
            else:
                band_magnitudes.append(-100)

        # Plotar
        x_pos = np.arange(len(center_freqs))
        ax.bar(x_pos, band_magnitudes, color=cmap(0.5))
        ax.set_title('Bandas de Oitava', color='black')
        ax.set_xlabel('Frequência (Hz)', color='black')
        ax.set_ylabel('Amplitude (dB)', color='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(f) for f in center_freqs], color='black')


        # >>> Fixar o eixo Y para não ficar subindo/descendo
        ax.set_ylim(-100, 100)

        ax.grid(True, axis='y', color='white', alpha=0.3)
        ax.tick_params(colors='black')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)

    def __del__(self):
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzer(root)
    root.mainloop()