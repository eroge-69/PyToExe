import tkinter as tk
from tkinter import ttk
import threading
import csv
import requests
import time
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# Número de threads paralelas
THREADS = 4
seed_counter = 0
start_time = time.time()

# API para consulta de saldo de endereços
API_URL = "https://blockstream.info/api/address/{}"

# Função para obter saldo de um endereço via API
def get_balance(address):
    try:
        r = requests.get(API_URL.format(address), timeout=10)
        if r.status_code == 200:
            data = r.json()
            funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
            spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
            return funded - spent
    except:
        pass
    return 0

# Função para derivar múltiplos endereços de uma seed
def derive_addresses(seed_words, count):
    seed_bytes = Bip39SeedGenerator(seed_words).Generate()
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    addresses = []
    for change in [Bip44Changes.CHAIN_EXT, Bip44Changes.CHAIN_INT]:
        for i in range(count):
            addr = bip44_mst.Purpose().Coin().Account(0).Change(change).AddressIndex(i).PublicKey().ToAddress()
            addresses.append(addr)
    return addresses

# Função executada por cada thread
def worker_thread(word_count, addr_count, stop_flag, update_callback):
    global seed_counter
    mnemo = Mnemonic("english")
    while not stop_flag["stop"]:
        seed_words = mnemo.generate(strength=128 if word_count==12 else 256)
        addresses = derive_addresses(seed_words, addr_count)
        total = sum(get_balance(a) for a in addresses)
        row = (seed_words, total, ", ".join(addresses[:3]) + (" ..." if len(addresses) > 3 else ""))
        seed_counter += 1
        update_callback(row)

# Inicia threads para geração de seeds
def start_generation(word_count, addr_count, stop_flag, update_callback):
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker_thread, args=(word_count, addr_count, stop_flag, update_callback))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

# Atualiza contador de seeds testadas e seeds por segundo
def update_stats():
    elapsed = time.time() - start_time
    sps = seed_counter / elapsed if elapsed > 0 else 0
    stats_var.set(f"Seeds testadas: {seed_counter} | Seeds/segundo: {sps:.2f}")
    root.after(1000, update_stats)

# Função para iniciar a geração de seeds via GUI
def start_thread():
    word_count = 12 if word_var.get() == "12 palavras" else 24
    addr_count = int(addr_count_var.get())
    stop_flag["stop"] = False
    thread = threading.Thread(target=start_generation, args=(word_count, addr_count, stop_flag, add_row))
    thread.start()

# Função para parar a geração
def stop_thread():
    stop_flag["stop"] = True

# Adiciona linha na tabela GUI e salva CSV
def add_row(row):
    tree.insert("", "end", values=row)
    with open("carteiras_resultado.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

# --- Construção da GUI ---
root = tk.Tk()
root.title("Verificador de Seeds BIP39")

frame_top = ttk.Frame(root)
frame_top.pack(pady=5)

ttk.Label(frame_top, text="Tipo de seed:").grid(row=0, column=0, padx=5)
word_var = tk.StringVar(value="12 palavras")
ttk.Radiobutton(frame_top, text="12 palavras", variable=word_var, value="12 palavras").grid(row=0, column=1)
ttk.Radiobutton(frame_top, text="24 palavras", variable=word_var, value="24 palavras").grid(row=0, column=2)

ttk.Label(frame_top, text="Endereços por tipo (externo/interno):").grid(row=1, column=0, padx=5, pady=5)
addr_count_var = tk.StringVar(value="20")
ttk.Entry(frame_top, textvariable=addr_count_var, width=5).grid(row=1, column=1, padx=5)

frame_buttons = ttk.Frame(root)
frame_buttons.pack(pady=5)
ttk.Button(frame_buttons, text="Iniciar", command=start_thread).grid(row=0, column=0, padx=5)
ttk.Button(frame_buttons, text="Parar", command=stop_thread).grid(row=0, column=1, padx=5)

cols = ("Seed BIP39", "Saldo total (satoshis)", "Alguns endereços derivados")
tree = ttk.Treeview(root, columns=cols, show="headings")
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=300 if c=="Seed BIP39" else 200)
tree.pack(fill="both", expand=True, pady=10)

stats_var = tk.StringVar(value="Seeds testadas: 0 | Seeds/segundo: 0.00")
ttk.Label(root, textvariable=stats_var).pack(pady=5)
ttk.Label(root, text="Resultados salvos em carteiras_resultado.csv").pack(pady=5)

stop_flag = {"stop": False}
root.geometry("950x550")

root.after(1000, update_stats)
root.mainloop()
