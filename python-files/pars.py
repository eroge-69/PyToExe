import requests
import os
import sys
import time
import random
import string
from colorama import init
import pyfiglet
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
import urllib.request

import hashlib, subprocess, re

def _wmic(cls, prop):
    out = subprocess.run(['wmic', cls, 'get', prop], capture_output=True, text=True).stdout.splitlines()
    return [l.strip() for l in out[1:] if l.strip()]

def _linux_file(path):
    try:
        return open(path).read().strip()
    except:
        return ''

def _collect():
    ids = []
    if os.name == 'nt':
        ids += _wmic('memorychip', 'serialnumber')
        ids += _wmic('baseboard',  'serialnumber')
        ids += _wmic('diskdrive',  'serialnumber')
    else:
        ids.append(_linux_file('/sys/class/dmi/id/board_serial'))
        ids.append(_linux_file('/sys/class/dmi/id/product_uuid'))
        try:
            ram = subprocess.check_output(['sudo', 'dmidecode', '-t', '17'], text=True)
            ids += re.findall(r'Serial Number:\s*([^\s]+)', ram)
        except: pass
        try:
            lsblk = subprocess.check_output(['lsblk', '-o', 'UUID'], text=True)
            ids += re.findall(r'[0-9a-fA-F-]{36}', lsblk)
        except: pass
    return ''.join(ids).encode()

def generate_hwid():
    return hashlib.sha256(_collect()).hexdigest().lower()

def fetch_allowed(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        txt = r.read().decode('utf-8', errors='ignore')
    return {line.strip().lower() for line in txt.splitlines() if line.strip()}

def copy_clip(text):
    try:
        import pyperclip; pyperclip.copy(text); return True
    except: pass
    if os.name == 'nt':
        p = subprocess.Popen(['clip'], stdin=subprocess.PIPE); p.communicate(text.encode()); return p.returncode==0
    from shutil import which
    if which('pbcopy'):
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE); p.communicate(text.encode()); return p.returncode==0
    if which('xclip'):
        p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE); p.communicate(text.encode()); return p.returncode==0
    return False

try:
    import pyperclip
except ImportError:
    print("Модуль pyperclip не найден. Устанавливаю...")
    os.system(f"{sys.executable} -m pip install pyperclip")
    import pyperclip

init()

banner_text = "PRCX TOOLS"

# Градиент фиолетовый -> белый (ANSI 256-color)
# Выбраны цвета с кодами 93 (фиолетовый) до 231 (белый)
# Можно расширить или сжать список по желанию
red_vertical_gradient = [
    52, 88, 124, 160, 196  # темнее → ярче
]

def ansi_color_256(code):
    return f'\033[38;5;{code}m'

def print_gradient_line(line):
    length = len(line)
    gradient_len = len(red_vertical_gradient)
    result = ''
    for i, ch in enumerate(line):
        # индекс цвета пропорционален позиции символа
        color_index = int(i / max(length - 1, 1) * (gradient_len - 1))
        color_code = red_vertical_gradient[color_index]
        result += f"{ansi_color_256(color_code)}{ch}"
    result += '\033[0m'
    print(result)

def print_gradient_text(text):
    for line in text.splitlines():
        print_gradient_line(line)

def print_gradient_banner():
    figlet = pyfiglet.Figlet(font="slant")
    ascii_art = figlet.renderText(banner_text)
    for line in ascii_art.splitlines():
        print_gradient_line(line)

# --- Ключи и активация ---

URL = 'https://pastebin.com/raw/K0Kd4QtV' 

def check_hwid() -> bool:
    """Возвращает True, если HWID найден в списке. Иначе сообщает
    пользователю, копирует HWID в буфер и возвращает False."""
    hwid = generate_hwid()

    try:
        allowed = fetch_allowed(URL)
    except Exception as e:
        print(f'Ошибка подключения: {e}')
        return False            # Можно сразу sys.exit(1)

    if hwid in allowed:
        print('✅ HWID найден. Доступ разрешён.')
        return True

    # --- HWID нет в списке ---
    if copy_clip(hwid):
        print('Отправьте HWID разработчику. HWID скопирован в буфер.')
    else:
        print(f'❌ HWID не найден и не удалось скопировать.\nВаш HWID: {hwid}')

    input('Нажмите Enter для выхода...')
    return False                # выходим

def main_menu():
    if not check_hwid():
        sys.exit(0)             # выход, меню не показываем

    # --- основное меню ---
    while True:
        print("\nВыберите режим:")
        print("1 - Парсинг участников")
        print("2 - Инвайтинг пользователей")
        print("0 - Выход")
        choice = input("Введите номер: ").strip()

        if choice == '1':
            run_parser()
        elif choice == '2':
            run_inviter()
        elif choice == '0':
            print("\n👋 Выход из программы...")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

def run_parser():
    try:
        api_id = int(input('API ID: '))
        api_hash = input('API Hash: ')
        group_link = input('Ссылка на чат или @username: ')

        premium_only_input = input('Парсить только пользователей с Telegram Premium? (да/нет): ').strip().lower()
        premium_only = premium_only_input == 'да'

        client = TelegramClient('parser_session', api_id, api_hash)
        client.start()

        chat = client.get_entity(group_link)
        all_participants = []
        offset = 0
        limit = 100

        print("\n⏳ Начинаю парсинг участников...")

        while True:
            participants = client(GetParticipantsRequest(
                chat,
                ChannelParticipantsSearch(''),
                offset,
                limit,
                hash=0
            ))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)
            time.sleep(1)

        with open('users.txt', 'w', encoding='utf-8') as f:
            count_saved = 0
            for user in all_participants:
                is_premium = getattr(user, 'premium', False)
                if premium_only and not is_premium:
                    continue
                username = user.username or 'None'
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                f.write(f'{name} | @{username} | ID: {user.id}\n')
                count_saved += 1

        print(f'\n✅ Результат: {count_saved} пользователей {"с Telegram Premium " if premium_only else ""}спарсено.')
        print("📁 Данные сохранены в users.txt")

    except Exception as e:
        print(f'\n❌ Произошла ошибка: {e}')

def run_inviter():
    try:
        api_id = int(input('API ID: '))
        api_hash = input('API Hash: ')
        source_group = input('Источник (чат с пользователями): ')
        target_group = input('Целевой чат для инвайта: ')

        delay = int(input('Задержка между инвайтами (в секундах): '))
        invites_per_account = int(input('Максимум инвайтов на один аккаунт: '))

        client = TelegramClient('inviter_session', api_id, api_hash)
        client.start()

        source = client.get_entity(source_group)
        target = client.get_entity(target_group)

        offset = 0
        limit = 100
        invited_users = set()
        errors = 0

        if os.path.exists("invited.txt"):
            with open("invited.txt", "r") as f:
                invited_users = set(line.strip() for line in f.readlines())

        users_to_invite = []

        while True:
            participants = client(GetParticipantsRequest(
                source,
                ChannelParticipantsSearch(''),
                offset,
                limit,
                hash=0
            ))
            if not participants.users:
                break
            users_to_invite.extend(participants.users)
            offset += len(participants.users)
            time.sleep(1)

        invited_count = 0
        skipped = 0

        for user in users_to_invite:
            if not user.username or str(user.id) in invited_users:
                skipped += 1
                continue
            try:
                client(InviteToChannelRequest(target, [user.id]))
                print(f"✅ Приглашён: @{user.username or user.id}")
                invited_users.add(str(user.id))
                invited_count += 1
                with open("invited.txt", "a") as f:
                    f.write(str(user.id) + "\n")
                time.sleep(delay)
                if invited_count >= invites_per_account:
                    print("🔁 Достигнут лимит инвайтов. Перезапуск...")
                    break
            except Exception as e:
                print(f"⚠️ Ошибка при инвайте {user.id}: {e}")
                errors += 1
                continue

        print("\n📊 Статистика инвайтинга:")
        print(f"   👥 Всего пользователей для инвайта: {len(users_to_invite)}")
        print(f"   ✅ Успешно приглашено: {invited_count}")
        print(f"   ⏭ Пропущено (уже были): {skipped}")
        print(f"   ❌ Ошибок: {errors}")

    except Exception as e:
        print(f'\n❌ Произошла ошибка при инвайтинге: {e}')

if __name__ == '__main__':
    print_gradient_banner()
    main_menu()
