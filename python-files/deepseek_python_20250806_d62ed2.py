import socket
import sounddevice as sd
import numpy as np

# Настройки
HOST = '0.0.0.0'  # Слушаем все интерфейсы
PORT = 50007
CHUNK = 1024
CHANNELS = 1
RATE = 44100
FORMAT = np.int16

# Создаем сокет
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Ожидание подключения на {HOST}:{PORT}...")
    conn, addr = s.accept()
    print(f"Подключен клиент {addr}")

    def callback(outdata, frames, time, status):
        # Получаем аудиоданные от клиента
        data = conn.recv(frames * CHANNELS * 2)  # 2 байта на sample (int16)
        if len(data) < frames * CHANNELS * 2:
            print("Клиент отключился")
            raise sd.CallbackAbort
        outdata[:] = np.frombuffer(data, dtype=FORMAT).reshape(-1, CHANNELS)
    
    # Запускаем воспроизведение
    with sd.OutputStream(samplerate=RATE, blocksize=CHUNK,
                         channels=CHANNELS, dtype=FORMAT, callback=callback):
        print("Воспроизведение начато. Нажмите Enter для остановки...")
        input()