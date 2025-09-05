import subprocess
import requests

def get_installed_apps():
    # PowerShell'i UTF-8 çıkışla çalıştır
    ps_command = 'Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName | ForEach-Object { $_.DisplayName }'
    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True,
        encoding="utf-8",  # UTF-8 ile decode et
        errors="ignore"    # decode edilemeyen karakterleri görmezden gel
    )
    apps = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return apps

WEBHOOK_URL = "https://discord.com/api/webhooks/1413672896261521510/9pX3ChqGVjmUcubiA9mTTmZw4SKarJRgHd7qTf9mzBFo8rXVdKcLIGKPhgWuqgPV1uIV"

def send_to_discord(app_list):
    data = {"content": "Yüklü uygulamalar:\n" + "\n".join(app_list[:50])}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Gönderildi!")
    else:
        print("Hata:", response.status_code, response.text)

apps = get_installed_apps()
send_to_discord(apps)
