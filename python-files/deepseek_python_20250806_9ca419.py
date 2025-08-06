import socket
import sounddevice as sd
import numpy as np

# Настройки
HOST = '192.168.1.100'  # IP сервера
PORT = 50007
CHUNK = 1024
CHANNELS = 1
RATE = 44100
FORMAT = np.int16

# Подключаемся к серверу
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Подключено к {HOST}:{PORT}")

    def callback(indata, frames, time, status):
        # Отправляем аудиоданные на сервер
        s.sendall(indata.tobytes())
    
    # Запускаем запись
    with sd.InputStream(samplerate=RATE, blocksize=CHUNK,
                        channels=CHANNELS, dtype=FORMAT, callback=callback):
        print("Запись начата. Нажмите Enter для остановки...")
        input()