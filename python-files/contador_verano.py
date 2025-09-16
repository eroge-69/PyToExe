import time
from datetime import datetime, timedelta

# Fecha de inicio del verano (21 de junio del año actual a las 00:00)
now = datetime.now()
year = now.year
summer_start = datetime(year, 6, 21)

# Si ya pasó este 21 de junio, se prepara para el próximo año
if now > summer_start:
    summer_start = datetime(year + 1, 6, 21)

def countdown(to_time):
    try:
        while True:
            now = datetime.now()
            remaining = to_time - now

            if remaining.total_seconds() <= 0:
                print("¡Ya es verano! ☀️")
                break

            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(rem, 60)

            print(f"Faltan {days} días, {hours:02d}:{minutes:02d}:{seconds:02d} para el verano ☀️", end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nContador detenido.")

# Ejecutar el contador
countdown(summer_start)
