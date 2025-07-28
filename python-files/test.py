import sounddevice as sd
import numpy as np
import soundfile as sf

# Загрузка нужного звука (например, правильный тон)
tone_data, tone_samplerate = sf.read('tone.wav')

# Настройки
threshold = 0.01  # Порог громкости
duration_to_play = 0.2  # секунд
mic_samplerate = 44100
blocksize = 1024

def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata)
    if volume_norm > threshold:
        sd.play(tone_data, tone_samplerate, blocking=False)

# Запуск прослушивания микрофона
with sd.InputStream(callback=audio_callback,
                    channels=1,
                    samplerate=mic_samplerate,
                    blocksize=blocksize):
    print("Слушаю микрофон... Нажмите Ctrl+C для выхода.")
    while True:
        pass