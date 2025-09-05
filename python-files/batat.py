import ctypes
from pydub import AudioSegment, playback

user32 = ctypes.windll.user32

while True:
    try:
        user32.MessageBoxW(
            0,
            "Яйце",
            "Яйце",
            0
        )
        a = AudioSegment.from_wav("батат.wav")
        playback.play(a)
    except KeyboardInterrupt:
        break