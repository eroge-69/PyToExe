from telethon.sync import TelegramClient
import sys
# Inserisci le tue credenziali API di Telegram
api_id = '85755'
api_hash = '1a0483a9a4aed1008b773d11112d300c'
client = TelegramClient('anon', api_id, api_hash)
me_phone = '+393891476048'
password = '28121985'
# Nome sessione
with TelegramClient('Daniele', api_id, api_hash) as client:
    # Sostituisci 'chat_username' con il nome utente o ID della chat
    for message in client.iter_messages('@GOLDFOREXSIGNALTEAM', limit=2):  # Legge gli ultimi 10 messaggi
        print(f"Mittente: {message.sender_id}, Messaggio: {message.text}")
# Apri un file in modalità scrittura
with open("output.txt", "w") as file:
    # Reindirizza stdout al file
    sys.stdout = file
    print(f"Mittente: {message.sender_id}, Messaggio: {message.text}")
    print("Anche questo sarà salvato!")  
