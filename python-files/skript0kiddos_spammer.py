import aiohttp
import asyncio
import sys
from colorama import Fore, init

init(autoreset=True)

BANNER = f"""
{Fore.RED}███████╗██████╗  █████╗ ███╗   ███╗██╗  ██╗
{Fore.RED}██╔════╝██╔══██╗██╔══██╗████╗ ████║██║ ██╔╝
{Fore.RED}███████╗██████╔╝███████║██╔████╔██║█████╔╝ 
{Fore.RED}╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║██╔═██╗ 
{Fore.RED}███████║██║     ██║  ██║██║ ╚═╝ ██║██║  ██╗
{Fore.RED}╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}► Spammer Tool v3.0 ◄
{Fore.CYAN}► Skript0Kiddos Edition ◄
{Fore.RED}⚠️ Warning: For educational purposes only!
"""

async def send_message(token, channel_id, message):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers=headers,
            json={"content": message},
        ) as resp:
            return resp.status

async def spam_attack(token, channel_id, message, delay=1.0):
    print(f"\n{Fore.GREEN}[+] Attack started! Press CTRL+C to stop")
    try:
        while True:
            status = await send_message(token, channel_id, message)
            print(f"{Fore.CYAN}[→] Sent: {Fore.WHITE}{message[:20]}... {Fore.YELLOW}| Status: {status}")
            await asyncio.sleep(delay)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}")

def main():
    print(BANNER)
    token = input(f"{Fore.YELLOW}[?] Enter Discord Token: ").strip('"')
    channel_id = input("[?] Channel ID: ")
    message = input("[?] Message: ")
    delay = float(input("[?] Delay (seconds): ") or 1.0)

    asyncio.run(spam_attack(token, channel_id, message, delay))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Stopped by user")
        sys.exit(0)