import pyaudio
import wave
import numpy as np
from datetime import datetime
from pydub import AudioSegment
import os

# Параметри запису
CHUNK = 1024          # розмір блоку семплів
FORMAT = pyaudio.paInt16
CHANNELS = 1          # моно
RATE = 44100          # частота дискретизації
SILENCE_THRESHOLD = 500  # поріг тиші (регулюй під себе)
SILENCE_CHUNKS = 30      # кількість блоків тиші для завершення запису (~0.7 сек)

def listen_and_record():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Прослуховування ввімкнено...")

    while True:
        frames = []
        silence_counter = 0

        # Чекаємо, поки з'явиться звук
        while True:
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()

            if volume > SILENCE_THRESHOLD:
                print("🔊 Звук виявлено, запис...")
                frames.append(data)
                break

        # Записуємо поки є звук
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()

            if volume < SILENCE_THRESHOLD:
                silence_counter += 1
                if silence_counter > SILENCE_CHUNKS:
                    break
            else:
                silence_counter = 0

        # Зберігаємо WAV файл
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        wav_filename = f"{timestamp}.wav"
        with wave.open(wav_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        # Конвертуємо у MP3
        mp3_filename = wav_filename.replace(".wav", ".mp3")
        sound = AudioSegment.from_wav(wav_filename)
        sound.export(mp3_filename, format="mp3")
        os.remove(wav_filename)

        print(f"Збережено: {mp3_filename}")

if __name__ == "__main__":
    listen_and_record()
