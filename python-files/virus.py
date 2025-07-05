from pydub import AudioSegment
from pydub.playback import play
import os

def play_at_max_volume(file):
    # Загрузка аудиофайла
    sound = AudioSegment.from_file(file)
    
    # Увеличение громкости до максимума (без искажений)
    # Вы можете регулировать коэффициент усиления (в dB)
    sound = sound + 20  # Увеличение на 20 dB
    
    print(f"Воспроизведение {file} на максимальной громкости")
    play(sound)

music_file = "music.mp3"

try:
    play_at_max_volume(music_file)
except FileNotFoundError:
    print(f"Ошибка: файл {music_file} не найден!")
except Exception as e:
    print(f"Ошибка воспроизведения: {e}")