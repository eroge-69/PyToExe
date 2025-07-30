import tkinter as tk
from tkinter import filedialog, messagebox
from mnemonic import Mnemonic
import bip32utils
import random
import time
import os
import psutil
from datetime import datetime
from threading import Thread
from colorama import Fore, Style, init
import hashlib

init(autoreset=True)

mnemo = Mnemonic("english")

injected_wallets = [
    "DBTQaqHxhBYVFsHQpJ1N5kv5C1SUjYtwSK",
    "D7Y5LK6TLqj4cMbMR2L7zUBHTS2dfAwQrw",
    "A4eJZha1b3FBQsEpACD6usw8EMQzuNTDaT",
    "D9smQop3FrXD7EYmc4DJ6qPYBvnMyb62W3",
    "A3c9fMX3oqs6ow4N3E7ava47GKUn3Qcngf"
]

start_time = None
generated_filename = None
matched_filename = None

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(b):
    n = int.from_bytes(b, 'big')
    res = ''
    while n > 0:
        n, r = divmod(n, 58)
        res = BASE58_ALPHABET[r] + res
    pad = 0
    for byte in b:
        if byte == 0:
            pad += 1
        else:
            break
    return '1' * pad + res

def base58check_encode(payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return base58_encode(payload + checksum)

def generate_wallet():
    # Randomize seed 20 times
    for _ in range(20):
        seed_phrase = mnemo.generate(strength=128)
        seed = mnemo.to_seed(seed_phrase, passphrase="")
        bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
        bip32_child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN) \
                                                      .ChildKey(3 + bip32utils.BIP32_HARDEN) \
                                                      .ChildKey(0 + bip32utils.BIP32_HARDEN) \
                                                      .ChildKey(0) \
                                                      .ChildKey(0)
    private_key = bip32_child_key_obj.WalletImportFormat()

    pubkey = bip32_child_key_obj.PublicKey()
    sha256_pk = hashlib.sha256(pubkey).digest()
    ripe160 = hashlib.new('ripemd160', sha256_pk).digest()
    # Dogecoin address prefix 0x1E
    payload = bytes([0x1E]) + ripe160
    address = base58check_encode(payload)

    return seed_phrase, private_key, address

def generate_fake_wallet():
    seed_phrase = "(injected) " + ' '.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=12))
    private_key = "(injected) " + ''.join(random.choices("abcdef0123456789", k=64))
    return seed_phrase, private_key

def load_target_addresses():
    filepath = filedialog.askopenfilename(title="Select DOGE Target Wallet File")
    if not filepath:
        return set()
    with open(filepath, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_match(seed, privkey, address):
    global matched_filename
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(matched_filename, 'a') as f:
        f.write(f"[{timestamp}]\nAddress: {address}\nSeed: {seed}\nPrivate Key: {privkey}\n\n")

def save_generated(seed, privkey, address):
    global generated_filename
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(generated_filename, 'a') as f:
        f.write(f"[{timestamp}]\nAddress: {address}\nSeed: {seed}\nPrivate Key: {privkey}\n\n")

def scanner(targets, log_text, stats):
    match_count = 0
    counter = 0
    global start_time
    start_time = time.time()

    for wallet in injected_wallets:
        counter += 1
        seed, privkey = generate_fake_wallet()
        if wallet in targets:
            match_count += 1
            save_match(seed, privkey, wallet)
            log_text.insert(tk.END, f"MATCH FOUND! {wallet} [Injected]\n", "match")
        else:
            save_generated(seed, privkey, wallet)
            log_text.insert(tk.END, f"Injected Wallet: {wallet}\n", "injected")

        stats['count'] = counter
        stats['matches'] = match_count
        stats['loaded'] = len(targets)

    while True:
        counter += 1
        seed, privkey, address = generate_wallet()
        save_generated(seed, privkey, address)

        if address in targets:
            match_count += 1
            save_match(seed, privkey, address)
            log_text.insert(tk.END, f"MATCH FOUND! {address}\n", "match")

        log_text.insert(tk.END, f"Generated #{counter}: {address}\n")
        log_text.see(tk.END)

        stats['count'] = counter
        stats['matches'] = match_count
        stats['loaded'] = len(targets)

        time.sleep(0.1)

def update_system_stats(stats_label, stats):
    while True:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        elapsed = int(time.time() - start_time) if start_time else 0
        clock = datetime.now().strftime("%H:%M:%S")
        stats_label.config(text=(
            f"⏱ Time: {clock}   🧠 CPU: {cpu}%   💾 RAM: {ram}%   "
            f"📦 Loaded: {stats['loaded']}   🎲 Generated: {stats['count']}   ✅ Matches: {stats['matches']}   ⏳ Uptime: {elapsed}s"
        ))
        time.sleep(1)

def start_scanning():
    global generated_filename, matched_filename
    targets = load_target_addresses()
    if not targets:
        messagebox.showerror("Error", "No target file selected.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generated_filename = f"generated_{timestamp}.txt"
    matched_filename = f"matched_{timestamp}.txt"

    stats = {'count': 0, 'matches': 0, 'loaded': len(targets)}
    Thread(target=scanner, args=(targets, log_text, stats), daemon=True).start()
    Thread(target=update_system_stats, args=(stats_label, stats), daemon=True).start()

# GUI
root = tk.Tk()
root.title("🐶 DOGE Wallet Hunter GUI")
root.geometry("820x600")

start_btn = tk.Button(root, text="🚀 Start Scanning", command=start_scanning, bg="lime", fg="black", font=("Helvetica", 12, "bold"))
start_btn.pack(pady=10)

stats_label = tk.Label(root, text="Status: Idle", font=("Courier", 10), bg="black", fg="white")
stats_label.pack(fill=tk.X)

log_text = tk.Text(root, wrap=tk.WORD, height=30, bg="black", fg="white")
log_text.pack(fill=tk.BOTH, expand=True)
log_text.tag_config("match", foreground="lime")
log_text.tag_config("injected", foreground="yellow")

root.mainloop()
