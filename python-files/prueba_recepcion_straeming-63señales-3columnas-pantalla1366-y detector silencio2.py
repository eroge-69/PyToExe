import threading
import queue
import ctypes
import time
import os
import platform
import numpy as np
import ffmpeg

from openal.al import *
from openal.alc import *

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

STREAMS = [
     ("Denia FM", "http://enlaces1.serviciospararadios.es:8000/deniafm"),
    ("Activa FM", "http://enlaces1.serviciospararadios.es:8000/activafm-FM"),
    ("Activa FMaac", "http://enlaces1.serviciospararadios.es:8000/activafm-aac"),
    ("Activa FM ALB", "http://enlaces1.serviciospararadios.es:8000/activafm-albacete"),
    ("Activa FM ALC DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-alicante-DAB"),
    ("Activa FM ALC FM", "http://enlaces1.serviciospararadios.es:8000/activafm-alicante-FM"),
    ("Activa FM BENIDORM", "http://enlaces1.serviciospararadios.es:8000/activafm-benidorm-FM"),
    ("Activa FM CS DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-castellon-DAB"),
    ("Activa FM CS FM", "http://enlaces1.serviciospararadios.es:8000/activafm-castellon-FM"),
    ("Activa FM CSOL", "http://enlaces1.serviciospararadios.es:8000/activafm-costadelsol"),
    ("Activa FM ELCHE DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-elche-DAB"),
    ("Activa FM ELCHE FM", "http://enlaces1.serviciospararadios.es:8000/activafm-elche-FM"),
    ("Activa FM ELDA", "http://enlaces1.serviciospararadios.es:8000/activafm-elda-FM"),
    ("Activa FM GIM21", "http://enlaces1.serviciospararadios.es:8000/activafm-gim21"),
    ("Activa FM LACOSTERA", "http://enlaces1.serviciospararadios.es:8000/activafm-lacostera-FM"),
    ("Activa FM LA RIBERA", "http://enlaces1.serviciospararadios.es:8000/activafm-laribera-FM"),
    ("Activa FM LASAFOR", "http://enlaces1.serviciospararadios.es:8000/activafm-lasafor-FM"),
    ("Activa FM MADRID DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-madrid-DAB"),
    ("Activa FM MAD DAB ibertel", "http://enlaces1.serviciospararadios.es:8000/activafm-madrid-DAB-ibertel"),
    ("Activa FM ML MALLORCA DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-mallorca-DAB"),
    ("Activa FM marinaalta FM", "http://enlaces1.serviciospararadios.es:8000/activafm-marinaalta-FM"),
    ("Activa FM MURCIA DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-murcia-DAB-ibertel"),
    ("Activa FM MURCIA DABibertel", "http://enlaces1.serviciospararadios.es:8000/activafm-murcia-DAB"),
    ("Activa FM ONTcostera FM", "http://enlaces1.serviciospararadios.es:8000/activafm-ontinyent-costera-FM"),
    ("Activa FM VAL DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-valencia-DAB"),
    ("Activa FM VAL DABibertel", "http://enlaces1.serviciospararadios.es:8000/activafm-valencia-DAB-ibertel"),
    ("Activa FM VAL FM", "http://enlaces1.serviciospararadios.es:8000/activafm-valencia-FM"),
    ("Activa FM VAL aac", "http://enlaces1.serviciospararadios.es:8000/activafm-valencia-aac"),
    ("Activa FM YECLA FM", "http://enlaces1.serviciospararadios.es:8000/activafm-yecla-FM"),
    ("Activa FM mp3", "http://enlaces1.serviciospararadios.es:8000/activafm.mp3"),
    ("Activa FM VALENCIA DAB", "http://enlaces1.serviciospararadios.es:8000/activafm-valencia-DAB"),
    ("Bikini ALIC-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-alicante-BR384"),
    ("Bikini Altea-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-altea-BR384"),
    ("Bikini Benidorm-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-benidorm-BR384"),
    ("Bikini cumbre-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-cumbre-BR384"),
    ("Bikini Denia-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-denia-BR384"),
    ("Bikini Elche-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-elche-BR384"),
    ("Bikini Gandia-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-gandia-BR384"),
    ("Bikini Gim21-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-gim21-BR384"),
    ("Bikini Murcia-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-murcia-BR384"),
    ("Bikini Torrevieja-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-torrevieja-BR384"),
    ("Bikini VLC-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-valencia-BR384"),
    ("Bikini VLC acc-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-valencia-acc"),
    ("Bikini Yecla-br384", "http://enlaces1.serviciospararadios.es:8000/bikini-yecla-BR384"),
    ("Bikini FM aac", "http://enlaces1.serviciospararadios.es:8000/bikinifm-aac"),
    ("Bikini FM Albacete DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-albacete-DAB"),
    ("Bikini FM Costasol DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-costadelsol-DAB"),
    ("Bikini FM Elche DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-elche-DAB"),
    ("Bikini FM Gibraltar DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-gibraltar-DAB"),
    ("Bikini FM Madrid DAB ibertel", "http://enlaces1.serviciospararadios.es:8000/bikinifm-madrid-DAB-ibertel"),
    ("Bikini FM Murcia DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-murcia-DAB"),
    ("Bikini FM Murcia DAB  ibertel", "http://enlaces1.serviciospararadios.es:8000/bikinifm-murcia-DAB-ibertel"),
    ("Bikini FM Valencia DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-valencia-DAB"),
    ("Bikini FM Valencia DAB", "http://enlaces1.serviciospararadios.es:8000/bikinifm-valencia-DAB"),
("Bikini FM Mp3", "http://enlaces1.serviciospararadios.es:8000/bikinifm.mp3"),
    ("Comboi FM", "http://enlaces1.serviciospararadios.es:8000/comboi-FM"),
    ("Corazón FM", "http://enlaces1.serviciospararadios.es:8000/corazonfm.mp3"),
    ("Esencia MA", "http://enlaces1.serviciospararadios.es:8000/esencia-marina-alta-FM"),
    ("Europa FM MA", "http://enlaces1.serviciospararadios.es:8000/europafmmarinaalta.mp3"),
    ("Gold FM", "http://enlaces1.serviciospararadios.es:8000/goldfm.mp3"),
    ("Hallo FM", "http://enlaces1.serviciospararadios.es:8000/hallofm-BR384"),
    ("Holapop", "http://enlaces1.serviciospararadios.es:8000/holapop"),
]


vumeter_values = [0 for _ in STREAMS]
audio_queues = [queue.Queue(maxsize=10) for _ in STREAMS]
current_play = {"idx": None}

SILENCE_THRESHOLD = 300            # Nivel RMS para considerar silencio
SILENCE_DURATION_SECONDS = 30     # Duración mínima para alarma silencio prolongado
LOG_PATH = r"C:\log"
LOG_FILE = os.path.join(LOG_PATH, "silencio_prolongado.log")

# Variables para controlar silencio prolongado y logging
silence_start_times = [None for _ in STREAMS]
silenced_logged = [False for _ in STREAMS]

def init_openal():
    device = alcOpenDevice(None)
    context = alcCreateContext(device, None)
    alcMakeContextCurrent(context)
    return device, context

def create_source():
    source = ctypes.c_uint()
    alGenSources(1, ctypes.byref(source))
    return source

def create_buffers(n):
    buffers = (ctypes.c_uint * n)()
    alGenBuffers(n, buffers)
    return list(buffers)

def fill_buffer(buffer_id, data):
    alBufferData(buffer_id, AL_FORMAT_MONO16, data, len(data), 22050)

def streamer(idx):
    name, url = STREAMS[idx]
    process = (
        ffmpeg.input(url)
            .output('pipe:', format='s16le', acodec='pcm_s16le', ac=1, ar=22050, loglevel='quiet')
            .run_async(pipe_stdout=True)
    )
    chunk = 2048
    while True:
        try:
            data = process.stdout.read(chunk)
            if not data:
                break
            audio = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio.astype(np.float32)**2))
            vumeter_values[idx] = rms
            if current_play["idx"] == idx:
                try:
                    audio_queues[idx].put(data, timeout=0.1)
                except queue.Full:
                    pass
        except Exception as e:
            print(f"[!] Error en stream {name}: {e}")
            break

def audio_player():
    init_openal()
    source = create_source()
    buffers = create_buffers(4)
    buffer_queue = buffers.copy()
    while True:
        idx = current_play["idx"]
        if idx is not None:
            try:
                data = audio_queues[idx].get(timeout=0.1)
            except queue.Empty:
                continue
            processed = ctypes.c_int()
            alGetSourcei(source, AL_BUFFERS_PROCESSED, ctypes.byref(processed))
            while processed.value > 0:
                unbuf = ctypes.c_uint()
                alSourceUnqueueBuffers(source, 1, ctypes.byref(unbuf))
                buffer_queue.append(unbuf.value)
                processed.value -= 1
            if buffer_queue:
                buf_id = buffer_queue.pop(0)
                fill_buffer(buf_id, data)
                alSourceQueueBuffers(source, 1, ctypes.byref(ctypes.c_uint(buf_id)))
                state = ctypes.c_int()
                alGetSourcei(source, AL_SOURCE_STATE, ctypes.byref(state))
                if state.value != AL_PLAYING:
                    alSourcePlay(source)
        else:
            time.sleep(0.1)

def switch_play(idx):
    current_play["idx"] = idx
    for q in audio_queues:
        with q.mutex:
            q.queue.clear()
    print(f"Ahora escuchando: {STREAMS[idx][0]}")

def stop_play():
    current_play["idx"] = None
    for q in audio_queues:
        with q.mutex:
            q.queue.clear()
    print("Reproducción detenida")

def log_silence(idx):
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        nombre, url = STREAMS[idx]
        f.write(f"{timestamp}  [{idx+1:02}]  {nombre}  ({url}) -> Silencio prolongado > {SILENCE_DURATION_SECONDS} seg\n")

def gui():
    global vumeter_widgets, label_widgets, root
    root = tk.Tk()
    root.title("🎵 Streams con detección de silencio prolongado y log")

    main_frame = tk.Frame(root)
    main_frame.pack(fill='both', expand=True)

    vumeter_widgets = []
    label_widgets = []
    rows = (len(STREAMS) + 2) // 3

    for i, (nombre, _) in enumerate(STREAMS):
        row = i % rows
        col = i // rows

        frame = tk.Frame(main_frame)
        frame.grid(row=row, column=col, padx=5, pady=2, sticky='w')

        lbl = tk.Label(frame, text=nombre, width=26, anchor='w', font=("Arial", 8))
        lbl.pack(side='left')

        fig = Figure(figsize=(2.0, 0.25), dpi=90)
        ax = fig.add_subplot(111)
        barh = ax.barh([0], [0], color='limegreen')
        ax.set_xlim(0, 12000)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(side='left')

        btn = tk.Button(frame, text="🎧 Escuchar", width=10,
                        command=lambda i=i: switch_play(i))
        btn.pack(side='left', padx=2)

        vumeter_widgets.append((barh, canvas))
        label_widgets.append(lbl)

    stop_btn = tk.Button(root, text="⏹️ Detener audio", width=15, command=stop_play)
    stop_btn.pack(pady=6)

    def update_vumeters():
        current_time = time.time()
        for i, (barh, canvas) in enumerate(vumeter_widgets):
            barh[0].set_width(vumeter_values[i])

            if vumeter_values[i] < SILENCE_THRESHOLD:
                barh[0].set_color('gray')
                label_widgets[i].config(fg='red')

                if silence_start_times[i] is None:
                    silence_start_times[i] = current_time

                elif (current_time - silence_start_times[i] >= SILENCE_DURATION_SECONDS
                      and not silenced_logged[i]):
                    silenced_logged[i] = True
                    log_silence(i)
                    print(f"[LOG] Silencio prolongado en: {STREAMS[i][0]}")

            else:
                barh[0].set_color('limegreen')
                label_widgets[i].config(fg='black')
                silence_start_times[i] = None
                silenced_logged[i] = False

            canvas.draw()

        root.after(100, update_vumeters)

    update_vumeters()
    root.mainloop()

if __name__ == "__main__":
    for i in range(len(STREAMS)):
        threading.Thread(target=streamer, args=(i,), daemon=True).start()
    threading.Thread(target=audio_player, daemon=True).start()
    gui()
