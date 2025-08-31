from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateStatusRequest
from telethon import errors, types, utils
import csv
import os
import time

# ANSI rang kodlari va emoji'lar
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
CHECK = '✅'
CROSS = '❌'
INFO = 'ℹ️'

# API ma'lumotlari
api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'

def remove_phone_number(filename, number):
    new_rows = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] != number:
                new_rows.append(row)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(new_rows)

def remove_session(phones):
    session_file = f"sessions/{phones}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
        print(f"{RED}{CROSS} Ishlamaydigan {session_file} fayli o'chirildi.{RESET}")

def remove_db(phones):
    session_file = f"sessions/{phones}.db"
    if os.path.exists(session_file):
        os.remove(session_file)
        print(f"{RED}{CROSS} Ishlamaydigan {session_file} fayli o'chirildi.{RESET}")

with open('phone.csv', 'r') as f:
    phone_numbers = [row[0] for row in csv.reader(f)]
    successful_count = 0
    for index, phone in enumerate(phone_numbers, start=1):
        phones = utils.parse_phone(phone)
        client = TelegramClient(f"sessions/{phones}", api_id, api_hash)
        try:
            ok = client.connect()
            if client.is_user_authorized():
                successful_count += 1
                print(f"{GREEN}{CHECK} [{index}/{len(phone_numbers)}] - {phone} ishlaydi.{RESET}")
                client.disconnect()
            else:
                client.disconnect()
                remove_session(phones)
                remove_db(phones)
                remove_phone_number('phone.csv', phone)
                print(f"{YELLOW}{INFO} [{index}/{len(phone_numbers)}] - {phone} ishlamaydi va ro'yxatdan o'chirildi.{RESET}")
        except Exception as e:
            print(f"{RED}{CROSS} {phone} nomer bilan bog'liq xatolik: {e}{RESET}")
            continue
