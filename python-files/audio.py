import pyttsx3
from pydub import AudioSegment, effects
# Texto a convertir
texto = """Bienvenidos lobatos y lobeznas a este portal intergaláctico. Gracias por ayudarnos
en esta misión.
Necesitamos explorar unos planetas aún no explorados, aprender sus características, cómo
es la gente que vive allí,
sus reglas y sus costumbres. ¡Confiamos en que ustedes podrán hacerlo! ¡Que comience la
aventura!"""
# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty("rate", 140) # velocidad más lenta
engine.save_to_file(texto, "mensaje.wav")
engine.runAndWait()
# Cargar audio generado
audio = AudioSegment.from_wav("mensaje.wav")
# Aplicar filtros tipo "espacial/NASA"
audio = effects.low_pass_filter(audio, 3500)
audio = effects.high_pass_filter(audio, 200)
audio = audio + 5 # subir volumen
# Guardar como MP3 final
audio.export("mensaje_espacial.mp3", format="mp3")
print("✅ Archivo generado: mensaje_espacial.mp3")