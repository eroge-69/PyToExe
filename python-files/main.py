import asyncio
import random
import curses
import threading
import os
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode

from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

del_file = 0  # 1 – delete after exit

history = []
history_lock = threading.Lock()

def init_color_pairs():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE,  curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK,  curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_BLUE,   curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLACK,  curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_CYAN,   curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(9, curses.COLOR_GREEN,  curses.COLOR_BLACK)
    curses.init_pair(10,curses.COLOR_BLACK,  curses.COLOR_GREEN)
    curses.init_pair(11,curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(12,curses.COLOR_BLACK,  curses.COLOR_YELLOW)

class ChatClient:
    def __init__(self, cipher: Fernet | None):
        self.reader = None
        self.writer = None
        self.username = "u" + "".join(str(random.randint(0,9)) for _ in range(10))
        self.send_queue = asyncio.Queue()
        self.running = True
        self.color_pair = 1
        self.cipher = cipher

    async def connect(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def sender_task(self):
        while self.running:
            try:
                payload = await asyncio.wait_for(self.send_queue.get(), timeout=1.0)
                # payload is already a str ending with \n
                self.writer.write(payload.encode('utf-8'))
                await self.writer.drain()
            except asyncio.TimeoutError:
                continue

    async def receiver_task(self):
        while self.running:
            try:
                raw = await asyncio.wait_for(self.reader.readline(), timeout=1.0)
                if not raw:
                    break
                text = raw.strip().decode('utf-8')
                # Разделяем префикс и тело
                if text.startswith("ENC:"):
                    body = text[4:]
                    try:
                        token = urlsafe_b64decode(body.encode('utf-8'))
                        decrypted = self.cipher.decrypt(token)
                        msg_obj = json.loads(decrypted.decode('utf-8'))
                    except (InvalidToken, ValueError):
                        # Падение декодирования/декрипта — пропускаем сообщение
                        continue
                elif text.startswith("RAW:"):
                    body = text[4:]
                    try:
                        msg_obj = json.loads(body)
                    except json.JSONDecodeError:
                        continue
                else:
                    # Нет префикса — тоже пытаемся как RAW
                    try:
                        msg_obj = json.loads(text)
                    except json.JSONDecodeError:
                        continue
                with history_lock:
                    history.append(msg_obj)

            except asyncio.TimeoutError:
                continue

    async def send_message(self, message_text):
        msg_obj = {
            'username': self.username,
            'message': message_text,
            'color_pair': self.color_pair
        }
        raw = json.dumps(msg_obj).encode('utf-8')
        if self.cipher:
            token = self.cipher.encrypt(raw)
            body = urlsafe_b64encode(token).decode('utf-8')
            payload = f"ENC:{body}\n"
        else:
            body = raw.decode('utf-8')
            payload = f"RAW:{body}\n"
        await self.send_queue.put(payload)

    def stop(self):
        self.running = False
        if self.writer:
            self.writer.close()

def curses_prompt(stdscr, prompt, y, x):
    curses.echo()
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    s = stdscr.getstr(y, x + len(prompt)).decode('utf-8').strip()
    curses.noecho()
    return s

def curses_interface(client: ChatClient):
    def chat_loop(stdscr):
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        init_color_pairs()
        curses.curs_set(1)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        input_buffer = ""
        need_refresh = True

        while client.running:
            h, w = stdscr.getmaxyx()
            if need_refresh:
                stdscr.clear()
                with history_lock:
                    visible = history[-(h-3):]
                for idx, msg in enumerate(visible):
                    text = f"{msg['username']}: {msg['message']}"
                    cp = msg.get('color_pair', 1)
                    stdscr.addstr(idx, 0, text[:w-1], curses.color_pair(cp))
                stdscr.addstr(h-3, 0, "=" * (w-1), curses.color_pair(client.color_pair))
                stdscr.addstr(h-2, 0, f"{client.username} >>> {input_buffer}"[:w-1], curses.color_pair(client.color_pair))
                stdscr.addstr(h-1, 0, f"Messages: {len(history)} | Ctrl+C to exit"[:w-1], curses.color_pair(client.color_pair))
                stdscr.refresh()
                need_refresh = False

            try:
                key = stdscr.get_wch()
                if key in ('\n', '\r', curses.KEY_ENTER):
                    cmd = input_buffer.strip()
                    if cmd == "/color":
                        # Меню выбора цвета
                        stdscr.clear()
                        title = "Выберите цветовую схему (1-12):"
                        stdscr.addstr(1, (w - len(title))//2, title, curses.A_BOLD)
                        last_str_Y = 0
                        for i in range(1, 13):
                            sample = f" Color {i} "
                            y = 2 + i
                            x = (w - len(sample))//2
                            stdscr.addstr(y, x, sample, curses.color_pair(i))
                            stdscr.addstr(y, x + len(sample) + 1, str(i))
                            last_str_Y = y
                        stdscr.addstr(last_str_Y + 2, w//2, "||")
                        stdscr.addstr(last_str_Y + 3, w//2, "||")
                        stdscr.addstr(last_str_Y + 4, w//2, "\\/")
                        stdscr.refresh()

                        selected = ""
                        while True:
                            try:
                                ch = stdscr.get_wch()
                            except curses.error:
                                continue
                            # Если цифра, добавляем в ввод
                            if isinstance(ch, str) and ch.isdigit():
                                selected += ch
                            # Backspace
                            elif ch in (curses.KEY_BACKSPACE, '\x08', '\x7f'):
                                if selected:
                                    selected = selected[:-1]
                            # Enter — подтверждаем выбор
                            elif ch == '\n':
                                if selected.isdigit():
                                    num = int(selected)
                                    if 1 <= num <= 12:
                                        client.color_pair = num
                                break
                            # Esc — выход без изменений
                            elif ch == '\x1b':
                                break
                            else:
                                continue
                            # Обновляем отображение текущего ввода
                            stdscr.move(last_str_Y + 5, 0)
                            stdscr.clrtoeol()
                            stdscr.addstr(last_str_Y + 5, (w - len(selected))//2, selected)
                            stdscr.refresh()

                        cmd = ""
                        input_buffer = ""
                        need_refresh = True

                    elif cmd == "/username":
                        stdscr.clear()
                        title = "Введите новый никнейм"
                        stdscr.addstr(1, (w - len(title))//2, title, curses.A_BOLD)
                        selected = ""
                        while True:
                            try:
                                ch = stdscr.get_wch()
                            except curses.error:
                                continue
                            # Если цифра, добавляем в ввод
                            if isinstance(ch, str) and 32 <= ord(ch) <= 126:
                                selected += ch
                            # Backspace
                            elif ch in (curses.KEY_BACKSPACE, '\x08', '\x7f'):
                                if selected:
                                    selected = selected[:-1]
                            # Enter — подтверждаем выбор
                            elif ch == '\n':
                                if selected:
                                    client.username = selected
                                    break
                            # Esc — выход без изменений
                            elif ch == '\x1b':
                                break
                            else:
                                continue
                            # Обновляем отображение текущего ввода
                            stdscr.move(2, 0)
                            stdscr.clrtoeol()
                            stdscr.addstr(2, (w - len(selected))//2, selected)
                            stdscr.refresh()
                        cmd = ""
                        input_buffer = ""
                        need_refresh = True

                    if cmd:
                        asyncio.run_coroutine_threadsafe(client.send_message(cmd), client.loop)
                    input_buffer = ""
                    need_refresh = True
                elif key in (curses.KEY_BACKSPACE, '\x08', '\x7f'):
                    input_buffer = input_buffer[:-1]
                    need_refresh = True
                elif isinstance(key, str) and ord(key) >= 32:
                    input_buffer += key
                    need_refresh = True
            except curses.error:
                pass
            except KeyboardInterrupt:
                break

            curr = len(history)
            if getattr(chat_loop, 'last_count', None) != curr:
                need_refresh = True
            chat_loop.last_count = curr

        client.stop()

    curses.wrapper(chat_loop)

async def main():
    # Collect connection params
    def collect_params(stdscr):
        curses.curs_set(1)
        stdscr.clear()
        host = curses_prompt(stdscr, "HOST: ", 2, 2)
        port = curses_prompt(stdscr, "PORT: ", 4, 2)
        password = curses_prompt(stdscr, "PASSWORD (empty = no encryption): ", 6, 2)
        stdscr.clear()
        return host, port, password

    host, port_str, password = curses.wrapper(collect_params)
    try:
        port = int(port_str)
    except ValueError:
        print("PORT должен быть числом")
        return

    # Prepare Fernet if password given
    cipher = None
    if password:
        salt = b'static_salt_16b'  # можно задать константу или запросить у пользователя
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        cipher = Fernet(key)

    client = ChatClient(cipher)
    try:
        await client.connect(host, port)
    except Exception as e:
        print(f"Не удалось подключиться: {e}")
        return

    client.loop = asyncio.get_event_loop()
    threading.Thread(target=curses_interface, args=(client,), daemon=True).start()

    sender = asyncio.create_task(client.sender_task())
    receiver = asyncio.create_task(client.receiver_task())

    while sender and receiver and client.running:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
