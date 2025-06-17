# smartMaint
import subprocess
import schedule
import time
import os
from datetime import datetime


# Funzione per eseguire uno script Python esterno
def run_script(script_name):
    print(f"\n▶️ Eseguendo {script_name}")
    subprocess.run(["python", script_name], check=True)


# Task orario: estrazione + inferenza
def run_script(script_name):
    base_path = os.path.dirname(
        os.path.abspath(__file__)
    )  # Percorso della cartella dove si trova smartMaint.py
    script_path = os.path.join(
        base_path, script_name
    )  # Costruisce il path assoluto dello script da eseguire
    subprocess.run(["python", script_path], check=True)


def hourly_task():
    run_script("extract_data.py")
    run_script("run_inference.py")


# Task mensile: addestramento modello
def monthly_task():
    today = datetime.today()
    if today.day == 1 and today.hour == 0:
        run_script("train_model.py")


# Pianifica l’estrazione e inferenza ogni ora
schedule.every().hour.at(":00").do(hourly_task)

# Pianifica il controllo per l’addestramento ogni ora
schedule.every().hour.at(":00").do(monthly_task)

print("⏳ smartMaint avviato. In attesa delle pianificazioni...")

# Loop infinito per il task scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
