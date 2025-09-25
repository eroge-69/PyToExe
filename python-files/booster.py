import json
import os
import random
import time
import logging
import hashlib
import base64
import requests
import httpx
import tls_client
from threading import Thread
from colorama import Fore, Style
from pystyle import Colors, Colorate, Center, Write, System

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%H:%M'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
logging.addLevelName(logging.INFO, '[?]')
logging.addLevelName(logging.ERROR, '[X]')
logging.addLevelName(logging.WARNING, '[!]')

try:
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError as e:
    logging.error(f"Configuration file not found: {e}")
    exit()
except json.JSONDecodeError as e:
    logging.error(f"Error decoding JSON: {e}")
    exit()

webhook_url = config.get('webhook_url')
use_log = config.get('use_log')
os.makedirs("data/output", exist_ok=True)
nickname = config.get('customisation', {}).get(
    'nickname', "Boosting tool")
bio = config.get('customisation', {}).get('bio', "Boost like a king!")

banner = r"""
Boost Tool v1.0.0
"""


def print_banner():
    print(Colorate.Vertical(Colors.cyan, Center.XCenter(banner)))


def send_webhook_message(url: str, message: str):
    if not url or not use_log:
        return
    try:
        payload = {"content": message}
        response = requests.post(url, json=payload)
        if response.status_code not in {200, 201, 202, 203, 204, 205, 206, 207}:
            logging.error(
                f"Failed to send webhook message. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Exception occurred while sending webhook message: {e}")


def get_checksum():
    md5_hash = hashlib.md5()
    with open(__file__, "rb") as file:
        md5_hash.update(file.read())
    return md5_hash.hexdigest()


def encoded(path: str, filename: str):
    try:
        image_path = os.path.join(path, filename)
        with open(image_path, "rb") as f:
            img = f.read()
        mime_type = "image/png" if filename.endswith(".png") else "image/gif"
        return f'data:{mime_type};base64,{base64.b64encode(img).decode("ascii")}'
    except Exception as e:
        logging.error(f'Encoding Error: {str(e).capitalize()}')
        return None


def get_stock(filename: str):
    tokens = []
    try:
        with open(filename, "r") as file:
            for line in file.read().splitlines():
                if line.strip():
                    token = line.split(":")[2].strip(
                    ) if ":" in line else line.strip()
                    tokens.append(token)
        return tokens
    except FileNotFoundError:
        logging.error(f"Token file {filename} not found")
        return []


def remove(token: str, filename: str):
    try:
        tokens = get_stock(filename)
        if token in tokens:
            tokens.remove(token)
            with open(filename, "w") as f:
                for t in tokens:
                    f.write(f"{t}\n")
    except Exception as e:
        logging.error(f"Error removing token from {filename}: {str(e)}")


def get_invite_code(inv: str):
    if "discord.gg" in inv:
        return inv.split("discord.gg/")[1]
    if "https://discord.gg" in inv:
        return inv.split("https://discord.gg/")[1]
    if 'discord.com/invite' in inv:
        return inv.split("discord.com/invite/")[1]
    if 'https://discord.com/invite/' in inv:
        return inv.split("https://discord.com/invite/")[1]
    return inv


def check_invite(invite: str):
    try:
        data = requests.get(
            f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true"
        ).json()
        if data.get("code") == 10006:
            return False
        return data["guild"]["id"]
    except Exception as e:
        logging.error(f"Error checking invite: {str(e)}")
        return False


class Booster:
    def __init__(self):
        self.proxy = self.get_proxy()
        self.chrome_v = f'Chrome_{random.randint(110, 118)}'
        self.client = tls_client.Session(
            client_identifier=self.chrome_v,
            random_tls_extension_order=True,
            ja3_string='771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,18-23-45-11-27-10-0-5-13-65037-16-51-17513-43-35-65281-41,25497-29-23-24,0'
        )
        self.locale = random.choice(
            ["en-US", "en-GB", "fr-FR", "de-DE", "es-ES"])
        self.useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.chrome_v}.0.0.0 Safari/537.36'
        self.failed = []
        self.success = []
        self.captcha = []
        self.get_x()
        self.fingerprints()

    def get_x(self):
        properties = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": self.locale,
            "browser_user_agent": self.useragent,
            "browser_version": f'{self.chrome_v}.0.0.0',
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 236850,
            "client_event_source": None
        }
        self.x = base64.b64encode(json.dumps(
            properties, separators=(',', ':')).encode("utf-8")).decode()

    def get_proxy(self):
        try:
            proxy = random.choice(
                open("data/proxies.txt", "r").read().splitlines())
            return f"http://{proxy}"
        except Exception:
            return None

    def fingerprints(self):
        headers = {
            "authority": "discord.com",
            "method": "GET",
            "path": "/api/v9/experiments",
            "scheme": "https",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.useragent
        }
        tries = 0
        while tries < 10:
            try:
                r = httpx.get(
                    'https://discord.com/api/v9/experiments', headers=headers)
                if r.status_code in (200, 201):
                    self.fp = r.json()['fingerprint']
                    self.ckis = f'locale=en-US; __dcfduid={r.cookies.get("__dcfduid")}; __sdcfduid={r.cookies.get("__sdcfduid")}; __cfruid={r.cookies.get("__cfruid")}; _cfuvid={r.cookies.get("_cfuvid")}'
                    return
                logging.error(f'Failed to fetch cookies: {r.text}')
                tries += 1
                time.sleep(1)
            except Exception as e:
                logging.error(
                    f'Failed to execute fingerprint request: {str(e).capitalize()}')
                tries += 1
                time.sleep(1)
        logging.error('Max retries reached for fingerprints')

    def validate_token(self, token):
        headers = {
            "Authorization": str(token),
            "User-Agent": self.useragent,
            "Accept": "*/*"
        }
        kwargs = {"headers": headers}
        if self.proxy:
            kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
        try:
            r = self.client.get(
                "https://discord.com/api/v9/users/@me", **kwargs)
            if r.status_code == 200:
                return True
            logging.error(
                f"Token validation failed: {token[-8:]+'*'*8}, Status: {r.status_code}, Response: {r.text}")
            return False
        except Exception as e:
            logging.error(
                f"Token validation error: {token[-8:]+'*'*8}, {str(e).capitalize()}")
            return False

    def change_nickname(self, token, guild_id, new_nickname):
        if not self.validate_token(token):
            return False
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Fingerprint": self.fp,
            "X-Super-Properties": self.x
        }
        kwargs = {"headers": headers}
        if self.proxy:
            kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
        tkv = token[-8:] + "*" * 8
        try:
            r = self.client.patch(
                f"https://discord.com/api/v9/guilds/{guild_id}/members/@me", json={"nick": new_nickname}, **kwargs)
            if r.status_code == 200:
                logging.info(f"[SUCCESS] Set nickname for {tkv}")
                return True
            elif r.status_code == 429:
                logging.warning(
                    f"Rate limited on nickname change: {tkv}, Retrying in 3s")
                time.sleep(3)
                return False
            else:
                logging.error(
                    f"Nickname change failed: {tkv}, Status: {r.status_code}, Response: {r.text}")
                return False
        except Exception as e:
            logging.error(
                f"Nickname change error: {tkv}, {str(e).capitalize()}")
            return False

    def humanizer(self, token, guild_id):
        if not self.validate_token(token):
            return False
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Fingerprint": self.fp,
            "X-Super-Properties": self.x
        }
        kwargs = {"headers": headers}
        if self.proxy:
            kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
        tkv = token[-8:] + "*" * 8
        ap = []
        try:
            r = self.client.patch(
                f"https://discord.com/api/v9/guilds/{guild_id}/members/@me", json={"nick": nickname}, **kwargs)
            if r.status_code == 200:
                ap.append('Nick')
                logging.info(f"[SUCCESS] Set nickname for {tkv}")
            elif r.status_code == 429:
                logging.warning(
                    f"Rate limited on nickname change: {tkv}, Retrying in 3s")
                time.sleep(3)
                return False
            else:
                logging.error(
                    f"Nickname change failed: {tkv}, Status: {r.status_code}, Response: {r.text}")
        except Exception as e:
            logging.error(
                f"Nickname change error: {tkv}, {str(e).capitalize()}")
            return False
        try:
            r = self.client.patch(
                "https://discord.com/api/v9/users/@me", json={"bio": bio}, **kwargs)
            if r.status_code == 200:
                ap.append('Bio')
                logging.info(f"[SUCCESS] Set bio for {tkv}")
            elif r.status_code == 429:
                logging.warning(
                    f"Rate limited on bio change: {tkv}, Retrying in 3s")
                time.sleep(3)
                return False
            else:
                logging.error(
                    f"Bio change failed: {tkv}, Status: {r.status_code}, Response: {r.text}")
        except Exception as e:
            logging.error(f"Bio change error: {tkv}, {str(e).capitalize()}")
            return False
        avatar = encoded('avatar', 'avatar.png')
        if avatar:
            try:
                r = self.client.patch(
                    "https://discord.com/api/v9/users/@me", json={"avatar": avatar}, **kwargs)
                if r.status_code == 200:
                    ap.append('Avatar')
                    logging.info(f"[SUCCESS] Set avatar for {tkv}")
                elif r.status_code == 429:
                    logging.warning(
                        f"Rate limited on avatar change: {tkv}, Retrying in 3s")
                    time.sleep(3)
                    return False
                else:
                    logging.error(
                        f"Avatar change failed: {tkv}, Status: {r.status_code}, Response: {r.text}")
            except Exception as e:
                logging.error(
                    f"Avatar change error: {tkv}, {str(e).capitalize()}")
                return False
        banner = encoded('banner', 'banner.gif')
        if banner:
            try:
                r = self.client.patch(
                    "https://discord.com/api/v9/users/@me", json={"banner": banner}, **kwargs)
                if r.status_code == 200:
                    ap.append('Banner')
                    logging.info(f"[SUCCESS] Set banner for {tkv}")
                elif r.status_code == 429:
                    logging.warning(
                        f"Rate limited on banner change: {tkv}, Retrying in 3s")
                    time.sleep(3)
                    return False
                else:
                    logging.error(
                        f"Banner change failed: {tkv}, Status: {r.status_code}, Response: {r.text}")
            except Exception as e:
                logging.error(
                    f"Banner change error: {tkv}, {str(e).capitalize()}")
                return False
        return bool(ap)

    def boost(self, token, invite, guild):
        if not self.validate_token(token):
            self.failed.append(token)
            with open("data/output/failed_boosts.txt", "a") as file:
                file.write(token + "\n")
            return False
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Fingerprint": self.fp,
            "X-Super-Properties": self.x
        }
        kwargs = {"headers": headers}
        if self.proxy:
            kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
        slots = self.client.get(
            "https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots",
            **kwargs
        )
        slot_json = slots.json()
        tkv = token[-8:] + "*" * 8
        if slots.status_code == 401 or slots.status_code != 200 or len(slot_json) == 0:
            logging.error(f"[INVALID] {tkv} Invalid/No-Nitro")
            self.failed.append(token)
            with open("data/output/failed_boosts.txt", "a") as file:
                file.write(token + "\n")
            return False
        tries = 0
        while tries < 3:
            try:
                r = self.client.post(
                    f"https://discord.com/api/v9/invites/{invite}", json={}, **kwargs
                )
                if r.status_code == 200:
                    self.guild_id = r.json()["guild"]["id"]
                    boosts_list = [boost["id"] for boost in slot_json]
                    payload = {
                        "user_premium_guild_subscription_slot_ids": boosts_list}
                    headers["method"] = "PUT"
                    headers["path"] = f"/api/v9/guilds/{guild}/premium/subscriptions"
                    boosted = self.client.put(
                        f"https://discord.com/api/v9/guilds/{guild}/premium/subscriptions",
                        json=payload, **kwargs
                    )
                    if boosted.status_code == 201:
                        self.success.append(token)
                        with open("data/output/success.txt", "a") as file:
                            file.write(token + "\n")
                        logging.info(f"Boosts Successful: {tkv}")
                        return True
                    else:
                        logging.error(
                            f"Boosts Failed: {tkv}, Status: {boosted.status_code}, Response: {boosted.text}")
                        self.failed.append(token)
                        with open("data/output/failed_boosts.txt", "a") as file:
                            file.write(token + "\n")
                        return False
                elif r.status_code == 429:
                    logging.warning(
                        f"Rate limited on join: {tkv}, Retrying in {r.json().get('retry_after', 3)}s")
                    time.sleep(r.json().get('retry_after', 3))
                    tries += 1
                else:
                    logging.error(
                        f"Failed to join server: {tkv}, Status: {r.status_code}, Response: {r.text}")
                    self.failed.append(token)
                    with open("data/output/failed_boosts.txt", "a") as file:
                        file.write(token + "\n")
                    return False
            except Exception as e:
                logging.error(f"Boost Error: {tkv}, {str(e).capitalize()}")
                tries += 1
                if tries < 3:
                    time.sleep(3)
        logging.error(f"Boost Failed after retries: {tkv}")
        self.failed.append(token)
        with open("data/output/failed_boosts.txt", "a") as file:
            file.write(token + "\n")
        return False

    def thread(self, invite, tokens, guild):
        threads = []
        for token in tokens:
            t = Thread(target=self.boost, args=(token, invite, guild))
            t.daemon = True
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return {
            "success": self.success,
            "failed": self.failed,
            "captcha": self.captcha
        }


def bot_leaver(guild_id, token):
    headers = {'Authorization': token}
    apilink = f"https://discord.com/api/v9/users/@me/guilds/{guild_id}"
    tries = 0
    tkv = token[-8:] + "*" * 8
    while tries < 3:
        try:
            r = requests.delete(apilink, headers=headers)
            if r.status_code == 204:
                logging.info(f"[SUCCESS] Left server: {tkv}")
                return True
            elif r.status_code == 429:
                logging.warning(
                    f"Rate limited on leave: {tkv}, Retrying in 3s")
                time.sleep(3)
                tries += 1
            else:
                logging.error(
                    f"Failed to leave server: {tkv}, Status: {r.status_code}, Response: {r.text}")
                return False
        except Exception as e:
            logging.error(f"Leave error: {tkv}, {str(e).capitalize()}")
            tries += 1
            if tries < 3:
                time.sleep(3)
    logging.error(f"Failed to leave server after retries: {tkv}")
    return False


def stockamt():
    return len(get_stock("tokens.txt"))


def main():
    print_banner()

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        hex_cyan = "\033[38;2;173;216;230m"
        reset = "\033[0m"

        print(f"{timestamp} {hex_cyan}INFO{reset} 1. Boost Server")
        print(f"{timestamp} {hex_cyan}INFO{reset} 2. Unboost Server")
        print(f"{timestamp} {hex_cyan}INFO{reset} 3. Check Stock")
        print(f"{timestamp} {hex_cyan}INFO{reset} 4. Exit")

        print()

        choice = input(
            f"{timestamp} {hex_cyan}INPUT{reset} Enter your choice --> ").strip()

        if choice == "1":
            invite = input(
                f"{timestamp} {hex_cyan}[>] Enter Discord invite code: {Fore.RESET}").strip()
            amount = input(
                f"{timestamp} {hex_cyan}[>] Boosts Amount (Only Even Numbers, Max 2x Tokens): {Fore.RESET}").strip()
            months = input(
                f"{timestamp} {hex_cyan}[>] How many months (1 or 3): {Fore.RESET}").strip()

            try:
                amount = int(amount)
                months = int(months)
            except ValueError:
                print(
                    f"{Fore.RED}[ERROR]: Amount and months must be numbers.{Fore.RESET}")
                time.sleep(0.8)
                os.system("clear")
                print_banner()
                continue

            if amount % 2 != 0:
                print(
                    f"{Fore.RED}[ERROR]: Number of boosts must be even.{Fore.RESET}")
                time.sleep(0.8)
                os.system("clear")
                print_banner()
                continue
            if months not in [1, 3]:
                print(f"{Fore.RED}[ERROR]: Months must be 1 or 3.{Fore.RESET}")
                time.sleep(0.8)
                os.system("clear")
                print_banner()
                continue

            invite_code = get_invite_code(invite)
            guild_id = check_invite(invite_code)
            if not guild_id:
                print(f"{Fore.RED}[X]: Invalid invite code.{Fore.RESET}")
                time.sleep(0.8)
                os.system("clear")
                print_banner()
                continue

            filename = f"data/{months}m.txt"
            tokens_stock = get_stock("tokens.txt")
            max_boosts = len(tokens_stock) * 2
            required_stock = amount // 2

            if not tokens_stock:
                print(
                    f"{Fore.RED}[X]: No tokens available in tokens.txt.{Fore.RESET}")
                time.sleep(0.8)
                os.system("clear")
                print_banner()
                continue

            if required_stock > len(tokens_stock):
                print(
                    f"{Fore.YELLOW}[!]: Requested boosts ({amount}) exceed available tokens ({len(tokens_stock)}). Using all available tokens for {max_boosts} boosts.{Fore.RESET}")
                required_stock = len(tokens_stock)
                amount = max_boosts

            boost = Booster()
            tokens = tokens_stock[:required_stock]

            print(
                f"\n{Fore.GREEN}[✓] New Process Started for {amount} boosts... at server {invite_code}{Fore.RESET}")
            start = time.time()
            status = boost.thread(invite_code, tokens, guild_id)
            time_taken = round(time.time() - start, 2)

            for token in status['success']:
                remove(token, filename)

            humanized_count = 0
            if config.get('customisation', {}).get('enable', False):
                for token in tokens:
                    if boost.humanizer(token, guild_id):
                        humanized_count += 1

            success_count = len(status['success']) * 2
            failed_count = len(status['failed'])
            captcha_count = len(status['captcha'])

            print(f"{Fore.GREEN}Boost Results:{Fore.RESET}")
            print(f"  Amount: {amount} {months}m Boosts")
            print(f"  Tokens Used: {required_stock}")
            print(f"  Server Link: .gg/{invite_code}")
            print(f"  Succeeded Boosts: {success_count}")
            print(f"  Failed Boosts: {failed_count}")
            print(f"  Captcha Issues: {captcha_count}")
            print(f"  Humanized Tokens: {humanized_count}")
            print(f"  Time Taken: {time_taken} seconds")
            print(f"  Successful Tokens: {status['success']}")
            print(f"  Failed Tokens: {status['failed']}")
            print(f"  Captcha Tokens: {status['captcha']}")
            time.sleep(3)
            os.system("clear")
            print_banner()
            if webhook_url and use_log:
                message = (f"**Boost Results**\n"
                           f"Amount: {amount} {months}m Boosts\n"
                           f"Tokens Used: {required_stock}\n"
                           f"Server Link: .gg/{invite_code}\n"
                           f"Succeeded Boosts: {success_count}\n"
                           f"Failed Boosts: {failed_count}\n"
                           f"Captcha Issues: {captcha_count}\n"
                           f"Humanized Tokens: {humanized_count}\n"
                           f"Time Taken: {time_taken}s\n"
                           f"Successful Tokens: {status['success']}\n"
                           f"Failed Tokens: {status['failed']}\n"
                           f"Captcha Tokens: {status['captcha']}")
                send_webhook_message(webhook_url, message)
            continue

        elif choice == "2":
            guild_id = input(
                f"{timestamp} {hex_cyan}[INPUT]{reset} Enter Guild ID: {Fore.RESET}").strip()
            tokens = get_stock("tokens.txt")
            if not tokens:
                print(
                    f"{Fore.RED}[X] No tokens found in tokens.txt.{Fore.RESET}")
                time.sleep(0.8)
                os.system("cls")
                print_banner()
                continue
            input(
                f"{timestamp} {hex_cyan}[INPUT]{reset} Press Enter to start mass leave of Discord server...{Fore.RESET}")
            print(
                f"{Fore.YELLOW}Starting unboost process for {len(tokens)} tokens...{Fore.RESET}")
            start = time.time()
            success_count = 0
            failed_count = 0
            for token in tokens:
                if bot_leaver(guild_id, token):
                    success_count += 1
                else:
                    failed_count += 1
            time_taken = round(time.time() - start, 2)
            print(f"{Fore.GREEN}Unboost Results:{Fore.RESET}")
            print(f"Success: {success_count} tokens")
            print(f"Failed: {failed_count} tokens")
            print(f"Time Taken: {time_taken} seconds")
            time.sleep(3)
            os.system("cls")
            print_banner()
            continue

        elif choice == "3":
            print(f"{Fore.YELLOW}Token stock: {stockamt()}{Fore.RESET}")
            input(f"{timestamp} {hex_cyan}INPUT{reset} Press Enter to continue...")
            os.system("clear")
            print_banner()
            continue

        elif choice == "4":
            print(f"{Fore.YELLOW}[EXIT] Exiting Boost Tool...{Fore.RESET}")
            time.sleep(1)
            os._exit(0)


if __name__ == "__main__":
    main()
    main()
