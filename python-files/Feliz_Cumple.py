
import time
import webbrowser

mensaje = """
🎉 Felicidades, acabas de subir de nivel.
+1 Sabiduría
+1 Carisma
+1 Canas
-1 Energía

Recompensa disponible: Presiona ENTER para reclamar.
"""

for letra in mensaje:
    print(letra, end="", flush=True)
    time.sleep(0.03)

input()
webbrowser.open("https://drive.google.com/file/d/1H9K2TXM17ivn0CCc1aI8RNN1mFUlsbmO/view?usp=sharing")
