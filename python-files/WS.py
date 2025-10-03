import requests
import time

def get_user_input(prompt):
    return input(prompt)

def send_message_to_webhook(url, message):
    payload = {'content': message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 204:
        print(f'Mensaje enviado exitosamente: {message}')
    else:
        print(f'Error al enviar el mensaje: {response.status_code}')

if __name__ == "__main__":
    webhook_url = get_user_input('URL: ')
    message = get_user_input('Mensaje: ')
    num_messages = int(get_user_input('Número de mensajes: '))
    interval = int(get_user_input('Intervalo entre mensajes (en segundos): '))

    for _ in range(num_messages):
        send_message_to_webhook(webhook_url, message)
        time.sleep(interval)