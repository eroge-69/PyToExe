import asyncio
import aioping
import sys
import statistics
import platform

THIRD_HOST = 100
OUTPUT_FILE = "alive.txt"

alive_subnets = []


async def ping_host(ip: str, timeout: float, sem: asyncio.Semaphore) -> bool:
    async with sem:
        try:
            await aioping.ping(ip, timeout=timeout)
            print(f"[OK] {ip}")
            return True
        except TimeoutError:
            print(f"[NO] {ip}")
            return False
        except Exception:
            return False


async def scan_prefix(prefix: str, timeout: float, sem: asyncio.Semaphore):
    hosts = [f"{prefix}.1", f"{prefix}.{THIRD_HOST}", f"{prefix}.254"]
    results = await asyncio.gather(*(ping_host(ip, timeout, sem) for ip in hosts))
    if any(results):
        subnet = f"{prefix}.0/24"
        alive_subnets.append(subnet)
        with open(OUTPUT_FILE, "a") as f:
            f.write(subnet + "\n")
        print(f"[ALIVE] {subnet}")


def gen_prefixes(choice):
    if choice == "192":
        for i in range(256):
            yield f"192.168.{i}"
    elif choice == "172":
        for a in range(16, 32):
            for b in range(256):
                yield f"172.{a}.{b}"
    elif choice == "10":
        for a in range(256):
            for b in range(256):
                yield f"10.{a}.{b}"
    else:
        print("[!] Invalid choice")
        sys.exit(1)


async def auto_tune():
    """تست اولیه برای تعیین Timeout و حداکثر کانکارنسی."""
    test_ips = ["8.8.8.8", "1.1.1.1"]
    delays = []
    for ip in test_ips:
        try:
            t = await aioping.ping(ip, timeout=1)
            delays.append(t)
        except:
            pass

    avg_delay = statistics.mean(delays) if delays else 0.3
    timeout = min(max(avg_delay * 3, 0.3), 1.0)

    # محدودیت تعداد پینگ همزمان
    system = platform.system().lower()
    if system == "windows":
        max_concurrency = 200
    else:
        max_concurrency = 800

    print(f"[AUTO] Ping timeout set to {timeout:.2f}s")
    print(f"[AUTO] Max concurrency set to {max_concurrency}")

    return timeout, max_concurrency


async def main():
    choice = input("Which range do you want to scan? (192 / 172 / 10): ").strip()
    prefixes = list(gen_prefixes(choice))
    total = len(prefixes)
    open(OUTPUT_FILE, "w").close()

    timeout, max_concurrency = await auto_tune()
    sem = asyncio.Semaphore(max_concurrency)

    tasks = []
    for i, prefix in enumerate(prefixes, start=1):
        tasks.append(scan_prefix(prefix, timeout, sem))
        if len(tasks) >= max_concurrency * 2:  # جلوگیری از پرشدن حافظه
            await asyncio.gather(*tasks)
            tasks.clear()
            print(f"[PROGRESS] {i}/{total}")

    if tasks:
        await asyncio.gather(*tasks)

    print("\n=== Summary ===")
    if alive_subnets:
        for s in alive_subnets:
            print(s)
    else:
        print("No active subnets found.")
    print(f"\n[+] Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")
        sys.exit(1)
