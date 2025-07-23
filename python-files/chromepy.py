import subprocess
import sys
import os

# Ruta del Chrome real renombrado
chrome_real = os.path.join(os.path.dirname(__file__), "chrome-bin", "chrome.exe")

# Parámetros originales recibidos
user_args = sys.argv[1:]

# Inyectamos --no-sandbox y otros flags si quieres
base_args = ["--no-sandbox", "--disable-gpu"]

# Comando completo
full_command = [chrome_real] + base_args + user_args

# Ejecutar el comando
subprocess.Popen(full_command)
