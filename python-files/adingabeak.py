import configparser
import time
import os
import re
import csv
import sys
from datetime import datetime

if sys.platform.startswith('win'):
    import winsound

# Leer el INI
config = configparser.ConfigParser()
config.read('konfig.ini')

fitxategia = config['orokorra']['fitxategia']
torno_zenbakiak = [int(x.strip()) for x in config['orokorra']['Torno_zenbakiak'].split(',')]
urtea = int(config['orokorra']['urtea'])

# Cargar CSV sin encabezados
csv_path = os.path.join(os.getcwd(), 'txartelak.csv')
personas = []

with open(csv_path, newline='', encoding='latin-1') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        persona = {
            'nombre': row[0],
            'apellidos': row[1],
            'año_nacimiento': int(row[2]),
            'numero_tarjeta': row[3].strip()
        }
        personas.append(persona)

# Preparar vigilancia del log
log_path = os.path.join(os.getcwd(), fitxategia)
patron = re.compile(r"Leída Tarjeta (\w+) en el lector (\d+)\.Socio Identificado")

ultima_mod = None
posicion = 0

print("Vigilando log... Ctrl+C para terminar.")

try:
    while True:
        if os.path.exists(log_path):
            mod_actual = os.path.getmtime(log_path)
            if ultima_mod is None or mod_actual != ultima_mod:
                ultima_mod = mod_actual

                tam_actual = os.path.getsize(log_path)

                with open(log_path, 'r', encoding='utf-8') as f:
                    if posicion > tam_actual:
                        posicion = 0

                    f.seek(posicion)
                    nuevas_lineas = f.readlines()
                    posicion = f.tell()

                for linea in nuevas_lineas:
                    fecha_str = linea[:10]  # Extraer dd/mm/yyyy
                    try:
                        fecha_linea = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                    except ValueError:
                        continue  # línea sin fecha válida, ignorar

                    if fecha_linea != datetime.now().date():
                        continue  # no es la fecha de hoy, ignorar

                    match = patron.search(linea)
                    if match:
                        tarjeta = match.group(1)
                        lector = int(match.group(2))

                        if lector in torno_zenbakiak:
                            persona = next((p for p in personas if p['numero_tarjeta'] == tarjeta), None)
                            if persona and persona['año_nacimiento'] > urtea:
                                mensaje = f"{persona['nombre']} {persona['apellidos']} (ADINGABEA)"
                                print(mensaje)
                                if sys.platform.startswith('win'):
                                    winsound.Beep(1000, 300)
                                else:
                                    print('\a')

        time.sleep(1)

except KeyboardInterrupt:
    print("Programa finalizado por el usuario.")
