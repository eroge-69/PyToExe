import pyperclip
import time
import subprocess

último = ""

print("🟢 Esperando nuevo texto en el portapapeles...")

while True:
    actual = pyperclip.paste().strip()
    if actual and actual != último:
        último = actual
        print(f"📋 Nuevo texto detectado: {actual[:40]}...")
        subprocess.run(["python", "C:\\Users\\ehu\\Desktop\\respuesta_chat.py"])
    time.sleep(2)  # Espera 2 segundos
