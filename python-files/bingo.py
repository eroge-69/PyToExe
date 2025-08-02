import requests
import threading
import queue
import re
import os
import sys

BING_URL = "https://www.bing.com/search?q={query}&count=50&first={start}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Threaded URL Parser
def bing_worker(dork_queue, url_set, pages, lock, print_lock):
    while True:
        try:
            dork = dork_queue.get_nowait()
        except queue.Empty:
            return

        for page in range(pages):
            start = page * 50 + 1
            full_url = BING_URL.format(query=dork, start=start)

            try:
                res = requests.get(full_url, headers=HEADERS, timeout=10)
                matches = re.findall(r'https?://[^\s"\'<>]+', res.text)

                with lock:
                    new_links = 0
                    for url in matches:
                        if url not in url_set:
                            url_set.add(url)
                            new_links += 1
                            with print_lock:
                                print(f"[+] {url}")
            except Exception:
                continue

        dork_queue.task_done()


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("\033[1m" + "=" * 50)
    print("              PAIN REAL DORKER")
    print("=" * 50 + "\033[0m")

    dork_file = input("[?] Enter dork file name (e.g. dorks.txt): ").strip()
    while not os.path.isfile(dork_file):
        print("[!] File not found. Try again.")
        dork_file = input("[?] Enter dork file name (e.g. dorks.txt): ").strip()

    try:
        pages = int(input("[?] Enter how many pages per dork to parse: ").strip())
        bots = int(input("[?] Enter number of bots (max 100): ").strip())
        bots = min(max(1, bots), 100)
    except ValueError:
        print("[!] Invalid number entered. Exiting.")
        return

    with open(dork_file, "r", encoding="utf-8") as f:
        dorks = [line.strip() for line in f if line.strip()]

    dork_queue = queue.Queue()
    for dork in dorks:
        dork_queue.put(dork)

    url_set = set()
    lock = threading.Lock()
    print_lock = threading.Lock()
    threads = []

    print(f"\n[+] Starting {bots} bots...\n")

    for _ in range(bots):
        t = threading.Thread(target=bing_worker, args=(dork_queue, url_set, pages, lock, print_lock))
        t.daemon = True
        t.start()
        threads.append(t)

    dork_queue.join()

    print(f"\n[✓] Done! {len(url_set)} unique URLs scraped.\n[+] Saving to URLs.txt ...")

    with open("URLs.txt", "w", encoding="utf-8") as f:
        for url in sorted(url_set):
            f.write(url + "\n")

    print("[✓] Saved successfully to URLs.txt")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.")
        sys.exit(1)