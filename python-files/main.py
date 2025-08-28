

print("Selecione o tipo de dispositivo (1 ou 2):\n1 - MDVR\n2 - Dashcam")
device = int(input())

print("Insira a quantidade de canais de gravação (de 1 a 8 canais):")
channels = int(input())

print("Insira o tempo total (em horas) de gravação por dia:")
record_time = int(input())

print("Selecione a qualidade desejada:\n1 - D1 (10 FPS)\n2 - D2 (25 FPS)\n3 - 720p (10 FPS)\n4 - 720p (25FPS)")
quality = int(input())

if device == 1:
    # Armazenamento em megabytes
    storage = 110000
elif device == 2:
    storage = 230000

if quality == 1:
    # Armazenamento por minuto em MB/min
    storage_per_minute = 2
elif quality == 2:
    storage_per_minute = 5
elif quality == 3:
    storage_per_minute = 6
elif quality == 4:
    storage_per_minute = 14

storage_per_minute = storage_per_minute * channels

storage_time_in_hours = (storage/storage_per_minute)/60
hours1 = int(storage_time_in_hours)
fraction1 = storage_time_in_hours - hours1

storage_time_in_days = storage_time_in_hours/record_time
days = int(storage_time_in_days)
fraction2 = storage_time_in_days - days

minutes = round(fraction1 * 60)
hours2 = round(fraction2 * 24)

print(f"Tempo estimado de armazenamento: {hours1} horas e {minutes} minutos")
print(f"Tempo estimado de armazenamento: {days} dias e {hours2} horas")