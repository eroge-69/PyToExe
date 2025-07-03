import time
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
from pygame import mixer
from comtypes import CLSCTX_ALL
import threading

# Inicializa o mixer
mixer.init()
mixer.music.load("AUDIO_STORY.mp3")

# Função para tocar a música com delay entre os loops
def tocar_com_delay():
    while True:
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.5)
        time.sleep(3)  # Espera 3 segundos antes de reiniciar a música

# Inicia a thread da música
threading.Thread(target=tocar_com_delay, daemon=True).start()

# Função que detecta se outro aplicativo está tocando som
def outro_som_ativo():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() not in ["python.exe", "pythonw.exe"]:
            vol_info = session._ctl.QueryInterface(IAudioMeterInformation)
            if vol_info.GetPeakValue() > 0.01:
                return True
    return False

musica_pausada = False
tempo_silencio = 0

try:
    while True:
        if outro_som_ativo():
            if not musica_pausada:
                mixer.music.pause()
                musica_pausada = True
            tempo_silencio = 0
        else:
            if musica_pausada:
                tempo_silencio += 0.5
                if tempo_silencio >= 2:
                    mixer.music.unpause()
                    musica_pausada = False
        time.sleep(0.5)
except KeyboardInterrupt:
    mixer.music.stop()
