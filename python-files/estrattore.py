import random
import json
import os
import ctypes

FILE_PATH = "numeri_estratti.json"
NUMERO_TOTALE = 353
NUMERI_DA_ESTRARRE = 4

if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as f:
        estratti = json.load(f)
else:
    estratti = []

rimanenti = [n for n in range(1, NUMERO_TOTALE + 1) if n not in estratti]

if len(rimanenti) < NUMERI_DA_ESTRARRE:
    message = "Non ci sono abbastanza numeri rimanenti da estrarre."
else:
    estrazione = random.sample(rimanenti, NUMERI_DA_ESTRARRE)
    estratti.extend(estrazione)
    with open(FILE_PATH, "w") as f:
        json.dump(estratti, f)
    message = f"Numeri estratti: {estrazione}"

# Mostra messaggio popup (finestra)
ctypes.windll.user32.MessageBoxW(0, message, "Estrazione Domande", 0)
