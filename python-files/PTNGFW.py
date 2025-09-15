#!/usr/bin/env python3
import requests
import argparse
import time
import os
import json
from tabulate import tabulate
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token.cache"


def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token}, f)


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("token")
    except Exception:
        return None


def get_token(base_url, username, password):
    """Получение токена по логину/паролю"""
    url = f"{base_url}/api/v2/Authorize"
    headers = {"Content-Type": "application/json"}
    body = {"username": username, "password": password}

    try:
        resp = requests.post(url, headers=headers, json=body, verify=False, timeout=10)
        resp.raise_for_status()
        token = resp.json().get("token")
        if not token:
            raise ValueError("Токен не получен")
        save_token(token)
        return token
    except Exception as e:
        print(f"[!] Ошибка авторизации: {e}")
        return None


def fetch_devices(api_url, token):
    """Запрос списка устройств"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    resp = requests.post(api_url, headers=headers, json={}, verify=False, timeout=10)
    if resp.status_code == 401:
        return None  # сигнал обновить токен
    resp.raise_for_status()
    return resp.json()


def print_devices(data):
    if not data or "logicalDevice" not in data:
        print("[!] Нет данных для отображения")
        return

    table = []
    for dev in data["logicalDevice"]:
        name = dev.get("name", "-")
        phys = dev.get("phisicalDevices", [{}])[0]
        address = phys.get("address", "-")
        model = phys.get("model", "-")
        version = phys.get("softwareVersion", "-")
        status = phys.get("connectionState", "-")

        # Контексты
        contexts = []
        for ctx in data.get("virtualContexts", []):
            if ctx.get("logicalDeviceId") == dev.get("id"):
                contexts.append(ctx.get("name", "-"))

        table.append([name, address, model, version, status, ", ".join(contexts)])

    print(tabulate(
        table,
        headers=["Имя", "IP-адрес", "Модель", "Версия ПО", "Статус", "Контексты"],
        tablefmt="pretty"
    ))
    print(f"\nВсего устройств: {data.get('total', 0)}\n")


def main():
    parser = argparse.ArgumentParser(description="PT NGFW Device List Utility")
    parser.add_argument("--base-url", default="https://10.29.19.186",
                        help="Базовый URL NGFW (без /api/v2)")
    parser.add_argument("--username", required=True, help="Логин")
    parser.add_argument("--password", required=True, help="Пароль")
    parser.add_argument("--interval", type=int, default=60,
                        help="Интервал опроса (сек)")
    args = parser.parse_args()

    token = load_token()
    if not token:
        token = get_token(args.base_url, args.username, args.password)
        if not token:
            return

    api_url = f"{args.base_url}/api/v2/ListLogicalDevices"

    while True:
        data = fetch_devices(api_url, token)
        if data is None:  # токен истёк
            print("[*] Обновление токена...")
            token = get_token(args.base_url, args.username, args.password)
            if not token:
                return
            data = fetch_devices(api_url, token)

        print_devices(data)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()