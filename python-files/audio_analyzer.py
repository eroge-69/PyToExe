# Paste your full audio analyzer code here
import os
import sys
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment

ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
AudioSegment.converter = ffmpeg_path

if len(sys.argv) < 2:
    print("Usage: audio_analyzer.exe <audiofile.wav/mp3>")
    sys.exit(1)

file_path = sys.argv[1]
ext = os.path.splitext(file_path)[1].lower()
if ext not in [".mp3", ".wav"]:
    print("🚫 Only MP3 and WAV files are supported.")
    sys.exit(1)

y, sr = librosa.load(file_path, sr=None)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')

with open("tempo.txt", "w") as f:
    f.write(f"{tempo:.2f}")
with open("onsets.txt", "w") as f:
    f.write(",".join([f"{o:.3f}" for o in onsets]))

plt.figure(figsize=(10, 4))
librosa.display.waveshow(y, sr=sr, alpha=0.6)
plt.vlines(onsets, ymin=-1, ymax=1, color='r', linestyle='--', label='Onsets')
plt.title("Waveform with Onsets")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.legend()
plt.tight_layout()
plt.savefig("waveform_onsets.png")
plt.close()

D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
plt.figure(figsize=(10, 4))
librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format="%+2.0f dB")
plt.title("Spectrogram")
plt.tight_layout()
plt.savefig("spectrogram.png")
plt.close()
