import numpy as np
import sounddevice as sd

rate = 8000  # частота дискретизации
t = np.arange(0, rate * 1000)  # 10 секунд

# Формула bytebeat
samples = ((t * 5 & t >> 7) | (t * 3 & t >> 10)) % 256
samples = (samples.astype(np.float32) - 128) / 128  # нормализация в [-1,1]

sd.play(samples, rate)
sd.wait()
