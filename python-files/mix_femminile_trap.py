from pydub import AudioSegment
from pydub.effects import normalize

# Percorsi file (modifica se necessario)
base_path = "base_trap_v3.wav"           # Base trap
vocal_female_path = "voce_femminile.wav" # Voce femminile TTS

# Carica audio
base = AudioSegment.from_wav(base_path)
vocal_female = AudioSegment.from_wav(vocal_female_path)

# Fade in/out
fade_ms = 2000
base = base.fade_in(fade_ms).fade_out(fade_ms)
vocal_female = vocal_female.fade_in(fade_ms).fade_out(fade_ms)

# Regola volumi
base = base - 2
vocal_female = vocal_female + 2

# Simula riverbero semplice con delay di 100ms
def add_reverb(audio, delay_ms=100, decay=0.3):
    silence = AudioSegment.silent(duration=delay_ms)
    delayed = silence + (audio - 10)
    return audio.overlay(delayed, gain_during_overlay=-6)

vocal_female = add_reverb(vocal_female)

# Mixaggio
mix_female = base.overlay(vocal_female)

# Normalizza
mix_female = normalize(mix_female)

# Esporta in mp3
output_file = "trap_femminile_finale.mp3"
mix_female.export(output_file, format="mp3")

print(f"Mixaggio completato! File '{output_file}' creato.")
