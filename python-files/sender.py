import psutil
import time
import os
import requests
import csv

SERVER_URL = "http://46.226.160.142:5000/upload"
FILE_TO_SEND = "data.csv"
DEVICE_ID = "2"  # Уникальный ID для каждого устройства

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        'MEM all': int(memory.total / (1024 ** 2)),        # MB
        'MEM usage': int(memory.used / (1024 ** 2)),
        'MEM free': int(memory.available / (1024 ** 2)),
        'MEM percent': round(memory.percent, 2)
    }

def write_metrics_to_csv(filepath):
    cpu = get_cpu_usage()
    mem = get_memory_usage()

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['CPU Usage', cpu])
        writer.writerow(['MEM all', mem['MEM all']])
        writer.writerow(['MEM usage', mem['MEM usage']])
        writer.writerow(['MEM free', mem['MEM free']])
        writer.writerow(['MEM percent', mem['MEM percent']])

def send_file():
    write_metrics_to_csv(FILE_TO_SEND)

    try:
        with open(FILE_TO_SEND, 'rb') as f:
            files = {'file': f}
            data = {'device_id': DEVICE_ID}
            response = requests.post(SERVER_URL, files=files, data=data)
            print("[+] Ответ сервера:", response.json())
    except Exception as e:
        print("[!] Ошибка отправки:", e)

    if os.path.exists(FILE_TO_SEND):
        os.remove(FILE_TO_SEND)

if __name__ == '__main__':
    while True:
        send_file()
        time.sleep(10)
